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

# @app.post("/api/task/create", response_model=TaskResponse)
# async def create_task(
#     task: TaskCreate,
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     background_tasks: BackgroundTasks = None
# ):
#     # Basic token validation (replace with proper auth)
#     if credentials.credentials != "dev_token":
#         raise HTTPException(status_code=401, detail="Invalid token")
    
#     # Create a new task with UUID
#     task_id = str(uuid.uuid4())
    
#     # Store task
#     tasks[task_id] = {
#         "id": task_id,
#         "type": task.type,
#         "target": task.target,
#         "scope": task.scope,
#         "description": task.description,
#         "status": "created",
#         "created_at": datetime.now().isoformat()
#     }
    
#     return {"task_id": task_id, "status": "created"}

# @app.get("/api/task/{task_id}")
# async def get_task(
#     task_id: str,
#     credentials: HTTPAuthorizationCredentials = Depends(security)
# ):
#     # Basic token validation
#     if credentials.credentials != "dev_token":
#         raise HTTPException(status_code=401, detail="Invalid token")
    
#     # Get task
#     if task_id not in tasks:
#         raise HTTPException(status_code=404, detail="Task not found")
    
#     return tasks[task_id]


# Update create_task endpoint
@app.post("/api/task/create", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    background_tasks: BackgroundTasks = None
):
    # Basic token validation
    if credentials.credentials != Config.AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Create a new task with UUID
    task_id = str(uuid.uuid4())
    
    # Prepare task data
    task_data = {
        "id": task_id,
        "type": task.type,
        "target": task.target,
        "scope": task.scope,
        "description": task.description,
        "status": "created",
        "created_at": datetime.now().isoformat()
    }
    
    # Store in Redis
    success = await redis_client.store_task(task_id, task_data)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to store task")
    
    return {"task_id": task_id, "status": "created"}

# Update get_task endpoint
@app.get("/api/task/{task_id}")
async def get_task(
    task_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Basic token validation
    if credentials.credentials != Config.AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get task from Redis
    task_data = await redis_client.get_task(task_id)
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get result if available
    result_data = await redis_client.get_result(task_id)
    
    # Combine task and result
    response = {
        "task": task_data,
        "result": result_data
    }
    
    return response

# Add Redis connection check on startup
@app.on_event("startup")
async def startup_event():
    # Check Redis connection
    connected = await redis_client.is_connected()
    if not connected:
        print("WARNING: Could not connect to Redis")



if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)