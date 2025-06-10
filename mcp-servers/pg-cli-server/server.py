#!/usr/bin/env python3
"""
MCP Server for PG CLI Commands

This server exposes the 'pg' (Claude Desktop MCP Playground) CLI commands
as MCP tools, allowing Claude Desktop to manage MCP servers directly.
"""

import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.lowlevel.server import NotificationOptions
from mcp.server.stdio import stdio_server

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pg-cli-server")

class PGCLIServer:
    def __init__(self):
        self.server = Server("pg-cli-server")
        self._setup_handlers()
    
    def _setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available PG CLI tools."""
            return [
                types.Tool(
                    name="pg_config_search",
                    description="Search available MCP servers in the registry",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for server names or descriptions"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="pg_config_info",
                    description="Get detailed information about a specific MCP server",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_id": {
                                "type": "string",
                                "description": "The ID of the server to get information about"
                            }
                        },
                        "required": ["server_id"]
                    }
                ),
                types.Tool(
                    name="pg_config_install",
                    description="Install an MCP server",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_id": {
                                "type": "string",
                                "description": "The ID of the server to install"
                            },
                            "args": {
                                "type": "object",
                                "description": "Additional arguments for server installation",
                                "additionalProperties": True
                            }
                        },
                        "required": ["server_id"]
                    }
                ),
                types.Tool(
                    name="pg_config_show",
                    description="Show the current Claude Desktop MCP configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                ),
                types.Tool(
                    name="pg_config_remove",
                    description="Remove an installed MCP server",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_id": {
                                "type": "string",
                                "description": "The ID of the server to remove"
                            }
                        },
                        "required": ["server_id"]
                    }
                ),
                types.Tool(
                    name="pg_config_install_with_config",
                    description="Install an MCP server with configuration (like API tokens)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_id": {
                                "type": "string",
                                "description": "The ID of the server to install"
                            },
                            "config": {
                                "type": "object",
                                "description": "Configuration parameters (e.g., API tokens, keys)",
                                "additionalProperties": True
                            }
                        },
                        "required": ["server_id", "config"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
            """Handle tool calls by executing PG CLI commands."""
            logger.info(f"Tool call received: {name} with arguments: {arguments}")
            try:
                # Handle install commands specially to provide better user feedback
                if name == "pg_config_install":
                    result = await self._handle_install_command(arguments)
                elif name == "pg_config_install_with_config":
                    result = await self._handle_install_with_config(arguments)
                else:
                    result = await self._execute_pg_command(name, arguments)
                
                logger.info(f"Tool call completed: {name}, result length: {len(result)}")
                return [types.TextContent(type="text", text=result)]
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}", exc_info=True)
                error_msg = f"Error: {str(e)}"
                return [types.TextContent(type="text", text=error_msg)]

    async def _execute_pg_command(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Execute the corresponding PG CLI command."""
        logger.info(f"Starting _execute_pg_command for tool: {tool_name}")
        
        # Try the direct Python import method first for all commands
        try:
            logger.info("Attempting direct Python import method")
            return await self._execute_direct_python(tool_name, arguments)
        except Exception as e:
            logger.error(f"Direct Python method failed: {e}")
            logger.info("Falling back to subprocess method...")
            # Fall back to subprocess method
            pass
        
        # Find the pg command - check common locations
        import platform
        system = platform.system().lower()
        
        if system == "windows":
            pg_locations = [
                "pg.bat",
                "pg.exe", 
                "pg",
                "C:\\Users\\seanp\\claude-desktop-mcp-playground\\pg.bat",
                "C:\\Users\\seanp\\claude-desktop-mcp-playground\\mcp-server-manager-windows-complete\\pg.bat",
                "C:\\Users\\seanp\\claude-desktop-mcp-playground\\mcp-server-manager-windows-source\\pg.bat",
                str(Path.home() / "claude-desktop-mcp-playground" / "pg.bat"),
                str(Path.home() / "AppData" / "Local" / "Programs" / "pg" / "pg.exe"),
                "C:\\Program Files\\pg\\pg.exe",
            ]
        else:
            pg_locations = [
                # Skip Node.js pg commands that use .gradio-mcp
                # We want to use the Python pg command from this project
            ]
        
        pg_cmd = None
        debug_info = []
        
        for location in pg_locations:
            try:
                debug_info.append(f"Trying: {location}")
                result = subprocess.run([location, "--version"], capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    pg_cmd = location
                    debug_info.append(f"✓ Found working pg command at: {location}")
                    break
                else:
                    debug_info.append(f"✗ Command failed with exit code {result.returncode}")
            except FileNotFoundError:
                debug_info.append(f"✗ File not found: {location}")
            except subprocess.TimeoutExpired:
                debug_info.append(f"✗ Timeout: {location}")
            except Exception as e:
                debug_info.append(f"✗ Error: {location} - {e}")
        
        if not pg_cmd:
            # Try Python fallback as last resort
            try:
                debug_info.append("Trying Python fallback: python -m claude_desktop_mcp.cli")
                result = subprocess.run(
                    ["python", "-m", "claude_desktop_mcp.cli", "--version"], 
                    capture_output=True, text=True, timeout=3,
                    cwd="C:\\Users\\seanp\\claude-desktop-mcp-playground" if system == "windows" else None
                )
                if result.returncode == 0:
                    pg_cmd = "python -m claude_desktop_mcp.cli"
                    debug_info.append(f"✓ Python fallback works: {result.stdout.strip()}")
                else:
                    debug_info.append(f"✗ Python fallback failed: {result.stderr}")
            except Exception as e:
                debug_info.append(f"✗ Python fallback error: {e}")
        
        if not pg_cmd:
            debug_details = "\n".join(debug_info)
            return f"Error: 'pg' command not found. Debug info:\n{debug_details}\n\nPlease ensure Claude Desktop MCP Playground is installed and in PATH."
        
        # Build command based on tool name
        if pg_cmd == "python -m claude_desktop_mcp.cli":
            cmd = ["python", "-m", "claude_desktop_mcp.cli"]
        else:
            cmd = [pg_cmd]
        
        if tool_name == "pg_config_search":
            cmd.extend(["config", "search", arguments["query"]])
        elif tool_name == "pg_config_info":
            cmd.extend(["config", "info", arguments["server_id"]])
        elif tool_name == "pg_config_install":
            cmd.extend(["config", "install", arguments["server_id"]])
            # Always add --yes to avoid confirmation prompts
            cmd.append("--yes")
            # Add any additional arguments
            if "args" in arguments:
                for key, value in arguments["args"].items():
                    cmd.extend([f"--{key}", str(value)])
        elif tool_name == "pg_config_show":
            cmd.extend(["config", "show"])
        elif tool_name == "pg_config_remove":
            cmd.extend(["config", "remove", arguments["server_id"]])
        else:
            return f"Error: Unknown tool '{tool_name}'"
        
        # Execute the command
        try:
            logger.info(f"Executing command: {' '.join(cmd)}")
            logger.info(f"Working directory: {cwd if 'cwd' in locals() else 'None'}")
            
            # Set working directory for Python fallback
            cwd = None
            if pg_cmd == "python -m claude_desktop_mcp.cli":
                if system == "windows":
                    cwd = "C:\\Users\\seanp\\claude-desktop-mcp-playground"
                else:
                    cwd = "/mnt/c/Users/seanp/claude-desktop-mcp-playground"
                logger.info(f"Using working directory: {cwd}")
            
            # Use longer timeout for installation commands
            timeout_seconds = 60 if tool_name == "pg_config_install" else 30
            
            # Set environment to handle Unicode properly on Windows
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=timeout_seconds,
                check=False,
                cwd=cwd,
                env=env
            )
            
            logger.info(f"Command finished with return code: {result.returncode}")
            logger.info(f"Stdout length: {len(result.stdout)} chars")
            logger.info(f"Stderr length: {len(result.stderr)} chars")
            
            # Return combined output
            output_parts = []
            if result.stdout:
                output_parts.append(f"Output:\n{result.stdout}")
            if result.stderr:
                output_parts.append(f"Errors:\n{result.stderr}")
            if result.returncode != 0:
                output_parts.append(f"Exit code: {result.returncode}")
            
            final_result = "\n\n".join(output_parts) if output_parts else "Command completed successfully with no output."
            logger.info(f"Returning result of length: {len(final_result)}")
            return final_result
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout_seconds} seconds")
            return f"Error: Command timed out after {timeout_seconds} seconds"
        except Exception as e:
            logger.error(f"Exception during command execution: {e}", exc_info=True)
            return f"Error executing command: {str(e)}"

    async def _execute_direct_python(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Execute pg command by importing the CLI module directly."""
        logger.info(f"Direct Python execution for tool: {tool_name}")
        
        import sys
        import io
        import platform
        import os
        from pathlib import Path
        from contextlib import redirect_stdout, redirect_stderr
        
        # Add the claude_desktop_mcp to path - handle both Windows and Linux paths
        system = platform.system().lower()
        
        # Nothing needed here - we'll patch the config manager instead
        
        if system == "windows":
            project_path = "C:\\Users\\seanp\\claude-desktop-mcp-playground"
        else:
            project_path = "/mnt/c/Users/seanp/claude-desktop-mcp-playground"
        
        logger.info(f"System: {system}, Adding to sys.path: {project_path}")
        if project_path not in sys.path:
            sys.path.insert(0, project_path)
        
        # Also try alternative paths
        alt_paths = [
            "C:\\Users\\seanp\\claude-desktop-mcp-playground",
            "/mnt/c/Users/seanp/claude-desktop-mcp-playground",
            str(Path(__file__).parent.parent.parent),  # Go up from mcp-servers/pg-cli-server/
        ]
        
        for alt_path in alt_paths:
            if alt_path not in sys.path and Path(alt_path).exists():
                logger.info(f"Adding alternative path: {alt_path}")
                sys.path.insert(0, alt_path)
        
        logger.info(f"Current sys.path: {sys.path[:5]}...")  # Log first 5 paths
        
        try:
            from claude_desktop_mcp.cli import main
            
            # Build command args
            if tool_name == "pg_config_search":
                args = ["config", "search", arguments["query"]]
            elif tool_name == "pg_config_info":
                args = ["config", "info", arguments["server_id"]]
            elif tool_name == "pg_config_install":
                args = ["config", "install", arguments["server_id"]]
                # Always add --yes to avoid confirmation prompts
                args.append("--yes")
                # Add any additional arguments
                if "args" in arguments:
                    for key, value in arguments["args"].items():
                        args.extend([f"--{key}", str(value)])
            elif tool_name == "pg_config_show":
                args = ["config", "show"]
            elif tool_name == "pg_config_remove":
                args = ["config", "remove", arguments["server_id"]]
            else:
                return f"Error: Unknown tool '{tool_name}'"
            
            logger.info(f"Direct execution args: {args}")
            
            # Capture stdout and stderr
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # Backup original argv and replace it
            original_argv = sys.argv
            try:
                sys.argv = ["pg"] + args
                
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    main()
                
                # Get captured output
                stdout_content = stdout_capture.getvalue()
                stderr_content = stderr_capture.getvalue()
                
                logger.info(f"Direct execution stdout: {len(stdout_content)} chars")
                logger.info(f"Direct execution stderr: {len(stderr_content)} chars")
                
                # Return combined output
                output_parts = []
                if stdout_content:
                    output_parts.append(f"Output:\n{stdout_content}")
                if stderr_content:
                    output_parts.append(f"Errors:\n{stderr_content}")
                
                return "\n\n".join(output_parts) if output_parts else "Command completed successfully with no output."
                
            finally:
                sys.argv = original_argv
                
        except SystemExit as e:
            # Handle sys.exit() calls from CLI
            stdout_content = stdout_capture.getvalue()
            stderr_content = stderr_capture.getvalue()
            
            output_parts = []
            if stdout_content:
                output_parts.append(f"Output:\n{stdout_content}")
            if stderr_content:
                output_parts.append(f"Errors:\n{stderr_content}")
            if e.code != 0:
                output_parts.append(f"Exit code: {e.code}")
            
            return "\n\n".join(output_parts) if output_parts else "Command completed successfully with no output."
        
        except Exception as e:
            logger.error(f"Direct Python execution failed: {e}", exc_info=True)
            raise

    async def _handle_install_command(self, arguments: dict[str, Any]) -> str:
        """Handle install commands with better user feedback and configuration prompts."""
        server_id = arguments["server_id"]
        logger.info(f"Installing MCP server: {server_id}")
        
        # First, get server info to understand what's needed
        try:
            info_result = await self._execute_pg_command("pg_config_info", {"server_id": server_id})
            logger.info(f"Server info retrieved for {server_id}")
        except Exception as e:
            logger.error(f"Failed to get server info for {server_id}: {e}")
            return f"Error: Could not retrieve information for server '{server_id}'. Please check if the server exists."
        
        # Check if this server requires special configuration
        special_configs = {
            "figma": {
                "required_env": ["FIGMA_ACCESS_TOKEN"],
                "setup_instructions": """
To install the Figma MCP server, you need:

1. **Figma Access Token** - Get this from your Figma account:
   - Go to https://www.figma.com/developers/api#authentication
   - Generate a personal access token
   - Copy the token

2. **Installation Options**:
   
   **Option A: Provide token now**
   I can install with your token. Reply with:
   "Install figma with token: your_token_here"
   
   **Option B: Manual setup after installation**
   I'll install without the token, then provide setup instructions.
   
   **Option C: Get more information first**
   Use: "Get info about figma server"

Which option would you prefer?"""
            },
            "github": {
                "required_env": ["GITHUB_TOKEN"],
                "setup_instructions": """
To install the GitHub MCP server, you need:

1. **GitHub Personal Access Token** - Get this from GitHub:
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Generate a new token with appropriate repository permissions
   - Copy the token

Would you like me to:
A) Install with your token now (reply: "Install github with token: your_token")
B) Install without token and provide manual setup instructions
C) Get more details about the GitHub server first"""
            },
            "brave-search": {
                "required_env": ["BRAVE_API_KEY"],
                "setup_instructions": """
