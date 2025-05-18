# WebSocket Handler for Task Updates

import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Any
import redis.asyncio as redis
from src.utils.config import Config

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.redis = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB
        )
        self.pubsub = self.redis.pubsub()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
    
    async def start_redis_listener(self):
        await self.pubsub.subscribe("task_updates")
        
        # Create background task to listen for Redis messages
        asyncio.create_task(self._redis_listener())
    
    async def _redis_listener(self):
        while True:
            try:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                if message and message["type"] == "message":
                    data = message["data"].decode("utf-8")
                    # Broadcast to all connected clients
                    await self.broadcast(data)
                
                # Small delay to prevent CPU overuse
                await asyncio.sleep(0.01)
            except Exception as e:
                print(f"Error in Redis listener: {e}")
                await asyncio.sleep(1)  # Delay before retry

# Create manager instance
connection_manager = ConnectionManager()