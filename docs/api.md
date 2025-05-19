# API Reference Documentation

This document provides a comprehensive reference for the API endpoints exposed by the AI-Driven Penetration Testing Framework.

## Table of Contents
- [Authentication](#authentication)
- [Task Management](#task-management)
- [Agent Management](#agent-management)
- [Workflow Management](#workflow-management)
- [Knowledge Base](#knowledge-base)
- [WebSocket Notifications](#websocket-notifications)
- [Error Handling](#error-handling)
- [Data Models](#data-models)
- [Examples](#examples)

## Authentication

All API endpoints require authentication using a bearer token.

**Authorization Header:**
```
Authorization: Bearer <token>
```

The token is configured in the `.env` file as `AUTH_TOKEN`.

Example:
```bash
curl -X GET "http://localhost:8000/api/tasks/active" \
  -H "Authorization: Bearer dev_token"
```

## Task Management

### Create Task

Creates a new security testing task.

**Endpoint:** `POST /api/task/create`

**Request Body:**
```json
{
  "type": "reconnaissance",
  "target": "192.168.1.1",
  "scope": {
    "ip_range": "192.168.1.0/24",
    "excluded_ips": [],
    "excluded_ports": [25, 139, 445],
    "max_depth": 2
  },
  "description": "Initial reconnaissance scan",
  "parent_task_id": null,
  "priority": 2
}
```

**Response:**
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "created",
  "created_at": "2025-05-19T12:34:56.789Z"
}
```

**Status Codes:**
- `200 OK`: Task created successfully
- `400 Bad Request`: Invalid task data
- `401 Unauthorized`: Invalid authentication token

### Get Task

Retrieves details about a specific task.

**Endpoint:** `GET /api/task/{task_id}`

**Path Parameters:**
- `task_id`: ID of the task to retrieve

**Response:**
```json
{
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "type": "reconnaissance",
    "target": "192.168.1.1",
    "scope": {
      "ip_range": "192.168.1.0/24",
      "excluded_ips": [],
      "excluded_ports": [25, 139, 445],
      "max_depth": 2
    },
    "description": "Initial reconnaissance scan",
    "status": "in_progress",
    "priority": 2,
    "progress": 45.0,
    "message": "Scanning ports 1-1000",
    "created_at": "2025-05-19T12:34:56.789Z",
    "updated_at": "2025-05-19T12:36:45.123Z"
  },
  "result": null
}
```

**Status Codes:**
- `200 OK`: Task found
- `401 Unauthorized`: Invalid authentication token
- `404 Not Found`: Task not found

### Get Task Status

Retrieves the status of a specific task.

**Endpoint:** `GET /api/task/{task_id}/status`

**Path Parameters:**
- `task_id`: ID of the task to retrieve status for

**Response:**
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "in_progress",
  "agent_id": "reconnaissance_agent_1",
  "progress": 45.0,
  "message": "Scanning ports 1-1000",
  "updated_at": "2025-05-19T12:36:45.123Z"
}
```

**Status Codes:**
- `200 OK`: Status found
- `401 Unauthorized`: Invalid authentication token
- `404 Not Found`: Task not found

### Update Task Status

Updates the status of a specific task.

**Endpoint:** `PUT /api/task/{task_id}/status`

**Path Parameters:**
- `task_id`: ID of the task to update

**Request Body:**
```json
{
  "status": "in_progress",
  "progress": 75.0,
  "message": "Analyzing service banners"
}
```

**Response:**
```json
{
  "status": "updated",
  "task_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Status Codes:**
- `200 OK`: Status updated
- `400 Bad Request`: Invalid status data
- `401 Unauthorized`: Invalid authentication token
- `404 Not Found`: Task not found

### Get Active Tasks

Retrieves all active tasks in the system.

**Endpoint:** `GET /api/tasks/active`

**Response:**
```json
[
  {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "in_progress",
    "agent_id": "reconnaissance_agent_1",
    "progress": 45.0,
    "message": "Scanning ports 1-1000",
    "updated_at": "2025-05-19T12:36:45.123Z"
  },
  {
    "task_id": "456e7890-e12b-34d5-a678-426614174000",
    "status": "created",
    "agent_id": null,
    "progress": 0.0,
    "message": null,
    "updated_at": "2025-05-19T12:40:12.456Z"
  }
]
```

**Status Codes:**
- `200 OK`: Successfully retrieved active tasks
- `401 Unauthorized`: Invalid authentication token

## Agent Management

### Register Agent

Registers a new agent with the system.

**Endpoint:** `POST /api/agents/register`

**Request Body:**
```json
{
  "agent_id": "reconnaissance_agent_1",
  "agent_type": "reconnaissance",
  "capabilities": [
    "network_scanning",
    "port_discovery",
    "service_detection",
    "os_fingerprinting",
    "banner_grabbing"
  ],
  "status": "idle"
}
```

**Response:**
```json
{
  "status": "success",
  "agent_id": "reconnaissance_agent_1"
}
```

**Status Codes:**
- `200 OK`: Agent registered successfully
- `400 Bad Request`: Invalid agent data
- `401 Unauthorized`: Invalid authentication token

### Get All Agents

Retrieves all registered agents in the system.

**Endpoint:** `GET /api/agents`

**Response:**
```json
{
  "agents": [
    {
      "agent_id": "reconnaissance_agent_1",
      "agent_type": "reconnaissance",
      "capabilities": [
        "network_scanning",
        "port_discovery",
        "service_detection",
        "os_fingerprinting",
        "banner_grabbing"
      ],
      "status": "idle",
      "registered_at": "2025-05-19T12:30:45.123Z"
    },
    {
      "agent_id": "vulnerability_discovery_agent_1",
      "agent_type": "vulnerability_discovery",
      "capabilities": [
        "vulnerability_discovery",
        "service_analysis",
        "cve_mapping",
        "risk_assessment"
      ],
      "status": "busy",
      "registered_at": "2025-05-19T12:32:15.456Z"
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Successfully retrieved agents
- `401 Unauthorized`: Invalid authentication token

### Get Agents by Type

Retrieves all agents of a specific type.

**Endpoint:** `GET /api/agents/type/{agent_type}`

**Path Parameters:**
- `agent_type`: Type of agents to retrieve (e.g., "reconnaissance")

**Response:**
```json
{
  "agent_type": "reconnaissance",
  "agents": [
    {
      "agent_id": "reconnaissance_agent_1",
      "agent_type": "reconnaissance",
      "capabilities": [
        "network_scanning",
        "port_discovery",
        "service_detection",
        "os_fingerprinting",
        "banner_grabbing"
      ],
      "status": "idle",
      "registered_at": "2025-05-19T12:30:45.123Z"
    },
    {
      "agent_id": "reconnaissance_agent_2",
      "agent_type": "reconnaissance",
      "capabilities": [
        "network_scanning",
        "port_discovery",
        "service_detection",
        "os_fingerprinting",
        "banner_grabbing"
      ],
      "status": "busy",
      "registered_at": "2025-05-19T12:35:22.789Z"
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Successfully retrieved agents
- `401 Unauthorized`: Invalid authentication token

### Unregister Agent

Unregisters an agent from the system.

**Endpoint:** `DELETE /api/agents/{agent_id}`

**Path Parameters:**
- `agent_id`: ID of the agent to unregister

**Response:**
```json
{
  "status": "success",
  "agent_id": "reconnaissance_agent_1"
}
```

**Status Codes:**
- `200 OK`: Agent unregistered successfully
- `401 Unauthorized`: Invalid authentication token
- `404 Not Found`: Agent not found

### Update Agent Status

Updates the status of a specific agent.

**Endpoint:** `PUT /api/agents/{agent_id}/status`

**Path Parameters:**
- `agent_id`: ID of the agent to update

**Request Body:**
```json
{
  "status": "busy"
}
```

**Response:**
```json
{
  "status": "updated",
  "agent_id": "reconnaissance_agent_1"
}
```

**Status Codes:**
- `200 OK`: Status updated
- `400 Bad Request`: Invalid status data
- `401 Unauthorized`: Invalid authentication token
- `404 Not Found`: Agent not found

## Workflow Management

### Create Reconnaissance and Vulnerability Discovery Workflow

Creates a new workflow that chains reconnaissance and vulnerability discovery tasks.

**Endpoint:** `POST /api/workflows/recon_vuln`

**Request Body:**
```json
{
  "target": "192.168.1.1",
  "scope": {
    "ip_range": "192.168.1.0/24",
    "excluded_ips": [],
    "excluded_ports": [25, 139, 445],
    "max_depth": 2
  },
  "description": "Security assessment of internal server"
}
```

**Response:**
```json
{
  "workflow_id": "789e0123-e45b-67d8-a901-426614174000",
  "status": "created"
}
```

**Status Codes:**
- `200 OK`: Workflow created successfully
- `400 Bad Request`: Invalid workflow data
- `401 Unauthorized`: Invalid authentication token

### Get Workflow

Retrieves details about a specific workflow.

**Endpoint:** `GET /api/workflows/{workflow_id}`

**Path Parameters:**
- `workflow_id`: ID of the workflow to retrieve

**Response:**
```json
{
  "id": "789e0123-e45b-67d8-a901-426614174000",
  "type": "recon_vuln",
  "target": "192.168.1.1",
  "scope": {
    "ip_range": "192.168.1.0/24",
    "excluded_ips": [],
    "excluded_ports": [25, 139, 445],
    "max_depth": 2
  },
  "status": "in_progress",
  "tasks": [
    {
      "task_id": "123e4567-e89b-12d3-a456-426614174000",
      "task_type": "reconnaissance",
      "added_at": "2025-05-19T12:45:32.123Z"
    },
    {
      "task_id": "456e7890-e12b-34d5-a678-426614174000",
      "task_type": "vulnerability_discovery",
      "added_at": "2025-05-19T12:50:15.456Z"
    }
  ],
  "created_at": "2025-05-19T12:45:30.789Z",
  "updated_at": "2025-05-19T12:50:15.456Z"
}
```

**Status Codes:**
- `200 OK`: Workflow found
- `401 Unauthorized`: Invalid authentication token
- `404 Not Found`: Workflow not found

### Get Workflow Results

Retrieves the results of a completed workflow.

**Endpoint:** `GET /api/workflows/{workflow_id}/results`

**Path Parameters:**
- `workflow_id`: ID of the workflow to retrieve results for

**Response:**
```json
{
  "workflow_id": "789e0123-e45b-67d8-a901-426614174000",
  "status": "completed",
  "target": "192.168.1.1",
  "tasks": [
    {
      "task_id": "123e4567-e89b-12d3-a456-426614174000",
      "task_type": "reconnaissance",
      "status": "completed",
      "result": {
        "target": "192.168.1.1",
        "open_ports": [22, 80, 443],
        "services": {
          "22": "SSH",
          "80": "HTTP",
          "443": "HTTPS"
        },
        "os_info": "Linux Ubuntu 20.04",
        "summary": "Reconnaissance completed successfully"
      }
    },
    {
      "task_id": "456e7890-e12b-34d5-a678-426614174000",
      "task_type": "vulnerability_discovery",
      "status": "completed",
      "result": {
        "target": "192.168.1.1",
        "services_analyzed": 3,
        "vulnerability_findings": [
          {
            "service": "Apache HTTP Server",
            "version": "2.4.41",
            "port": 80,
            "vulnerabilities": [
              {
                "name": "Apache HTTP Server: mod_proxy SSRF",
                "cve_id": "CVE-2021-40438",
                "cvss_score": 7.5,
                "risk_level": "High"
              }
            ],
            "total_vulnerabilities": 1,
            "highest_risk": 7.5
          }
        ],
        "total_vulnerabilities": 1,
        "critical_vulnerabilities": 0,
        "high_risk_vulnerabilities": 1,
        "summary": "Found 1 high-risk vulnerability in Apache HTTP Server 2.4.41"
      }
    }
  ],
  "created_at": "2025-05-19T12:45:30.789Z",
  "updated_at": "2025-05-19T13:15:22.456Z"
}
```

**Status Codes:**
- `200 OK`: Results found
- `401 Unauthorized`: Invalid authentication token
- `404 Not Found`: Workflow not found

### Generate Workflow Report

Generates an HTML report for a completed workflow.

**Endpoint:** `GET /api/workflows/{workflow_id}/report`

**Path Parameters:**
- `workflow_id`: ID of the workflow to generate report for

**Response:**
HTML content with security assessment report

**Content Type:** `text/html`

**Status Codes:**
- `200 OK`: Report generated successfully
- `400 Bad Request`: Workflow not completed yet
- `401 Unauthorized`: Invalid authentication token
- `404 Not Found`: Workflow not found

## Knowledge Base

### Query Attack Patterns

Queries attack patterns in the knowledge base.

**Endpoint:** `POST /api/knowledge/attack_patterns`

**Request Body:**
```json
{
  "query": "password brute force",
  "n_results": 5,
  "tactics": ["Credential Access"]
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "attack_pattern_1",
      "name": "Password Spraying",
      "description": "Adversaries may use a single or small list of commonly used passwords against many different accounts to attempt to acquire valid credentials...",
      "mitre_id": "T1110.003",
      "tactics": ["Credential Access"],
      "techniques": ["Brute Force"],
      "similarity": 0.92
    },
    {
      "id": "attack_pattern_2",
      "name": "Brute Force",
      "description": "Adversaries may use brute force techniques to gain access to accounts when passwords are unknown or when password hashes are obtained...",
      "mitre_id": "T1110",
      "tactics": ["Credential Access"],
      "techniques": ["Brute Force"],
      "similarity": 0.85
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Query successful
- `401 Unauthorized`: Invalid authentication token

### Query Vulnerabilities

Queries vulnerabilities in the knowledge base.

**Endpoint:** `POST /api/knowledge/vulnerabilities`

**Request Body:**
```json
{
  "query": "Apache 2.4.41 vulnerability",
  "n_results": 5,
  "affected_service": "Apache HTTP Server",
  "min_cvss": 7.0
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "vuln_1",
      "name": "Apache HTTP Server: mod_proxy SSRF",
      "description": "A Server Side Request Forgery (SSRF) vulnerability existed in mod_proxy...",
      "cve_id": "CVE-2021-40438",
      "cvss_score": 7.5,
      "affected_services": ["Apache HTTP Server"],
      "attack_vectors": ["SSRF"],
      "similarity": 0.88
    },
    {
      "id": "vuln_2",
      "name": "Apache HTTP Server: mod_auth_digest Buffer Overflow",
      "description": "A buffer overflow in mod_auth_digest in Apache HTTP Server...",
      "cve_id": "CVE-2016-2161",
      "cvss_score": 7.5,
      "affected_services": ["Apache HTTP Server"],
      "attack_vectors": ["Buffer Overflow"],
      "similarity": 0.75
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Query successful
- `401 Unauthorized`: Invalid authentication token

### Query Service Fingerprints

Queries service fingerprints in the knowledge base.

**Endpoint:** `POST /api/knowledge/service_fingerprints`

**Request Body:**
```json
{
  "query": "SSH server Ubuntu",
  "n_results": 5,
  "service_name": "OpenSSH",
  "port": 22
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "service_1",
      "service_name": "OpenSSH",
      "version_pattern": "OpenSSH_([\\d.]+)",
      "description": "OpenSSH is the premier connectivity tool for remote login with the SSH protocol...",
      "default_ports": [22],
      "banner_patterns": ["SSH-2.0-OpenSSH"],
      "similarity": 0.94
    },
    {
      "id": "service_2",
      "service_name": "Dropbear SSH",
      "version_pattern": "dropbear_([\\d.]+)",
      "description": "Dropbear is a relatively small SSH server and client...",
      "default_ports": [22],
      "banner_patterns": ["SSH-2.0-dropbear"],
      "similarity": 0.72
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Query successful
- `401 Unauthorized`: Invalid authentication token

## WebSocket Notifications

### Task Updates WebSocket

Receives real-time updates on task status changes.

**WebSocket Endpoint:** `ws://localhost:8000/ws/task-updates`

**Message Format:**
```json
{
  "event": "task_updated",
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "in_progress",
  "progress": 75.0,
  "message": "Analyzing service banners",
  "timestamp": "2025-05-19T12:38:22.456Z"
}
```

**Event Types:**
- `task_created`: A new task has been created
- `task_assigned`: A task has been assigned to an agent
- `task_updated`: A task's status has been updated
- `task_completed`: A task has been completed
- `task_failed`: A task has failed

## Error Handling

API errors are returned as JSON objects with the following structure:

```json
{
  "detail": "Error message describing the issue"
}
```

Common HTTP status codes:
- `200 OK`: Request successful
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Invalid authentication token
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

## Data Models

### Task Models

```python
class TaskScope(BaseModel):
    ip_range: str
    excluded_ips: List[str] = []
    excluded_ports: List[int] = []
    max_depth: int = 2

class TaskCreate(BaseModel):
    type: Literal["reconnaissance", "vulnerability_discovery", "exploitation", "reporting"]
    target: str
    scope: TaskScope
    description: str
    parent_task_id: Optional[UUID] = None
    priority: int = 1

class TaskResponse(BaseModel):
    task_id: UUID
    status: str
    created_at: datetime

class TaskStatus(BaseModel):
    task_id: UUID
    status: Literal["created", "assigned", "in_progress", "completed", "failed"]
    agent_id: Optional[str] = None
    progress: float = 0.0
    message: Optional[str] = None
    updated_at: datetime

class TaskResult(BaseModel):
    task_id: UUID
    status: Literal["success", "partial", "failed"]
    data: Dict[str, Any]
    summary: str
    created_at: datetime
```

### Message Models

```python
class Message(BaseModel):
    message_id: UUID
    sender_id: str
    recipient_id: Optional[str] = None
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime
    reply_to: Optional[UUID] = None
    metadata: Dict[str, Any] = {}

class TaskAssignmentMessage(Message):
    message_type: str = "task_assignment"
    content: Dict[str, Any]

class TaskStatusUpdateMessage(Message):
    message_type: str = "task_status_update"
    content: Dict[str, Any]

class TaskResultMessage(Message):
    message_type: str = "task_result"
    content: Dict[str, Any]

class KnowledgeQueryMessage(Message):
    message_type: str = "knowledge_query"
    content: Dict[str, Any]

class KnowledgeResponseMessage(Message):
    message_type: str = "knowledge_response"
    content: Dict[str, Any]
```

## Examples

### Create and Monitor a Reconnaissance Task

```python
import requests
import json
import time

# Authentication token
headers = {
    "Authorization": "Bearer dev_token",
    "Content-Type": "application/json"
}

# Create a reconnaissance task
task_data = {
    "type": "reconnaissance",
    "target": "192.168.1.1",
    "scope": {
        "ip_range": "192.168.1.0/24",
        "excluded_ips": [],
        "excluded_ports": [],
        "max_depth": 2
    },
    "description": "Test reconnaissance task",
    "priority": 2
}

# Send the request
response = requests.post(
    "http://localhost:8000/api/task/create",
    headers=headers,
    json=task_data
)

# Get the task ID
task_id = response.json()["task_id"]
print(f"Created task with ID: {task_id}")

# Monitor task status until completion
while True:
    status_response = requests.get(
        f"http://localhost:8000/api/task/{task_id}/status",
        headers=headers
    )
    
    status = status_response.json()
    print(f"Status: {status['status']} - Progress: {status['progress']}%")
    print(f"Message: {status['message']}")
    
    if status["status"] in ["completed", "failed"]:
        break
    
    time.sleep(2)

# Get the task result
result_response = requests.get(
    f"http://localhost:8000/api/task/{task_id}",
    headers=headers
)

result = result_response.json()
print("\nTask Result:")
print(json.dumps(result["result"], indent=2))
```

### Run a Complete Security Assessment Workflow

```python
import requests
import json
import time

# Authentication token
headers = {
    "Authorization": "Bearer dev_token",
    "Content-Type": "application/json"
}

# Create a workflow
workflow_data = {
    "target": "192.168.1.1",
    "scope": {
        "ip_range": "192.168.1.0/24",
        "excluded_ips": [],
        "excluded_ports": [],
        "max_depth": 2
    },
    "description": "Test security assessment"
}

# Send the request
response = requests.post(
    "http://localhost:8000/api/workflows/recon_vuln",
    headers=headers,
    json=workflow_data
)

# Get the workflow ID
workflow_id = response.json()["workflow_id"]
print(f"Created workflow with ID: {workflow_id}")

# Monitor workflow status until completion
while True:
    workflow_response = requests.get(
        f"http://localhost:8000/api/workflows/{workflow_id}",
        headers=headers
    )
    
    workflow = workflow_response.json()
    print(f"Workflow status: {workflow['status']}")
    print(f"Tasks: {len(workflow.get('tasks', []))}")
    
    if workflow["status"] == "completed":
        break
    
    time.sleep(5)

# Get the workflow results
results_response = requests.get(
    f"http://localhost:8000/api/workflows/{workflow_id}/results",
    headers=headers
)

results = results_response.json()
print("\nWorkflow Results:")
print(json.dumps(results, indent=2))

# Generate an HTML report
report_response = requests.get(
    f"http://localhost:8000/api/workflows/{workflow_id}/report",
    headers=headers
)

# Save the report to a file
with open("security_report.html", "w") as f:
    f.write(report_response.text)

print("\nSecurity report saved to security_report.html")
```

### Connect to WebSocket for Real-Time Updates

```javascript
// Browser JavaScript
const socket = new WebSocket('ws://localhost:8000/ws/task-updates');

socket.onopen = function(event) {
    console.log('Connected to WebSocket server');
};

socket.onmessage = function(event) {
    const update = JSON.parse(event.data);
    console.log('Task update received:', update);
    
    // Update UI based on the event type
    if (update.event === 'task_created') {
        console.log(`New task created: ${update.task_id}`);
    } else if (update.event === 'task_updated') {
        console.log(`Task ${update.task_id} updated: ${update.status} (${update.progress}%)`);
        console.log(`Message: ${update.message}`);
    } else if (update.event === 'task_completed') {
        console.log(`Task ${update.task_id} completed`);
    }
};

socket.onclose = function(event) {
    console.log('Disconnected from WebSocket server');
};

socket.onerror = function(error) {
    console.error('WebSocket error:', error);
};
```