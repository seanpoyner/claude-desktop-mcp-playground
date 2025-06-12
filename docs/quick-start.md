# Quick Start Guide

Get up and running with Claude Desktop MCP Playground in minutes!

## 🎯 Goal

By the end of this guide, you'll have:
- ✅ Installed the `pg` command-line tool and GUI application
- ✅ Discovered and installed your first MCP server
- ✅ Configured Claude Desktop to use the server

## 📦 Step 1: Install

Choose your preferred installation method:

### Option A: One-Line Install (Recommended)
```bash
# Linux/macOS
curl -sSL https://raw.githubusercontent.com/seanpoyner/claude-desktop-mcp-playground/main/install-full.sh | bash

# Windows (PowerShell as Admin)
irm https://raw.githubusercontent.com/seanpoyner/claude-desktop-mcp-playground/main/install-full.ps1 | iex
```

### Option B: Manual Install
```bash
git clone https://github.com/seanpoyner/claude-desktop-mcp-playground.git
cd claude-desktop-mcp-playground
pip install -e .
./setup-pg-command.sh  # or .ps1 on Windows
```

## 🔍 Step 2: Discover Servers

Search the registry of 44+ available MCP servers:

```bash
# Search for file-related servers
pg config search file

# Search for database servers
pg config search database

# Search for web automation
pg config search web

# List all available servers
pg config search
```

**Example output:**
```
🔍 Found 2 MCP server(s):
==================================================

🏛️ filesystem - Filesystem Server
   Secure file operations with configurable access controls.
   📦 Package: @modelcontextprotocol/server-filesystem

🌟 google-drive - Google Drive Server
   Access Google Drive files and folders.
   📦 Package: @modelcontextprotocol/server-gdrive
```

## 📋 Step 3: Get Server Details

Learn more about a specific server:

```bash
pg config info filesystem
```

**Example output:**
```
🏛️ Filesystem Server
==================================================
ID: filesystem
Category: official
Description: Secure file operations with configurable access controls.
Package: @modelcontextprotocol/server-filesystem

Installation:
  Method: npm
  Command: npx

Required Arguments:
  • path

Setup Help:
  Provide a path to the directory you want Claude to access

Example Usage:
  Access files in your workspace directory

💡 Install with: pg config install filesystem
```

## ⚡ Step 4: Install Your First Server

Install the filesystem server to let Claude access your files:

```bash
# Install with required arguments
pg config install filesystem --arg path=/home/user/projects

# Or use dry-run to see what would happen
pg config install filesystem --dry-run --arg path=/home/user/projects
```

**Example output:**
```
📦 Installing: Filesystem Server
✅ Server installed successfully!
✅ Configuration updated
✅ Claude Desktop config saved

Next steps:
1. Restart Claude Desktop
2. The filesystem server is now available in Claude
```

## 🖥️ Step 5: Configure Claude Desktop

The installation automatically updates your Claude Desktop configuration, but you may need to restart Claude Desktop for changes to take effect.

### Verify Configuration
```bash
# Check current configuration
pg config show

# List installed servers
pg config list
```

## 🎉 Step 6: Test in Claude Desktop

1. **Restart Claude Desktop** to load the new configuration
2. **Open a new conversation** in Claude
3. **Test the server** by asking Claude to access files:
   
   *"Can you list the files in my projects directory?"*
   
   *"Please read the contents of my README.md file"*

## 🚀 Next Steps

### Install More Servers

```bash
# Install a database server
pg config install sqlite --arg database_path=./app.db

# Install a web search server  
pg config install brave-search
# (Set BRAVE_API_KEY environment variable)

# Install browser automation
pg config install puppeteer
```

### Manage Your Configuration

```bash
# Show current setup
pg config show

# List all installed servers
pg config list

# Remove a server
pg config remove server-name

# Validate configuration
pg config validate
```

### Use the Setup Wizard

For guided configuration:

```bash
# Interactive setup wizard
pg setup

# Quick setup with defaults
pg setup --quick

# Check dependencies only
pg setup --deps-only
```

## 💡 Common Workflows

### For Developers
```bash
# Install development tools
pg config install filesystem --arg path=/home/user/code
pg config install github  # Set GITHUB_TOKEN env var
pg config install jetbrains
```

### For Data Analysis
```bash
# Install data tools
pg config install postgres  # Set POSTGRES_URL env var
pg config install sqlite --arg database_path=./data.db
pg config install fetch  # For web data
```

### For Content Creation
```bash
# Install content tools
pg config install memory  # For persistent memory
pg config install brave-search  # Set BRAVE_API_KEY
pg config install google-drive  # Set credentials
```

## 🔧 Configuration Tips

### Environment Variables
Some servers require environment variables. Set them in your shell profile:

```bash
# ~/.bashrc or ~/.zshrc
export GITHUB_TOKEN="your_token_here"
export BRAVE_API_KEY="your_api_key_here"
export POSTGRES_URL="postgresql://user:pass@host:port/db"
```

### Directory Paths
Use absolute paths for consistency:
```bash
# Good
pg config install filesystem --arg path=/home/user/projects

# Avoid relative paths
pg config install filesystem --arg path=./projects
```

### Multiple Servers
You can install multiple servers of the same type with different configurations:
```bash
pg config install filesystem --name work-files --arg path=/work
pg config install filesystem --name personal-files --arg path=/home
```

## 🆘 Troubleshooting

### Server Not Working
1. **Restart Claude Desktop** after installation
2. **Check configuration**: `pg config show`
3. **Validate setup**: `pg config validate`
4. **Check environment variables** if required

### Command Not Found
```bash
# Reload shell configuration
source ~/.bashrc  # or ~/.zshrc

# Or restart your terminal
```

### Installation Fails
```bash
# Check dependencies
pg setup --deps-only

# Try manual installation
pip install -e .
./setup-pg-command.sh
```

## 📚 Learn More

- **[CLI Reference](cli-reference.md)** - Complete command documentation
- **[Server Management](server-management.md)** - Detailed server management guide
- **[Examples](examples.md)** - Real-world usage examples
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

---

**Ready to explore?** Check out the [Server Management Guide](server-management.md) for advanced usage!