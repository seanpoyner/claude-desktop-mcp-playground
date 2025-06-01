# Claude Desktop MCP Playground

## Overview

Claude Desktop MCP Playground is a Python framework for creating AI-powered productivity workflows using Claude Desktop's Model Context Protocol (MCP) servers. The project enables agentic systems with interconnected AI agents and complex workflow automation.

### Key Features

- **🛠️ Configuration Management CLI** - Easy-to-use command-line tool for managing Claude Desktop MCP server configurations
- **🔄 Simplified Configuration Format** - Convert between Claude Desktop's JSON format and user-friendly key-value pairs
- **🌍 Cross-Platform Support** - Works seamlessly on macOS, Windows, and Linux
- **🚀 Quick Setup** - Streamlined installation and configuration process
- **🧪 Comprehensive Testing** - Fully tested codebase with extensive test coverage

### Quick Start

```bash
# Install the package
pip install -e .

# Import your current Claude Desktop configuration
playground config import
# or use the short form:
pg config import

# View configured MCP servers
pg config show

# Add a new server
pg config add my-server "python" --args "-m" --args "my_module"
```

## Table of Contents

1. [Getting Started](docs/01-getting-started.md)
2. [Installation Guide](docs/02-installation.md)
3. [Basic Configuration](docs/03-basic-configuration.md)
4. [Advanced Server Setup](docs/04-advanced-setup.md)
5. [Productivity Workflows](docs/05-productivity-workflows.md)
6. [Agentic Experimentation](docs/06-agentic-experimentation.md)
7. [Troubleshooting](docs/07-troubleshooting.md)

## Contributing

Contributions to this project are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before getting started.

## License

This project is licensed under the [MIT License](LICENSE.md)
