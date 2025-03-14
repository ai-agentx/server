# agentx

**agentx** provides a REST API wrapper for the openai agents framework, allowing you to create, manage, and run agents via HTTP endpoints.

## Features

- Create and manage agents with various configurations
- Run agents with custom input and context
- Clone existing agents with modifications
- Support for tools and model settings
- Simple in-memory storage for agents (can be extended to use a database)

## Installation

1. Clone repository:
   ```
   git clone https://github.com/ai-agentx/server.git
   cd server
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Running the Server

Start the server with:

```
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

```
docker-compose up -d
```

## Python Client

```python
from agent_client import AgentClient

client = AgentClient()

# Create an agent
agent = client.create_agent(
    name="Assistant",
    instructions="You are a helpful AI assistant.",
    model="gpt-4",
    tools=["echo"]
)

# Run the agent
result = client.run_agent(
    agent_id=agent["id"],
    input="Hello, can you help me?",
    context={"user_name": "Alice"}
)
print(result["result"])
```

## Reference

- [ruff](https://github.com/astral-sh/ruff)
