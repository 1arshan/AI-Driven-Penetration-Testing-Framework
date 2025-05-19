from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
import json
from datetime import datetime
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from redis_client import RedisClient
# from src.mcp_server.redis_client import RedisClient
from src.mcp_server.ws_handler import connection_manager
from src.mcp_server.task_queue import TaskQueue
from src.utils.config import Config
from src.models.task_models import TaskCreate, TaskResponse, TaskStatus, TaskResult
from src.agents.agent_registry import AgentRegistry
from src.knowledge_base.importers.security_data_importer import SecurityDataImporter
from src.knowledge_base.security_kb import SecurityKnowledgeBase
from src.mcp_server.message_bus import MessageBus

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

# Initialize agent registry
agent_registry = AgentRegistry()

# Initialize message bus
message_bus = MessageBus()

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

# Add PUT endpoint for updating task status
@app.put("/api/task/{task_id}/status")
async def update_task_status(
    task_id: str,
    status_update: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Validate token
    if credentials.credentials != Config.AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
   
    # Get task
    task = await task_queue.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
      
    # Update status
    success = await task_queue.update_task_status(
        task_id=task_id,
        status=status_update.get("status", task.get("status")),
        progress=status_update.get("progress", task.get("progress", 0.0)),
        message=status_update.get("message", "")
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update task status")
    
    return {"status": "updated", "task_id": task_id}


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
    
    connected = await redis_client.is_connected()
    if not connected:
        print("WARNING: Could not connect to Redis")

    await task_queue.initialize()
    # Start Redis listener for WebSocket broadcasts
    await connection_manager.start_redis_listener()
    print("WebSocket notification system initialized")

    # Initialize message bus
    await message_bus.initialize()
    print("Message bus initialized")

    # Initialize security knowledge base
    try:
        kb = SecurityKnowledgeBase()
        importer = SecurityDataImporter(kb)
        results = importer.import_all_data()
        print(f"Initialized security knowledge base with {results['total']} items")
    except Exception as e:
        print(f"WARNING: Failed to initialize security knowledge base: {e}")
    
    print("Server startup complete")

# Add WebSocket endpoint
@app.websocket("/ws/task-updates")
async def websocket_endpoint(websocket: WebSocket):
    
    await connection_manager.connect(websocket)
    try:
        while True:
            # Just keep the connection alive
            # Redis listener will handle sending messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)

# Add endpoints for agent management
@app.post("/api/agents/register")
async def register_agent(
    agent_info: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Register a new agent with the system.
    
    Agents call this endpoint to announce their existence and capabilities.
    """
    # Validate token
    if credentials.credentials != Config.AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Register agent
    success = await agent_registry.register_agent(agent_info)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to register agent")
    
    return {"status": "success", "agent_id": agent_info.get("agent_id")}

@app.get("/api/agents")
async def get_all_agents(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get all registered agents.
    
    Returns information about all agents currently registered with the system.
    """
    # Validate token
    if credentials.credentials != Config.AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get all agents
    agents = await agent_registry.get_all_agents()
    
    return {"agents": agents}


@app.get("/api/agents/type/{agent_type}")
async def get_agents_by_type(
    agent_type: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get agents by type.
    
    Returns information about all agents of a specific type (e.g., reconnaissance).
    """
    # Validate token
    if credentials.credentials != Config.AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get agents by type
    agents = await agent_registry.get_agents_by_type(agent_type)
    
    return {"agent_type": agent_type, "agents": agents}

@app.delete("/api/agents/{agent_id}")
async def unregister_agent(
    agent_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Unregister an agent from the system.
    
    Removes an agent from the registry, typically called when an agent shuts down.
    """
    # Validate token
    if credentials.credentials != Config.AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Unregister agent
    success = await agent_registry.unregister_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {"status": "success", "agent_id": agent_id}

@app.put("/api/agents/{agent_id}/status")
async def update_agent_status(
    agent_id: str,
    status_update: Dict[str, str],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Update agent status.
    
    Updates the status of an agent (e.g., idle, busy, offline).
    """
    # Validate token
    if credentials.credentials != Config.AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Check if status is provided
    if "status" not in status_update:
        raise HTTPException(status_code=400, detail="Status not provided")
    
    # Update agent status
    success = await agent_registry.update_agent_status(agent_id, status_update["status"])
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {"status": "updated", "agent_id": agent_id}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)