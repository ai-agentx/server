# server

**server** provides a rest api wrapper for the agent framework, allowing you to create, manage, and run agents via http endpoints.

## Features

- Create and manage agents with various configurations
- Run agents with custom input and context
- Clone existing agents with modifications
- Support for tools and model settings
- Simple in-memory storage for agents (can be extended to use a database)

## Installation

### Clone repository

```bash
git clone https://github.com/ai-agentx/server.git
cd server
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

```bash
python server.py
```

The server will be available at http://localhost:9090 by default.

### API Endpoints

#### Tools

- `GET /tools` - List all available tools

#### Agents

- `POST /agents` - Create a new agent
- `GET /agents` - List all agents
- `GET /agents/{agent_id}` - Get a specific agent
- `DELETE /agents/{agent_id}` - Delete a specific agent
- `POST /agents/{agent_id}/run` - Run an agent with input and context
- `POST /agents/{agent_id}/clone` - Clone an agent with updates

### Docker Deployment

```bash
docker-compose up -d
```

## Reference

- [mcp-agent](https://github.com/lastmile-ai/mcp-agent)
- [openai-agents-mcp](https://github.com/lastmile-ai/openai-agents-mcp/commit/0f0cdd0c7c40bbe15bba27fc8dd3420037288e47#diff-b335630551682c19a781afebcf4d07bf978fb1f8ac04c6bf87428ed5106870f5)
- [openai-agents-python](https://github.com/openai/openai-agents-python)
- [ruff](https://github.com/astral-sh/ruff)
