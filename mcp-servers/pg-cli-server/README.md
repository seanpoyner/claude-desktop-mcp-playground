# PG CLI MCP Server

An MCP server that wraps the `pg` (Claude Desktop MCP Playground) CLI commands, allowing Claude Desktop to directly manage MCP servers through natural language conversation.

## ✨ Features

This MCP server provides the following tools:

- **pg_config_search** - Search available MCP servers in the registry
- **pg_config_info** - Get detailed information about a specific MCP server  
- **pg_config_install** - Install an MCP server
- **pg_config_show** - Show the current Claude Desktop configuration
- **pg_config_remove** - Remove an installed MCP server

## 🚀 Auto-Installation

The server features **automatic detection and dependency management**:

- ✅ **Auto-detects server path** across Windows, macOS, and Linux
- ✅ **Automatically installs MCP dependency** if not present
- ✅ **Cross-platform support** including WSL
- ✅ **No manual configuration required**

## 📋 Prerequisites

- Python 3.9 or higher
- The `pg` CLI tool must be installed and available in PATH
- Claude Desktop MCP Playground must be set up

## 🔧 Installation

### Option 1: Auto-Installation (Recommended)
Install through the MCP Server Manager GUI or CLI:
```bash
pg config install pg-cli-server
```

The system will automatically:
1. Detect your platform and locate the server files
2. Install the MCP dependency if needed
3. Configure Claude Desktop

### Option 2: Manual Installation
1. Ensure dependencies are available:
   ```bash
   pip install mcp>=1.0.0
   ```

2. Add to your Claude Desktop configuration:
   ```json
   {
     "mcpServers": {
       "pg-cli-server": {
         "command": "python",
         "args": ["C:\\path\\to\\launcher.py"]
       }
     }
   }
   ```

## 💬 Usage

Once installed, you can ask Claude Desktop to:

- **"Search for filesystem servers"** → Finds servers matching "filesystem"
- **"Install the github server"** → Installs GitHub MCP server
- **"Show my current MCP configuration"** → Displays all configured servers
- **"What servers are available for databases?"** → Searches for database-related servers
- **"Remove the memory server"** → Uninstalls the memory server

## 🔧 Available Tools

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `pg_config_search` | Search servers by name/description | Search for "git" servers |
| `pg_config_info` | Get detailed server information | Get info about "filesystem" server |
| `pg_config_install` | Install a server from registry | Install "github" server |
| `pg_config_show` | Show current configuration | Show all my servers |
| `pg_config_remove` | Remove an installed server | Remove "memory" server |

## 🛠 Technical Details

### Architecture
- **Launcher Script**: `launcher.py` handles dependency installation and server startup
- **Main Server**: `server.py` contains the core MCP server implementation
- **Auto-Detection**: Platform-specific path detection for seamless setup

### Error Handling
- Missing `pg` command detection
- Command timeouts (60 second limit)
- Invalid server ID validation
- Installation failure recovery
- Dependency installation automation

### Cross-Platform Support
- **Windows**: Native Python installation
- **macOS**: Python3 with homebrew support
- **Linux**: Standard Python3 installation
- **WSL**: Automatic Windows filesystem detection

## 📁 File Structure

```
mcp-servers/pg-cli-server/
├── launcher.py          # Auto-installing launcher script
├── server.py           # Main MCP server implementation
├── install.py          # Manual installation helper
├── requirements.txt    # Python dependencies
├── pyproject.toml     # Package configuration
└── README.md          # This file
```

## 🐛 Troubleshooting

**Server won't start?**
- Ensure Python 3.9+ is installed
- Verify `pg` command is in PATH: `pg --version`
- Check Claude Desktop logs for error details

**Dependencies missing?**
- The launcher automatically installs MCP dependency
- For manual install: `pip install mcp>=1.0.0`

**Auto-detection fails?**
- Ensure files are in expected location: `claude-desktop-mcp-playground/mcp-servers/pg-cli-server/`
- Use manual installation with absolute paths