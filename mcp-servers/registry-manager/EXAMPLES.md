# Registry Manager Usage Examples

This document provides practical examples of how to use the Registry Manager MCP Server to add and manage custom MCP servers.

## Example 1: Adding a Simple NPM-based Server

```json
{
  "tool": "add_custom_server",
  "arguments": {
    "server_id": "weather-api",
    "server_definition": {
      "name": "Weather API Server",
      "description": "Provides weather data through OpenWeatherMap API",
      "category": "custom",
      "install_method": "npm",
      "package": "weather-mcp-server",
      "command": "npx",
      "args_template": ["-y", "weather-mcp-server"],
      "env_vars": {
        "OPENWEATHER_API_KEY": "Your OpenWeatherMap API key"
      },
      "setup_help": "Get API key from https://openweathermap.org/api",
      "example_usage": "Get current weather and forecasts for any location",
      "homepage": "https://github.com/user/weather-mcp-server"
    }
  }
}
```

After adding this server, you can:
- Search for it: `pg config search weather`
- Install it: `pg config install weather-api`
- View details: `pg config info weather-api`

## Example 2: Adding a Git-based Development Tool

```json
{
  "tool": "add_custom_server",
  "arguments": {
    "server_id": "code-formatter",
    "server_definition": {
      "name": "Code Formatter",
      "description": "Formats code in multiple languages using prettier and black",
      "category": "custom",
      "install_method": "git",
      "repository": "https://github.com/user/code-formatter-mcp",
      "command": "node",
      "args_template": ["<repo_path>/dist/server.js", "--config", "<config_file>"],
      "required_args": ["config_file"],
      "setup_help": "Create a config file with formatting rules for different languages",
      "example_usage": "Format JavaScript, Python, JSON, and other code files",
      "homepage": "https://github.com/user/code-formatter-mcp"
    }
  }
}
```

## Example 3: Adding a Python-based Data Analysis Server

```json
{
  "tool": "add_custom_server",
  "arguments": {
    "server_id": "data-analyzer",
    "server_definition": {
      "name": "Data Analyzer",
      "description": "Analyzes CSV and Excel files with statistical insights",
      "category": "custom",
      "install_method": "uvx",
      "package": "data-analyzer-mcp",
      "command": "uvx",
      "args_template": ["data-analyzer-mcp", "--data-dir", "<data_directory>"],
      "required_args": ["data_directory"],
      "setup_help": "Provide the directory containing your data files",
      "example_usage": "Generate statistical summaries, create visualizations, detect patterns",
      "homepage": "https://pypi.org/project/data-analyzer-mcp/"
    }
  }
}
```

## Example 4: Adding a Docker-based Service

```json
{
  "tool": "add_custom_server",
  "arguments": {
    "server_id": "pdf-processor",
    "server_definition": {
      "name": "PDF Processor",
      "description": "Extracts text, merges, splits, and manipulates PDF files",
      "category": "custom",
      "install_method": "docker",
      "package": "pdf-processor-mcp",
      "command": "docker",
      "args_template": [
        "run", "-i", "--rm", 
        "-v", "<pdf_directory>:/data",
        "pdf-processor-mcp"
      ],
      "required_args": ["pdf_directory"],
      "setup_help": "Requires Docker installed. Provide directory containing PDF files",
      "example_usage": "Extract text from PDFs, combine multiple PDFs, split large PDFs",
      "homepage": "https://hub.docker.com/r/user/pdf-processor-mcp"
    }
  }
}
```

## Example 5: Creating a Server Template First

```json
{
  "tool": "create_server_template",
  "arguments": {
    "install_method": "npm",
    "server_type": "api"
  }
}
```

This will generate a template that you can customize and then add using `add_custom_server`.

## Example 6: Managing Your Custom Registry

### List all custom servers
```json
{
  "tool": "list_custom_servers",
  "arguments": {}
}
```

### Export your registry for backup
```json
{
  "tool": "export_custom_registry",
  "arguments": {
    "format": "json"
  }
}
```

### Import servers from another registry
```json
{
  "tool": "import_custom_servers",
  "arguments": {
    "servers": {
      "backup-server": {
        "name": "Backup Server",
        "description": "Automated backup solution",
        "install_method": "npm",
        "command": "npx",
        "args_template": ["-y", "backup-mcp-server"]
      }
    },
    "overwrite": false
  }
}
```

### Update an existing server
```json
{
  "tool": "update_custom_server",
  "arguments": {
    "server_id": "weather-api",
    "server_definition": {
      "description": "Enhanced weather data with forecasts and historical data",
      "homepage": "https://github.com/user/weather-mcp-server-v2"
    }
  }
}
```

### Remove a server
```json
{
  "tool": "remove_custom_server",
  "arguments": {
    "server_id": "old-server"
  }
}
```

## Installation Methods Explained

### NPM (`install_method: "npm"`)
- Uses `npx` to run npm packages
- Good for Node.js-based servers
- Packages published to npmjs.com

### Git (`install_method: "git"`)
- Clones repository and builds if needed
- Good for development versions or custom servers
- Requires Git installed

### UVX (`install_method: "uvx"`)
- Uses `uvx` to run Python packages
- Good for Python-based servers
- Packages published to PyPI

### Docker (`install_method: "docker"`)
- Uses Docker containers
- Good for complex dependencies or isolation
- Requires Docker installed

### Script (`install_method: "script"`)
- Custom installation scripts
- Good for platform-specific installers
- Can auto-detect installed locations

## Best Practices

1. **Use descriptive server IDs**: Choose IDs that clearly identify the server's purpose
2. **Provide clear descriptions**: Help users understand what the server does
3. **Include setup help**: Explain any required configuration or credentials
4. **Test before sharing**: Validate your server definitions work correctly
5. **Document environment variables**: Clearly explain what each env var does
6. **Include examples**: Show typical usage scenarios
7. **Keep categories consistent**: Use "custom" for your own servers

## Integration with PG Commands

Once you add a custom server through Registry Manager:

1. **Search**: `pg config search myserver` - finds your server
2. **Info**: `pg config info myserver` - shows detailed information  
3. **Install**: `pg config install myserver` - installs and configures
4. **List**: `pg config show` - shows installed servers including yours
5. **Remove**: `pg config remove myserver` - uninstalls the server

Your custom servers appear alongside official ones in all `pg` command operations!
