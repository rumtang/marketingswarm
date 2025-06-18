#!/usr/bin/env node
// Debug helper for troubleshooting the marketing swarm

const axios = require('axios');
const colors = require('colors');

// Configure colors
colors.setTheme({
  success: 'green',
  error: 'red',
  warn: 'yellow',
  info: 'blue'
});

const API_BASE = 'http://localhost:8000';

async function checkHealth() {
  console.log('\n<å Checking System Health...'.info);
  
  try {
    const response = await axios.get(`${API_BASE}/api/health`);
    const health = response.data;
    
    console.log(` Backend Status: ${health.status}`.success);
    console.log(`ñ  Uptime: ${health.uptime}s`);
    
    Object.entries(health.components).forEach(([component, status]) => {
      const icon = status === 'healthy' ? '' : 'L';
      const color = status === 'healthy' ? 'success' : 'error';
      console.log(`${icon} ${component}: ${status}`[color]);
    });
    
    return true;
  } catch (error) {
    console.log(`L Health check failed: ${error.message}`.error);
    return false;
  }
}

async function checkAgents() {
  console.log('\n> Checking Agent Status...'.info);
  
  try {
    const response = await axios.get(`${API_BASE}/api/agents/status`);
    const agents = response.data;
    
    Object.entries(agents).forEach(([agent, info]) => {
      const icon = info.status === 'ready' ? '' : 'L';
      const color = info.status === 'ready' ? 'success' : 'error';
      console.log(`${icon} ${agent}: ${info.status}`[color]);
      
      if (info.stats) {
        console.log(`   Total responses: ${info.stats.total_responses}`);
        console.log(`   Last response: ${info.stats.last_response || 'Never'}`);
      }
    });
    
    return true;
  } catch (error) {
    console.log(`L Agent check failed: ${error.message}`.error);
    return false;
  }
}

async function checkLaunchStatus() {
  console.log('\n=€ Checking Launch Status...'.info);
  
  try {
    const response = await axios.get(`${API_BASE}/api/launch-status`);
    const status = response.data;
    
    console.log(`Progress: ${status.percentage}% (${status.overall_progress})`.info);
    console.log(`Demo Ready: ${status.ready_for_demo ? 'YES' : 'NO'}`[status.ready_for_demo ? 'success' : 'warn']);
    
    if (status.blocking_issues && status.blocking_issues.length > 0) {
      console.log('\n=¨ Blocking Issues:'.error);
      status.blocking_issues.forEach(issue => {
        console.log(`   ${issue.phase}: ${issue.missing.join(', ')}`.error);
      });
    }
    
    return status.ready_for_demo;
  } catch (error) {
    console.log(`L Launch status check failed: ${error.message}`.error);
    return false;
  }
}

async function testConversation() {
  console.log('\n=¬ Testing Conversation Flow...'.info);
  
  try {
    const response = await axios.post(`${API_BASE}/api/conversation/start`, {
      query: 'Test query from debug helper',
      test_mode: true
    });
    
    const result = response.data;
    
    if (result.conversation_id) {
      console.log(` Conversation started: ${result.conversation_id}`.success);
      return true;
    } else {
      console.log(`L Failed to start conversation: ${result.message}`.error);
      return false;
    }
  } catch (error) {
    console.log(`L Conversation test failed: ${error.message}`.error);
    return false;
  }
}

async function runDiagnostics() {
  console.log('= Marketing Swarm Diagnostics'.info.bold);
  console.log('================================'.info);
  
  const results = {
    health: await checkHealth(),
    agents: await checkAgents(),
    launch: await checkLaunchStatus(),
    conversation: await testConversation()
  };
  
  console.log('\n=Ê Diagnostic Summary:'.info.bold);
  console.log('================================'.info);
  
  Object.entries(results).forEach(([test, passed]) => {
    const icon = passed ? '' : 'L';
    const color = passed ? 'success' : 'error';
    console.log(`${icon} ${test}: ${passed ? 'PASSED' : 'FAILED'}`[color]);
  });
  
  const allPassed = Object.values(results).every(r => r);
  if (allPassed) {
    console.log('\n<‰ All diagnostics passed! System is ready.'.success.bold);
  } else {
    console.log('\n   Some diagnostics failed. Check the issues above.'.warn.bold);
  }
  
  process.exit(allPassed ? 0 : 1);
}

// Run diagnostics
runDiagnostics().catch(error => {
  console.error('Fatal error:'.error, error);
  process.exit(1);
});