"""Map Agent – handles Care Maze location search and route generation.

Uses the Google Maps MCP server to find nearby pharmacies, clinics, hospitals,
and labs, and to generate navigation routes for patients.
"""

import os

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from cure_quest.config import get_settings

settings = get_settings()

_google_maps_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-google-maps"],
    env=os.environ.copy(),
)

map_agent = LlmAgent(
    model=settings.gemini_fast_model_id,
    name="cure_quest_map_agent",
    description=(
        "Finds nearby care destinations (pharmacies, clinics, hospitals, labs) "
        "and generates navigation routes using Google Maps MCP tools. "
        "Handles all location-based queries for the Care Maze workflow."
    ),
    instruction=(
        "You are the Cure-Quest Map Agent. Your role is to help patients find "
        "nearby healthcare destinations and navigate to them.\n\n"
        "CAPABILITIES:\n"
        "1. NEARBY SEARCH: Find pharmacies, clinics, hospitals, and labs near "
        "the patient's location using Google Maps search tools.\n"
        "2. ROUTE GENERATION: Build navigation routes from the patient's current "
        "location to a selected care destination.\n"
        "3. DISTANCE & ETA: Provide estimated travel time and distance.\n"
        "4. CONTEXT-AWARE: Consider medication name or condition context when "
        "recommending destinations (e.g., pharmacies that may stock a specific medication).\n\n"
        "RULES:\n"
        "- Always include a map link or directions URL in your response.\n"
        "- State the source used (Google Maps) for transparency.\n"
        "- If location is not provided, ask the patient for their location or suggest "
        "using browser geolocation.\n"
        "- Provide at least 2-3 nearby options when searching for destinations.\n"
        "- Include address, distance, and estimated travel time when available."
    ),
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(server_params=_google_maps_params),
        ),
    ],
)
