# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Desktop MCP Playground is a Python CLI tool for managing Claude Desktop's Model Context Protocol (MCP) servers. It provides easy installation, configuration management, and a searchable registry of 30+ MCP servers from the official repository.

### Core Features

- **Server Registry**: Comprehensive database of 30+ MCP servers with installation details
- **CLI Interface**: User-friendly command-line tool (`pg`) for server management  
- **Auto-Installation**: One-line installers for Linux/macOS/Windows
- **Configuration Management**: Direct integration with Claude Desktop configuration files
- **Cross-Platform**: Full support for macOS, Windows, and Linux

### Claude Desktop Configuration Management

The CLI tool manages Claude Desktop's MCP server configuration (`claude_desktop_config.json`):

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

# Add pg command to PATH (manual setup)
./setup-pg-command.sh      # Linux/Mac
.\setup-pg-command.ps1     # Windows
```

### Testing
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=claude_desktop_mcp

# Run specific test module
pytest tests/test_cli.py
```

### Code Quality
```bash
# Linting and formatting
black .
isort .
flake8 .
mypy .
```

### CLI Usage
```bash
# Server management
pg config search <query>       # Search MCP servers
pg config info <server_id>     # Get server details
pg config install <server_id>  # Install a server
pg config list                 # List installed servers
pg config show                 # Show current configuration

# Setup wizard
pg setup                       # Interactive setup
pg setup --quick              # Quick setup with defaults
```

## Architecture Overview

### Core Components
- **CLI Interface** (`cli.py`): Click-based command-line interface
- **Configuration Manager** (`config_manager.py`): Handles Claude Desktop config files
- **Server Registry** (`server_registry.py`): Database of available MCP servers
- **Setup Wizard** (`setup_wizard.py`): Interactive installation and configuration

### Technology Stack
- **Python 3.9+** (3.10+ recommended)
- **Click** for CLI framework
- **Rich** for enhanced terminal output
- **PyTest** for testing
- **Cross-platform** file system operations

### Key Files
- **pyproject.toml**: Modern Python packaging with entry points for `pg` command
- **requirements.txt**: Python dependencies
- **install-full.sh/ps1**: Cross-platform installation scripts
- **setup-pg-command.sh/ps1**: Manual PATH setup scripts

## MCP Server Registry

The registry contains 30+ servers categorized as:

### Official Servers (15)
Current and archived servers from @modelcontextprotocol:
- `filesystem`, `memory`, `puppeteer`, `everything`, `sequential-thinking`
- `fetch`, `brave-search`, `github`, `gitlab`, `postgres`, `slack`
- `google-drive`, `google-maps`, `sqlite`, `time`

### Community Servers (19)
Popular third-party servers:
- **Cloud**: `aws-third-party`, `azure`, `cloudflare`, `heroku`
- **Databases**: `elasticsearch`, `clickhouse`
- **Development**: `jetbrains`, `e2b`, `xcode`
- **Web**: `browserbase`, `firecrawl`, `exa`, `kagi`
- **Project Management**: `linear`, `hubspot`, `grafana`
- **Messaging**: `confluence`
- **Design**: `figma`, `json-resume`

## Development Guidelines

### Environment Variables
Required for testing and development:
- `CLAUDE_MCP_API_KEY`: Anthropic API key (if needed)
- `CLAUDE_MCP_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Code Standards
- Follow PEP 8 style guide
- Include type hints for all functions
- Use conventional commit format: `type(scope): description`
- Write unit tests for new functionality
- Update documentation for user-facing changes

### Testing Strategy
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test CLI commands end-to-end
- **Configuration Tests**: Verify Claude Desktop config file handling
- **Cross-Platform Tests**: Ensure compatibility across OS platforms

### Security Notes
- No API keys or sensitive data in repository
- Configuration files handle user credentials securely
- Installation scripts use official package sources only
- PATH modifications are user-scoped, not system-wide

## File Structure

```
claude_desktop_mcp/
├── __init__.py                 # Package initialization
├── cli.py                      # Main CLI interface
├── config_manager.py           # Configuration file management
├── server_registry.py          # MCP server database
└── setup_wizard.py             # Interactive setup

tests/
├── conftest.py                 # Test configuration
├── test_cli.py                 # CLI command tests
├── test_config_manager.py      # Configuration tests
└── test_import_script.py       # Import functionality tests

docs/                           # User documentation
install-full.sh/ps1            # Cross-platform installers
setup-pg-command.sh/ps1        # PATH setup scripts
pyproject.toml                 # Package configuration
requirements.txt               # Dependencies
```

## Important Implementation Notes

### Server Registry Format
Each server entry includes:
- `name`, `description`, `category` (official/community)
- `package`, `install_method`, `command`, `args_template`
- `required_args`, `env_vars`, `setup_help`
- `homepage` for documentation

### CLI Commands Structure
- `pg config` - All configuration management commands
- `pg setup` - Interactive setup wizard
- Global options: `--help`, `--version`

### Cross-Platform Considerations
- Use `pathlib.Path` for file operations
- Handle Windows/Unix path differences
- Test shell profile updates (.bashrc, .zshrc, PowerShell)
- Consider case sensitivity in file operations