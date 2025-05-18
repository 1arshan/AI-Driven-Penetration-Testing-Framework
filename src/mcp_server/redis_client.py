import redis.asyncio as redis
import json
from typing import Dict, Any, Optional
from src.utils.config import Config

class RedisClient:
    def __init__(self):
        self.redis = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB
        )
    
    async def is_connected(self) -> bool:
        """Check if connected to Redis"""
        try:
            return await self.redis.ping()
        except Exception:
            return False
    
    async def store_task(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """Store a task in Redis"""
        try:
            await self.redis.set(f"task:{task_id}", json.dumps(task_data))
            return True
        except Exception as e:
            print(f"Error storing task in Redis: {e}")
            return False
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task from Redis"""
        try:
            task_data = await self.redis.get(f"task:{task_id}")
            if task_data:
                return json.loads(task_data)
            return None
        except Exception as e:
            print(f"Error getting task from Redis: {e}")
            return None
    
    async def update_task_status(self, task_id: str, status: str) -> bool:
        """Update task status"""
        try:
            task_data = await self.get_task(task_id)
            if task_data:
                task_data["status"] = status
                await self.store_task(task_id, task_data)
                return True
            return False
        except Exception as e:
            print(f"Error updating task status in Redis: {e}")
            return False
    
    async def store_result(self, task_id: str, result_data: Dict[str, Any]) -> bool:
        """Store a task result in Redis"""
        try:
            await self.redis.set(f"result:{task_id}", json.dumps(result_data))
            return True
        except Exception as e:
            print(f"Error storing result in Redis: {e}")
            return False
    
    async def get_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task result from Redis"""
        try:
            result_data = await self.redis.get(f"result:{task_id}")
            if result_data:
                return json.loads(result_data)
            return None
        except Exception as e:
            print(f"Error getting result from Redis: {e}")
            return None