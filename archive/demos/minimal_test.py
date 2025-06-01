#!/usr/bin/env python3
"""
Minimal websocket test
"""

import asyncio
import json
import websockets
import sys

async def echo_server(websocket, path):
    """Very basic echo server."""
    print(f"Client connected from {websocket.remote_address}")
    try:
        await websocket.send(json.dumps({"type": "hello", "message": "Welcome!"}))
        
        async for message in websocket:
            print(f"Received: {message}")
            data = json.loads(message)
            response = {"type": "echo", "received": data}
            await websocket.send(json.dumps(response))
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        print("Client disconnected")

async def test_client():
    """Test client."""
    try:
        print("Connecting to server...")
        async with websockets.connect("ws://localhost:8766") as websocket:
            print("Connected!")
            
            # Receive welcome
            welcome = await websocket.recv()
            print(f"Welcome: {welcome}")
            
            # Send test message
            await websocket.send(json.dumps({"type": "test", "message": "Hello server!"}))
            
            # Receive echo
            echo = await websocket.recv()
            print(f"Echo: {echo}")
            
        print("Test completed successfully!")
        return True
    except Exception as e:
        print(f"Client error: {e}")
        return False

async def main():
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        print("Starting echo server on port 8766...")
        await websockets.serve(echo_server, "localhost", 8766)
        print("Server running. Press Ctrl+C to stop.")
        await asyncio.Future()  # Run forever
    else:
        success = await test_client()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())