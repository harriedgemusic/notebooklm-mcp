# NotebookLM MCP Server

This is an unofficial Model Context Protocol (MCP) server for [Google NotebookLM](https://notebooklm.google.com), allowing AI agents and assistants (like Google Antigravity, Claude Code, Cursor, etc.) to query your Notebooks and retrieve citation-backed answers.

## Prerequisites

- Python 3.10+
- A Google NotebookLM session cookie.

## Installation

1. Clone this repository.
2. Initialize and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install .
   ```

## Configuration

You need to authenticate the unofficial API so it can access your Notebooks.

1. **Authenticate via Playwright**:
   Run the interactive login command provided by `notebooklm-py`:
   ```bash
   uv run notebooklm login
   # or if using a standard python venv:
   notebooklm login
   ```
   This will open a Chromium browser window where you can log in to your Google Account. Once logged in and on the NotebookLM page, close the browser. The session will be saved locally.


## Usage

Start the MCP server over `stdio` using the command-line entry point:

```bash
uv run python -m mcp_notebooklm
# or if using standard python venv:
python -m mcp_notebooklm
```

### Server Tools

This server exposes the following MCP tools:

- `list_notebooks`: Lists all your Notebooks (returns their IDs and Titles).
- `get_notebook_sources`: Retrieves the data sources for a specific notebook.
- `ask_notebook`: Passes a natural language query to a specific notebook and returns the AI-generated answer.

## Using with Claude Desktop or Antigravity

Add this to your MCP settings configuration (`mcp.json` or equivalent):

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "/path/to/your/virtualenv/bin/python",
      "args": [
        "-m",
        "mcp_notebooklm"
      ],
      "cwd": "/path/to/this/repo"
    }
  }
}
```
