#!/usr/bin/env node
// Test all connections between frontend and backend

const axios = require('axios');
const io = require('socket.io-client');

const API_BASE = 'http://localhost:8000';
const SOCKET_URL = 'http://localhost:8000';

class ConnectionTester {
  constructor() {
    this.results = {};
  }

  async runAllTests() {
    console.log('>ê Starting Connection Tests...\n');
    
    const tests = [
      { name: 'Backend API', fn: this.testBackendAPI },
      { name: 'WebSocket', fn: this.testWebSocket },
      { name: 'Database', fn: this.testDatabase },
      { name: 'OpenAI API', fn: this.testOpenAI },
      { name: 'Agent Communication', fn: this.testAgents },
      { name: 'End-to-End Flow', fn: this.testEndToEnd }
    ];
    
    for (const test of tests) {
      process.stdout.write(`Testing ${test.name}... `);
      
      try {
        const result = await test.fn.call(this);
        this.results[test.name] = { status: 'PASS', details: result };
        console.log(' PASS');
      } catch (error) {
        this.results[test.name] = { status: 'FAIL', error: error.message };
        console.log(`L FAIL - ${error.message}`);
      }
    }
    
    this.printSummary();
  }

  async testBackendAPI() {
    const response = await axios.get(`${API_BASE}/api/health`);
    if (response.data.status !== 'healthy') {
      throw new Error('Backend not healthy');
    }
    return response.data;
  }

  async testWebSocket() {
    return new Promise((resolve, reject) => {
      const socket = io(SOCKET_URL, {
        transports: ['websocket'],
        timeout: 5000
      });
      
      const timeout = setTimeout(() => {
        socket.disconnect();
        reject(new Error('Connection timeout'));
      }, 5000);
      
      socket.on('connect', () => {
        clearTimeout(timeout);
        socket.disconnect();
        resolve('Connected successfully');
      });
      
      socket.on('connect_error', (error) => {
        clearTimeout(timeout);
        reject(error);
      });
    });
  }

  async testDatabase() {
    const response = await axios.get(`${API_BASE}/api/launch-status`);
    // If we can get launch status, database is working
    if (!response.data.phases) {
      throw new Error('Database query failed');
    }
    return 'Database operational';
  }

  async testOpenAI() {
    const response = await axios.get(`${API_BASE}/api/launch-status`);
    const apiStatus = response.data.phases?.['1_environment_setup']?.completed || [];
    
    if (!apiStatus.includes('openai_key_valid')) {
      throw new Error('OpenAI API key not validated');
    }
    return 'OpenAI API configured';
  }

  async testAgents() {
    const response = await axios.get(`${API_BASE}/api/agents/status`);
    const agents = response.data;
    
    const expectedAgents = ['sarah', 'marcus', 'elena', 'david', 'priya', 'alex'];
    const missingAgents = expectedAgents.filter(name => !agents[name] || agents[name].status !== 'ready');
    
    if (missingAgents.length > 0) {
      throw new Error(`Agents not ready: ${missingAgents.join(', ')}`);
    }
    
    return `All ${expectedAgents.length} agents ready`;
  }

  async testEndToEnd() {
    // Start a test conversation
    const startResponse = await axios.post(`${API_BASE}/api/conversation/start`, {
      query: 'Connection test query',
      test_mode: true
    });
    
    if (!startResponse.data.conversation_id) {
      throw new Error('Failed to start conversation');
    }
    
    const conversationId = startResponse.data.conversation_id;
    
    // Connect to WebSocket and wait for a response
    return new Promise((resolve, reject) => {
      const socket = io(SOCKET_URL, { transports: ['websocket'] });
      let responseReceived = false;
      
      const timeout = setTimeout(() => {
        socket.disconnect();
        if (!responseReceived) {
          reject(new Error('No agent responses received'));
        }
      }, 15000); // 15 second timeout
      
      socket.on('connect', () => {
        socket.emit('join_conversation', { conversation_id: conversationId });
      });
      
      socket.on('agent_response', (data) => {
        responseReceived = true;
        clearTimeout(timeout);
        socket.disconnect();
        resolve(`Received response from ${data.agent}`);
      });
      
      socket.on('error', (error) => {
        clearTimeout(timeout);
        socket.disconnect();
        reject(new Error(`Socket error: ${error}`));
      });
    });
  }

  printSummary() {
    console.log('\n=Ê CONNECTION TEST SUMMARY');
    console.log('==========================');
    
    const passed = Object.values(this.results).filter(r => r.status === 'PASS').length;
    const failed = Object.values(this.results).filter(r => r.status === 'FAIL').length;
    
    console.log(` Passed: ${passed}`);
    console.log(`L Failed: ${failed}`);
    
    if (failed > 0) {
      console.log('\nL FAILED TESTS:');
      Object.entries(this.results).forEach(([name, result]) => {
        if (result.status === 'FAIL') {
          console.log(`   ${name}: ${result.error}`);
        }
      });
    }
    
    const allPassed = failed === 0;
    console.log(`\n${allPassed ? '<‰ ALL TESTS PASSED!' : '   SOME TESTS FAILED'}`);
    
    process.exit(allPassed ? 0 : 1);
  }
}

// Check if backend is running first
axios.get(`${API_BASE}/api/health`)
  .then(() => {
    const tester = new ConnectionTester();
    return tester.runAllTests();
  })
  .catch(() => {
    console.error('L Backend is not running. Start it with: ./scripts/dev-startup.sh');
    process.exit(1);
  });