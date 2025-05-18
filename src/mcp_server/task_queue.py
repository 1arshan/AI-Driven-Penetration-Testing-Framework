import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import redis.asyncio as redis
from src.utils.config import Config

class TaskQueue:
    def __init__(self):
        self.redis = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB
        )
        self.pubsub = self.redis.pubsub()
    
    async def initialize(self):
        """Initialize the task queue"""
        await self.pubsub.subscribe("task_updates")
    
    async def enqueue_task(self, task_data: Dict[str, Any]) -> str:
        """Add a task to the queue"""
        task_id = str(uuid.uuid4())
        task_data["id"] = task_id
        task_data["status"] = "created"
        task_data["created_at"] = datetime.now().isoformat()
        
        # Store task data
        await self.redis.set(f"task:{task_id}", json.dumps(task_data))
        
        # Add to queue based on task type
        task_type = task_data.get("type", "unknown")
        await self.redis.lpush(f"queue:{task_type}", task_id)
        
        # Publish update
        await self.redis.publish("task_updates", json.dumps({
            "event": "task_created",
            "task_id": task_id,
            "task_type": task_type,
            "timestamp": datetime.now().isoformat()
        }))
        
        return task_id
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task data by ID"""
        task_data = await self.redis.get(f"task:{task_id}")
        if task_data:
            return json.loads(task_data)
        return None
    
    async def update_task_status(
        self, task_id: str, status: str, 
        agent_id: Optional[str] = None, 
        progress: Optional[float] = None,
        message: Optional[str] = None
    ) -> bool:
        """Update task status"""
        task_data = await self.get_task(task_id)
        if not task_data:
            return False
        
        task_data["status"] = status
        task_data["updated_at"] = datetime.now().isoformat()
        
        if agent_id:
            task_data["agent_id"] = agent_id
        
        if progress is not None:
            task_data["progress"] = progress
        
        if message:
            task_data["message"] = message
        
        # Store updated task
        await self.redis.set(f"task:{task_id}", json.dumps(task_data))
        
        # Publish update
        await self.redis.publish("task_updates", json.dumps({
            "event": "task_updated",
            "task_id": task_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }))
        
        return True
    
    async def store_task_result(self, task_id: str, result_data: Dict[str, Any]) -> bool:
        """Store task result"""
        result_data["task_id"] = task_id
        result_data["timestamp"] = datetime.now().isoformat()
        
        # Store result
        await self.redis.set(f"result:{task_id}", json.dumps(result_data))
        
        # Mark task as completed
        await self.update_task_status(task_id, "completed", progress=100.0)
        
        # Publish update
        await self.redis.publish("task_updates", json.dumps({
            "event": "task_completed",
            "task_id": task_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        return True
    
    async def get_next_task(self, task_type: str, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get the next task of a specific type"""
        task_id = await self.redis.rpop(f"queue:{task_type}")
        if not task_id:
            return None
        
        task_id = task_id.decode("utf-8")
        task_data = await self.get_task(task_id)
        
        if task_data:
            # Mark as assigned
            await self.update_task_status(
                task_id=task_id,
                status="assigned",
                agent_id=agent_id,
                progress=0.0,
                message=f"Assigned to agent {agent_id}"
            )
            
            return task_data
            
        return None
    
    async def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get all active tasks"""
        active_tasks = []
        
        # Get task IDs using pattern matching
        task_keys = await self.redis.keys("task:*")
        
        for key in task_keys:
            task_id = key.decode("utf-8").split(":", 1)[1]
            task_data = await self.get_task(task_id)
            
            if task_data and task_data.get("status") in ["created", "assigned", "in_progress"]:
                active_tasks.append(task_data)
        
        return active_tasks