# Documentation Analyzer MCP Server

An intelligent MCP server that analyzes documentation from HTTP URLs to automatically extract the information needed to register MCP servers in your registry. This server automates the discovery and registration of new MCP servers by parsing their documentation!

## 🌟 Features

### Core Capabilities
- **Smart Documentation Analysis** - Extracts server information from Markdown, HTML, and GitHub repositories
- **Multi-Format Support** - Handles README files, GitHub repos, documentation sites, and more
- **Automatic Field Detection** - Identifies installation methods, packages, commands, and environment variables
- **Validation Engine** - Checks extracted information for completeness and correctness
- **Batch Processing** - Analyze multiple server documentations at once
- **Registry Integration** - Generates ready-to-use commands for the registry manager

### Available Tools

1. **analyze_mcp_documentation**
   - Analyzes MCP server documentation from a URL
   - Extracts registration information automatically
   - Validates the extracted data

2. **extract_server_definition**
   - Extracts a complete server definition ready for registry manager
   - Allows manual overrides for extracted information
   - Generates JSON definition for easy copy-paste

3. **preview_registration**
   - Shows what would be registered without actually registering
   - Helps verify information before committing to registry
   - Shows post-registration commands

4. **batch_analyze_urls**
   - Analyze multiple documentation URLs at once
   - Auto-generates server IDs
   - Provides summary of analysis results

5. **generate_registry_commands**
   - Creates ready-to-use commands for registry manager
   - Provides both tool arguments and CLI commands
   - Includes validation checklist

## 📦 Installation

### Option 1: Via PG CLI (Recommended)
```bash
# Search for the doc analyzer
pg config search doc-analyzer

# Install it
pg config install doc-analyzer
```

### Option 2: Manual Installation
Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "doc-analyzer": {
      "command": "python",
      "args": ["<path_to_repo>/mcp-servers/doc-analyzer/launcher.py"],
      "env": {}
    }
  }
}
```

## 🚀 Usage Examples

### Basic Documentation Analysis
```
Use the analyze_mcp_documentation tool with:
url: "https://github.com/username/mcp-weather-server"
```

### Extract Server Definition
```
Use the extract_server_definition tool with:
url: "https://github.com/username/mcp-weather-server"
server_id: "weather-server"
```

### Batch Analysis
```
Use the batch_analyze_urls tool with:
urls: [
  "https://github.com/user1/mcp-server1",
  "https://github.com/user2/mcp-server2",
  "https://example.com/mcp-docs"
]
```

## 🔍 What It Extracts

The analyzer looks for and extracts:

- **Server Name** - From title, package.json, or first heading
- **Description** - From README introduction or description sections
- **Installation Method** - NPM, Git, Python/uvx, Docker, or manual
- **Package Name** - For NPM or Python packages
- **Repository URL** - For Git-based installations
- **Command** - The executable command to run the server
- **Arguments Template** - Command-line arguments needed
- **Environment Variables** - Required API keys or configuration
- **Setup Instructions** - Additional setup requirements
- **Usage Examples** - How to use the server

## 🎯 Supported Documentation Formats

### Markdown Files
- README.md files
- Documentation in Markdown format
- GitHub repository main pages

### HTML Pages
- Documentation websites
- Project homepages
- API documentation sites

### GitHub Repositories
- Automatic detection of GitHub URLs
- Extracts repository information
- Infers common patterns

## 🔧 How It Works

1. **Fetches Documentation** - Downloads content from the provided URL
2. **Detects Format** - Identifies if content is Markdown, HTML, or a GitHub repo
3. **Extracts Information** - Uses pattern matching to find relevant data:
   - Installation commands (npm install, git clone, pip install, etc.)
   - Environment variable documentation
   - Usage examples and setup instructions
4. **Validates Data** - Checks for required fields and consistency
5. **Generates Output** - Provides structured data for registration

## 🛠️ Integration with Registry Manager

After analyzing documentation, you can register the server using the Registry Manager:

1. Use `extract_server_definition` to get the JSON definition
2. Copy the generated server definition
3. Use the Registry Manager's `add_custom_server` tool
4. Install the newly registered server with `pg config install <server-id>`

## 📝 Pattern Detection

The analyzer recognizes common documentation patterns:

### Installation Patterns
- `npm install <package>` → NPM installation
- `npx <package>` → NPM with npx
- `git clone <repo>` → Git installation
- `pip install <package>` → Python package
- `uvx <package>` → Python with uvx
- `docker run <image>` → Docker container

### Environment Variables
- `VARIABLE_NAME=value` format
- `export VARIABLE_NAME=value`
- Tables with variable descriptions
- Code blocks with .env examples

### Command Patterns
- `node index.js` → Node.js execution
- `python server.py` → Python execution
- `./run.sh` → Script execution
- Docker run commands

## ⚠️ Limitations

- Requires publicly accessible URLs (no authentication)
- Best results with well-structured documentation
- May need manual review for complex installations
- Cannot execute code or test installations
- Limited to text-based documentation analysis

## 🔍 Troubleshooting

### Common Issues

1. **"Could not extract server name"**
   - Ensure the documentation has a clear title or heading
   - Try using a direct link to README.md

2. **"Could not determine installation method"**
   - Check if installation instructions are clearly documented
   - May need to manually specify the method

3. **"HTTP error fetching documentation"**
   - Verify the URL is publicly accessible
   - Check for typos in the URL
   - Try using the raw GitHub content URL

4. **"Validation failed"**
   - Review the extracted information
   - Use `preview_registration` to see what's missing
   - Consider manual overrides in `extract_server_definition`

## 🤝 Best Practices

1. **Use Direct Documentation URLs**
   - Link directly to README.md or docs
   - Avoid landing pages or marketing sites

2. **Verify Extracted Information**
   - Always use `preview_registration` first
   - Check environment variables are complete
   - Ensure commands are correct

3. **Handle Complex Servers**
   - Use manual overrides for complex setups
   - Add detailed setup_help for multi-step installations
   - Document all required environment variables

4. **Batch Processing**
   - Group similar servers together
   - Process up to 10 URLs at once
   - Review results before bulk registration

## 📚 Example Workflow

1. **Find an MCP Server**
   ```
   Found interesting MCP server at: https://github.com/cool/mcp-translator
   ```

2. **Analyze Documentation**
   ```
   Use analyze_mcp_documentation with url: "https://github.com/cool/mcp-translator"
   ```

3. **Preview Registration**
   ```
   Use preview_registration with:
   url: "https://github.com/cool/mcp-translator"
   server_id: "translator"
   ```

4. **Extract Definition**
   ```
   Use extract_server_definition with:
   url: "https://github.com/cool/mcp-translator"
   server_id: "translator"
   ```

5. **Register with Registry Manager**
   ```
   Use add_custom_server (from registry-manager) with the extracted definition
   ```

6. **Install and Use**
   ```bash
   pg config install translator
   ```

## 🎉 Contributing

To improve documentation extraction patterns:
1. Test with various documentation formats
2. Add new pattern recognition in `extract_server_info_from_*` methods
3. Enhance validation rules
4. Submit pull requests with test cases

## 📄 License

MIT License - Feel free to use and modify!
