from pydantic_ai import Agent
from pydantic import BaseModel
from typing import Any, Dict, List
import importlib
import os
from pathlib import Path


class AgentConfig(BaseModel):
    system_prompt: str
    model: str = "" # Configure LLM model here (Llama  or something)
    tools: List[str] = []


class AIAgentManager:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent = Agent(
            model=config.model,
            system_prompt=config.system_prompt
        )
        self._register_tools()
    
    def _register_tools(self):
        """Dynamically register tools from the tools directory"""
        tools_dir = Path("tools")
        if not tools_dir.exists():
            return
        
        for tool_file in tools_dir.glob("*.py"):
            if tool_file.name.startswith("__"):
                continue
            
            module_name = f"tools.{tool_file.stem}"
            try:
                module = importlib.import_module(module_name)
                
                # Look for functions that don't start with underscore
                for attr_name in dir(module):
                    if not attr_name.startswith("_"):
                        attr = getattr(module, attr_name)
                        if callable(attr) and hasattr(attr, "__doc__"):
                            # Register the tool with the agent
                            self.agent.tool(attr)
            except Exception as e:
                print(f"Error loading tool from {tool_file}: {e}")
    
    async def run(self, message: str) -> str:
        """Run the agent with a message"""
        result = await self.agent.run(message)
        return result.data


# Default configuration
DEFAULT_CONFIG = AgentConfig(
    system_prompt="""You are a helpful AI assistant. You have access to various tools to help users accomplish tasks. 
    Use the available tools when appropriate to provide accurate and helpful responses.""",
    model="" # Configure LLM model here (Llama  or something)
)