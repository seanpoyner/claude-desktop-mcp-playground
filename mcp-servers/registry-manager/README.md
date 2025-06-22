# Registry Manager MCP Server

The Registry Manager MCP Server allows you to dynamically add, manage, and organize custom MCP servers in your Claude Desktop MCP Playground registry. Custom servers added through this manager become discoverable and installable via the `pg` command.

## Features

- ✅ **Add Custom Servers** - Register new MCP servers with complete metadata
- 📋 **List Management** - View, update, and remove custom servers
- 🔍 **Validation** - Automatic validation of server definitions
- 📤 **Import/Export** - Share custom registries as JSON or Markdown
- 📝 **Templates** - Generate templates for different server types
- 🔄 **Live Updates** - Automatically updates the main registry for `pg` command integration

## Installation

### Option 1: Direct Installation via PG Command

If you have the `pg` command available:

```bash
# Search for the registry manager
pg config search registry-manager

# Install it
pg config install registry-manager
```

### Option 2: Manual Setup

1. **Ensure the server files are in place** (already done in your playground):
   ```
   claude-desktop-mcp-playground/
   └── mcp-servers/
       └── registry-manager/
           ├── server.py
           ├── launcher.py
           ├── requirements.txt
           └── README.md
   ```

2. **Install dependencies**:
   ```bash
   cd mcp-servers/registry-manager
   pip install -r requirements.txt
   ```

3. **Add to Claude Desktop configuration**:
   
   **Windows:** Edit `%APPDATA%\Claude\claude_desktop_config.json`
   **macOS:** Edit `~/Library/Application Support/Claude/claude_desktop_config.json`
   **Linux:** Edit `~/.config/Claude/claude_desktop_config.json`

   ```json
   {
     "mcpServers": {
       "registry-manager": {
         "command": "python",
         "args": ["C:/Users/seanp/claude-desktop-mcp-playground/mcp-servers/registry-manager/launcher.py"]
       }
     }
   }
   ```

4. **Restart Claude Desktop**

## Usage

Once installed, you can use these tools directly in Claude Desktop:

### Add a Custom Server

```
Use the add_custom_server tool with:

server_id: "my-awesome-server"
server_definition: {
  "name": "My Awesome Server",
  "description": "Does awesome things with my data",
  "install_method": "npm",
  "command": "npx",
  "args_template": ["-y", "my-awesome-server"],
  "package": "my-awesome-server",
  "env_vars": {
    "API_KEY": "Your API key"
  },
  "setup_help": "Get API key from awesome-service.com",
  "example_usage": "Process data and generate insights",
  "homepage": "https://github.com/user/my-awesome-server"
}
```

### List Custom Servers

```
Use the list_custom_servers tool to see all your registered custom servers.
```

### Generate Templates

```
Use the create_server_template tool with:
install_method: "npm" (or "git", "uvx", "docker", "script", "manual")
server_type: "api" (or "tool", "data", "automation", "integration")
```

### Import/Export

```
# Export your registry
Use export_custom_registry tool with format: "json" or "markdown"

# Import servers from another registry
Use import_custom_servers tool with a servers object
```

## Server Definition Schema

A complete server definition includes:

### Required Fields

- **name** (string): Display name for the server
- **description** (string): What the server does
- **command** (string): Command to run the server
- **install_method** (string): One of `npm`, `git`, `uvx`, `docker`, `script`, `manual`

### Optional Fields

- **category** (string): Defaults to "custom"
- **package** (string): Package name for npm/uvx installs
- **repository** (string): Git repository URL
- **args_template** (array): Command arguments template
- **required_args** (array): List of required user arguments
- **env_vars** (object): Environment variables with descriptions
- **setup_help** (string): Setup instructions
- **example_usage** (string): Usage example
- **homepage** (string): Documentation URL
- **platform** (string): Platform requirement (windows, macos, linux)

## Server Types and Install Methods

### NPM Servers
```json
{
  "install_method": "npm",
  "package": "my-server-package",
  "command": "npx",
  "args_template": ["-y", "my-server-package"]
}
```

### Git-based Servers
```json
{
  "install_method": "git",
  "repository": "https://github.com/user/my-server",
  "command": "node",
  "args_template": ["<repo_path>/dist/index.js"]
}
```

### Python Servers (uvx)
```json
{
  "install_method": "uvx",
  "package": "my-python-server",
  "command": "uvx",
  "args_template": ["my-python-server"]
}
```

### Docker Servers
```json
{
  "install_method": "docker",
  "package": "my-docker-image",
  "command": "docker",
  "args_template": ["run", "-i", "--rm", "my-docker-image"]
}
```

### Script-based Servers
```json
{
  "install_method": "script",
  "command": "auto_detect",
  "platform_config": {
    "windows": {
      "command": "cmd",
      "args_template": ["/c", "{installation_path}\\server.exe"]
    }
  }
}
```

## Integration with PG Command

Once you add a custom server through this manager:

1. **Search for it**: `pg config search my-server`
2. **Get info**: `pg config info my-server`
3. **Install it**: `pg config install my-server`
4. **List installed**: `pg config show`

The registry manager automatically updates the main registry so your custom servers appear alongside official ones.

## File Storage

- **Custom Registry**: `claude-desktop-mcp-playground/custom_registry.json`
- **Main Registry Integration**: Updates `claude_desktop_mcp/server_registry.py`

## Examples

### Adding an API Integration Server

```json
{
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
```

### Adding a Local Tool Server

```json
{
  "name": "File Organizer",
  "description": "Organizes files in directories based on rules",
  "category": "custom",
  "install_method": "git",
  "repository": "https://github.com/user/file-organizer-mcp",
  "command": "node",
  "args_template": ["<repo_path>/dist/server.js", "--config", "<config_file>"],
  "required_args": ["config_file"],
  "setup_help": "Create a config file with organization rules",
  "example_usage": "Automatically organize downloads, photos, or documents"
}
```

## Troubleshooting

### Server Not Appearing in PG Search

1. Check that the server was added successfully with `list_custom_servers`
2. Verify the main registry was updated (restart Claude Desktop)
3. Try searching with partial names: `pg config search partial-name`

### Installation Failures

1. Validate your server definition with `validate_server_definition`
2. Check that required fields are present and correctly formatted
3. Test the command manually before adding to registry

### Registry File Issues

- **Location**: Custom servers are stored in `custom_registry.json`
- **Backup**: Use `export_custom_registry` to backup your servers
- **Recovery**: Use `import_custom_servers` to restore from backup

## Contributing

To contribute to the Registry Manager:

1. Test new server definitions thoroughly
2. Use descriptive names and clear documentation
3. Include proper error handling for edge cases
4. Follow the existing code style and patterns

## License

Part of the Claude Desktop MCP Playground project - MIT License
