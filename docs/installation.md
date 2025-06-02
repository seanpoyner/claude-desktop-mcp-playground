# Installation Guide

Complete installation instructions for Claude Desktop MCP Playground.

## 🚀 One-Line Installation (Recommended)

### Linux and macOS
```bash
curl -sSL https://raw.githubusercontent.com/seanpoyner/claude-desktop-mcp-playground/main/install-full.sh | bash
```

### Windows
```powershell
irm https://raw.githubusercontent.com/seanpoyner/claude-desktop-mcp-playground/main/install-full.ps1 | iex
```

**Note**: Run PowerShell as Administrator for automatic dependency installation.

## What the Installer Does

✅ **Dependency Check**: Verifies Python 3.9+, Node.js 16+, uv, git  
✅ **Auto-Install**: Installs missing dependencies using system package managers  
✅ **PATH Setup**: Adds `pg` command to your system PATH  
✅ **MCP Servers**: Installs common MCP servers (filesystem, sqlite, etc.)  
✅ **Configuration**: Sets up Claude Desktop configuration  

## 📋 Manual Installation

If you prefer manual installation or the one-line installer doesn't work:

### Prerequisites
- **Python 3.9+** (3.10+ recommended)
- **Node.js 16+** (for MCP servers)
- **Git** (for version control)

### Step 1: Clone Repository
```bash
git clone https://github.com/seanpoyner/claude-desktop-mcp-playground.git
cd claude-desktop-mcp-playground
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### Step 3: Install Package
```bash
# Install in development mode
pip install -e .
```

### Step 4: Setup PATH
```bash
# Linux/macOS
./setup-pg-command.sh

# Windows
.\setup-pg-command.ps1
```

### Step 5: Verify Installation
```bash
# Check if pg command works
pg --version
pg --help

# Run setup wizard
pg setup
```

## 🔧 Platform-Specific Notes

### Linux

**Ubuntu/Debian:**
```bash
# Install prerequisites if needed
sudo apt update
sudo apt install python3 python3-pip nodejs npm git curl
```

**CentOS/RHEL:**
```bash
# Install prerequisites if needed
sudo dnf install python3 python3-pip nodejs npm git curl
```

**Arch Linux:**
```bash
# Install prerequisites if needed
sudo pacman -S python python-pip nodejs npm git curl
```

### macOS

**With Homebrew:**
```bash
# Install prerequisites if needed
brew install python node git
```

**Without Homebrew:**
- Download Python from [python.org](https://python.org)
- Download Node.js from [nodejs.org](https://nodejs.org)
- Install Xcode Command Line Tools: `xcode-select --install`

### Windows

**With winget (Windows 10+):**
```powershell
# Install prerequisites if needed
winget install Python.Python.3.11
winget install OpenJS.NodeJS
winget install Git.Git
```

**Manual Installation:**
- Download Python from [python.org](https://python.org) (check "Add Python to PATH")
- Download Node.js from [nodejs.org](https://nodejs.org)
- Download Git from [git-scm.com](https://git-scm.com)

## 🧪 Verify Installation

After installation, test the setup:

```bash
# Check core functionality
pg config search database
pg config info filesystem
pg config list

# Test installation (dry-run)
pg config install filesystem --dry-run --arg path=/test

# Run setup wizard
pg setup --quick
```

## 🔧 Configuration Locations

After installation, Claude Desktop configuration files are located at:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

## 🚨 Troubleshooting

### Common Issues

**Command not found: pg**
```bash
# Reload shell configuration
source ~/.bashrc  # or ~/.zshrc

# Or restart your terminal
```

**Permission denied during installation**
```bash
# Linux/macOS: Run with appropriate permissions
sudo chmod +x install-full.sh
./install-full.sh

# Windows: Run PowerShell as Administrator
```

**Python version too old**
```bash
# Check Python version
python --version

# Install newer Python version using system package manager
# or download from python.org
```

**Node.js not found**
```bash
# Check Node.js version
node --version

# Install Node.js using system package manager
# or download from nodejs.org
```

### Clean Installation
If you need to start over:

```bash
# Remove installation
rm -rf ~/.local/bin/pg  # Linux/macOS
rm -rf $env:USERPROFILE\Scripts\pg.cmd  # Windows

# Remove virtual environment
rm -rf .venv

# Start fresh
git clean -fdx
```

## 🆘 Getting Help

If installation fails:

1. **Check prerequisites**: Ensure Python 3.9+, Node.js 16+ are installed
2. **Run diagnostics**: `pg setup --deps-only`
3. **Check logs**: Look for error messages during installation
4. **Report issues**: [Create an issue](https://github.com/seanpoyner/claude-desktop-mcp-playground/issues) with:
   - Operating system and version
   - Python and Node.js versions
   - Complete error message
   - Installation method used

## ⬆️ Updating

To update to the latest version:

```bash
# If installed via git clone
cd claude-desktop-mcp-playground
git pull origin main
pip install -e .

# If using one-line installer, re-run it
curl -sSL https://raw.githubusercontent.com/seanpoyner/claude-desktop-mcp-playground/main/install-full.sh | bash
```

---

**Next**: [Quick Start Guide](quick-start.md)