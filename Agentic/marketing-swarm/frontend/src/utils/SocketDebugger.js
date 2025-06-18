// Socket.IO Debugging Utility
// This helps diagnose WebSocket connection issues

export class SocketDebugger {
  constructor(socket) {
    this.socket = socket;
    this.events = [];
    this.startTime = Date.now();
  }

  startLogging() {
    console.log('🔍 Socket Debugger Started');
    console.log('Socket URL:', this.socket.io.uri);
    console.log('Socket Options:', this.socket.io.opts);
    
    // Log all events
    this.socket.onAny((eventName, ...args) => {
      const event = {
        time: Date.now() - this.startTime,
        event: eventName,
        args: args,
        timestamp: new Date().toISOString()
      };
      
      this.events.push(event);
      console.log(`📨 [${event.time}ms] ${eventName}:`, args);
    });

    // Log connection events
    this.socket.on('connect', () => {
      console.log('✅ CONNECTED');
      console.log('Socket ID:', this.socket.id);
      console.log('Transport:', this.socket.io.engine.transport.name);
    });

    this.socket.on('connect_error', (error) => {
      console.error('❌ CONNECTION ERROR:', error.type, error.message);
    });

    this.socket.on('disconnect', (reason) => {
      console.log('🔌 DISCONNECTED:', reason);
    });

    // Log engine events
    this.socket.io.on('upgrade', (transport) => {
      console.log('🚀 Transport upgraded to:', transport.name);
    });

    this.socket.io.on('packet', (packet) => {
      console.log('📦 Packet:', packet.type, packet.data);
    });
  }

  getEventHistory() {
    return this.events;
  }

  printSummary() {
    console.log('\n📊 Socket Debug Summary:');
    console.log('Total Events:', this.events.length);
    console.log('Connected:', this.socket.connected);
    console.log('Socket ID:', this.socket.id);
    console.log('Transport:', this.socket.io.engine?.transport?.name);
    
    // Group events by type
    const eventCounts = {};
    this.events.forEach(e => {
      eventCounts[e.event] = (eventCounts[e.event] || 0) + 1;
    });
    
    console.log('\nEvent Counts:');
    Object.entries(eventCounts).forEach(([event, count]) => {
      console.log(`  ${event}: ${count}`);
    });
  }

  testEmit(eventName, data) {
    console.log(`\n🧪 Testing emit: ${eventName}`, data);
    this.socket.emit(eventName, data);
  }

  async testConnection() {
    console.log('\n🧪 Running Connection Test...');
    
    if (!this.socket.connected) {
      console.log('❌ Socket not connected');
      return false;
    }
    
    console.log('✅ Socket connected');
    console.log('Socket ID:', this.socket.id);
    console.log('Transport:', this.socket.io.engine.transport.name);
    
    // Test echo
    return new Promise((resolve) => {
      const testId = Date.now();
      const timeout = setTimeout(() => {
        console.log('❌ Echo test timeout');
        resolve(false);
      }, 5000);
      
      this.socket.once('echo', (data) => {
        clearTimeout(timeout);
        if (data.testId === testId) {
          console.log('✅ Echo test passed');
          resolve(true);
        } else {
          console.log('❌ Echo test failed - ID mismatch');
          resolve(false);
        }
      });
      
      console.log('Sending echo test...');
      this.socket.emit('echo', { testId });
    });
  }
}

// Browser console helper
if (typeof window !== 'undefined') {
  window.SocketDebugger = SocketDebugger;
  
  window.startSocketDebug = () => {
    if (!window.socketRef?.current) {
      console.error('No socket found at window.socketRef.current');
      return;
    }
    
    const debugger = new SocketDebugger(window.socketRef.current);
    debugger.startLogging();
    window.socketDebugger = debugger;
    
    console.log('Socket debugger started. Access it at window.socketDebugger');
    console.log('Commands:');
    console.log('  window.socketDebugger.printSummary()');
    console.log('  window.socketDebugger.getEventHistory()');
    console.log('  window.socketDebugger.testConnection()');
    console.log('  window.socketDebugger.testEmit(eventName, data)');
    
    return debugger;
  };
  
  console.log('💡 Socket Debugger loaded. Run: window.startSocketDebug()');
}