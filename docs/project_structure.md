# Project Directory Structure

```
ai-driven-pentesting/
├── .env                              # Environment variables (API keys, settings)
├── .gitignore                        # Git ignore file
├── docker-compose.yml                # Docker configuration for all services
├── Dockerfile                        # Base Docker image for the project
├── README.md                         # Project overview and quick start guide
├── requirements.txt                  # Python dependencies
│
├── docs/                             # Comprehensive documentation
│   ├── images/                       # Diagrams and screenshots
│   │   ├── architecture_diagram.png  # System architecture visualization
│   │   └── workflow_diagram.png      # Multi-agent workflow visualization
│   ├── overview.md                   # Project overview and introduction
│   ├── architecture.md               # Detailed architecture description
│   ├── agents.md                     # Agent system documentation
│   ├── knowledge_base.md             # Knowledge base documentation
│   ├── mcp_server.md                 # MCP server documentation
│   ├── api.md                        # API reference
│   └── examples.md                   # Usage examples
│
├── src/                              # Source code
│   ├── __init__.py                   # Package initialization
│   ├── main.py                       # Application entry point
│   │
│   ├── agents/                       # Agent implementations
│   │   ├── __init__.py               # Package initialization
│   │   ├── base_agent.py             # Base agent class with common functionality
│   │   ├── agent_registry.py         # Registry for tracking agent instances
│   │   ├── reconnaissance_agent.py   # Agent for reconnaissance tasks
│   │   ├── kb_reconnaissance_agent.py # Knowledge-enhanced reconnaissance agent
│   │   ├── vulnerability_discovery_agent.py # Agent for vulnerability discovery
│   │   └── knowledge_base_agent.py   # Agent for knowledge base queries
│   │
│   ├── knowledge_base/              # Knowledge base implementation
│   │   ├── __init__.py              # Package initialization
│   │   ├── base_kb.py               # Base knowledge base with ChromaDB integration
│   │   ├── security_kb.py           # Security-specific knowledge base
│   │   │
│   │   ├── importers/               # Data importers for the knowledge base
│   │   │   ├── __init__.py          # Package initialization
│   │   │   ├── security_data_importer.py # Main importer for security data
│   │   │   ├── mitre_importer.py    # Importer for MITRE ATT&CK data
│   │   │   ├── vulnerability_importer.py # Importer for vulnerability data
│   │   │   └── service_importer.py  # Importer for service fingerprints
│   │
│   ├── mcp_server/                  # MCP (Multi-agent Cooperation Protocol) server
│   │   ├── __init__.py              # Package initialization
│   │   ├── app.py                   # FastAPI application with API endpoints
│   │   ├── task_queue.py            # Enhanced task management with Redis
│   │   ├── ws_handler.py            # WebSocket connection manager
│   │   ├── message_bus.py           # Agent communication message bus
│   │   ├── workflow_orchestrator.py # Orchestration for multi-agent workflows
│   │   └── report_generator.py      # Security report generation
│   │
│   ├── models/                      # Data models
│   │   ├── __init__.py              # Package initialization
│   │   ├── task_models.py           # Models for task data
│   │   └── message_models.py        # Models for agent communication
│   │
│   └── utils/                       # Utilities
│       ├── __init__.py              # Package initialization
│       ├── config.py                # Configuration utilities
│       ├── claude_client.py         # Claude API integration
│       ├── run_agent.py             # Utility for running agents
│       ├── test_agent_communication.py # Test for agent communication
│       ├── test_chromadb.py         # Test for ChromaDB connection
│       ├── test_kb_integration.py   # Test for KB integration
│       ├── test_task_queue.py       # Test for task queue
│       ├── test_workflow.py         # Test for multi-agent workflow
│       ├── view_messages.py         # Utility for viewing agent messages
│       ├── ws_client.py             # WebSocket client for testing
│       └── agent_manager.py         # Manager for running multiple agents
│
└── tests/                          # Test suite
    ├── __init__.py                 # Package initialization
    └── test_mcp_server.py          # Tests for MCP server
```

## Key Files and Their Functions

### Core Server Components

- **src/main.py**: Main entry point for the application, starts the FastAPI server
- **src/mcp_server/app.py**: FastAPI application with API endpoints for task management, agent registry, and workflows
- **src/mcp_server/task_queue.py**: Redis-backed task queue system for distributing and tracking tasks
- **src/mcp_server/ws_handler.py**: WebSocket connection manager for real-time updates
- **src/mcp_server/message_bus.py**: Message bus for agent-to-agent communication
- **src/mcp_server/workflow_orchestrator.py**: Orchestrates multi-agent workflows by chaining tasks
- **src/mcp_server/report_generator.py**: Creates HTML security assessment reports from workflow results

### Agent System

- **src/agents/base_agent.py**: Base agent class providing common functionality for all agents
- **src/agents/agent_registry.py**: Registry for tracking and discovering agents in the system
- **src/agents/reconnaissance_agent.py**: Agent specialized for reconnaissance tasks
- **src/agents/vulnerability_discovery_agent.py**: Agent for discovering vulnerabilities in services
- **src/agents/knowledge_base_agent.py**: Agent providing access to the knowledge base
- **src/agents/kb_reconnaissance_agent.py**: Enhanced reconnaissance agent with knowledge base integration

### Knowledge Base

- **src/knowledge_base/base_kb.py**: Base knowledge base class with ChromaDB vector database integration
- **src/knowledge_base/security_kb.py**: Security-specific knowledge base with specialized collections
- **src/knowledge_base/importers/security_data_importer.py**: Main importer for security data
- **src/knowledge_base/importers/mitre_importer.py**: Importer for MITRE ATT&CK data
- **src/knowledge_base/importers/vulnerability_importer.py**: Importer for vulnerability data
- **src/knowledge_base/importers/service_importer.py**: Importer for service fingerprints

### Data Models

- **src/models/task_models.py**: Pydantic models for task data structures
- **src/models/message_models.py**: Pydantic models for agent communication messages

### Utilities

- **src/utils/config.py**: Configuration utilities for accessing environment variables
- **src/utils/claude_client.py**: Client for interacting with the Claude API
- **src/utils/run_agent.py**: Utility for running individual agents
- **src/utils/agent_manager.py**: Manager for running multiple agents concurrently
- **src/utils/test_workflow.py**: Test utility for running multi-agent workflows
- **src/utils/view_messages.py**: Utility for viewing agent messages
- **src/utils/ws_client.py**: WebSocket client for testing the notification system

### Testing

- **tests/test_mcp_server.py**: Tests for the MCP server endpoints
- **src/utils/test_task_queue.py**: Tests for the task queue
- **src/utils/test_chromadb.py**: Tests for the ChromaDB connection
- **src/utils/test_kb_integration.py**: Tests for knowledge base integration
- **src/utils/test_agent_communication.py**: Tests for agent communication

### Configuration

- **.env**: Environment variables for API keys and configuration
- **docker-compose.yml**: Docker configuration for the MCP server, Redis, and ChromaDB
- **Dockerfile**: Docker image definition for the application
- **requirements.txt**: Python dependencies for the project

### Documentation

- **README.md**: Quick start guide and project overview
- **docs/overview.md**: Comprehensive project description
- **docs/architecture.md**: Detailed architecture documentation
- **docs/agents.md**: Documentation for the agent system
- **docs/knowledge_base.md**: Documentation for the knowledge base
- **docs/mcp_server.md**: Documentation for the MCP server
- **docs/api.md**: API reference documentation
- **docs/examples.md**: Usage examples