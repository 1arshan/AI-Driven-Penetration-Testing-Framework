from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
import json
from datetime import datetime
from pydantic import BaseModel
from typing import Dict, List, Optional, Any

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

@app.get("/")
async def root():
    return {"message": "AI-Driven Penetration Testing Framework MCP Server"}

@app.post("/api/task/create", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    background_tasks: BackgroundTasks = None
):
    # Basic token validation (replace with proper auth)
    if credentials.credentials != "dev_token":
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Create a new task with UUID
    task_id = str(uuid.uuid4())
    
    # Store task
    tasks[task_id] = {
        "id": task_id,
        "type": task.type,
        "target": task.target,
        "scope": task.scope,
        "description": task.description,
        "status": "created",
        "created_at": datetime.now().isoformat()
    }
    
    return {"task_id": task_id, "status": "created"}

@app.get("/api/task/{task_id}")
async def get_task(
    task_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Basic token validation
    if credentials.credentials != "dev_token":
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get task
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks[task_id]

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)