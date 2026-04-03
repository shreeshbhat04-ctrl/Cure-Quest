# Cure-Quest V1 Implementation Plan

## Immediate goal

Set up the repo so local development can start today with the right foundations:

- Python service scaffold
- MCP server wiring
- Google ADK agent wiring
- environment and dependency files
- local smoke tests

## First milestone

The first working milestone is infrastructure, not full product logic:

1. Boot a FastAPI app locally.
2. Expose a local MCP server with deterministic tools.
3. Configure an ADK agent to connect to the MCP server.
4. Verify imports, tool discovery, and basic request flow.

## Deferred after setup

- Real pharmacy, insurance, and EHR integrations
- Full patient workflow persistence
- Production auth and compliance work
- Rich frontend
