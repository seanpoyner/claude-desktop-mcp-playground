# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Desktop MCP Playground is a Python framework for creating AI-powered productivity workflows using Claude Desktop's Model Context Protocol (MCP) servers. The project enables agentic systems with interconnected AI agents and complex workflow automation.

### Claude Desktop Configuration Management

This project includes a CLI tool for managing Claude Desktop's MCP server configuration (`claude_desktop_config.json`). The CLI allows users to quickly add, configure, and manage MCP servers without manually editing JSON files.

**Configuration File Locations:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

## Development Commands

### Setup and Installation
```bash
# Environment setup
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Development installation
pip install -e .
```

### Testing
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=claude_desktop_mcp

# Run specific test module
pytest tests/test_agent_framework.py
```

### Code Quality
```bash
# Linting and formatting
black .
isort .
flake8 .
mypy .
```

### Claude Desktop Configuration Management
```bash
# Import current Claude Desktop configuration
playground config import
# or use the short form:
pg config import

# Show current MCP servers configuration
pg config show

# Add a new MCP server
pg config add <server-name> <command> [--args] [--env]

# Remove an MCP server
pg config remove <server-name>

# Validate Claude Desktop configuration
pg config validate

# Apply simplified configuration back to Claude Desktop
pg config apply [simplified-config.json]
```

## Architecture Overview

### Core Components
- **Agent Framework**: Manages AI agent creation and lifecycle
- **Workflow Orchestrator**: Coordinates complex task sequences with timeouts and error handling
- **Resource Manager**: Handles computational resources and API interactions
- **Extensibility Layer**: Plugin system for custom functionality

### Technology Stack
- **Python 3.9+** (3.10+ recommended)
- **Anthropic Claude API** for AI capabilities
- **AsyncIO/aiohttp** for async operations
- **Ray/Dask** for distributed computing
- **Pydantic** for data validation
- **PyTorch/Transformers** for ML operations

### Key Configuration Files
- **config.yaml**: Main configuration with API settings, agent defaults, and workflow configurations
- **example.env**: Environment template with required variables (CLAUDE_MCP_API_KEY, CLAUDE_MCP_WORKSPACE, etc.)
- **package-setup.py**: Python package configuration with entry point `claude-desktop-mcp=claude_desktop_mcp.cli:main`

## Development Guidelines

### Environment Variables
Copy `example.env` to `.env` and configure:
- `CLAUDE_MCP_API_KEY`: Your Anthropic API key
- `CLAUDE_MCP_WORKSPACE`: Path to workspace directory
- `CLAUDE_MCP_LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
- `CLAUDE_MCP_LOG_PATH`: Log file directory (default: ./logs)

### Code Standards
- Follow PEP 8 style guide
- Include type hints for all functions
- Use conventional commit format: `type(scope): description`
- Write unit tests for new functionality

### Security Notes
- API keys are protected via environment variables
- Configuration files support encryption for sensitive data
- Never commit API keys or sensitive credentials