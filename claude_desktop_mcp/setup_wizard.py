"""Interactive setup wizard for Claude Desktop MCP Playground

Provides guided setup for first-time users including dependency checking,
installation assistance, and MCP server configuration.
"""

import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import time
import signal
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click

from .config_manager import ClaudeDesktopConfigManager, save_simplified_config


def setup_logging(log_level=logging.INFO):
    """Setup logging for the setup wizard"""
    log_dir = Path.home() / ".claude-mcp-logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"setup-{int(time.time())}.log"
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Setup logger
    logger = logging.getLogger('claude_mcp_setup')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log file location
    click.echo(f"[INFO] Logging to: {log_file}")
    logger.info(f"Setup wizard started. Log file: {log_file}")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Python: {sys.version}")
    
    return logger


def timeout_handler(signum, frame):
    """Handle timeout for prompts"""
    raise TimeoutError("Operation timed out")


def safe_prompt(prompt_func, timeout_seconds=30, *args, **kwargs):
    """Wrapper for prompts with timeout (Unix only)"""
    if platform.system() == "Windows":
        # Windows doesn't support signal-based timeouts
        return prompt_func(*args, **kwargs)
    
    # Set up timeout
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        result = prompt_func(*args, **kwargs)
        signal.alarm(0)  # Cancel timeout
        return result
    except TimeoutError:
        signal.alarm(0)  # Cancel timeout
        click.echo(f"\n[WARNING] Prompt timed out after {timeout_seconds} seconds, using default")
        # Return default if available
        if 'default' in kwargs:
            return kwargs['default']
        return None
    finally:
        signal.signal(signal.SIGALRM, old_handler)