To install the Brave Search MCP server, you need:

1. **Brave Search API Key** - Get this from Brave:
   - Go to https://api.search.brave.com/
   - Sign up for an API key
   - Copy the API key

Would you like me to:
A) Install with your API key now (reply: "Install brave-search with key: your_key")
B) Install without key and provide manual setup instructions
C) Get more details about the Brave Search server first"""
            }
        }
        
        if server_id in special_configs:
            config = special_configs[server_id]
            return f"🔧 **{server_id.title()} Server Configuration Required**\n\n{config['setup_instructions']}"
        
        # For servers that don't need special config, proceed with installation
        try:
            result = await self._execute_pg_command("pg_config_install", arguments)
            
            # Check if installation was successful or if npm package is missing
            if "npm package NOT installed" in result:
                return f"⚠️ **{server_id} configuration added but npm package NOT installed!**\n\n{result}\n\n💡 **To complete installation:**\n1. Install the npm package manually (see command above)\n2. OR re-run with auto-install: `pg config install {server_id} --auto-install`\n3. Then restart Claude Desktop"
            elif "Successfully installed" in result and "npm package NOT installed" not in result:
                return f"✅ **{server_id} installed successfully!**\n\n{result}\n\n💡 **Next steps:**\n- Restart Claude Desktop to load the new server\n- The server should appear in your MCP server list\n- Check the installation with: `pg config show`"
            elif "already installed" in result.lower():
                return f"ℹ️ **{server_id} is already installed.**\n\n{result}"
            else:
                return f"⚠️ **Installation may need attention:**\n\n{result}\n\n💡 Try checking the status with: `pg config show`"
                
        except Exception as e:
            logger.error(f"Installation failed for {server_id}: {e}")
            return f"❌ **Installation failed for {server_id}**\n\nError: {str(e)}\n\n💡 **Troubleshooting:**\n- Check if you have the required dependencies\n- Try getting more info first: `pg config info {server_id}`\n- Ensure you have internet connectivity"

    async def _handle_install_with_config(self, arguments: dict[str, Any]) -> str:
        """Handle install commands with user-provided configuration."""
        server_id = arguments["server_id"]
        config = arguments["config"]
        logger.info(f"Installing MCP server {server_id} with config: {list(config.keys())}")
        
        # Build install arguments with environment variables
        install_args = {"server_id": server_id}
        
        # Convert config to environment variables for the installation
        env_vars = {}
        config_mapping = {
            "figma": {
                "token": "FIGMA_TOKEN", 
                "api_token": "FIGMA_TOKEN",
                "FIGMA_TOKEN": "FIGMA_TOKEN",
                "FIGMA_ACCESS_TOKEN": "FIGMA_TOKEN"
            },
            "github": {"token": "GITHUB_TOKEN", "api_token": "GITHUB_TOKEN", "github_token": "GITHUB_TOKEN"},
            "brave-search": {"key": "BRAVE_API_KEY", "api_key": "BRAVE_API_KEY"},
            "slack": {"token": "SLACK_BOT_TOKEN", "bot_token": "SLACK_BOT_TOKEN"},
            "google-drive": {"credentials": "GOOGLE_DRIVE_CREDENTIALS_FILE"},
            "postgres": {
                "host": "POSTGRES_HOST",
                "port": "POSTGRES_PORT", 
                "database": "POSTGRES_DB",
                "user": "POSTGRES_USER",
                "password": "POSTGRES_PASSWORD"
            }
        }
        
        if server_id in config_mapping:
            mapping = config_mapping[server_id]
            for user_key, env_var in mapping.items():
                if user_key in config:
                    env_vars[env_var] = config[user_key]
        
        # Add environment variables to install args
        if env_vars:
            install_args["env"] = env_vars
        
        try:
            # Execute installation with environment variables by modifying the execution context
            if env_vars:
                result = await self._execute_pg_command_with_env("pg_config_install", install_args, env_vars)
            else:
                result = await self._execute_pg_command("pg_config_install", install_args)
            
            # Provide user-friendly feedback
            if "Successfully installed" in result or "Installation completed" in result:
                env_summary = ", ".join([f"{k}=***" for k in env_vars.keys()])
                return f"✅ **{server_id} installed successfully with configuration!**\n\n{result}\n\n🔧 **Configuration applied:**\n- {env_summary}\n\n💡 **Next steps:**\n- Restart Claude Desktop to load the new server\n- The server should now be available with your configuration\n- Test the server functionality"
            else:
                return f"⚠️ **Installation completed with configuration, but please verify:**\n\n{result}\n\n🔧 **Configuration provided:** {list(env_vars.keys())}"
                
        except Exception as e:
            logger.error(f"Configured installation failed for {server_id}: {e}")
            return f"❌ **Installation with configuration failed for {server_id}**\n\nError: {str(e)}\n\n💡 **Note:** Your configuration was not saved. Please try again or install manually."

    async def _execute_pg_command_with_env(self, tool_name: str, arguments: dict[str, Any], env_vars: dict[str, str]) -> str:
        """Execute pg command with custom environment variables."""
        logger.info(f"Executing {tool_name} with environment variables: {list(env_vars.keys())}")
        
        import sys
        import io
        import os
        import platform
        from contextlib import redirect_stdout, redirect_stderr
        
        # Add the claude_desktop_mcp to path
        system = platform.system().lower()
        if system == "windows":
            project_path = "C:\\Users\\seanp\\claude-desktop-mcp-playground"
        else:
            project_path = "/mnt/c/Users/seanp/claude-desktop-mcp-playground"
        
        if project_path not in sys.path:
            sys.path.insert(0, project_path)
        
        try:
            from claude_desktop_mcp.cli import main
            
            # Build command args (remove env from arguments)
            clean_args = {k: v for k, v in arguments.items() if k != "env"}
            
            if tool_name == "pg_config_install":
                args = ["config", "install", clean_args["server_id"], "--yes"]
                # Add environment variables as CLI arguments
                for key, value in env_vars.items():
                    args.extend(["--env", f"{key}={value}"])
            else:
                return await self._execute_pg_command(tool_name, clean_args)
            
            logger.info(f"Direct execution with env vars: {args}")
            
            try:
                # Capture stdout and stderr
                stdout_capture = io.StringIO()
                stderr_capture = io.StringIO()
                
                # Backup original argv and replace it
                original_argv = sys.argv
                sys.argv = ["pg"] + args
                
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    main()
                
                # Get captured output
                stdout_content = stdout_capture.getvalue()
                stderr_content = stderr_capture.getvalue()
                
                # Return combined output
                output_parts = []
                if stdout_content:
                    output_parts.append(f"Output:\n{stdout_content}")
                if stderr_content:
                    output_parts.append(f"Errors:\n{stderr_content}")
                
                return "\n\n".join(output_parts) if output_parts else "Command completed successfully with no output."
                
            finally:
                # Restore original argv
                sys.argv = original_argv
                
        except SystemExit as e:
            # Handle sys.exit() calls from CLI
            stdout_content = stdout_capture.getvalue()
            stderr_content = stderr_capture.getvalue()
            
            output_parts = []
            if stdout_content:
                output_parts.append(f"Output:\n{stdout_content}")
            if stderr_content:
                output_parts.append(f"Errors:\n{stderr_content}")
            if e.code != 0:
                output_parts.append(f"Exit code: {e.code}")
            
            return "\n\n".join(output_parts) if output_parts else "Command completed successfully with no output."
        
        except Exception as e:
            logger.error(f"Direct Python execution with env failed: {e}", exc_info=True)
            raise

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="pg-cli-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

async def main():
    """Main entry point."""
    server = PGCLIServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())