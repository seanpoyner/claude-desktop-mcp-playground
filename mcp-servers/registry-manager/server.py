#!/usr/bin/env python3
"""
Registry Manager MCP Server

This MCP server allows dynamic addition and management of custom MCP servers
in the Claude Desktop MCP Playground registry. Custom servers can then be
discovered and installed using the 'pg' command.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.lowlevel.server import NotificationOptions
from mcp.server.stdio import stdio_server

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("registry-manager-server")

class RegistryManagerServer:
    def __init__(self):
        self.server = Server("registry-manager")
        self.custom_registry_file = self._get_custom_registry_path()
        self._setup_handlers()
        self._ensure_custom_registry_exists()
    
    def _get_custom_registry_path(self) -> Path:
        """Get the path to the custom registry file."""
        # Store custom servers in the playground directory
        playground_dir = Path.home() / "claude-desktop-mcp-playground"
        if not playground_dir.exists():
            # Fallback to current directory if playground not found
            playground_dir = Path(__file__).parent.parent.parent
        return playground_dir / "custom_registry.json"
    
    def _ensure_custom_registry_exists(self):
        """Ensure the custom registry file exists."""
        if not self.custom_registry_file.exists():
            self._save_custom_registry({})
    
    def _load_custom_registry(self) -> Dict[str, Dict[str, Any]]:
        """Load custom servers from the registry file."""
        try:
            if self.custom_registry_file.exists():
                with open(self.custom_registry_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading custom registry: {e}")
        return {}
    
    def _save_custom_registry(self, registry: Dict[str, Dict[str, Any]]):
        """Save custom servers to the registry file."""
        try:
            with open(self.custom_registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving custom registry: {e}")
            raise
    
    def _validate_server_definition(self, server_def: Dict[str, Any]) -> List[str]:
        """Validate a server definition and return any errors."""
        errors = []
        required_fields = ["name", "description", "command", "install_method"]
        
        for field in required_fields:
            if field not in server_def:
                errors.append(f"Missing required field: {field}")
        
        # Validate install_method
        valid_install_methods = ["npm", "git", "uvx", "docker", "script", "manual"]
        if "install_method" in server_def:
            if server_def["install_method"] not in valid_install_methods:
                errors.append(f"Invalid install_method. Must be one of: {', '.join(valid_install_methods)}")
        
        # Validate command format
        if "command" in server_def and not isinstance(server_def["command"], str):
            errors.append("'command' must be a string")
        
        # Validate args_template if provided
        if "args_template" in server_def and not isinstance(server_def["args_template"], list):
            errors.append("'args_template' must be a list")
        
        # Validate env_vars if provided
        if "env_vars" in server_def and not isinstance(server_def["env_vars"], dict):
            errors.append("'env_vars' must be a dict")
        
        return errors
    
    def _setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available registry management tools."""
            return [
                types.Tool(
                    name="add_custom_server",
                    description="Add a custom MCP server to the registry",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_id": {
                                "type": "string",
                                "description": "Unique identifier for the server"
                            },
                            "server_definition": {
                                "type": "object",
                                "description": "Complete server definition with metadata",
                                "properties": {
                                    "name": {"type": "string", "description": "Display name for the server"},
                                    "description": {"type": "string", "description": "Description of what the server does"},
                                    "category": {"type": "string", "description": "Category (official, community, custom)", "default": "custom"},
                                    "command": {"type": "string", "description": "Command to run the server"},
                                    "args_template": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Template for command arguments (use <placeholder> for user inputs)"
                                    },
                                    "install_method": {
                                        "type": "string",
                                        "enum": ["npm", "git", "uvx", "docker", "script", "manual"],
                                        "description": "How to install the server"
                                    },
                                    "package": {"type": "string", "description": "Package name (for npm/uvx)"},
                                    "repository": {"type": "string", "description": "Git repository URL (for git installs)"},
                                    "required_args": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of required arguments"
                                    },
                                    "env_vars": {
                                        "type": "object",
                                        "description": "Environment variables with descriptions"
                                    },
                                    "setup_help": {"type": "string", "description": "Help text for setup"},
                                    "example_usage": {"type": "string", "description": "Example of how to use the server"},
                                    "homepage": {"type": "string", "description": "Homepage or documentation URL"},
                                    "platform": {"type": "string", "description": "Platform requirement (windows, macos, linux)"}
                                },
                                "required": ["name", "description", "command", "install_method"]
                            }
                        },
                        "required": ["server_id", "server_definition"]
                    }
                ),
                types.Tool(
                    name="list_custom_servers",
                    description="List all custom servers in the registry",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                ),
                types.Tool(
                    name="remove_custom_server",
                    description="Remove a custom server from the registry",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_id": {
                                "type": "string",
                                "description": "ID of the server to remove"
                            }
                        },
                        "required": ["server_id"]
                    }
                ),
                types.Tool(
                    name="update_custom_server",
                    description="Update an existing custom server definition",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_id": {
                                "type": "string",
                                "description": "ID of the server to update"
                            },
                            "server_definition": {
                                "type": "object",
                                "description": "Updated server definition (partial updates allowed)",
                                "additionalProperties": True
                            }
                        },
                        "required": ["server_id", "server_definition"]
                    }
                ),
                types.Tool(
                    name="export_custom_registry",
                    description="Export the custom registry to share or backup",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "format": {
                                "type": "string",
                                "enum": ["json", "markdown"],
                                "default": "json",
                                "description": "Export format"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="import_custom_servers",
                    description="Import custom servers from a JSON definition",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "servers": {
                                "type": "object",
                                "description": "Server definitions to import (server_id -> definition mapping)"
                            },
                            "overwrite": {
                                "type": "boolean",
                                "default": False,
                                "description": "Whether to overwrite existing servers"
                            }
                        },
                        "required": ["servers"]
                    }
                ),
                types.Tool(
                    name="validate_server_definition",
                    description="Validate a server definition without adding it",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_definition": {
                                "type": "object",
                                "description": "Server definition to validate"
                            }
                        },
                        "required": ["server_definition"]
                    }
                ),
                types.Tool(
                    name="create_server_template",
                    description="Create a template for a new server definition",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "install_method": {
                                "type": "string",
                                "enum": ["npm", "git", "uvx", "docker", "script", "manual"],
                                "description": "Installation method for the template"
                            },
                            "server_type": {
                                "type": "string",
                                "enum": ["api", "tool", "data", "automation", "integration"],
                                "description": "Type of server for appropriate template"
                            }
                        },
                        "required": ["install_method"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
            """Handle tool calls for registry management."""
            logger.info(f"Tool call received: {name} with arguments keys: {list(arguments.keys())}")
            
            try:
                if name == "add_custom_server":
                    result = await self._add_custom_server(arguments)
                elif name == "list_custom_servers":
                    result = await self._list_custom_servers()
                elif name == "remove_custom_server":
                    result = await self._remove_custom_server(arguments)
                elif name == "update_custom_server":
                    result = await self._update_custom_server(arguments)
                elif name == "export_custom_registry":
                    result = await self._export_custom_registry(arguments)
                elif name == "import_custom_servers":
                    result = await self._import_custom_servers(arguments)
                elif name == "validate_server_definition":
                    result = await self._validate_server_definition_tool(arguments)
                elif name == "create_server_template":
                    result = await self._create_server_template(arguments)
                else:
                    result = f"Error: Unknown tool '{name}'"
                
                logger.info(f"Tool call completed: {name}")
                return [types.TextContent(type="text", text=result)]
                
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}", exc_info=True)
                error_msg = f"Error: {str(e)}"
                return [types.TextContent(type="text", text=error_msg)]

    async def _add_custom_server(self, arguments: dict[str, Any]) -> str:
        """Add a custom server to the registry."""
        server_id = arguments["server_id"]
        server_def = arguments["server_definition"]
        
        # Validate the server definition
        errors = self._validate_server_definition(server_def)
        if errors:
            return f"❌ **Validation failed for '{server_id}':**\n\n" + "\n".join(f"• {error}" for error in errors)
        
        # Load current registry
        registry = self._load_custom_registry()
        
        # Check if server already exists
        if server_id in registry:
            return f"⚠️ **Server '{server_id}' already exists in custom registry.**\n\nUse 'update_custom_server' to modify it, or choose a different ID."
        
        # Set default category
        if "category" not in server_def:
            server_def["category"] = "custom"
        
        # Add server to registry
        registry[server_id] = server_def
        self._save_custom_registry(registry)
        
        # Also update the main registry file if possible
        try:
            await self._update_main_registry()
        except Exception as e:
            logger.warning(f"Could not update main registry: {e}")
        
        return f"✅ **Custom server '{server_id}' added successfully!**\n\n" \
               f"📝 **Name:** {server_def['name']}\n" \
               f"📋 **Description:** {server_def['description']}\n" \
               f"🛠️ **Install method:** {server_def['install_method']}\n" \
               f"⚙️ **Command:** {server_def['command']}\n\n" \
               f"💡 **Next steps:**\n" \
               f"• Test with: `pg config search {server_id}`\n" \
               f"• Install with: `pg config install {server_id}`\n" \
               f"• View info with: `pg config info {server_id}`"

    async def _list_custom_servers(self) -> str:
        """List all custom servers in the registry."""
        registry = self._load_custom_registry()
        
        if not registry:
            return "📭 **No custom servers in registry.**\n\nUse 'add_custom_server' to add your first custom server!"
        
        result = f"📋 **Custom MCP Servers** ({len(registry)} servers)\n\n"
        
        for server_id, server_def in registry.items():
            result += f"**{server_id}** - {server_def['name']}\n"
            result += f"   📄 {server_def['description']}\n"
            result += f"   🛠️ Install: {server_def['install_method']}"
            if server_def.get('package'):
                result += f" ({server_def['package']})"
            result += f"\n   ⚙️ Command: {server_def['command']}\n"
            if server_def.get('platform'):
                result += f"   🖥️ Platform: {server_def['platform']}\n"
            result += "\n"
        
        result += "💡 **Available commands:**\n"
        result += "• Install any server: `pg config install <server_id>`\n"
        result += "• Get details: `pg config info <server_id>`\n"
        result += "• Remove server: Use 'remove_custom_server' tool"
        
        return result

    async def _remove_custom_server(self, arguments: dict[str, Any]) -> str:
        """Remove a custom server from the registry."""
        server_id = arguments["server_id"]
        
        registry = self._load_custom_registry()
        
        if server_id not in registry:
            return f"❌ **Server '{server_id}' not found in custom registry.**\n\nUse 'list_custom_servers' to see available servers."
        
        # Get server name for confirmation
        server_name = registry[server_id].get("name", server_id)
        
        # Remove from registry
        del registry[server_id]
        self._save_custom_registry(registry)
        
        # Update main registry
        try:
            await self._update_main_registry()
        except Exception as e:
            logger.warning(f"Could not update main registry: {e}")
        
        return f"✅ **Custom server '{server_id}' ({server_name}) removed successfully!**\n\n" \
               f"The server is no longer available for installation via `pg config install`."

    async def _update_custom_server(self, arguments: dict[str, Any]) -> str:
        """Update an existing custom server definition."""
        server_id = arguments["server_id"]
        updates = arguments["server_definition"]
        
        registry = self._load_custom_registry()
        
        if server_id not in registry:
            return f"❌ **Server '{server_id}' not found in custom registry.**\n\nUse 'add_custom_server' to create it first."
        
        # Merge updates with existing definition
        current_def = registry[server_id].copy()
        current_def.update(updates)
        
        # Validate the updated definition
        errors = self._validate_server_definition(current_def)
        if errors:
            return f"❌ **Validation failed for updated '{server_id}':**\n\n" + "\n".join(f"• {error}" for error in errors)
        
        # Save updated definition
        registry[server_id] = current_def
        self._save_custom_registry(registry)
        
        # Update main registry
        try:
            await self._update_main_registry()
        except Exception as e:
            logger.warning(f"Could not update main registry: {e}")
        
        updated_fields = list(updates.keys())
        return f"✅ **Custom server '{server_id}' updated successfully!**\n\n" \
               f"🔄 **Updated fields:** {', '.join(updated_fields)}\n\n" \
               f"💡 **Test the changes:**\n" \
               f"• View info: `pg config info {server_id}`\n" \
               f"• Install/reinstall: `pg config install {server_id}`"

    async def _export_custom_registry(self, arguments: dict[str, Any]) -> str:
        """Export the custom registry."""
        format_type = arguments.get("format", "json")
        registry = self._load_custom_registry()
        
        if not registry:
            return "📭 **No custom servers to export.**"
        
        if format_type == "json":
            json_output = json.dumps(registry, indent=2, ensure_ascii=False)
            return f"📤 **Custom Registry Export (JSON)**\n\n```json\n{json_output}\n```\n\n" \
                   f"💾 **To backup:** Save this JSON to a file\n" \
                   f"📥 **To restore:** Use 'import_custom_servers' tool"
        
        elif format_type == "markdown":
            md_output = f"# Custom MCP Servers Registry\n\n"
            md_output += f"Total servers: {len(registry)}\n\n"
            
            for server_id, server_def in registry.items():
                md_output += f"## {server_def['name']}\n\n"
                md_output += f"**ID:** `{server_id}`\n"
                md_output += f"**Description:** {server_def['description']}\n"
                md_output += f"**Install method:** {server_def['install_method']}\n"
                md_output += f"**Command:** `{server_def['command']}`\n"
                
                if server_def.get('package'):
                    md_output += f"**Package:** {server_def['package']}\n"
                if server_def.get('repository'):
                    md_output += f"**Repository:** {server_def['repository']}\n"
                if server_def.get('platform'):
                    md_output += f"**Platform:** {server_def['platform']}\n"
                if server_def.get('homepage'):
                    md_output += f"**Homepage:** {server_def['homepage']}\n"
                
                md_output += f"\n**Installation:**\n```bash\npg config install {server_id}\n```\n\n"
                
                if server_def.get('example_usage'):
                    md_output += f"**Example usage:** {server_def['example_usage']}\n\n"
                
                md_output += "---\n\n"
            
            return f"📤 **Custom Registry Export (Markdown)**\n\n```markdown\n{md_output}\n```"
        
        return f"❌ **Unknown format '{format_type}'. Use 'json' or 'markdown'.**"

    async def _import_custom_servers(self, arguments: dict[str, Any]) -> str:
        """Import custom servers from a JSON definition."""
        servers = arguments["servers"]
        overwrite = arguments.get("overwrite", False)
        
        if not isinstance(servers, dict):
            return "❌ **Invalid servers format. Expected a dictionary of server_id -> definition.**"
        
        registry = self._load_custom_registry()
        imported_count = 0
        skipped_count = 0
        error_count = 0
        results = []
        
        for server_id, server_def in servers.items():
            try:
                # Validate server definition
                errors = self._validate_server_definition(server_def)
                if errors:
                    results.append(f"❌ {server_id}: {', '.join(errors)}")
                    error_count += 1
                    continue
                
                # Check if exists
                if server_id in registry and not overwrite:
                    results.append(f"⏭️ {server_id}: Already exists (use overwrite=true)")
                    skipped_count += 1
                    continue
                
                # Set default category
                if "category" not in server_def:
                    server_def["category"] = "custom"
                
                # Add to registry
                registry[server_id] = server_def
                results.append(f"✅ {server_id}: Imported successfully")
                imported_count += 1
                
            except Exception as e:
                results.append(f"❌ {server_id}: {str(e)}")
                error_count += 1
        
        # Save registry if any imports succeeded
        if imported_count > 0:
            self._save_custom_registry(registry)
            try:
                await self._update_main_registry()
            except Exception as e:
                logger.warning(f"Could not update main registry: {e}")
        
        summary = f"📥 **Import Summary**\n\n"
        summary += f"✅ **Imported:** {imported_count} servers\n"
        summary += f"⏭️ **Skipped:** {skipped_count} servers\n"
        summary += f"❌ **Errors:** {error_count} servers\n\n"
        
        if results:
            summary += "**Details:**\n" + "\n".join(results)
        
        if imported_count > 0:
            summary += f"\n\n💡 **Next steps:**\n"
            summary += f"• Test servers: `pg config search`\n"
            summary += f"• Install any: `pg config install <server_id>`"
        
        return summary

    async def _validate_server_definition_tool(self, arguments: dict[str, Any]) -> str:
        """Validate a server definition without adding it."""
        server_def = arguments["server_definition"]
        
        errors = self._validate_server_definition(server_def)
        
        if not errors:
            return f"✅ **Server definition is valid!**\n\n" \
                   f"📝 **Name:** {server_def.get('name', 'Not specified')}\n" \
                   f"📋 **Description:** {server_def.get('description', 'Not specified')}\n" \
                   f"🛠️ **Install method:** {server_def.get('install_method', 'Not specified')}\n" \
                   f"⚙️ **Command:** {server_def.get('command', 'Not specified')}\n\n" \
                   f"💡 **Ready to add with 'add_custom_server' tool.**"
        else:
            return f"❌ **Validation failed:**\n\n" + "\n".join(f"• {error}" for error in errors) + \
                   f"\n\n💡 **Fix these issues and try again.**"

    async def _create_server_template(self, arguments: dict[str, Any]) -> str:
        """Create a template for a new server definition."""
        install_method = arguments["install_method"]
        server_type = arguments.get("server_type", "tool")
        
        templates = {
            "npm": {
                "name": "My NPM Server",
                "description": "Description of what this server does",
                "category": "custom",
                "package": "my-mcp-server",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "my-mcp-server"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {
                    "API_KEY": "Your API key for the service"
                },
                "setup_help": "Get API key from service provider",
                "example_usage": "Interact with external service",
                "homepage": "https://github.com/user/my-mcp-server"
            },
            "git": {
                "name": "My Git Server",
                "description": "Server installed from Git repository",
                "category": "custom",
                "repository": "https://github.com/user/my-mcp-server",
                "install_method": "git",
                "command": "node",
                "args_template": ["<repo_path>/dist/index.js"],
                "required_args": ["repo_path"],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Repository will be cloned automatically",
                "example_usage": "Custom functionality from Git repo",
                "homepage": "https://github.com/user/my-mcp-server"
            },
            "uvx": {
                "name": "My Python Server",
                "description": "Python-based MCP server via uvx",
                "category": "custom",
                "package": "my-python-mcp-server",
                "install_method": "uvx",
                "command": "uvx",
                "args_template": ["my-python-mcp-server"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Requires uvx (pip install uvx)",
                "example_usage": "Python-based server functionality",
                "homepage": "https://pypi.org/project/my-python-mcp-server/"
            },
            "docker": {
                "name": "My Docker Server",
                "description": "Containerized MCP server",
                "category": "custom",
                "package": "my-docker-image",
                "install_method": "docker",
                "command": "docker",
                "args_template": ["run", "-i", "--rm", "my-docker-image"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {
                    "CONFIG_VAR": "Configuration value"
                },
                "setup_help": "Requires Docker installed and running",
                "example_usage": "Containerized server functionality",
                "homepage": "https://hub.docker.com/r/user/my-docker-image"
            },
            "script": {
                "name": "My Script Server",
                "description": "Server installed via custom script",
                "category": "custom",
                "install_method": "script",
                "command": "auto_detect",
                "args_template": [],
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Custom installation via provided installer script",
                "example_usage": "Custom script-based functionality",
                "homepage": "https://example.com/my-server",
                "platform_config": {
                    "windows": {
                        "command": "cmd",
                        "args_template": ["/c", "{installation_path}\\server.exe"],
                        "default_paths": [
                            "{LOCALAPPDATA}\\my-server\\server.exe"
                        ]
                    },
                    "linux": {
                        "command": "sh",
                        "args_template": ["-c", "{installation_path}/server"],
                        "default_paths": [
                            "{HOME}/.local/bin/my-server"
                        ]
                    }
                }
            },
            "manual": {
                "name": "My Manual Server",
                "description": "Server requiring manual installation",
                "category": "custom",
                "install_method": "manual",
                "command": "path/to/server",
                "args_template": ["--config", "<config_file>"],
                "required_args": ["config_file"],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Manual installation required. Download from homepage and configure path.",
                "example_usage": "Manually installed server functionality",
                "homepage": "https://example.com/my-server/download"
            }
        }
        
        if install_method not in templates:
            return f"❌ **Unknown install method '{install_method}'.**\n\n" \
                   f"Available methods: {', '.join(templates.keys())}"
        
        template = templates[install_method]
        
        # Customize based on server type
        type_customizations = {
            "api": {
                "description": "Provides API integration for external services",
                "env_vars": {"API_KEY": "API key for the external service"},
                "setup_help": "Get API credentials from service provider"
            },
            "data": {
                "description": "Provides data access and manipulation capabilities",
                "env_vars": {"DATABASE_URL": "Connection string for data source"},
                "setup_help": "Configure data source connection"
            },
            "automation": {
                "description": "Automates tasks and workflows",
                "setup_help": "Configure automation triggers and actions"
            },
            "integration": {
                "description": "Integrates with external tools and platforms",
                "env_vars": {"INTEGRATION_TOKEN": "Token for platform integration"},
                "setup_help": "Set up platform integration credentials"
            }
        }
        
        if server_type in type_customizations:
            customization = type_customizations[server_type]
            template.update(customization)
        
        json_template = json.dumps(template, indent=2, ensure_ascii=False)
        
        return f"📋 **Server Template ({install_method})**\n\n" \
               f"```json\n{json_template}\n```\n\n" \
               f"💡 **Usage:**\n" \
               f"1. Customize the template above with your server details\n" \
               f"2. Use 'add_custom_server' tool with this definition\n" \
               f"3. Replace placeholder values (like 'my-mcp-server')\n" \
               f"4. Update URLs, package names, and descriptions\n\n" \
               f"🔧 **Key fields to customize:**\n" \
               f"• `name`: Display name for your server\n" \
               f"• `description`: What your server does\n" \
               f"• `package`/`repository`: Where to find your server\n" \
               f"• `env_vars`: Required environment variables\n" \
               f"• `homepage`: Documentation or source URL"

    async def _update_main_registry(self):
        """Update the main server registry with custom servers."""
        try:
            # Load custom servers
            custom_servers = self._load_custom_registry()
            
            if not custom_servers:
                return
            
            # Get the main registry file path
            registry_file = Path(__file__).parent.parent.parent / "claude_desktop_mcp" / "server_registry.py"
            
            if not registry_file.exists():
                logger.warning("Main registry file not found, skipping update")
                return
            
            # Read current registry file
            with open(registry_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create the custom servers section
            custom_section = "\n            # Custom servers (managed by registry-manager)\n"
            for server_id, server_def in custom_servers.items():
                custom_section += f'            "{server_id}": {json.dumps(server_def, indent=16)[16:].rstrip()},\n'
            
            # Insert or replace custom servers section
            start_marker = "            # Custom servers (managed by registry-manager)"
            end_marker = "        }"
            
            start_idx = content.find(start_marker)
            if start_idx != -1:
                # Replace existing custom section
                end_idx = content.find(end_marker, start_idx)
                before = content[:start_idx]
                after = content[end_idx:]
                new_content = before + custom_section + "        " + after[8:]  # Adjust indentation
            else:
                # Add custom section before the closing brace
                end_idx = content.rfind("        }")
                if end_idx != -1:
                    before = content[:end_idx]
                    after = content[end_idx:]
                    new_content = before + custom_section + after
                else:
                    logger.warning("Could not find insertion point in registry file")
                    return
            
            # Write updated content
            with open(registry_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"Updated main registry with {len(custom_servers)} custom servers")
            
        except Exception as e:
            logger.error(f"Failed to update main registry: {e}")
            raise

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="registry-manager",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

async def main():
    """Main entry point."""
    server = RegistryManagerServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
