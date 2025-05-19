# Agent System Documentation

This document provides a detailed overview of the agent system in the AI-Driven Penetration Testing Framework.

## Table of Contents
- [Overview](#overview)
- [Agent Architecture](#agent-architecture)
- [Agent Types](#agent-types)
- [Agent Lifecycle](#agent-lifecycle)
- [Agent Communication](#agent-communication)
- [Agent Capabilities](#agent-capabilities)
- [Implementation Details](#implementation-details)
- [Extending the Agent System](#extending-the-agent-system)

## Overview

The agent system forms the core of the AI-Driven Penetration Testing Framework. It uses a multi-agent architecture where specialized agents collaborate to perform security testing tasks. Each agent has specific capabilities and responsibilities, enabling a modular and extensible approach to security testing.

The agent system is built on these principles:
- **Specialization**: Each agent focuses on specific security testing tasks
- **Autonomy**: Agents can work independently, making decisions based on their expertise
- **Collaboration**: Agents communicate and share information to achieve complex tasks
- **Intelligence**: Agents leverage AI capabilities (via Claude) for advanced reasoning

## Agent Architecture

### Base Agent

All agents inherit from the `BaseAgent` class, which provides core functionality:

- **Task Management**: Retrieving, processing, and updating tasks
- **Status Reporting**: Communicating progress to the MCP server
- **Memory Management**: Maintaining context between operations
- **Message Handling**: Sending and receiving messages
- **LLM Integration**: Interacting with Claude for analysis and reasoning

The base agent implements an event loop that continuously:
1. Polls for available tasks matching the agent's type
2. Processes retrieved tasks
3. Stores results
4. Maintains memory for context

### Agent Registry

The `AgentRegistry` provides a centralized mechanism for:

- Registering new agents with the system
- Tracking agent capabilities and status
- Finding agents by type or identifier
- Maintaining a directory of available agents

## Agent Types

The framework currently implements the following agent types:

### 1. Reconnaissance Agent

**Purpose**: Gather information about target systems and networks

**Capabilities**:
- Network scanning
- Port discovery
- Service detection
- OS fingerprinting
- Banner grabbing

**Implementation**: `src/agents/reconnaissance_agent.py`

**Key Functions**:
- `process_task()`: Performs reconnaissance on a target
- `get_capabilities()`: Returns the agent's capabilities

### 2. Knowledge-Enhanced Reconnaissance Agent

**Purpose**: Extended reconnaissance with knowledge base integration

**Capabilities**:
- All standard reconnaissance capabilities
- Integration with security knowledge base
- Service fingerprinting with pattern matching
- Potential vulnerability identification during reconnaissance

**Implementation**: `src/agents/kb_reconnaissance_agent.py`

**Key Functions**:
- `enrich_service_info()`: Enhances service information with knowledge base data
- `process_task()`: Performs knowledge-enhanced reconnaissance

### 3. Vulnerability Discovery Agent

**Purpose**: Identify security vulnerabilities in target systems

**Capabilities**:
- Vulnerability assessment
- CVE mapping
- Risk scoring
- Exploit potential evaluation

**Implementation**: `src/agents/vulnerability_discovery_agent.py`

**Key Functions**:
- `process_task()`: Analyzes reconnaissance results for vulnerabilities
- `analyze_service_vulnerabilities()`: Evaluates services for security weaknesses

### 4. Knowledge Base Agent

**Purpose**: Provide access to the security knowledge base

**Capabilities**:
- Knowledge queries
- Attack pattern lookup
- Vulnerability information retrieval
- Service fingerprint matching

**Implementation**: `src/agents/knowledge_base_agent.py`

**Key Functions**:
- `handle_knowledge_query()`: Processes knowledge queries from other agents
- `_format_query_results()`: Formats query results for consumption

## Agent Lifecycle

Agents follow a defined lifecycle:

1. **Initialization**:
   - Agent is created with a type and optional ID
   - Redis connection is established
   - Claude client is initialized

2. **Registration**:
   - Agent registers with the MCP server
   - Capabilities are declared
   - Status is set to "idle"

3. **Task Processing Loop**:
   - Agent continuously polls for tasks matching its type
   - When a task is found, it's marked as "assigned"
   - Task is processed according to the agent's specialty
   - Results are stored and status is updated

4. **Shutdown**:
   - Running flag is set to false
   - Current tasks are completed
   - Agent unregisters from the system

## Agent Communication

Agents communicate through a message-based system:

### Message Types:

1. **Task Assignment**: Directs an agent to perform a specific task
2. **Task Status Update**: Reports progress on a task
3. **Task Result**: Contains the outcome of a completed task
4. **Knowledge Query**: Requests information from the knowledge base
5. **Knowledge Response**: Returns requested knowledge

### Communication Flow:

1. Agent creates a message with sender, recipient, type, and content
2. Message is sent through the message bus
3. Message bus delivers to appropriate recipient(s)
4. Recipient processes the message according to its type
5. Optionally, recipient sends a response message

### Implementation:

The agent communication system uses Redis pub/sub for message delivery, with messages stored in Redis for reliability. The `MessageBus` class in `src/mcp_server/message_bus.py` handles the routing and delivery of messages.

## Agent Capabilities

Agents advertise their capabilities during registration, allowing the system to route tasks appropriately. Capabilities are represented as a list of strings.

**Example Capabilities**:

```python
# Reconnaissance Agent
[
    "network_scanning",
    "port_discovery",
    "service_detection",
    "os_fingerprinting",
    "banner_grabbing"
]

# Vulnerability Discovery Agent
[
    "vulnerability_discovery",
    "service_analysis",
    "cve_mapping",
    "risk_assessment",
    "exploit_potential"
]

# Knowledge Base Agent
[
    "knowledge_query",
    "attack_pattern_lookup",
    "vulnerability_lookup",
    "service_fingerprint_lookup"
]
```

## Implementation Details

### BaseAgent Class

The `BaseAgent` class provides the foundation for all agent implementations:

```python
class BaseAgent:
    def __init__(self, agent_type: str, agent_id: Optional[str] = None):
        # Initialize agent with type and ID
        
    async def register_agent(self):
        # Register agent with the MCP server
        
    def get_capabilities(self) -> List[str]:
        # Return agent capabilities
        
    async def get_task(self) -> Optional[Dict[str, Any]]:
        # Get a task from the queue
        
    async def update_task_status(self, task_id: str, status: str, progress: float = 0.0, message: str = ""):
        # Update task status
        
    async def store_result(self, task_id: str, result: Dict[str, Any]):
        # Store task result
        
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Process a task (implemented by subclasses)
        
    async def add_to_memory(self, item: Dict[str, Any]):
        # Add item to agent memory
        
    async def get_memory(self, limit: int = 10) -> List[Dict[str, Any]]:
        # Get recent memory items
        
    async def start(self):
        # Start the agent's main processing loop
        
    async def stop(self):
        # Stop the agent
        
    async def send_message(self, message: Dict[str, Any]) -> str:
        # Send a message to another agent
        
    async def handle_task_assignment(self, message: Dict[str, Any]):
        # Handle a task assignment message
        
    async def handle_knowledge_response(self, message: Dict[str, Any]):
        # Handle a knowledge response message
        
    async def query_knowledge_base(self, query: str, collection: str, n_results: int = 5) -> str:
        # Query the knowledge base
```

### Task Processing

The core of each agent is its `process_task` method, which implements the agent's specialized functionality:

```python
# In ReconnaissanceAgent
async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
    # Extract task details
    target = task.get("target")
    scope = task.get("scope", {})
    task_id = task.get("id")
    
    # Update status
    await self.update_task_status(
        task_id=task_id,
        status="in_progress",
        progress=10.0,
        message=f"Starting reconnaissance on {target}"
    )
    
    # Perform reconnaissance (simulation)
    # In a real implementation, this would use actual security tools
    
    # Return results
    return {
        "target": target,
        "open_ports": [22, 80, 443],
        "services": {
            "22": "SSH",
            "80": "HTTP",
            "443": "HTTPS"
        },
        "os_info": "Linux Ubuntu 20.04",
        "summary": "Reconnaissance completed successfully"
    }
```

## Extending the Agent System

The agent system is designed to be extensible, allowing for new agent types to be added easily:

### Creating a New Agent Type

1. Create a new class that inherits from `BaseAgent`
2. Implement the `get_capabilities()` method to declare capabilities
3. Implement the `process_task()` method with specialized functionality
4. Optionally, add custom message handlers for specific message types

Example:

```python
class ReportingAgent(BaseAgent):
    def __init__(self, agent_id=None):
        super().__init__(agent_type="reporting", agent_id=agent_id)
    
    def get_capabilities(self) -> List[str]:
        return [
            "report_generation",
            "finding_aggregation",
            "risk_assessment",
            "remediation_recommendation"
        ]
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation for report generation
        # ...
        return report_data
```

### Registering a New Agent Type

1. Add the new agent type to the `run_agent.py` utility
2. Update the `agent_manager.py` to support the new agent type
3. Add any necessary API endpoints to the MCP server

### Agent Collaboration Patterns

When creating new agent types, consider these collaboration patterns:

1. **Sequential Processing**: Agents work in a predefined sequence (e.g., reconnaissance → vulnerability discovery → exploitation)
2. **Parallel Processing**: Multiple agents work simultaneously on different aspects of a task
3. **Hierarchical Collaboration**: Higher-level agents delegate subtasks to specialized agents
4. **Peer-to-Peer Collaboration**: Agents communicate directly to share information and coordinate activities
