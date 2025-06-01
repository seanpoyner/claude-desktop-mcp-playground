# CLI Reference

Complete command reference for the `pg` (playground) command-line tool.

## 📋 Global Commands

### pg --help
Show global help information.

```bash
pg --help
```

### pg --version
Display the current version.

```bash
pg --version
```

## 🔧 Configuration Commands

All configuration commands are under the `pg config` namespace.

### pg config search [query]

Search for available MCP servers in the registry.

```bash
# Search for specific functionality
pg config search database
pg config search "file system"
pg config search web

# List all available servers
pg config search

# Filter by category
pg config search --category official
pg config search --category community

# Different output formats
pg config search database --format table    # Default
pg config search database --format json     # JSON output
pg config search database --format simple   # Server names only
```

**Options:**
- `--category TEXT`: Filter by category (official, community)
- `--format [table|json|simple]`: Output format (default: table)

**Examples:**
```bash
pg config search database
pg config search --category official
pg config search web --format json
```

### pg config info <server_id>

Show detailed information about a specific server.

```bash
pg config info filesystem
pg config info postgres
pg config info github
```

**Output includes:**
- Server name and description
- Installation method and package
- Required and optional arguments
- Environment variables needed
- Setup instructions and examples

**Example:**
```bash
pg config info filesystem
```

### pg config install <server_id>

Install and configure an MCP server.

```bash
# Install with required arguments
pg config install filesystem --arg path=/workspace

# Install with multiple arguments
pg config install postgres --arg host=localhost --arg port=5432

# Install with environment variables
pg config install github --env GITHUB_TOKEN=your_token

# Install with custom name
pg config install filesystem --name project-files --arg path=/projects

# Dry run (show what would be installed)
pg config install filesystem --dry-run --arg path=/test

# Auto-install npm packages
pg config install filesystem --auto-install --arg path=/workspace
```

**Options:**
- `--name TEXT`: Custom name for the server instance
- `--arg KEY=VALUE`: Required arguments (can be used multiple times)
- `--env KEY=VALUE`: Environment variables (can be used multiple times)
- `--dry-run`: Show what would be installed without actually installing
- `--auto-install`: Automatically install npm packages if needed

**Examples:**
```bash
pg config install filesystem --arg path=/home/user/code
pg config install sqlite --arg database_path=./app.db
pg config install github --env GITHUB_TOKEN=ghp_xxx
pg config install postgres --dry-run
```

### pg config list

List all currently installed MCP servers.

```bash
# List installed servers
pg config list

# List with detailed status
pg config list --status

# Include npm global packages
pg config list --npm-global

# Different output formats
pg config list --format table    # Default
pg config list --format json     # JSON output
pg config list --format simple   # Names only
```

**Options:**
- `--status`: Show server status (running, stopped, error)
- `--npm-global`: Include npm global packages in the list
- `--format [table|json|simple]`: Output format

**Example output:**
```
📦 Installed MCP Servers:
==================================================

🏛️ filesystem (/workspace)
   Status: ✅ Configured
   Package: @modelcontextprotocol/server-filesystem

🌟 sqlite (./app.db)
   Status: ✅ Configured  
   Package: @modelcontextprotocol/server-sqlite
```

### pg config show

Display the current Claude Desktop configuration.

```bash
# Show current configuration
pg config show

# Show raw JSON format
pg config show --raw

# Show only MCP servers section
pg config show --servers-only
```

**Options:**
- `--raw`: Display raw JSON configuration
- `--servers-only`: Show only the MCP servers section

### pg config validate

Validate the current configuration for errors.

```bash
pg config validate
```

**Checks:**
- Configuration file syntax (valid JSON)
- Required fields presence
- Server command validity
- Environment variable references
- File path existence (for filesystem servers)

### pg config remove <server_name>

Remove an installed MCP server.

```bash
# Remove a server (with confirmation)
pg config remove filesystem

# Remove without confirmation prompt  
pg config remove filesystem --confirm

# Dry run (show what would be removed)
pg config remove filesystem --dry-run
```

**Options:**
- `--confirm`: Skip confirmation prompt
- `--dry-run`: Show what would be removed without actually removing

