import json
import os
from pathlib import Path
from typing import Callable, Optional

from langgraph.types import interrupt
from langchain_core.tools import BaseTool, tool
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient


def load_mcp_servers(config_path):
    """
    Load MCP server definitions from a JSON config file.
    Expects a top-level 'mcpServers' dict in the config.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r") as f:
        config = json.load(f)
    servers = config.get("mcpServers", {})
    # Optionally add default transports if missing
    for name, server in servers.items():
        if "command" in server and "transport" not in server:
            server["transport"] = "stdio"
        if "url" in server and "transport" not in server:
            server["transport"] = "streamable_http"
    return servers


def add_approval(main_tool: Callable | BaseTool) -> BaseTool:
    """Wrap a tool to support human-in-the-loop review."""
    if not isinstance(main_tool, BaseTool):
        main_tool = tool(main_tool)

    @tool(  
        main_tool.name,
        description=main_tool.description,
        args_schema=main_tool.args_schema
    )
    async def call_main_tool_with_hitl(config: RunnableConfig, **tool_input):
        decision = interrupt({
            "awaiting": main_tool.name,
            "args": tool_input
        })

        # tool approved
        if isinstance(decision, dict) and decision.get("approved"):
            result = await main_tool.ainvoke(tool_input, config)
            return result

        # tool rejected
        return "Cancelled by human. Continue without executing that tool and provide next steps."
        

    return call_main_tool_with_hitl


# Cache for loaded tools to avoid reloading on every request
_cached_tools: Optional[list] = None
_cached_checkpointer = None


async def get_mcp_tools_with_hitl():
    """
    Async function to load and wrap MCP tools with HITL approval.
    Caches the result to avoid reloading on every request.
    """
    global _cached_tools
    
    if _cached_tools is not None:
        return _cached_tools
    
    config_path = Path(__file__).parent.parent / "config" / "mcp_servers.json"
    
    mcp_servers = load_mcp_servers(str(config_path))
    client = MultiServerMCPClient(mcp_servers)
    mcp_tools = await client.get_tools()
    tools_with_hitl = [add_approval(tool) for tool in mcp_tools]
    
    _cached_tools = tools_with_hitl
    return tools_with_hitl


async def get_agent():
    """
    Get or create the MCP agent with HITL-wrapped tools.
    
    NOTE: We create a fresh agent each time but use a SHARED checkpointer.
    This allows different requests to access the same conversation state
    while avoiding issues with cached agent instances.
    """
    global _cached_checkpointer
    
    # Create checkpointer once and reuse it
    if _cached_checkpointer is None:
        _cached_checkpointer = InMemorySaver()
    
    tools_with_hitl = await get_mcp_tools_with_hitl()
    
    agent = create_react_agent(
        model="openai:gpt-4o-mini",
        prompt="You are a GitHub Assistant that helps users manage their GitHub repositories and workflows.",
        tools=tools_with_hitl,
        checkpointer=_cached_checkpointer,  # Shared across all agents
    )
    
    return agent





# --- Exports ---
__all__ = ["get_agent"]