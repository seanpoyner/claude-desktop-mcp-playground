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
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
            """Handle tool calls by executing PG CLI commands."""
            logger.info(f"Tool call received: {name} with arguments: {arguments}")
            try:
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
        
        # For debugging, try the direct Python import method first
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
                "/usr/local/bin/pg",
                "/usr/bin/pg", 
                str(Path.home() / ".local" / "bin" / "pg"),
                "pg"  # Assume it's in PATH
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
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,  # 10 second timeout
                check=False,
                cwd=cwd
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
            logger.error("Command timed out after 10 seconds")
            return "Error: Command timed out after 10 seconds"
        except Exception as e:
            logger.error(f"Exception during command execution: {e}", exc_info=True)
            return f"Error executing command: {str(e)}"

    async def _execute_direct_python(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Execute pg command by importing the CLI module directly."""
        logger.info(f"Direct Python execution for tool: {tool_name}")
        
        import sys
        import io
        import platform
        from contextlib import redirect_stdout, redirect_stderr
        
        # Add the claude_desktop_mcp to path - handle both Windows and Linux paths
        system = platform.system().lower()
        if system == "windows":
            project_path = "C:\\Users\\seanp\\claude-desktop-mcp-playground"
        else:
            project_path = "/mnt/c/Users/seanp/claude-desktop-mcp-playground"
        
        logger.info(f"Adding to sys.path: {project_path}")
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