class DependencyChecker:
    """Check and install required dependencies"""
    
    def __init__(self):
        self.system = platform.system()
        self.missing_deps = []
        self.install_commands = {
            "Windows": {
                "node": "Download from https://nodejs.org/ or use winget install OpenJS.NodeJS",
                "python": "Download from https://python.org/ or use Microsoft Store",
                "uv": "powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"",
                "git": "Download from https://git-scm.com/ or use winget install Git.Git"
            },
            "Darwin": {  # macOS
                "node": "brew install node or download from https://nodejs.org/",
                "python": "brew install python or download from https://python.org/",
                "uv": "curl -LsSf https://astral.sh/uv/install.sh | sh",
                "git": "xcode-select --install or brew install git"
            },
            "Linux": {
                "node": "sudo apt install nodejs npm  # Ubuntu/Debian\nsudo dnf install nodejs npm  # Fedora",
                "python": "sudo apt install python3 python3-pip  # Ubuntu/Debian\nsudo dnf install python3 python3-pip  # Fedora",
                "uv": "curl -LsSf https://astral.sh/uv/install.sh | sh",
                "git": "sudo apt install git  # Ubuntu/Debian\nsudo dnf install git  # Fedora"
            }
        }
    
    def check_command(self, command: str) -> bool:
        """Check if a command is available in PATH"""
        return shutil.which(command) is not None
    
    def check_python_version(self) -> Tuple[bool, str]:
        """Check if Python version is 3.9+"""
        try:
            version = sys.version_info
            if version >= (3, 9):
                return True, f"{version.major}.{version.minor}.{version.micro}"
            else:
                return False, f"{version.major}.{version.minor}.{version.micro}"
        except Exception:
            return False, "unknown"
    
    def check_node_version(self) -> Tuple[bool, str]:
        """Check if Node.js version is 16+"""
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version_str = result.stdout.strip().lstrip('v')
                major_version = int(version_str.split('.')[0])
                if major_version >= 16:
                    return True, version_str
                else:
                    return False, version_str
            return False, "not found"
        except Exception:
            return False, "not found"
    
    def check_dependencies(self) -> Dict[str, Dict]:
        """Check all required dependencies"""
        deps = {}
        
        # Check Python
        python_ok, python_version = self.check_python_version()
        deps["python"] = {
            "available": python_ok,
            "version": python_version,
            "required": "3.9+",
            "install_cmd": self.install_commands[self.system].get("python", "")
        }
        
        # Check Node.js
        node_ok, node_version = self.check_node_version()
        deps["node"] = {
            "available": node_ok,
            "version": node_version,
            "required": "16+",
            "install_cmd": self.install_commands[self.system].get("node", "")
        }
        
        # Check other tools
        for tool in ["uv", "git"]:
            available = self.check_command(tool)
            deps[tool] = {
                "available": available,
                "version": "installed" if available else "not found",
                "required": "latest",
                "install_cmd": self.install_commands[self.system].get(tool, "")
            }
        
        return deps
    
    def install_mcp_servers(self) -> Dict[str, bool]:
        """Install common MCP servers via npm"""
        logger = logging.getLogger('claude_mcp_setup')
        servers = {
            "@modelcontextprotocol/server-filesystem": "File system operations",
            "mcp-server-sqlite-npx": "SQLite database access",
            "@modelcontextprotocol/server-brave-search": "Brave search integration",
            "@modelcontextprotocol/server-everything": "Everything search (Windows)"
        }
        
        logger.info(f"Installing {len(servers)} MCP servers")
        results = {}
        
        for server, description in servers.items():
            try:
                click.echo(f"[INFO] Installing {server} ({description})...")
                logger.info(f"Installing {server}")
                
                result = subprocess.run(
                    ["npm", "install", "-g", server],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                results[server] = result.returncode == 0
                
                if result.returncode == 0:
                    click.echo(f"[SUCCESS] {server} installed successfully")
                    logger.info(f"Successfully installed {server}")
                else:
                    click.echo(f"[ERROR] Failed to install {server}: {result.stderr[:100]}")
                    logger.error(f"Failed to install {server}. Return code: {result.returncode}")
                    logger.error(f"STDERR: {result.stderr}")
                    logger.error(f"STDOUT: {result.stdout}")
                    
            except subprocess.TimeoutExpired:
                click.echo(f"[ERROR] Timeout installing {server} (120s)")
                logger.error(f"Timeout installing {server} after 120 seconds")
                results[server] = False
            except Exception as e:
                click.echo(f"[ERROR] Error installing {server}: {e}")
                logger.error(f"Exception installing {server}: {e}")
                results[server] = False
        
        return results


class MCPServerPresets:
    """Predefined MCP server configurations"""
    
    @staticmethod
    def get_presets() -> Dict[str, Dict]:
        """Get available server presets"""
        return {
            "filesystem": {
                "name": "Filesystem Server",
                "description": "Access and manipulate files and directories",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem"],
                "env": {},
                "requires": ["node"],
                "setup_args": ["workspace_path"]
            },
            "sqlite": {
                "name": "SQLite Database Server",
                "description": "Query and manage SQLite databases",
                "command": "npx",
                "args": ["-y", "mcp-server-sqlite-npx"],
                "env": {},
                "requires": ["node"],
                "setup_args": ["database_path"]
            },
            "brave-search": {
                "name": "Brave Search Server",
                "description": "Search the web using Brave Search API",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-brave-search"],
                "env": {"BRAVE_API_KEY": ""},
                "requires": ["node"],
                "setup_args": ["api_key"]
            },
            "github": {
                "name": "GitHub Server",
                "description": "Access GitHub repositories and issues",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {"GITHUB_TOKEN": ""},
                "requires": ["node"],
                "setup_args": ["github_token"]
            },
            "python-example": {
                "name": "Python Example Server",
                "description": "Custom Python MCP server example",
                "command": "python",
                "args": ["-m", "claude_desktop_mcp.example_server"],
                "env": {"LOG_LEVEL": "INFO"},
                "requires": ["python"],
                "setup_args": []
            }
        }


class SetupWizard:
    """Interactive setup wizard"""
    
    def __init__(self):
        self.checker = DependencyChecker()
        self.config_manager = ClaudeDesktopConfigManager()
        self.presets = MCPServerPresets()
        self.logger = logging.getLogger('claude_mcp_setup')
    
    def welcome(self):
        """Display welcome message"""
        click.echo("Welcome to Claude Desktop MCP Playground Setup!")
        click.echo("=" * 50)
        click.echo()
        click.echo("This wizard will help you:")
        click.echo("  • Check and install required dependencies")
        click.echo("  • Set up common MCP servers")
        click.echo("  • Configure Claude Desktop for optimal use")
        click.echo()
    
    def check_dependencies_interactive(self) -> bool:
        """Interactive dependency checking"""
        click.echo("[INFO] Checking dependencies...")
        self.logger.info("Starting dependency check")
        click.echo()
        
        try:
            deps = self.checker.check_dependencies()
            self.logger.info(f"Dependency check completed: {deps}")
        except Exception as e:
            self.logger.error(f"Error during dependency check: {e}")
            click.echo(f"[ERROR] Dependency check failed: {e}")
            return False
        all_good = True
        self.logger.info("Processing dependency results...")
        
        for name, info in deps.items():
            status = "[OK]" if info["available"] else "[MISSING]"
            version_info = f"({info['version']})" if info["version"] != "not found" else ""
            click.echo(f"  {status} {name.title()} {version_info}")
            
            if not info["available"]:
                all_good = False
                click.echo(f"    Required: {info['required']}")
                click.echo(f"    Install: {info['install_cmd']}")
                click.echo()
        
        if not all_good:
            self.logger.info("Some dependencies missing, asking for install instructions")
            click.echo("[ERROR] Some dependencies are missing!")
            click.echo()
            if click.confirm("Would you like to see installation instructions?"):
                self.show_install_instructions(deps)
            return False
        else:
            self.logger.info("All dependencies satisfied")
            click.echo("[SUCCESS] All dependencies are available!")
            return True
    
    def show_install_instructions(self, deps: Dict):
        """Show detailed installation instructions"""
        click.echo("📋 Installation Instructions:")
        click.echo("=" * 30)
        
        for name, info in deps.items():
            if not info["available"]:
                click.echo(f"\n{name.title()}:")
                click.echo(f"  {info['install_cmd']}")
        
        click.echo("\nAfter installing dependencies, run 'pg setup' again.")
    
    def setup_mcp_servers(self):
        """Interactive MCP server setup"""
        click.echo("🔧 Setting up MCP servers...")
        click.echo()
        
        presets = self.presets.get_presets()
        selected_servers = {}
        
        # Show available presets
        click.echo("Available MCP servers:")
        for i, (key, preset) in enumerate(presets.items(), 1):
            click.echo(f"  {i}. {preset['name']} - {preset['description']}")
        
        click.echo(f"  {len(presets) + 1}. Skip server setup")
        click.echo()
        
        while True:
            try:
                choice = click.prompt(
                    "Select servers to install (comma-separated numbers, e.g., 1,2,3)",
                    type=str,
                    default=str(len(presets) + 1)
                )
                
                if choice.strip() == str(len(presets) + 1):
                    break
                
                choices = [int(x.strip()) for x in choice.split(",")]
                
                for choice_num in choices:
                    if 1 <= choice_num <= len(presets):
                        preset_key = list(presets.keys())[choice_num - 1]
                        preset = presets[preset_key]
                        
                        click.echo(f"\n⚙️ Configuring {preset['name']}...")
                        server_config = self.configure_server(preset_key, preset)
                        if server_config:
                            selected_servers[preset_key] = server_config
                
                break
                
            except (ValueError, IndexError):
                click.echo("Invalid selection. Please try again.")
        
        return selected_servers
    
    def configure_server(self, key: str, preset: Dict) -> Optional[Dict]:
        """Configure a specific server"""
        config = {
            "command": preset["command"],
            "args": preset["args"].copy(),
            "env": preset["env"].copy(),
            "enabled": True
        }
        
        # Handle special setup arguments
        if "setup_args" in preset:
            for arg_type in preset["setup_args"]:
                if arg_type == "workspace_path":
                    default_path = str(Path.home() / "workspace")
                    path = click.prompt(
                        f"Workspace path for {preset['name']}",
                        default=default_path,
                        type=click.Path()
                    )
                    config["args"].append(path)
                
                elif arg_type == "database_path":
                    default_path = str(Path.home() / "documents" / "database.db")
                    path = click.prompt(
                        f"SQLite database path",
                        default=default_path,
                        type=click.Path()
                    )
                    config["args"].append(path)
                
                elif arg_type == "api_key":
                    api_key = click.prompt(
                        f"API key for {preset['name']} (leave empty to skip)",
                        default="",
                        hide_input=True
                    )
                    if api_key:
                        if "BRAVE_API_KEY" in config["env"]:
                            config["env"]["BRAVE_API_KEY"] = api_key
                    else:
                        click.echo(f"Skipping {preset['name']} - no API key provided")
                        return None
                
                elif arg_type == "github_token":
                    token = click.prompt(
                        f"GitHub token for {preset['name']} (leave empty to skip)",
                        default="",
                        hide_input=True
                    )
                    if token:
                        config["env"]["GITHUB_TOKEN"] = token
                    else:
                        click.echo(f"Skipping {preset['name']} - no token provided")
                        return None
        
        return config
    
    def install_servers(self) -> bool:
        """Install MCP server packages"""
        self.logger.info("Starting MCP server installation process")
        
        try:
            # Simple confirmation prompt with fallback
            self.logger.info("About to show confirmation prompt")
            
            # Check if we're in an interactive environment
            import sys
            if not sys.stdin.isatty():
                self.logger.info("Non-interactive environment detected, defaulting to yes")
                response = True
            else:
                try:
                    import select
                    import time
                    
                    click.echo("Install common MCP server packages via npm? [Y/n]: ", nl=False)
                    
                    # Try to read input with timeout (Unix only)
                    if hasattr(select, 'select'):
                        ready, _, _ = select.select([sys.stdin], [], [], 10.0)
                        if ready:
                            user_input = sys.stdin.readline().strip().lower()
                            response = user_input in ['', 'y', 'yes']
                            self.logger.info(f"User input: '{user_input}', interpreted as: {response}")
                        else:
                            self.logger.info("Prompt timeout (10s), defaulting to yes")
                            response = True
                    else:
                        # Windows fallback - just use input() 
                        user_input = input().strip().lower()
                        response = user_input in ['', 'y', 'yes']
                        self.logger.info(f"User input: '{user_input}', interpreted as: {response}")
                        
                except (EOFError, KeyboardInterrupt, OSError):
                    self.logger.info("Prompt interrupted or failed, defaulting to yes")
                    response = True
            
            if not response:
                self.logger.info("User declined MCP server installation")
                return True
            
            click.echo("[INFO] Installing MCP server packages...")
            self.logger.info("Installing MCP server packages")
            results = self.checker.install_mcp_servers()
        except KeyboardInterrupt:
            self.logger.warning("Installation interrupted by user")
            click.echo("\n[WARNING] Installation interrupted")
            return False
        except Exception as e:
            self.logger.error(f"Error during server installation: {e}")
            click.echo(f"[ERROR] Installation failed: {e}")
            return False
        
        success_count = sum(results.values())
        total_count = len(results)
        
        click.echo(f"\n📊 Installation summary: {success_count}/{total_count} packages installed successfully")
        
        if success_count < total_count:
            click.echo("[WARNING] Some packages failed to install. You can install them manually later.")
        
        return success_count > 0
    
    def apply_configuration(self, servers: Dict[str, Dict]):
        """Apply server configuration to Claude Desktop"""
        if not servers:
            click.echo("No servers configured.")
            return
        
        click.echo(f"\n💾 Applying configuration for {len(servers)} server(s)...")
        
        # Save simplified configuration
        save_simplified_config(servers, "claude_desktop_simplified.json")
        click.echo("[SUCCESS] Saved simplified configuration to claude_desktop_simplified.json")
        
        # Apply to Claude Desktop
        claude_config = self.config_manager.export_from_simplified(servers)
        self.config_manager.save_config(claude_config)
        click.echo("[SUCCESS] Applied configuration to Claude Desktop")
        
        click.echo("\n[SUCCESS] Setup complete!")
        click.echo("\nNext steps:")
        click.echo("  1. Restart Claude Desktop to load the new configuration")
        click.echo("  2. Try using the new MCP servers in your conversations")
        click.echo("  3. Use 'pg config show' to view your configuration")
        click.echo("  4. Edit 'claude_desktop_simplified.json' to modify settings")
        
    def run_full_setup(self):
        """Run the complete setup wizard"""
        self.logger.info("Starting welcome screen")
        self.welcome()
        self.logger.info("Welcome screen completed")
        
        # Check dependencies
        self.logger.info("Starting dependency check")
        deps_ok = self.check_dependencies_interactive()
        self.logger.info(f"Dependency check completed: {deps_ok}")
        if not deps_ok:
            self.logger.warning("Dependencies not satisfied, exiting setup")
            return
        
        # Install MCP server packages
        self.logger.info("About to call install_servers method")
        self.install_servers()
        self.logger.info("install_servers method completed")
        
        # Configure servers
        servers = self.setup_mcp_servers()
        
        # Apply configuration
        self.apply_configuration(servers)


def create_example_server():
    """Create an example Python MCP server"""
    example_server_content = '''"""Example Python MCP Server

A simple example server demonstrating MCP protocol implementation.
"""

import json
import sys
from typing import Any, Dict

def create_server_response(id: str, result: Any = None, error: str = None) -> Dict:
    """Create a JSON-RPC response"""
    response = {"jsonrpc": "2.0", "id": id}
    if error:
        response["error"] = {"code": -1, "message": error}
    else:
        response["result"] = result
    return response

def handle_initialize(params: Dict) -> Dict:
    """Handle initialize request"""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "example-server",
            "version": "0.1.0"
        }
    }

def handle_tools_list() -> Dict:
    """Handle tools/list request"""
    return {
        "tools": [
            {
                "name": "echo",
                "description": "Echo back the input text",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to echo back"
                        }
                    },
                    "required": ["text"]
                }
            }
        ]
    }

def handle_tools_call(params: Dict) -> Dict:
    """Handle tools/call request"""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    if tool_name == "echo":
        text = arguments.get("text", "")
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Echo: {text}"
                }
            ]
        }
    else:
        raise ValueError(f"Unknown tool: {tool_name}")

def main():
    """Main server loop"""
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            method = request.get("method")
            params = request.get("params", {})
            id = request.get("id")
            
            if method == "initialize":
                result = handle_initialize(params)
                response = create_server_response(id, result)
            elif method == "tools/list":
                result = handle_tools_list()
                response = create_server_response(id, result)
            elif method == "tools/call":
                result = handle_tools_call(params)
                response = create_server_response(id, result)
            else:
                response = create_server_response(id, error=f"Unknown method: {method}")
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except Exception as e:
            error_response = create_server_response(
                request.get("id") if "request" in locals() else None,
                error=str(e)
            )
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
'''
    
    # Create example server file
    example_server_path = Path(__file__).parent / "example_server.py"
    with open(example_server_path, 'w') as f:
        f.write(example_server_content)
    
    return str(example_server_path)


# CLI command integration
@click.command()
@click.option('--quick', is_flag=True, help='Quick setup with defaults')
@click.option('--deps-only', is_flag=True, help='Only check dependencies')
def setup(quick: bool, deps_only: bool):
    """Interactive setup wizard for Claude Desktop MCP Playground"""
    
    # Setup logging first
    logger = setup_logging()
    logger.info(f"Setup wizard called with quick={quick}, deps_only={deps_only}")
    
    # Create example server
    create_example_server()
    
    try:
        wizard = SetupWizard()
        logger.info("SetupWizard initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize SetupWizard: {e}")
        click.echo(f"[ERROR] Setup initialization failed: {e}")
        return
    
    if deps_only:
        wizard.check_dependencies_interactive()
        return
    
    if quick:
        click.echo("[INFO] Quick setup mode...")
        logger.info("Starting quick setup mode")
        
        try:
            deps_ok = wizard.check_dependencies_interactive()
            logger.info(f"Dependency check result: {deps_ok}")
            
            if deps_ok:
                logger.info("Dependencies OK, installing servers")
                install_success = wizard.install_servers()
                logger.info(f"Server installation result: {install_success}")
                
                if install_success:
                    # Apply minimal configuration
                    basic_servers = {
                        "filesystem": {
                            "command": "npx",
                            "args": ["-y", "@modelcontextprotocol/server-filesystem", str(Path.home() / "workspace")],
                            "env": {},
                            "enabled": True
                        }
                    }
                    logger.info("Applying basic configuration")
                    wizard.apply_configuration(basic_servers)
                    logger.info("Quick setup completed successfully")
            else:
                logger.warning("Dependencies not satisfied, skipping server installation")
                
        except Exception as e:
            logger.error(f"Error during quick setup: {e}")
            click.echo(f"[ERROR] Quick setup failed: {e}")
    else:
        logger.info("Starting full setup mode")
        try:
            wizard.run_full_setup()
            logger.info("Full setup completed")
        except Exception as e:
            logger.error(f"Error during full setup: {e}")
            click.echo(f"[ERROR] Full setup failed: {e}")


if __name__ == "__main__":
    setup()