### pg config add <name> <command>

Manually add a custom MCP server configuration.

```bash
# Add a custom server
pg config add my-server "python3 my_server.py"

# Add with arguments
pg config add my-server "npx my-mcp-server" --args "--port=3000"

# Add with environment variables
pg config add my-server "node server.js" --env API_KEY=abc123
```

**Options:**
- `--args TEXT`: Command line arguments
- `--env KEY=VALUE`: Environment variables (can be used multiple times)

### pg config import

Import existing Claude Desktop configuration.

```bash
# Import current Claude Desktop config
pg config import

# Import from specific file
pg config import --file /path/to/config.json

# Import and create backup
pg config import --backup
```

**Options:**
- `--file PATH`: Import from specific configuration file
- `--backup`: Create backup of current configuration before importing

### pg config export

Export configuration to different formats.

```bash
# Export to simplified format
pg config export

# Export to specific file
pg config export --file my-config.json

# Export in different formats
pg config export --format simplified  # Default
pg config export --format claude      # Claude Desktop format
pg config export --format env         # Environment variables
```

**Options:**
- `--file PATH`: Export to specific file
- `--format [simplified|claude|env]`: Export format

## 🚀 Setup Commands

### pg setup

Run the interactive setup wizard.

```bash
# Full interactive setup
pg setup

# Quick setup with defaults
pg setup --quick

# Check dependencies only
pg setup --deps-only

# Skip dependency installation
pg setup --skip-deps

# Use specific configuration file
pg setup --config-file ./my-config.json
```

**Options:**
- `--quick`: Use default settings with minimal prompts
- `--deps-only`: Only check and install dependencies
- `--skip-deps`: Skip dependency checking and installation
- `--config-file PATH`: Use specific configuration file

**What the setup wizard does:**
1. Checks system dependencies (Python, Node.js, uv, git)
2. Offers to install missing dependencies
3. Imports existing Claude Desktop configuration
4. Suggests popular MCP servers to install
5. Guides through server configuration
6. Applies settings to Claude Desktop

## 📝 Output Formats

### Table Format (Default)
Human-readable table with colors and formatting.

### JSON Format
Machine-readable JSON output for scripting.

```bash
pg config search database --format json | jq '.[] | .name'
```

### Simple Format
Plain text output with server names only.

```bash
pg config list --format simple
```

## 🔧 Advanced Usage

### Scripting and Automation

```bash
#!/bin/bash
# Install multiple servers
servers=("filesystem" "sqlite" "github")
for server in "${servers[@]}"; do
    pg config install "$server" --auto-install
done
```

### Environment Variable Integration

```bash
# Set environment variables
export GITHUB_TOKEN="your_token"
export POSTGRES_URL="postgresql://user:pass@host/db"

# Install servers (will use environment variables)
pg config install github
pg config install postgres
```

### Configuration Management

```bash
# Backup current configuration
pg config export --file backup.json

# Make changes
pg config install new-server --arg path=/test

# Restore if needed
pg config import --file backup.json
```

## 🐛 Error Handling

### Common Exit Codes
- `0`: Success
- `1`: General error
- `2`: Command line argument error
- `3`: Configuration error
- `4`: Installation error

### Verbose Output
Add `-v` or `--verbose` to most commands for detailed output:

```bash
pg config install filesystem --arg path=/test --verbose
```

### Debug Mode
Use `--debug` for maximum verbosity:

```bash
pg setup --debug
```

## 🔗 Environment Variables

### Configuration
- `CLAUDE_CONFIG_PATH`: Override Claude Desktop config file location
- `PG_REGISTRY_URL`: Use custom server registry URL

### Logging
- `PG_LOG_LEVEL`: Set log level (DEBUG, INFO, WARNING, ERROR)
- `PG_LOG_FILE`: Write logs to specific file

### Examples
```bash
export CLAUDE_CONFIG_PATH="/custom/path/claude_desktop_config.json"
export PG_LOG_LEVEL="DEBUG"
pg config show
```

---

**Need help?** Use `pg --help` or `pg <command> --help` for command-specific information.