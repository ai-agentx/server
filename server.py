from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, TypeVar
from contextlib import asynccontextmanager
import uuid
import uvicorn
import os

from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    RunContextWrapper,
    Runner,
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
)
from agents.items import ItemHelpers
from agents.model_settings import ModelSettings
from agents.tool import function_tool
from openai import AsyncOpenAI

BASE_URL = os.getenv("AGENTX_BASE_URL") or "https://api.openai.com/v1"
API_KEY = os.getenv("AGENTX_API_KEY") or "YOUR_KEY"

if not BASE_URL or not API_KEY:
    raise ValueError(
        "Please set EXAMPLE_BASE_URL, EXAMPLE_API_KEY via env var or code."
    )

client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)

set_default_openai_client(client=client, use_for_tracing=False)
set_default_openai_api("chat_completions")
set_tracing_disabled(disabled=True)


class ToolModel(BaseModel):
    name: str
    description: str


class ModelSettingsModel(BaseModel):
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    max_tokens: Optional[int] = 1000


class CreateAgentRequest(BaseModel):
    name: str
    instructions: str
    handoff_description: Optional[str] = None
    model: Optional[str] = None
    model_settings: Optional[ModelSettingsModel] = None
    tools: List[str] = []


class AgentResponse(BaseModel):
    id: str
    name: str
    instructions: str
    handoff_description: Optional[str] = None
    model: Optional[str] = None
    tools: List[str] = []


class RunAgentRequest(BaseModel):
    input: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class RunAgentResponse(BaseModel):
    agent_id: str
    result: str


agents_db = {}
available_tools = {}


class DefaultContext:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


TContext = TypeVar('TContext')


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_available_tools()
    yield
    agents_db.clear()


app = FastAPI(title="agentx", description="rest api wrapper for the multi-agent framework", lifespan=lifespan)


def load_available_tools():
    @function_tool(name_override="echo", description_override="Echo back the input")
    async def echo_tool(context: RunContextWrapper, input: str) -> str:
        return f"Echo: {input}"

    available_tools["echo"] = echo_tool


@app.get("/")
async def root():
    return {"message": "agentx"}


@app.get("/tools", response_model=List[ToolModel])
async def get_tools():
    return [
        ToolModel(name=name, description=tool.description)
        for name, tool in available_tools.items()
    ]


@app.post("/agents", response_model=AgentResponse)
async def create_agent(agent_data: CreateAgentRequest):
    agent_id = str(uuid.uuid4())

    model_settings = ModelSettings()
    if agent_data.model_settings:
        model_settings.temperature = agent_data.model_settings.temperature
        model_settings.top_p = agent_data.model_settings.top_p
        model_settings.max_tokens = agent_data.model_settings.max_tokens

    tools = []
    for tool_name in agent_data.tools:
        if tool_name in available_tools:
            tools.append(available_tools[tool_name])
        else:
            raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")

    agent = Agent(
        name=agent_data.name,
        instructions=agent_data.instructions,
        handoff_description=agent_data.handoff_description,
        model=OpenAIChatCompletionsModel(model=agent_data.model, openai_client=client),
        model_settings=model_settings,
        tools=tools
    )

    agents_db[agent_id] = agent

    return AgentResponse(
        id=agent_id,
        name=agent.name,
        instructions=agent_data.instructions,
        handoff_description=agent.handoff_description,
        model=agent_data.model,
        tools=agent_data.tools
    )


@app.get("/agents", response_model=List[AgentResponse])
async def list_agents():
    return [
        AgentResponse(
            id=agent_id,
            name=agent.name,
            instructions=agent.instructions if isinstance(agent.instructions, str) else "dynamic",
            handoff_description=agent.handoff_description,
            model=agent.model if isinstance(agent.model, str) else str(agent.model) if agent.model else None,
            tools=[tool.name for tool in agent.tools]
        )
        for agent_id, agent in agents_db.items()
    ]


@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = agents_db[agent_id]
    return AgentResponse(
        id=agent_id,
        name=agent.name,
        instructions=agent.instructions if isinstance(agent.instructions, str) else "dynamic",
        handoff_description=agent.handoff_description,
        model=agent.model if isinstance(agent.model, str) else str(agent.model) if agent.model else None,
        tools=[tool.name for tool in agent.tools]
    )


@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    del agents_db[agent_id]
    return {"message": f"Agent {agent_id} deleted successfully"}


@app.post("/agents/{agent_id}/run", response_model=RunAgentResponse)
async def run_agent(agent_id: str, run_request: RunAgentRequest):
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = agents_db[agent_id]

    context = DefaultContext(**run_request.context)

    try:
        result = await Runner.run(
            starting_agent=agent,
            input=run_request.input,
            context=context
        )

        text_result = ItemHelpers.text_message_outputs(result.new_items)

        return RunAgentResponse(
            agent_id=agent_id,
            result=text_result,
        )
    except Exception as e:
        print(f"ERROR:    {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error running agent: {str(e)}")


@app.post("/agents/{agent_id}/clone", response_model=AgentResponse)
async def clone_agent(agent_id: str, updates: Dict[str, Any]):
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    original_agent = agents_db[agent_id]

    new_agent_id = str(uuid.uuid4())

    new_agent = original_agent.clone(**updates)
    agents_db[new_agent_id] = new_agent

    return AgentResponse(
        id=new_agent_id,
        name=new_agent.name,
        instructions=new_agent.instructions if isinstance(new_agent.instructions, str) else "dynamic",
        handoff_description=new_agent.handoff_description,
        model=new_agent.model if isinstance(new_agent.model, str) else str(
            new_agent.model) if new_agent.model else None,
        tools=[tool.name for tool in new_agent.tools]
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 9090))
    uvicorn.run(app, host="0.0.0.0", port=port)
