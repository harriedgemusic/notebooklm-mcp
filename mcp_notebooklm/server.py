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
from notebooklm.rpc import (
    ReportFormat,
    AudioFormat,
    AudioLength,
    VideoFormat,
    VideoStyle,
    SlideDeckFormat,
    SlideDeckLength,
    InfographicOrientation,
    InfographicDetail,
)
import re
import pathlib

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

def sanitize_filename(name: str) -> str:
    """Sanitize a string to be used as a valid directory/file name."""
    return re.sub(r'[^\\w\\-]', '_', name).strip('_')

@mcp.tool()
async def select_notebook(notebook_id: str) -> str:
    """
    Selects a notebook by ID and creates a local directory for it based on its title.
    Returns the path to the created directory.
    
    Args:
        notebook_id: The ID of the NotebookLM notebook.
    """
    try:
        async with await NotebookLMClient.from_storage() as client:
            notebooks = await client.notebooks.list()
            title = "Untitled_Notebook"
            for nb in notebooks:
                if nb.id == notebook_id:
                    title = nb.title
                    break
            
            safe_title = sanitize_filename(title)
            output_dir = pathlib.Path(os.getcwd()) / safe_title
            output_dir.mkdir(parents=True, exist_ok=True)
            return f"Created/verified directory: {output_dir.absolute()}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def create_note(notebook_id: str, title: str, content: str) -> str:
    """
    Create a new note in the specified notebook.
    
    Args:
        notebook_id: The ID of the NotebookLM notebook.
        title: The title of the new note.
        content: The text content of the note.
    """
    try:
        async with await NotebookLMClient.from_storage() as client:
            note = await client.notes.create(notebook_id, title=title, content=content)
            return f"Created note '{title}' with ID: {note.id}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def download_notes(notebook_id: str, subfolder_name: str = "notes") -> str:
    """
    Downloads all notes from a specific notebook into a local subfolder within the
    directory created for that notebook. Note: select_notebook should typically be run first to get the main folder.
    
    Args:
        notebook_id: The ID of the NotebookLM notebook.
        subfolder_name: The name of the subfolder to save notes (default: "notes").
    """
    try:
        async with await NotebookLMClient.from_storage() as client:
            notebooks = await client.notebooks.list()
            title = "Untitled_Notebook"
            for nb in notebooks:
                if nb.id == notebook_id:
                    title = nb.title
                    break
            
            safe_title = sanitize_filename(title)
            base_dir = pathlib.Path(os.getcwd()) / safe_title
            notes_dir = base_dir / sanitize_filename(subfolder_name)
            notes_dir.mkdir(parents=True, exist_ok=True)
            
            notes = await client.notes.list(notebook_id)
            count = 0
            for note in notes:
                safe_note_title = sanitize_filename(note.title or "Untitled_Note")
                # Append .md if not present
                filename = f"{safe_note_title}.md"
                file_path = notes_dir / filename
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"# {note.title}\\n\\n{note.content}")
                count += 1
                
            return f"Downloaded {count} notes to {notes_dir.absolute()}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def generate_audio(notebook_id: str, instructions: str = "") -> str:
    """
    Generates an Audio Overview (podcast) for a notebook.
    
    Args:
        notebook_id: The ID of the NotebookLM notebook.
        instructions: Custom instructions for the podcast hosts.
    """
    try:
        async with await NotebookLMClient.from_storage() as client:
            status = await client.artifacts.generate_audio(notebook_id, instructions=instructions)
            return f"Started audio generation. Task ID: {status.task_id} (Status: {status.status})"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def generate_video(notebook_id: str, instructions: str = "") -> str:
    """
    Generates a Video Overview for a notebook.
    
    Args:
        notebook_id: The ID of the NotebookLM notebook.
        instructions: Custom instructions for video generation.
    """
    try:
        async with await NotebookLMClient.from_storage() as client:
            status = await client.artifacts.generate_video(notebook_id, instructions=instructions)
            return f"Started video generation. Task ID: {status.task_id} (Status: {status.status})"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def generate_slides(notebook_id: str, instructions: str = "") -> str:
    """
    Generates a Slide Deck for a notebook.
    
    Args:
        notebook_id: The ID of the NotebookLM notebook.
        instructions: Custom instructions for slide deck generation.
    """
    try:
        async with await NotebookLMClient.from_storage() as client:
            status = await client.artifacts.generate_slide_deck(notebook_id, instructions=instructions)
            return f"Started slide deck generation. Task ID: {status.task_id} (Status: {status.status})"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def generate_infographic(notebook_id: str, instructions: str = "") -> str:
    """
    Generates an Infographic for a notebook.
    
    Args:
        notebook_id: The ID of the NotebookLM notebook.
        instructions: Custom instructions for infographic generation.
    """
    try:
        async with await NotebookLMClient.from_storage() as client:
            status = await client.artifacts.generate_infographic(notebook_id, instructions=instructions)
            return f"Started infographic generation. Task ID: {status.task_id} (Status: {status.status})"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def generate_report(notebook_id: str, format_type: str = "BRIEFING_DOC", instructions: str = "") -> str:
    """
    Generates a Report for a notebook.
    
    Args:
        notebook_id: The ID of the NotebookLM notebook.
        format_type: The type of report to generate. Options: BRIEFING_DOC, STUDY_GUIDE, BLOG_POST, CUSTOM.
        instructions: Custom instructions (required if format_type is CUSTOM).
    """
    try:
        report_format = getattr(ReportFormat, format_type.upper(), ReportFormat.BRIEFING_DOC)
        async with await NotebookLMClient.from_storage() as client:
            status = await client.artifacts.generate_report(
                notebook_id, 
                report_format=report_format, 
                custom_prompt=instructions if format_type.upper() == "CUSTOM" else None
            )
            return f"Started report generation. Task ID: {status.task_id} (Status: {status.status})"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """Run the MCP server over stdio."""
    mcp.run()

if __name__ == "__main__":
    main()
