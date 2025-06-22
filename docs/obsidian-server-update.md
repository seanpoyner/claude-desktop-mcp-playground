# Obsidian MCP Server Configuration Update

## Summary

Added support for both Obsidian MCP server options and fixed configuration issues:

1. **Fixed existing `obsidian` server** - Now uses correct command line arguments
2. **Added new `obsidian-mcp-server`** - Advanced REST API-based server with more features

## Two Obsidian Server Options

### Option 1: `obsidian` (Direct File Access)
- **Package**: `mcp-obsidian`
- **Method**: Direct file system access
- **Setup**: Provide vault path as command line argument
- **Best for**: Simple file operations, no additional Obsidian setup required

### Option 2: `obsidian-mcp-server` (REST API)
- **Package**: `obsidian-mcp-server` 
- **Method**: Uses Obsidian's Local REST API plugin
- **Setup**: Requires Local REST API plugin + API key
- **Best for**: Advanced operations, atomic transactions, caching, full feature set

## Fixed Configuration Formats

### Option 1: Direct File Access (`obsidian`)
```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "mcp-obsidian", "C:\\Users\\seanp\\seans-vault"],
      "env": {}
    }
  }
}
```

### Option 2: REST API (`obsidian-mcp-server`)
```json
{
  "mcpServers": {
    "obsidian-mcp-server": {
      "command": "npx",
      "args": ["obsidian-mcp-server"],
      "env": {
        "OBSIDIAN_API_KEY": "your-api-key-here",
        "OBSIDIAN_BASE_URL": "http://127.0.0.1:27123"
      }
    }
  }
}
```

### Both Options Together
```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "mcp-obsidian", "C:\\Users\\seanp\\seans-vault"],
      "env": {}
    },
    "obsidian-mcp-server": {
      "command": "npx",
      "args": ["obsidian-mcp-server"],
      "env": {
        "OBSIDIAN_API_KEY": "your-api-key-here",
        "OBSIDIAN_BASE_URL": "https://127.0.0.1:27124"
      }
    }
  }
}
```

## Changes Made

### 1. Fixed `obsidian` Server (`claude_desktop_mcp/server_registry.py`)

**Before:**
- Used environment variable `OBSIDIAN_VAULT_PATH`
- `"args_template": ["-y", "mcp-obsidian"]`
- `"required_args": []`

**After:**
- Uses command line argument for vault path
- `"args_template": ["-y", "mcp-obsidian", "<vault_path>"]`
- `"required_args": ["vault_path"]`

### 2. Added `obsidian-mcp-server` Entry

**New server with:**
- Advanced REST API integration
- Comprehensive environment variable configuration
- Detailed setup instructions for Local REST API plugin
- Support for HTTPS, SSL verification, and caching options

### 3. Updated Installation Commands

**Option 1 Installation:**
```bash
pg config install obsidian --arg vault_path="C:\Users\seanp\seans-vault"
```

**Option 2 Installation:**
```bash
pg config install obsidian-mcp-server --env OBSIDIAN_API_KEY="your-key" --env OBSIDIAN_BASE_URL="http://127.0.0.1:27123"
```

## Setup Instructions

### For Option 1 (Direct File Access)
1. Install: `pg config install obsidian --arg vault_path="/path/to/vault"`
2. Restart Claude Desktop
3. No additional Obsidian configuration needed

### For Option 2 (REST API)
1. **Install Local REST API plugin in Obsidian:**
   - Go to Settings → Community plugins → Browse
   - Search for "Local REST API" and install
   - Enable the plugin
2. **Get API key:**
   - Go to plugin settings and copy the API key
3. **Install server:**
   ```bash
   pg config install obsidian-mcp-server --env OBSIDIAN_API_KEY="your-api-key"
   ```
4. **Restart Claude Desktop**

## Feature Comparison

| Feature | `obsidian` (Direct) | `obsidian-mcp-server` (REST API) |
|---------|-------------------|----------------------------------|
| **Setup Complexity** | Simple | Moderate (requires plugin) |
| **File Operations** | ✅ Basic | ✅ Advanced |
| **Frontmatter Editing** | ✅ Basic | ✅ Atomic operations |
| **Search** | ✅ Basic | ✅ Advanced with filters |
| **Tag Management** | ✅ Basic | ✅ Comprehensive |
| **Caching** | ❌ | ✅ Performance optimized |
| **Atomic Transactions** | ❌ | ✅ Prevents corruption |
| **Live Obsidian Integration** | ❌ | ✅ Works with open Obsidian |

## Why This Fix Was Needed

1. **Wrong configuration method**: `mcp-obsidian` expects vault path as command argument, not environment variable
2. **Missing advanced option**: Many users need the more feature-rich REST API server
3. **Error logs**: Users were seeing "Usage: mcp-obsidian <vault-directory>" errors

## Verification

After these updates, users can:
1. ✅ Install either server option without errors
2. ✅ Use both servers simultaneously for different use cases
3. ✅ Choose the best option for their workflow
4. ✅ Access comprehensive setup instructions through `pg config info`
