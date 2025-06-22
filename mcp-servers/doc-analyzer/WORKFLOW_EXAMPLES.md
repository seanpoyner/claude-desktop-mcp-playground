# Documentation Analyzer + Registry Manager Workflow

This document shows how to use the Documentation Analyzer MCP Server to examine MCP server documentation and automatically register servers using the Registry Manager.

## 🚀 Complete Workflow Example

### Step 1: Install Both Servers

```bash
# Search for servers
pg config search doc-analyzer
pg config search registry-manager

# Install them
pg config install doc-analyzer
pg config install registry-manager
```

### Step 2: Analyze an MCP Server Documentation

Let's analyze a real MCP server from GitHub:

**In Claude Desktop:**
```
Use the analyze_mcp_documentation tool with:
url: "https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search"
```

This will return:
- Extracted server name, description, installation method
- Package information and command details
- Environment variables needed
- Validation status

### Step 3: Extract Server Definition

```
Use the extract_server_definition tool with:
url: "https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search"
server_id: "brave-search-custom"
```

This generates a complete JSON definition ready for registration.

### Step 4: Register with Registry Manager

```
Use the add_custom_server tool (from registry-manager) with:
server_id: "brave-search-custom"
server_definition: {
  "name": "Brave Search Server",
  "description": "Web search capabilities using Brave Search API",
  "category": "community",
  "install_method": "npm",
  "command": "npx",
  "args_template": ["-y", "@modelcontextprotocol/server-brave-search"],
  "homepage": "https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search",
  "package": "@modelcontextprotocol/server-brave-search",
  "env_vars": {
    "BRAVE_API_KEY": "Your Brave Search API key"
  },
  "setup_help": "Get API key from https://brave.com/search/api/",
  "example_usage": "Search the web for current information"
}
```

### Step 5: Install Your Custom Server

```bash
# Now your custom server is discoverable!
pg config search brave-search-custom
pg config install brave-search-custom --env BRAVE_API_KEY=your_api_key
```

## 📋 Quick Examples

### Example 1: NPM Package Server

```
# Analyze
Use analyze_mcp_documentation with:
url: "https://www.npmjs.com/package/weather-mcp-server"

# Extract
Use extract_server_definition with:
url: "https://www.npmjs.com/package/weather-mcp-server"
server_id: "weather-server"

# Register (copy the definition from extract output)
Use add_custom_server with the extracted definition
```

### Example 2: GitHub Repository Server

```
# Analyze
Use analyze_mcp_documentation with:
url: "https://github.com/username/my-mcp-server"

# Preview what will be registered
Use preview_registration with:
url: "https://github.com/username/my-mcp-server"
server_id: "my-custom-server"

# Generate commands
Use generate_registry_commands with:
url: "https://github.com/username/my-mcp-server"
server_id: "my-custom-server"
```

### Example 3: Batch Analysis

```
# Analyze multiple servers at once
Use batch_analyze_urls with:
urls: [
  "https://github.com/user1/mcp-server1",
  "https://github.com/user2/mcp-server2",
  "https://npmjs.com/package/cool-mcp-server"
]
auto_generate_ids: true
```

## 🔧 Advanced Usage

### Override Extracted Information

If the analyzer doesn't extract everything correctly:

```
Use extract_server_definition with:
url: "https://github.com/example/server"
server_id: "example-server"
override_info: {
  "name": "Custom Name",
  "command": "node",
  "args_template": ["index.js"]
}
```

### Working with Private Registries

1. Export your custom registry:
```
Use export_custom_registry (from registry-manager) with:
format: "json"
```

2. Share the exported file with your team

3. Import on another system:
```
Use import_custom_servers (from registry-manager) with:
servers_data: <paste JSON here>
```

## 🎯 Best Practices

1. **Always Preview First**
   - Use `preview_registration` before registering
   - Check that all required fields are extracted

2. **Validate Environment Variables**
   - Ensure all API keys are documented
   - Add setup_help for complex configurations

3. **Use Meaningful Server IDs**
   - Choose descriptive IDs like "weather-api" not "server1"
   - Keep IDs consistent with the server's purpose

4. **Document Custom Servers**
   - Add comprehensive descriptions
   - Include example usage
   - Document all environment variables

## 🚨 Troubleshooting

### "Could not extract server name"
- Check if the documentation has a clear title
- Use manual override in extract_server_definition

### "HTTP error fetching documentation"
- Ensure the URL is publicly accessible
- Try using raw GitHub content URLs
- Check for authentication requirements

### "Installation method not detected"
- Look for clear installation instructions in docs
- Manually specify in override_info

## 💡 Pro Tips

1. **GitHub URLs**: Use the main branch URL or README directly
2. **NPM Packages**: The NPM page often has better structured data
3. **Complex Servers**: May need manual overrides for build steps
4. **Docker Servers**: Ensure Docker command patterns are detected

## 🔗 Integration Points

The Documentation Analyzer works seamlessly with:
- **Registry Manager**: For adding analyzed servers
- **PG CLI**: For installing registered servers
- **Claude Desktop**: For AI-assisted server discovery

## 📚 Example Server Definitions

### NPM Server
```json
{
  "name": "Example NPM Server",
  "description": "An example NPM-based MCP server",
  "install_method": "npm",
  "command": "npx",
  "args_template": ["-y", "example-mcp-server"],
  "package": "example-mcp-server"
}
```

### Git Server
```json
{
  "name": "Example Git Server",
  "description": "An example Git-based MCP server",
  "install_method": "git",
  "command": "node",
  "args_template": ["dist/index.js"],
  "repository": "https://github.com/user/example-server"
}
```

### Python Server
```json
{
  "name": "Example Python Server",
  "description": "An example Python MCP server",
  "install_method": "uvx",
  "command": "uvx",
  "args_template": ["example-mcp-server"],
  "package": "example-mcp-server"
}
```

## 🎉 Success!

You now have a powerful workflow for discovering and registering MCP servers automatically!
