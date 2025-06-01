# Basic Configuration Management

## Overview

The Claude Desktop MCP Playground provides a powerful CLI for managing your Claude Desktop MCP server configurations. This guide covers the essential configuration management commands and workflows.

## Configuration File Locations

The CLI automatically works with Claude Desktop's configuration files:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Simplified Configuration Format

The CLI also uses a simplified format (`claude_desktop_simplified.json`) that's easier to edit:

```json
{
  "server-name": {
    "command": "python",
    "args": ["-m", "my_module"],
    "env": {"KEY": "value"},
    "enabled": true
  }
}
```

## Essential CLI Commands

### 1. Import Current Configuration

```bash
# Import Claude Desktop config to simplified format
pg config import

# Import to custom file
pg config import --output my_config.json
```

### 2. View Current Configuration

```bash
# Show all configured servers
pg config show

# Show in JSON format
pg config show --format json
```

### 3. Add New MCP Servers

```bash
# Add a Python-based server
pg config add my-server "python" \
  --args "-m" --args "my_module" \
  --env "API_KEY=secret" --env "DEBUG=true"

# Add a Node.js server
pg config add node-server "node" \
  --args "server.js" --args "--port" --args "3000"

# Add a binary executable
pg config add binary-server "/path/to/executable"
```

### 4. Remove Servers

```bash
# Remove a server (with confirmation)
pg config remove my-server

# Remove without confirmation
pg config remove my-server --confirm
```

### 5. Validate Configuration

```bash
# Check configuration for errors
pg config validate
```

### 6. Apply Simplified Configuration

```bash
# Apply changes from simplified format back to Claude Desktop
pg config apply claude_desktop_simplified.json
```

## Working with Simplified Configuration

### Example Workflow

1. **Import your current config**:
   ```bash
   pg config import
   ```

2. **Edit the simplified file** (`claude_desktop_simplified.json`):
   ```json
   {
     "filesystem": {
       "command": "npx",
       "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"],
       "env": {},
       "enabled": true
     },
     "email-client": {
       "command": "python",
       "args": ["-m", "email_client.server"],
       "env": {
         "SMTP_SERVER": "smtp.gmail.com",
         "SMTP_PORT": "587"
       },
       "enabled": false
     }
   }
   ```

3. **Apply changes back to Claude Desktop**:
   ```bash
   pg config apply
   ```

4. **Restart Claude Desktop** for changes to take effect.

### Simplified Format Benefits

- **Easy editing**: Plain JSON with clear structure
- **Enable/disable**: Toggle servers without removing them
- **Version control**: Track configuration changes
- **Backup**: Keep multiple configuration versions

## Common Configuration Examples

### Adding Popular MCP Servers

```bash
# Filesystem server for file operations
pg config add filesystem "npx" \
  --args "-y" --args "@modelcontextprotocol/server-filesystem" \
  --args "/path/to/workspace"

# GitHub integration
pg config add github "npx" \
  --args "-y" --args "@modelcontextprotocol/server-github" \
  --env "GITHUB_TOKEN=your_token"

# SQLite database access
pg config add sqlite "npx" \
  --args "-y" --args "@modelcontextprotocol/server-sqlite" \
  --args "/path/to/database.db"

# Custom Python server
pg config add my-python-server "python" \
  --args "-m" --args "my_package.server" \
  --env "CONFIG_PATH=/etc/myserver.conf"
```

## Best Practices

### Security
- **Never commit API keys**: Use environment variables for sensitive data
- **Use the `env` section**: Store configuration in environment variables
- **Regular backups**: Export simplified configs regularly

### Organization  
- **Descriptive names**: Use clear server names like `email-client`, not `server1`
- **Enable/disable**: Use the `enabled` flag instead of deleting servers
- **Documentation**: Comment your simplified config files

### Workflow
- **Test changes**: Use `validate` before applying configurations
- **Incremental updates**: Make small changes and test frequently
- **Version control**: Track your simplified config files in git

## Troubleshooting

### Common Issues

1. **Server not appearing in Claude Desktop**:
   - Restart Claude Desktop after configuration changes
   - Check that `enabled: true` in simplified config
   - Verify command paths are correct

2. **Command not found errors**:
   - Check that executables are in your PATH
   - Use absolute paths for custom binaries
   - Verify npm packages are globally installed

3. **Permission denied**:
   - Check file permissions on executables
   - Ensure Claude Desktop has necessary access rights

4. **Configuration validation errors**:
   ```bash
   pg config validate
   ```
   - Fix any reported issues before applying

## Next Steps

- [Learn Advanced Server Setup](04-advanced-setup.md)
- [Explore Productivity Workflows](05-productivity-workflows.md)
- [Troubleshooting Guide](07-troubleshooting.md)
