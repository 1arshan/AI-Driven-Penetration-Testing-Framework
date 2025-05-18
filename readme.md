# AI-Driven Penetration Testing Framework

A multi-agent system using LangChain and Claude to automate reconnaissance and vulnerability discovery phases of penetration testing.

## Project Overview

This framework uses AI agents powered by large language models to automate and enhance the penetration testing process. The system orchestrates specialized agents through a Multi-agent Cooperation Protocol (MCP) server, enabling them to collaborate on security testing tasks while maintaining human oversight.

Key features:
- Automated reconnaissance and vulnerability discovery
- Integration with industry-standard security tools
- Vector database for intelligent pattern matching
- Human oversight for critical decisions
- Comprehensive reporting system

## Current Status

**Week 1 Complete**: Basic infrastructure, MCP server, and Claude integration implemented.

- ✅ Project structure established
- ✅ FastAPI server with basic endpoints
- ✅ Docker containerization
- ✅ Redis integration for task management
- ✅ Claude API client for AI capabilities
- ✅ Initial testing framework

## Installation & Setup

### Prerequisites

- Docker and Docker Compose
- Anthropic API key for Claude

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AI-Driven-PenTest-Framework.git
cd AI-Driven-PenTest-Framework
```

2. Create a `.env` file in the root directory:
```
# API Keys
ANTHROPIC_API_KEY=your_api_key_here

# Server settings
MCP_SERVER_PORT=8000
ENVIRONMENT=development

# Security
AUTH_TOKEN=dev_token
```

3. Build and start the containers:
```bash
docker-compose up --build
```

4. The server will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access the interactive API documentation at http://localhost:8000/docs

### Create a Task

```bash
curl -X POST "http://localhost:8000/api/task/create" \
  -H "Authorization: Bearer dev_token" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "reconnaissance",
    "target": "192.168.1.1",
    "scope": {
      "ip_range": "192.168.1.0/24"
    },
    "description": "Initial reconnaissance scan"
  }'
```

### Get Task Status

```bash
curl -X GET "http://localhost:8000/api/task/{task_id}" \
  -H "Authorization: Bearer dev_token"
```

## Project Structure

```
AI-Driven-PenTest-Framework/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── src/
│   ├── main.py                  # Application entry point
│   ├── mcp_server/              # MCP server implementation
│   │   ├── app.py               # FastAPI application
│   │   └── redis_client.py      # Redis integration
│   ├── agents/                  # Agent implementations (upcoming)
│   ├── knowledge_base/          # Vector database (upcoming)
│   ├── tools/                   # Security tool integrations (upcoming)
│   └── utils/
│       ├── claude_client.py     # Claude API wrapper
│       └── config.py            # Configuration utilities
└── tests/                       # Test suite
```

## Development Roadmap

- **Week 1**: Project setup and basic infrastructure ✅
- **Week 2**: Agent framework and Redis task management
- **Week 3**: Reconnaissance agent implementation
- **Week 4**: Tool integration framework
- **Week 5**: Vulnerability discovery agent
- **Week 6-7**: Knowledge base with vector database
- **Week 8-9**: End-to-end workflows and reporting
- **Week 10-12**: Testing, optimization, and documentation

## Security Notice

This project is for educational and legitimate security testing purposes only. Always ensure proper authorization before conducting any security testing.

## License

MIT