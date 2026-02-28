import sys
import logging
from typing import Any

# Disable all logging which might write to stdout and break MCP JSON-RPC
logging.basicConfig(level=logging.ERROR)
logging.getLogger().setLevel(logging.ERROR)
# Force notebooklm logging to error as well
import os
os.environ["NOTEBOOKLM_LOG_LEVEL"] = "ERROR"

from mcp.server.fastmcp import FastMCP
from notebooklm.client import NotebookLMClient

# Initialize the MCP Server
mcp = FastMCP("NotebookLM-MCP")

@mcp.tool()
async def list_notebooks() -> list[dict[str, Any]]:
    """
    List all available NotebookLM notebooks for the authenticated user.
    """
    try:
        async with await NotebookLMClient.from_storage() as client:
            notebooks = await client.notebooks.list()
            # Convert the Notebook objects to dictionaries
            return [{"id": nb.id, "title": nb.title, "sources_count": nb.sources_count} for nb in notebooks]
    except Exception as e:
        return [{"error": str(e), "message": "Failed to list notebooks. Are you authenticated via 'notebooklm-py login'?"}]

@mcp.tool()
async def get_notebook_sources(notebook_id: str) -> list[dict[str, Any]]:
    """
    Get all sources associated with a specific NotebookLM notebook.
    
    Args:
        notebook_id: The ID of the NotebookLM notebook.
    """
    try:
        async with await NotebookLMClient.from_storage() as client:
            sources = await client.sources.list(notebook_id)
            return [{"id": src.id, "title": src.title, "type": getattr(src, "source_type", "unknown"), "url": getattr(src, "url", None)} for src in sources]
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
async def ask_notebook(notebook_id: str, query: str) -> str:
    """
    Ask a question to a specific NotebookLM notebook and get an AI-generated answer.
    
    Args:
        notebook_id: The ID of the NotebookLM notebook.
        query: The question to ask in natural language.
    """
    try:
        async with await NotebookLMClient.from_storage() as client:
            result = await client.chat.ask(notebook_id, query)
            return str(result.answer) if hasattr(result, 'answer') else str(result)
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """Run the MCP server over stdio."""
    mcp.run()

if __name__ == "__main__":
    main()
