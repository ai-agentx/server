import requests
import json
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel


class AgentClient:
    def __init__(self, base_url: str = "http://localhost:9090"):
        self.base_url = base_url

    def get_tools(self) -> List[Dict[str, str]]:
        response = requests.get(f"{self.base_url}/tools")
        response.raise_for_status()
        return response.json()

    def create_agent(
            self,
            name: str,
            instructions: str,
            handoff_description: Optional[str] = None,
            model: Optional[str] = None,
            model_settings: Optional[Dict[str, Any]] = None,
            tools: List[str] = []
    ) -> Dict[str, Any]:
        payload = {
            "name": name,
            "instructions": instructions,
            "handoff_description": handoff_description,
            "model": model,
            "model_settings": model_settings,
            "tools": tools
        }

        response = requests.post(
            f"{self.base_url}/agents",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def list_agents(self) -> List[Dict[str, Any]]:
        response = requests.get(f"{self.base_url}/agents")
        response.raise_for_status()
        return response.json()

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/agents/{agent_id}")
        response.raise_for_status()
        return response.json()

    def delete_agent(self, agent_id: str) -> Dict[str, str]:
        response = requests.delete(f"{self.base_url}/agents/{agent_id}")
        response.raise_for_status()
        return response.json()

    def run_agent(
            self,
            agent_id: str,
            input: str,
            context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        payload = {
            "input": input,
            "context": context or {}
        }

        response = requests.post(
            f"{self.base_url}/agents/{agent_id}/run",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def clone_agent(
            self,
            agent_id: str,
            updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/agents/{agent_id}/clone",
            json=updates
        )
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    client = AgentClient()

    tools = client.get_tools()
    print(f"Available tools: {tools}")

    agent = client.create_agent(
        name="Assistant",
        instructions="You are a helpful AI assistant. Answer user questions concisely and accurately.",
        model="deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
        model_settings={"temperature": 0.7},
        tools=["echo"] if "echo" in [t["name"] for t in tools] else []
    )
    print(f"Created agent: {agent}")

    result = client.run_agent(
        agent_id=agent["id"],
        input="Hello, can you help me?",
        context={"user_name": "Alice"}
    )
    print(f"Agent response: {result}")

    cloned_agent = client.clone_agent(
        agent_id=agent["id"],
        updates={
            "name": "Specialized Assistant",
            "instructions": "You are a specialized AI assistant focusing on technical questions."
        }
    )
    print(f"Cloned agent: {cloned_agent}")

    client.delete_agent(agent["id"])
    client.delete_agent(cloned_agent["id"])
