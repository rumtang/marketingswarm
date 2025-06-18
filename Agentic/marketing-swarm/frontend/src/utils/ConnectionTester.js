import io from 'socket.io-client';

export class ConnectionTester {
  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8001';
    this.tests = [
      { name: 'API Configuration', test: this.testApiConfiguration },
      { name: 'Backend API Ping', test: this.testBackendPing },
      { name: 'Agent Status', test: this.testAgentInitialization },
      { name: 'WebSocket Connection', test: this.testWebSocketConnection },
      { name: 'Conversation Start', test: this.testConversationFlow },
      { name: 'WebSocket Events', test: this.testWebSocketEvents },
      { name: 'Real-time Updates', test: this.testRealTimeUpdates },
      { name: 'Error Handling', test: this.testErrorHandling }
    ];
    this.results = {
      timestamp: new Date().toISOString(),
      tests: {},
      summary: { total: 0, passed: 0, failed: 0 }
    };
  }

  recordTest(testName, passed, details = '') {
    this.results.tests[testName] = {
      passed,
      details,
      timestamp: new Date().toISOString()
    };
    this.results.summary.total++;
    if (passed) {
      this.results.summary.passed++;
    } else {
      this.results.summary.failed++;
    }

    const status = passed ? '✅ PASS' : '❌ FAIL';
    console.log(`${status} - ${testName}`);
    if (details && !passed) {
      console.log(`    Details: ${details}`);
    }
  }

  async runAllTests() {
    console.log('=' + '='.repeat(59));
    console.log('🧪 Marketing Swarm Frontend Connection Tests');
    console.log('=' + '='.repeat(59));
    
    // Reset results
    this.results = {
      timestamp: new Date().toISOString(),
      tests: {},
      summary: { total: 0, passed: 0, failed: 0 }
    };
    
    for (const test of this.tests) {
      try {
        console.log(`\n🔍 Testing: ${test.name}...`);
        const result = await test.test.call(this);
        this.recordTest(test.name, true, result);
      } catch (error) {
        this.recordTest(test.name, false, error.message);
      }
    }

    this.displayTestSummary();
    
    // Save results to localStorage
    localStorage.setItem('connectionTestResults', JSON.stringify(this.results));
    console.log('\n💾 Results saved to localStorage');
    
    return this.results;
  }

  async testApiConfiguration() {
    this.recordTest('API Base URL', !!this.baseUrl, `URL: ${this.baseUrl}`);
    
    try {
      const response = await fetch(this.baseUrl);
      this.recordTest('API URL Reachable', response.ok || response.status === 404, 
        `Status: ${response.status}`);
      return 'API configuration verified';
    } catch (error) {
      throw new Error(`API unreachable: ${error.message}`);
    }
  }

  async testBackendPing() {
    const response = await fetch(`${this.baseUrl}/api/health`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    if (!data.status) throw new Error('Invalid health response');
    return `Status: ${data.status}, Mode: ${data.mode || 'unknown'}`;
  }

  async testWebSocketConnection() {
    return new Promise((resolve, reject) => {
      const socket = io(this.baseUrl, {
        transports: ['websocket', 'polling'],
        timeout: 5000
      });
      
      const timeout = setTimeout(() => {
        socket.disconnect();
        reject(new Error('WebSocket connection timeout'));
      }, 5000);

      socket.on('connect', () => {
        clearTimeout(timeout);
        const socketId = socket.id;
        socket.disconnect();
        resolve(`Connected with ID: ${socketId}`);
      });

      socket.on('connect_error', (error) => {
        clearTimeout(timeout);
        socket.disconnect();
        reject(new Error(`WebSocket connection failed: ${error.message}`));
      });
    });
  }

  async testAgentInitialization() {
    const response = await fetch(`${this.baseUrl}/api/agents/status`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    const agents = await response.json();
    const expectedAgents = ['sarah', 'marcus', 'elena', 'david', 'priya', 'alex'];
    let readyCount = 0;
    
    for (const agent of expectedAgents) {
      const isReady = agents[agent] && agents[agent].status === 'ready';
      this.recordTest(`Agent: ${agent}`, isReady, 
        agents[agent] ? `Status: ${agents[agent].status}` : 'Missing');
      if (isReady) readyCount++;
    }
    
    if (readyCount < expectedAgents.length) {
      throw new Error(`Only ${readyCount}/${expectedAgents.length} agents ready`);
    }
    
    return `All ${expectedAgents.length} agents ready`;
  }

  async testConversationFlow() {
    const response = await fetch(`${this.baseUrl}/api/conversation/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        user_query: 'Test query for connection validation',
        test_mode: true 
      })
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    const result = await response.json();
    if (!result.conversation_id) {
      throw new Error('No conversation ID returned');
    }
    
    return `Conversation started: ${result.conversation_id}`;
  }

  async testWebSocketEvents() {
    return new Promise((resolve, reject) => {
      const socket = io(this.baseUrl);
      let eventsReceived = [];
      
      const timeout = setTimeout(() => {
        socket.disconnect();
        if (eventsReceived.length === 0) {
          reject(new Error('No WebSocket events received'));
        } else {
          resolve(`Events received: ${eventsReceived.join(', ')}`);
        }
      }, 3000);

      socket.on('connect', () => {
        eventsReceived.push('connect');
      });

      socket.on('connection_established', (data) => {
        eventsReceived.push('connection_established');
        clearTimeout(timeout);
        socket.disconnect();
        resolve(`Events received: ${eventsReceived.join(', ')}`);
      });
    });
  }

  async testRealTimeUpdates() {
    return new Promise((resolve, reject) => {
      const socket = io(this.baseUrl);
      let phasesReceived = [];
      let agentResponses = 0;
      
      const timeout = setTimeout(() => {
        socket.disconnect();
        if (agentResponses === 0) {
          reject(new Error('No agent responses received'));
        } else {
          resolve(`Received ${agentResponses} responses, phases: ${phasesReceived.join(', ')}`);
        }
      }, 20000);

      socket.on('connect', () => {
        socket.emit('start_conversation', { 
          query: 'Test real-time updates',
          test_mode: true 
        });
      });

      socket.on('conversation_started', (data) => {
        if (data.conversation_id) {
          socket.emit('join_conversation', { 
            conversation_id: data.conversation_id,
            query: 'Test query'
          });
        }
      });

      socket.on('phase', (data) => {
        phasesReceived.push(data.phase);
      });

      socket.on('agent_response', (data) => {
        agentResponses++;
        if (agentResponses >= 6) { // Expect at least 6 responses
          clearTimeout(timeout);
          socket.disconnect();
          resolve(`Received ${agentResponses} responses, phases: ${phasesReceived.join(', ')}`);
        }
      });

      socket.on('conversation_complete', () => {
        clearTimeout(timeout);
        socket.disconnect();
        resolve(`Conversation completed: ${agentResponses} responses, phases: ${phasesReceived.join(', ')}`);
      });

      socket.on('error', (error) => {
        clearTimeout(timeout);
        socket.disconnect();
        reject(new Error(`Socket error: ${error}`));
      });
    });
  }

  async testErrorHandling() {
    // Test 404 handling
    try {
      const response = await fetch(`${this.baseUrl}/api/invalid-endpoint`);
      this.recordTest('404 Error Handling', response.status === 404, 
        `Status: ${response.status}`);
    } catch (error) {
      this.recordTest('404 Error Handling', false, error.message);
    }
    
    // Test validation error
    try {
      const response = await fetch(`${this.baseUrl}/api/conversation/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}) // Missing required field
      });
      
      const isValidationError = response.status === 400 || response.status === 422;
      this.recordTest('Validation Error Handling', isValidationError, 
        `Status: ${response.status}`);
    } catch (error) {
      this.recordTest('Validation Error Handling', false, error.message);
    }
    
    return 'Error handling tests completed';
  }

  displayTestSummary() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 Test Summary');
    console.log('=' + '='.repeat(59));
    console.log(`Total Tests: ${this.results.summary.total}`);
    console.log(`Passed: ${this.results.summary.passed} ✅`);
    console.log(`Failed: ${this.results.summary.failed} ❌`);
    
    if (this.results.summary.total > 0) {
      const passRate = (this.results.summary.passed / this.results.summary.total) * 100;
      console.log(`Pass Rate: ${passRate.toFixed(1)}%`);
    }
    
    if (this.results.summary.failed > 0) {
      console.log('\n🚨 FAILED TESTS:');
      Object.entries(this.results.tests).forEach(([name, result]) => {
        if (!result.passed) {
          console.log(`   ${name}: ${result.details}`);
        }
      });
    }
    
    console.log('\n' + (this.results.summary.failed === 0 ? '🎉 ALL TESTS PASSED!' : '⚠️  SOME TESTS FAILED'));
  }
}

// Make available globally in browser
if (typeof window !== 'undefined') {
  window.ConnectionTester = ConnectionTester;
  window.connectionTester = new ConnectionTester();
  console.log('🧪 Connection Tester loaded. Run: connectionTester.runAllTests()');
}