import asyncio
import socketio

async def test_connection():
    sio = socketio.AsyncClient()
    
    @sio.event
    async def connect():
        print("✅ Connected to WebSocket server")
        
    @sio.event
    async def connection_established(data):
        print(f"✅ Server acknowledged connection: {data}")
        await sio.disconnect()
        
    @sio.event
    async def disconnect():
        print("✅ Disconnected successfully")
    
    try:
        await sio.connect('http://localhost:8001')
        await asyncio.sleep(2)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        if sio.connected:
            await sio.disconnect()

asyncio.run(test_connection())
