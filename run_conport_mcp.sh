#!/bin/bash

# Debug wrapper for ConPort MCP server
echo "Starting ConPort MCP Server Debug Wrapper" >&2
echo "Working Directory: $(pwd)" >&2
echo "Python Path: $(which python)" >&2
echo "Virtual Env Python: /home/matt/projects/conport/context-portal-git/.venv/bin/python" >&2
echo "Arguments: $@" >&2

# Set environment
export PYTHONPATH="/home/matt/projects/conport/context-portal-git/src"
cd "/home/matt/projects/conport/context-portal-git"

# Run the server
exec /home/matt/projects/conport/context-portal-git/.venv/bin/python -m src.context_portal_mcp.main "$@"




