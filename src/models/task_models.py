from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from uuid import UUID, uuid4

class TaskScope(BaseModel):
    ip_range: str = Field(..., description="IP range in CIDR notation")
    excluded_ips: List[str] = Field(default=[], description="IPs to exclude from scope")
    excluded_ports: List[int] = Field(default=[], description="Ports to exclude from scope")
    max_depth: int = Field(default=2, description="Maximum depth for discovery")

class TaskCreate(BaseModel):
    type: Literal["reconnaissance", "vulnerability_discovery", "exploitation", "reporting"] = Field(
        ..., description="Type of task to perform"
    )
    target: str = Field(..., description="Target IP or hostname")
    scope: TaskScope = Field(..., description="Scope of the task")
    description: str = Field(..., description="Human-readable description of the task")
    parent_task_id: Optional[UUID] = Field(default=None, description="Parent task ID if this is a subtask")
    priority: int = Field(default=1, description="Task priority (1-5)")

class TaskResponse(BaseModel):
    task_id: UUID = Field(..., description="UUID of the created task")
    status: str = Field(..., description="Status of the task")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")

class TaskStatus(BaseModel):
    task_id: UUID = Field(..., description="UUID of the task")
    status: Literal["created", "assigned", "in_progress", "completed", "failed"] = Field(
        ..., description="Status of the task"
    )
    agent_id: Optional[str] = Field(default=None, description="ID of the agent assigned to the task")
    progress: float = Field(default=0.0, description="Progress of the task (0-100)")
    message: Optional[str] = Field(default=None, description="Status message")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

class TaskResult(BaseModel):
    task_id: UUID = Field(..., description="UUID of the task")
    status: Literal["success", "partial", "failed"] = Field(..., description="Result status")
    data: Dict[str, Any] = Field(..., description="Result data")
    summary: str = Field(..., description="Human-readable summary of the result")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")