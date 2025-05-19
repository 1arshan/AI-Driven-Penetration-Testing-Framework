from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID, uuid4


class Message(BaseModel):
    """
    Base message model for agent communication.

    Represents the structure of messages exchanged between agents
    in the multi-agent system.
    """

    message_id: UUID = Field(default_factory=uuid4, description="Unique message ID")
    sender_id: str = Field(..., description="Sender agent ID")
    recipient_id: Optional[str] = Field(default=None, description="Recipient agent ID")
    message_type: str = Field(..., description="Type of message")
    content: Dict[str, Any] = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    reply_to: Optional[UUID] = Field(default=None, description="ID of message this is replying to")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TaskAssignmentMessage(Message):
    """
    Message for assigning a task to an agent.
    """

    message_type: str = "task_assignment"
    content: Dict[str, Any] = Field(
        ...,
        description="Task assignment details",
        example={
            "task_id": "123e4567-e89b-12d3-a456-426614174000",
            "task_type": "reconnaissance",
            "target": "192.168.1.1",
            "scope": {"ip_range": "192.168.1.0/24"},
            "description": "Initial reconnaissance scan"
        }
    )


class TaskStatusUpdateMessage(Message):
    """
    Message for updating task status.
    """

    message_type: str = "task_status_update"
    content: Dict[str, Any] = Field(
        ...,
        description="Task status update details",
        example={
            "task_id": "123e4567-e89b-12d3-a456-426614174000",
            "status": "in_progress",
            "progress": 45.0,
            "message": "Scanning ports 1-1000"
        }
    )


class TaskResultMessage(Message):
    """
    Message for reporting task results.
    """

    message_type: str = "task_result"
    content: Dict[str, Any] = Field(
        ...,
        description="Task result details",
        example={
            "task_id": "123e4567-e89b-12d3-a456-426614174000",
            "status": "success",
            "result": {"open_ports": [22, 80, 443]},
            "summary": "Found 3 open ports"
        }
    )


class KnowledgeQueryMessage(Message):
    """
    Message for querying the knowledge base.
    """

    message_type: str = "knowledge_query"
    content: Dict[str, Any] = Field(
        ...,
        description="Knowledge query details",
        example={
            "query": "vulnerabilities for Apache 2.4.41",
            "collection": "vulnerabilities",
            "n_results": 5
        }
    )


class KnowledgeResponseMessage(Message):
    """
    Message with knowledge base query results.
    """

    message_type: str = "knowledge_response"
    content: Dict[str, Any] = Field(
        ...,
        description="Knowledge response details",
        example={
            "query": "vulnerabilities for Apache 2.4.41",
            "results": [{"id": "vuln1", "name": "Apache Range Header DoS"}]
        }
    )