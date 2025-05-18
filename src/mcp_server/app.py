from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
import json
from datetime import datetime
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from src.mcp_server.redis_client import RedisClient
from src.utils.config import Config
from src.mcp_server.task_queue import TaskQueue
from src.models.task_models import TaskCreate, TaskResponse, TaskStatus, TaskResult

# Create FastAPI app
app = FastAPI(
    title="AI-Driven Penetration Testing Framework",
    description="MCP Server for orchestrating AI agents for security testing",
    version="0.1.0"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up authentication
security = HTTPBearer()

# Initialize task queue
task_queue = TaskQueue()

# Model definitions
class TaskCreate(BaseModel):
    type: str
    target: str
    scope: Dict[str, Any]
    description: str

class TaskResponse(BaseModel):
    task_id: str
    status: str

# Simple in-memory storage for development
# Will be replaced with Redis later
tasks = {}

# Initialize Redis client
redis_client = RedisClient()

@app.get("/")
async def root():
    return {"message": "AI-Driven Penetration Testing Framework MCP Server"}


# Updated create_task endpoint
@app.post("/api/task/create", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    background_tasks: BackgroundTasks = None
):
    # Validate token
    if credentials.credentials != Config.AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Convert to dict
    task_dict = task.model_dump()
    
    # Enqueue task using the new task queue
    task_id = await task_queue.enqueue_task(task_dict)
    
    return TaskResponse(
        task_id=task_id,
        status="created",
        created_at=datetime.now()
    )

# Updated get_task endpoint
@app.get("/api/task/{task_id}")
async def get_task(
    task_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Validate token
    if credentials.credentials != Config.AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get task from Redis via the task queue
    task = await task_queue.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get result if available
    result = await task_queue.get_result(task_id)
    
    # Combine task and result
    response = {
        "task": task,
        "result": result
    }
    
    return response

# Add endpoint to get task status
@app.get("/api/task/{task_id}/status", response_model=TaskStatus)
async def get_task_status(
    task_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Validate token
    if credentials.credentials != Config.AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get task
    task = await task_queue.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskStatus(
        task_id=task_id,
        status=task.get("status", "unknown"),
        agent_id=task.get("agent_id"),
        progress=task.get("progress", 0.0),
        message=task.get("message"),
        updated_at=datetime.fromisoformat(task.get("updated_at", datetime.now().isoformat()))
    )

# Add endpoint to get active tasks
@app.get("/api/tasks/active", response_model=List[TaskStatus])
async def get_active_tasks(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Validate token
    if credentials.credentials != Config.AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get active tasks
    active_tasks = await task_queue.get_active_tasks()
    
    return [
        TaskStatus(
            task_id=task["id"],
            status=task.get("status", "unknown"),
            agent_id=task.get("agent_id"),
            progress=task.get("progress", 0.0),
            message=task.get("message"),
            updated_at=datetime.fromisoformat(task.get("updated_at", datetime.now().isoformat()))
        )
        for task in active_tasks
    ]

# Add Redis connection check on startup
@app.on_event("startup")
async def startup_event():
    # Check Redis connection
    await task_queue.initialize()
    connected = await redis_client.is_connected()
    if not connected:
        print("WARNING: Could not connect to Redis")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)