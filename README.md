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

- [ruff](https://github.com/astral-sh/ruff)
