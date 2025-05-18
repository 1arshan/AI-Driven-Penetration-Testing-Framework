#!/usr/bin/env python3
import asyncio
import websockets
import json
import sys

async def connect_to_server():
    uri = "ws://localhost:8000/ws/task-updates"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket server. Waiting for updates...")
        
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received update: {json.dumps(data, indent=2)}")

if __name__ == "__main__":
    try:
        asyncio.run(connect_to_server())
    except KeyboardInterrupt:
        print("\nDisconnected from server")
        sys.exit(0)