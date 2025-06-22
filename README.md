# Claude Desktop MCP Playground

A comprehensive command-line tool and desktop GUI for managing Claude Desktop's Model Context Protocol (MCP) servers with easy installation, configuration, and a searchable registry of 44+ available servers.

## 🌟 Features

- **🖥️ Desktop GUI Application** - Modern Electron-based desktop interface with React frontend
- **🔍 Server Discovery** - Search through 44+ MCP servers from official and community sources
- **⚡ One-Click Installation** - Install MCP servers with automatic configuration
- **🛠️ Configuration Management** - CLI and GUI tools for managing Claude Desktop settings
- **📊 Visual Dashboard** - Real-time server status monitoring and management
- **🌍 Cross-Platform** - Works on macOS, Windows, and Linux
- **🚀 Quick Setup** - Automated dependency detection and installation
- **📦 Complete Registry** - Official and community servers with descriptions and setup help

## 🚀 Quick Start

### One-Line Installation

**Linux/macOS:**
```bash
curl -sSL https://raw.githubusercontent.com/seanpoyner/claude-desktop-mcp-playground/main/install-full.sh | bash
```

**Windows (PowerShell as Admin):**
```powershell
irm https://raw.githubusercontent.com/seanpoyner/claude-desktop-mcp-playground/main/install-full.ps1 | iex
```

The installer automatically:
- ✅ Installs dependencies (Python 3.9+, Node.js 16+, uv)
- ✅ Sets up the `pg` command globally
- ✅ Installs common MCP servers
- ✅ Configures Claude Desktop

### Manual Setup (if needed)

```bash
# Clone repository
git clone https://github.com/seanpoyner/claude-desktop-mcp-playground.git
cd claude-desktop-mcp-playground

# Install dependencies
pip install -e .

# Add pg command to PATH
./setup-pg-command.sh      # Linux/macOS
.\setup-pg-command.ps1     # Windows

# Run setup wizard
pg setup
```

## 💡 Usage

### Desktop GUI Application

**Launch the GUI:**
```bash
# After installation, start the desktop application
cd mcp-gui
npm run dev           # Development mode
npm run build && npm run electron    # Production mode
```

The GUI provides:
- **Visual Dashboard** - Server status overview and statistics
- **One-Click Installation** - Install servers with guided configuration forms
- **Real-Time Monitoring** - Live server status and error reporting
- **Configuration Editor** - Visual interface for server settings
- **Smart Search** - Find servers by name, description, or category

### CLI Interface

### Search and Install MCP Servers

```bash
# Search available servers
pg config search database
pg config search web
pg config search "file system"

# Get detailed server info
pg config info filesystem
pg config info postgres

# Install a server
pg config install filesystem --arg path=/workspace
pg config install sqlite --arg database_path=./app.db

# List all available servers
pg config search
```

### Manage Configuration

```bash
# Show current configuration
pg config show

# List installed servers
pg config list

# Interactive setup wizard
pg setup

# Quick setup with defaults
pg setup --quick
```

## 📦 Available Servers

The registry includes **44 servers** from official and community sources:

### Official Servers (15)
- **filesystem** - Secure file operations with access controls
- **memory** - Knowledge graph-based persistent memory
- **puppeteer** - Browser automation and web scraping
- **github/gitlab** - Git repository management
- **postgres/sqlite** - Database operations
- **slack** - Slack workspace interaction
- **google-drive/google-maps** - Google services integration

### Popular Community Servers (29)
- **Cloud Platforms**: aws, azure, cloudflare, heroku
- **Databases**: elasticsearch, clickhouse
- **Development Tools**: jetbrains, xcode, e2b
- **Web & Automation**: firecrawl, browserbase, screenshotone
- **Project Management**: linear, hubspot, grafana
- **Office & Productivity**: excel, office-word, office-powerpoint
- **Data Analysis**: jupyter-notebook, quickchart
- **AI & Search**: vectorize, kagi, exa

[View complete server list →](https://github.com/modelcontextprotocol/servers)

## 🔧 Configuration Locations

Claude Desktop configuration files:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

## 🛠️ Development

### CLI Development
```bash
# Setup development environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

pip install -e .

# Run tests
pytest tests/

# Code formatting
black .
isort .
```

### GUI Development
```bash
# Setup GUI development
cd mcp-gui
npm install

# Install Python backend dependencies
pip install flask flask-cors

# Development mode (3 terminals)
python backend/api.py      # Terminal 1: Backend API
npm run dev               # Terminal 2: React frontend  
npm run electron-dev      # Terminal 3: Electron app

# Build for distribution
npm run build             # Build React app
npm run dist             # Package for current platform
npm run dist:all         # Package for all platforms
```

## 📚 Examples

### Install Filesystem Server
```bash
pg config install filesystem --arg path=/home/user/projects
```

### Install Database Server
```bash
pg config install postgres
# Set environment variables:
# POSTGRES_URL=postgresql://user:pass@localhost:5432/db
```

### Search for Development Tools
```bash
pg config search ide
# Returns: jetbrains, xcode, grafana
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- [Official MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- All contributors to the MCP ecosystem

## 🔧 Recent Updates

### Obsidian MCP Server Support (Latest)
Now supports **both** Obsidian MCP server options:
- **`obsidian`** (`mcp-obsidian`): Direct file access - `pg config install obsidian --arg vault_path="/path/to/vault"`
- **`obsidian-mcp-server`**: Advanced REST API integration - `pg config install obsidian-mcp-server --env OBSIDIAN_API_KEY="your-key"`

**Key fixes:**
- ✅ Fixed command line argument configuration for `mcp-obsidian`
- ✅ Added advanced `obsidian-mcp-server` with atomic operations and caching
- ✅ Support for both servers simultaneously
- ✅ Comprehensive setup instructions for Local REST API plugin

See [docs/obsidian-server-update.md](docs/obsidian-server-update.md) for detailed comparison and setup guide.

## 🆘 Support

- [Documentation](docs/)
- [Issues](https://github.com/seanpoyner/claude-desktop-mcp-playground/issues)
- [Contributing Guide](CONTRIBUTING.md)

---

**Made with ❤️ for the Claude Desktop community**