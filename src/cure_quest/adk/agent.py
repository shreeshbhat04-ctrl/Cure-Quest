import os
from pathlib import Path
import sys

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from cure_quest.config import get_settings

settings = get_settings()
repo_root = Path(__file__).resolve().parents[3]

server_command = sys.executable if settings.mcp_server_command == "python" else settings.mcp_server_command

server_params = StdioServerParameters(
    command=server_command,
    args=settings.mcp_server_arg_list,
    cwd=str(repo_root),
    env=os.environ.copy(),
)

google_maps_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-google-maps"],
    env=os.environ.copy(),
)

from cure_quest.adk.recipe_agent import recipe_agent
from cure_quest.adk.vision_agent import vision_agent

root_agent = LlmAgent(
    model=settings.adk_model,
    name="cure_quest_root",
    description="Development agent for verifying Cure-Quest MCP connectivity.",
    instruction=(
        "You are the Cure-Quest bootstrap agent. Use MCP tools to verify local connectivity "
        "and summarize patient context conservatively. Delegate recipe specific tasks "
        "to the recipe agent. Delegate any uploaded medical image analysis "
        "to the vision agent."
    ),
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(server_params=server_params),
        ),
        McpToolset(
            connection_params=StdioConnectionParams(server_params=google_maps_params),
        ),
    ],
    delegates=[recipe_agent, vision_agent],
)

