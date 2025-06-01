# Claude Desktop MCP Playground Installation Guide

## Supported Platforms

- **Windows 10/11** (64-bit) with WSL2 support
- **macOS 11.0+** (Big Sur and later) on Intel and Apple Silicon
- **Linux** (Ubuntu 20.04+, Fedora 33+, CentOS 8+)

## Prerequisites

- **Python 3.9+** (3.10+ recommended)
- **Claude Desktop application** installed
- **pip** or **uv** package manager
- Virtual environment support

## Installation Methods

### 1. Quick Installation (Recommended)

```bash
# Clone and install in one command
git clone https://github.com/seanpoyner/pg-playground.git
cd pg-playground
pip install -e .
```

### 2. Development Installation

```bash
# For contributors and advanced users
git clone https://github.com/seanpoyner/pg-playground.git
cd pg-playground
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
```

## Core Dependencies

The following packages are automatically installed:

- **click** - Command-line interface framework
- **pydantic** - Data validation and settings management
- **pyyaml** - YAML configuration file support
- **pathlib** - Cross-platform path handling

### Optional Dependencies

```bash
# For testing
pip install pytest pytest-cov

# For development
pip install black isort mypy flake8
```

## Claude Desktop Configuration Locations

The CLI automatically detects your Claude Desktop configuration:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### No Additional Setup Required

Unlike other MCP tools, this playground works with your existing Claude Desktop installation. No API keys or additional configuration needed!

## Verification

Verify installation by running:

```bash
# Check CLI is available
playground --help
# or use the short form:
pg --help

# View current configuration
pg config show

# Import existing config (if any)
pg config import
```

## Troubleshooting Installation

### Common Issues

1. **Python Version**: Ensure Python 3.9+ is installed
   ```bash
   python --version  # Should show 3.9 or higher
   ```

2. **Virtual Environment**: Use virtual environments to avoid conflicts
   ```bash
   python -m venv claude_mcp_env
   source claude_mcp_env/bin/activate
   ```

3. **Permission Issues**: On some systems, use `--user` flag
   ```bash
   pip install --user -e .
   ```

4. **Path Issues**: Ensure the CLI is in your PATH
   ```bash
   which playground  # Should show installation path
   which pg         # Both commands should work
   ```

### System Requirements

- **Minimum**: Python 3.9+, 1GB RAM, 100MB disk space
- **Recommended**: Python 3.10+, 4GB RAM, 500MB disk space
- **Operating System**: Any platform that supports Python and Claude Desktop

## Next Steps

- [Learn Basic Configuration Management](03-basic-configuration.md)
- [Explore Advanced Setup Options](04-advanced-setup.md)
- [Start Building Productivity Workflows](05-productivity-workflows.md)

## Getting Help

If you encounter issues:

1. Check our [Troubleshooting Guide](07-troubleshooting.md)
2. Review the CLI help: `playground --help` or `pg --help`
3. Open an issue on [GitHub](https://github.com/seanpoyner/pg-playground/issues)
