# MCP Server Documentation

This document provides a comprehensive overview of the Multi-agent Cooperation Protocol (MCP) Server in the AI-Driven Penetration Testing Framework.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Core Components](#core-components)
- [API Endpoints](#api-endpoints)
- [Task Management](#task-management)
- [Message Bus](#message-bus)
- [WebSocket Notification System](#websocket-notification-system)
- [Workflow Orchestration](#workflow-orchestration)
- [Report Generation](#report-generation)
- [Security Considerations](#security-considerations)
- [Implementation Details](#implementation-details)
- [Performance Considerations](#performance-considerations)
- [Extending the MCP Server](#extending-the-mcp-server)

## Overview

The Multi-agent Cooperation Protocol (MCP) Server serves as the central orchestration layer of the AI-Driven Penetration Testing Framework. It coordinates the activities of specialized agents, manages tasks and workflows, handles communication between components, and provides APIs for controlling the system.

Key responsibilities of the MCP Server include:
- **Task Management**: Creation, distribution, and tracking of security testing tasks
- **Agent Coordination**: Registration, discovery, and coordination of agents
- **Real-time Updates**: Providing WebSocket-based notifications of system events
- **Workflow Orchestration**: Managing multi-step security testing workflows
- **Message Routing**: Facilitating communication between agents
- **Report Generation**: Creating security assessment reports

## Architecture

The MCP Server is built on FastAPI, a modern, high-performance web framework for building APIs. It uses Redis as a message broker and data store, providing persistent storage, pub/sub capabilities, and task queues.

### Architecture Diagram

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   Web Client  │     │  API Client   │     │  WebSocket    │
│               │     │               │     │  Client       │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        │                     │                     │
┌───────▼─────────────────────▼─────────────────────▼───────┐
│                                                           │
│                       FastAPI Server                      │
│                                                           │
├───────────────┬───────────────┬───────────────────────────┤
│ API Endpoints │ Auth & Auth   │ WebSocket Connections     │
├───────────────┴───────┬───────┴───────────────────────────┤
│                       │                                   │
│                       ▼                                   │
│  ┌───────────────────────────────────────────────────┐   │
│  │                   MCP Server                       │   │
│  │                                                    │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐   │   │
│  │  │ Task Queue │  │ Agent      │  │ Message    │   │   │
│  │  │            │  │ Registry   │  │ Bus        │   │   │
│  │  └────────────┘  └────────────┘  └────────────┘   │   │
│  │                                                    │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐   │   │
│  │  │ Workflow   │  │ Report     │  │ WebSocket  │   │   │
│  │  │ Orchestr.  │  │ Generator  │  │ Handler    │   │   │
│  │  └────────────┘  └────────────┘  └────────────┘   │   │
│  └───────────────────────────────────────────────────┘   │
│                                                           │
└────────────────────────────┬────────────────────────────┬┘
                             │                            │
                             ▼                            ▼
                      ┌────────────┐              ┌────────────┐
                      │            │              │            │
                      │   Redis    │              │  ChromaDB  │
                      │            │              │            │
                      └────────────┘              └────────────┘
```

## Core Components

The MCP Server consists of several core components, each with specific responsibilities:

### 1. Task Queue

The task queue manages the creation, distribution, and tracking of security testing tasks.

**Key Features**:
- Task creation and validation
- Type-based task queues
- Priority-based task distribution
- Progress tracking and status updates
- Result storage and retrieval

**Implementation**: `src/mcp_server/task_queue.py`

### 2. Agent Registry

The agent registry manages the registration and discovery of agents in the system.

**Key Features**:
- Agent registration and unregistration
- Capability tracking
- Agent type classification
- Status monitoring
- Discovery by type or ID

**Implementation**: `src/agents/agent_registry.py`

### 3. Message Bus

The message bus facilitates communication between agents in the system.

**Key Features**:
- Message routing and delivery
- Message type handling
- Pub/sub communication
- Message storage and retrieval
- Handler registration

**Implementation**: `src/mcp_server/message_bus.py`

### 4. WebSocket Handler

The WebSocket handler manages real-time communication with clients.

**Key Features**:
- Connection management
- Event broadcasting
- Client tracking
- Redis pub/sub integration
- Status updates

**Implementation**: `src/mcp_server/ws_handler.py`

### 5. Workflow Orchestrator

The workflow orchestrator manages multi-step security testing workflows.

**Key Features**:
- Workflow creation and tracking
- Task chaining and dependencies
- Status monitoring
- Result aggregation
- Automated task creation

**Implementation**: `src/mcp_server/workflow_orchestrator.py`

### 6. Report Generator

The report generator creates security assessment reports from workflow results.

**Key Features**:
- HTML report generation
- Finding aggregation
- Risk assessment
- Visualization
- Formatting

**Implementation**: `src/mcp_server/report_generator.py`

## API Endpoints

The MCP Server exposes several API endpoints for interacting with the system:

### Task Management

- **POST /api/task/create**: Create a new task
- **GET /api/task/{task_id}**: Get task details
- **GET /api/task/{task_id}/status**: Get task status
- **PUT /api/task/{task_id}/status**: Update task status
- **GET /api/tasks/active**: Get all active tasks

### Agent Management

- **POST /api/agents/register**: Register a new agent
- **GET /api/agents**: Get all registered agents
- **GET /api/agents/type/{agent_type}**: Get agents by type
- **DELETE /api/agents/{agent_id}**: Unregister an agent
- **PUT /api/agents/{agent_id}/status**: Update agent status

### Workflow Management

- **POST /api/workflows/recon_vuln**: Create a reconnaissance and vulnerability discovery workflow
- **GET /api/workflows/{workflow_id}**: Get workflow details
- **GET /api/workflows/{workflow_id}/results**: Get workflow results
- **GET /api/workflows/{workflow_id}/report**: Generate HTML report for workflow

### WebSocket Endpoint

- **WebSocket /ws/task-updates**: Real-time task status updates

## Task Management

The task management system is central to the MCP Server's functionality, providing a way to distribute and track security testing tasks.

### Task Structure

Tasks are represented using the `TaskCreate` model:

```python
class TaskCreate(BaseModel):
    type: Literal["reconnaissance", "vulnerability_discovery", "exploitation", "reporting"]
    target: str
    scope: TaskScope
    description: str
    parent_task_id: Optional[UUID] = None
    priority: int = 1
```

### Task Lifecycle

1. **Creation**: A task is created via the API or by another task
2. **Queuing**: The task is added to a type-specific queue
3. **Assignment**: An agent retrieves the task from the queue
4. **Processing**: The agent performs the task and updates status
5. **Completion**: The agent stores the result and marks the task complete

### Task Status Updates

Task status is updated throughout the lifecycle:
- **created**: Task has been created but not assigned
- **assigned**: Task has been assigned to an agent
- **in_progress**: Agent is currently processing the task
- **completed**: Task has been successfully completed
- **failed**: Task failed to complete

### Task Result Storage

Task results are stored in Redis with the key `result:{task_id}` and include:
- Task ID
- Agent ID
- Result data
- Timestamp

## Message Bus

The message bus enables communication between agents in the system, allowing them to share information and coordinate activities.

### Message Structure

Messages are represented using the `Message` model:

```python
class Message(BaseModel):
    message_id: UUID
    sender_id: str
    recipient_id: Optional[str]
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime
    reply_to: Optional[UUID]
    metadata: Dict[str, Any]
```

### Message Types

- **task_assignment**: Directs an agent to perform a task
- **task_status_update**: Reports progress on a task
- **task_result**: Contains the outcome of a completed task
- **knowledge_query**: Requests information from the knowledge base
- **knowledge_response**: Returns requested knowledge

### Message Flow

1. Agent creates a message and sends it through the message bus
2. Message bus stores the message in Redis
3. Message bus publishes a notification on the "agent_messages" channel
4. Message listener picks up the notification and retrieves the message
5. Message is dispatched to registered handlers based on message type
6. Handler processes the message and optionally sends a response

## WebSocket Notification System

The WebSocket notification system provides real-time updates to clients about task status changes and system events.

### Connection Management

The `ConnectionManager` class handles WebSocket connections:
- Tracking active connections
- Accepting new connections
- Handling disconnections
- Sending personal messages
- Broadcasting to all connections

### Event Broadcasting

Events are broadcast to all connected clients in real-time:
- Task created
- Task assigned
- Task status updated
- Task completed
- Task failed

### Redis Integration

The WebSocket system integrates with Redis pub/sub:
- Subscribes to the "task_updates" channel
- Listens for task-related events
- Broadcasts events to all connected clients

## Workflow Orchestration

The workflow orchestrator manages multi-step security testing workflows, automatically chaining tasks based on dependencies.

### Workflow Types

- **recon_vuln**: Reconnaissance followed by vulnerability discovery

### Workflow Structure

A workflow consists of:
- Workflow ID
- Type
- Target
- Scope
- Status
- Task list
- Timestamps

### Workflow Lifecycle

1. **Creation**: A workflow is created via the API
2. **Initialization**: Initial tasks are created based on workflow type
3. **Monitoring**: The orchestrator monitors task completion
4. **Chaining**: When a task completes, dependent tasks are created
5. **Completion**: The workflow is marked complete when all tasks are done

### Task Dependencies

Tasks in a workflow can depend on other tasks:
- A vulnerability discovery task depends on reconnaissance results
- An exploitation task depends on vulnerability discovery results
- A reporting task depends on all previous tasks

## Report Generation

The report generator creates formatted security assessment reports from workflow results.

### Report Types

- **HTML**: Rich HTML report with styling and interactive elements

### Report Structure

A security assessment report includes:
- Executive summary
- Target information
- Vulnerability findings
- Risk assessment
- Remediation recommendations
- Technical details

### Report Generation Process

1. Retrieve workflow results
2. Extract vulnerability findings
3. Organize by service/vulnerability
4. Calculate risk statistics
5. Generate HTML content
6. Apply styling
7. Return formatted report

## Security Considerations

The MCP Server implements several security measures:

### Authentication

- Token-based authentication for API endpoints
- Validation of credentials for all requests

### Authorization

- Role-based access control (planned)
- Capability-based authorization (planned)

### Scope Enforcement

- Strict validation of task scope
- Prevention of out-of-scope testing

### Audit Logging

- Logging of all API calls
- Tracking of agent activities
- Recording of task execution

## Implementation Details

### FastAPI Application

The MCP Server is implemented as a FastAPI application in `src/mcp_server/app.py`:

```python
app = FastAPI(
    title="AI-Driven Penetration Testing Framework",
    description="MCP Server for orchestrating AI agents for security testing",
    version="0.1.0"
)
```

### Redis Connection

Redis is used for task queues, message passing, and data storage:

```python
redis_client = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB
)
```

### Task Queue Implementation

The task queue uses Redis lists and key-value storage:

```python
# Add to queue
await self.redis.lpush(f"queue:{task_type}", task_id)

# Get from queue
task_id = await self.redis.rpop(f"queue:{task_type}")
```

### WebSocket Management

WebSocket connections are managed by the `ConnectionManager` class:

```python
# Accept connection
await websocket.accept()
self.active_connections.append(websocket)

# Broadcast message
for connection in self.active_connections:
    await connection.send_text(message)
```

### Message Bus

The message bus uses Redis pub/sub for notification:

```python
# Publish notification
await self.redis.publish("agent_messages", json.dumps({
    "event": "new_message",
    "message_id": message["message_id"]
}))

# Listen for messages
message = await self.pubsub.get_message(ignore_subscribe_messages=True)
```

## Performance Considerations

### Connection Pooling

For Redis connections, consider using connection pooling to handle multiple concurrent requests efficiently.

### Task Queue Optimization

For high-volume systems, consider:
- Separate Redis instances for different task types
- Priority queues for critical tasks
- Batch processing for similar tasks

### WebSocket Scaling

For systems with many connected clients:
- Implement WebSocket load balancing
- Consider using a specialized WebSocket server
- Implement message throttling

### Message Bus Performance

For high-volume message passing:
- Consider sharding messages by type or recipient
- Implement message expiration
- Use dedicated Redis instance for message passing

## Extending the MCP Server

### Adding New API Endpoints

To add a new API endpoint:

1. Define the endpoint in `src/mcp_server/app.py`:

```python
@app.post("/api/new_endpoint")
async def new_endpoint(
    data: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Validate token
    if credentials.credentials != Config.AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Process request
    result = await process_request(data)
    
    return {"status": "success", "result": result}
```

2. Implement the request processing logic
3. Update documentation

### Adding New Workflow Types

To add a new workflow type:

1. Implement a new method in the workflow orchestrator:

```python
async def start_new_workflow_type(self, target: str, scope: Dict[str, Any], description: str) -> str:
    # Create workflow
    workflow_id = await self.create_workflow("new_workflow_type", target, scope)
    
    # Create initial tasks
    # ...
    
    # Set up monitoring
    # ...
    
    return workflow_id
```

2. Add an API endpoint for the new workflow type
3. Implement task completion handlers

### Enhancing the Report Generator

To add a new report format:

1. Add a new method to the report generator:

```python
@staticmethod
def generate_pdf_report(workflow_results: Dict[str, Any]) -> bytes:
    # Generate PDF content
    # ...
    
    return pdf_bytes
```

2. Add an API endpoint for the new report format
3. Update documentation