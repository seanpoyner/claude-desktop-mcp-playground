"""Claude Desktop Configuration Manager

Handles importing, exporting, and managing Claude Desktop MCP server configurations.
"""

import json
import os
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional


class ClaudeDesktopConfigManager:
    """Manages Claude Desktop configuration files across platforms."""
    
    def __init__(self):
        self.config_path = self._get_config_path()
        self.servers_dir = self._get_servers_directory()
    
    def _is_wsl(self) -> bool:
        """Check if we're running in WSL."""
        system = platform.system()
        if system == "Linux":
            try:
                with open("/proc/version", "r") as f:
                    version_info = f.read().lower()
                    if "microsoft" in version_info or "wsl" in version_info:
                        return True
            except:
                pass
        return False
    
    def _get_config_path(self) -> Path:
        """Get the Claude Desktop config file path for the current platform."""
        system = platform.system()
        
        # Check if we're running in WSL
        is_wsl = False
        if system == "Linux":
            # Check for WSL by looking for Microsoft or WSL in /proc/version
            try:
                with open("/proc/version", "r") as f:
                    version_info = f.read().lower()
                    if "microsoft" in version_info or "wsl" in version_info:
                        is_wsl = True
            except:
                pass
        
        if system == "Darwin":  # macOS
            base_path = Path.home() / "Library" / "Application Support" / "Claude"
        elif system == "Windows" or is_wsl:
            # For Windows or WSL, use the Windows path
            if is_wsl:
                # In WSL, we need to use the Windows user profile path
                # Try to find the Windows username by checking environment or existing paths
                windows_appdata = None
                
                # Method 1: Check if APPDATA is set in WSL (sometimes it is)
                if "APPDATA" in os.environ:
                    windows_appdata = os.environ["APPDATA"].replace("C:\\", "/mnt/c/").replace("\\", "/")
                
                # Method 2: Try to find the actual Windows user directory
                if not windows_appdata:
                    # Look for the claude config in common Windows user directories
                    users_dir = Path("/mnt/c/Users")
                    if users_dir.exists():
                        for user_dir in users_dir.iterdir():
                            if user_dir.is_dir() and user_dir.name not in ["Default", "Public", "WsiAccount", "defaultuser0"]:
                                potential_config = user_dir / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
                                if potential_config.exists():
                                    windows_appdata = str(user_dir / "AppData" / "Roaming")
                                    break
                
                # Method 3: Fallback to common pattern
                if not windows_appdata:
                    # Try the most common pattern
                    windows_appdata = "/mnt/c/Users/seanp/AppData/Roaming"
                
                base_path = Path(windows_appdata) / "Claude"
            else:
                appdata = os.environ.get("APPDATA")
                if not appdata:
                    # Fallback to typical Windows path if APPDATA is not set
                    appdata = f"C:\\Users\\{os.environ.get('USERNAME', 'seanp')}\\AppData\\Roaming"
                base_path = Path(appdata) / "Claude"
        else:  # Linux (non-WSL) and others
            # IMPORTANT: Double-check we're not in WSL
            if is_wsl:
                # This should never happen, but just in case
                windows_appdata = "/mnt/c/Users/seanp/AppData/Roaming"
                base_path = Path(windows_appdata) / "Claude"
            else:
                base_path = Path.home() / ".config" / "Claude"
        
        return base_path / "claude_desktop_config.json"
    
    def _get_servers_directory(self) -> Path:
        """Get the directory where MCP servers are installed."""
        system = platform.system()
        
        # Check if we're running in WSL
        is_wsl = False
        if system == "Linux":
            # Check for WSL by looking for Microsoft or WSL in /proc/version
            try:
                with open("/proc/version", "r") as f:
                    version_info = f.read().lower()
                    if "microsoft" in version_info or "wsl" in version_info:
                        is_wsl = True
            except:
                pass
        
        if system == "Darwin":  # macOS
            base_path = Path.home() / "Library" / "Application Support" / "Claude" / "mcp_servers"
        elif system == "Windows" or is_wsl:
            # For Windows or WSL, use the Windows path
            if is_wsl:
                # In WSL, we need to use the Windows user profile path
                # Try to find the Windows username by checking environment or existing paths
                windows_appdata = None
                
                # Method 1: Check if APPDATA is set in WSL (sometimes it is)
                if "APPDATA" in os.environ:
                    windows_appdata = os.environ["APPDATA"].replace("C:\\", "/mnt/c/").replace("\\", "/")
                
                # Method 2: Try to find the actual Windows user directory
                if not windows_appdata:
                    # Look for the claude config in common Windows user directories
                    users_dir = Path("/mnt/c/Users")
                    if users_dir.exists():
                        for user_dir in users_dir.iterdir():
                            if user_dir.is_dir() and user_dir.name not in ["Default", "Public", "WsiAccount", "defaultuser0"]:
                                potential_config = user_dir / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
                                if potential_config.exists():
                                    windows_appdata = str(user_dir / "AppData" / "Roaming")
                                    break
                
                # Method 3: Fallback to common pattern
                if not windows_appdata:
                    # Try the most common pattern
                    windows_appdata = "/mnt/c/Users/seanp/AppData/Roaming"
                
                base_path = Path(windows_appdata) / "Claude" / "mcp_servers"
            else:
                appdata = os.environ.get("APPDATA")
                if not appdata:
                    # Fallback to typical Windows path if APPDATA is not set
                    appdata = f"C:\\Users\\{os.environ.get('USERNAME', 'seanp')}\\AppData\\Roaming"
                base_path = Path(appdata) / "Claude" / "mcp_servers"
        else:  # Linux (non-WSL) and others
            # IMPORTANT: Double-check we're not in WSL
            if is_wsl:
                # This should never happen, but just in case
                windows_appdata = "/mnt/c/Users/seanp/AppData/Roaming"
                base_path = Path(windows_appdata) / "Claude" / "mcp_servers"
            else:
                base_path = Path.home() / ".config" / "Claude" / "mcp_servers"
        
        return base_path
    
    def config_exists(self) -> bool:
        """Check if Claude Desktop config file exists."""
        return self.config_path.exists()
    
    def load_config(self) -> Dict[str, Any]:
        """Load current Claude Desktop configuration."""
        if not self.config_exists():
            return {"mcpServers": {}}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise RuntimeError(f"Failed to load Claude Desktop config: {e}")
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to Claude Desktop config file."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"save_config called - self.config_path: {self.config_path}")
        logger.info(f"save_config called - config path exists: {self.config_path.exists()}")
        
        # DEBUG: Print to stderr to see in pg-cli-server logs
        import sys
        print(f"[CONFIG_MANAGER] Saving to: {self.config_path}", file=sys.stderr)
        
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved config to: {self.config_path}")
            print(f"[CONFIG_MANAGER] Successfully saved to: {self.config_path}", file=sys.stderr)
        except IOError as e:
            raise RuntimeError(f"Failed to save Claude Desktop config: {e}")
    
    def import_to_simplified(self) -> Dict[str, Dict[str, Any]]:
        """Import Claude Desktop config and convert to simplified k-v structure."""
        config = self.load_config()
        simplified = {}
        
        mcp_servers = config.get("mcpServers", {})
        for server_name, server_config in mcp_servers.items():
            simplified[server_name] = {
                "command": server_config.get("command", ""),
                "args": server_config.get("args", []),
                "env": server_config.get("env", {}),
                "enabled": True  # Add enabled flag for easy management
            }
        
        return simplified
    
    def export_from_simplified(self, simplified_config: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Convert simplified k-v structure back to Claude Desktop format."""
        mcp_servers = {}
        
        for server_name, server_data in simplified_config.items():
            if server_data.get("enabled", True):  # Only include enabled servers
                mcp_servers[server_name] = {
                    "command": server_data.get("command", ""),
                    "args": server_data.get("args", []),
                    "env": server_data.get("env", {})
                }
        
        return {"mcpServers": mcp_servers}
    
    def add_server(self, name: str, command: str, args: Optional[list] = None, 
                  env: Optional[Dict[str, str]] = None) -> None:
        """Add a new MCP server to the configuration."""
        config = self.load_config()
        
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        config["mcpServers"][name] = {
            "command": command,
            "args": args or [],
            "env": env or {}
        }
        
        self.save_config(config)
    
    def remove_server(self, name: str) -> bool:
        """Remove an MCP server from the configuration."""
        config = self.load_config()
        
        if "mcpServers" not in config or name not in config["mcpServers"]:
            return False
        
        del config["mcpServers"][name]
        self.save_config(config)
        return True
    
    def list_servers(self) -> Dict[str, Dict[str, Any]]:
        """List all configured MCP servers."""
        config = self.load_config()
        return config.get("mcpServers", {})
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate the current Claude Desktop configuration."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        if not self.config_exists():
            validation_result["warnings"].append("Claude Desktop config file does not exist")
            return validation_result
        
        try:
            config = self.load_config()
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Failed to load config: {e}")
            return validation_result
        
        # Validate structure
        if "mcpServers" not in config:
            validation_result["warnings"].append("No 'mcpServers' section found")
        else:
            servers = config["mcpServers"]
            for server_name, server_config in servers.items():
                if not isinstance(server_config, dict):
                    validation_result["errors"].append(f"Server '{server_name}' config is not a dictionary")
                    validation_result["valid"] = False
                    continue
                
                if "command" not in server_config:
                    validation_result["errors"].append(f"Server '{server_name}' missing 'command' field")
                    validation_result["valid"] = False
                
                # Check if command exists (basic validation)
                command = server_config.get("command", "")
                if command and not Path(command).exists() and not any(
                    Path(p) / command for p in os.environ.get("PATH", "").split(os.pathsep) 
                    if (Path(p) / command).exists()
                ):
                    validation_result["warnings"].append(f"Command '{command}' for server '{server_name}' may not exist")
        
        return validation_result
    
    def install_git_server(self, server_id: str, git_url: str, build_commands: list = None) -> Path:
        """Install a git-based MCP server."""
        # Create servers directory if it doesn't exist
        self.servers_dir.mkdir(parents=True, exist_ok=True)
        
        # Define installation path
        server_path = self.servers_dir / server_id
        
        # Remove existing installation if it exists
        if server_path.exists():
            shutil.rmtree(server_path)
        
        try:
            # Clone the repository
            print(f"Cloning {git_url}...")
            subprocess.run(
                ["git", "clone", git_url, str(server_path)],
                check=True,
                capture_output=True,
                text=True
            )
            
            # Run build commands if provided
            if build_commands:
                original_cwd = os.getcwd()
                try:
                    os.chdir(server_path)
                    for command in build_commands:
                        print(f"Running: {' '.join(command) if isinstance(command, list) else command}")
                        subprocess.run(command, check=True, shell=True if isinstance(command, str) else False)
                finally:
                    os.chdir(original_cwd)
            
            return server_path
            
        except subprocess.CalledProcessError as e:
            # Clean up on failure
            if server_path.exists():
                shutil.rmtree(server_path)
            raise RuntimeError(f"Failed to install git server: {e}")
    
    def get_git_server_executable(self, server_id: str, executable_path: str) -> Optional[Path]:
        """Get the full path to a git server's executable."""
        server_path = self.servers_dir / server_id
        if not server_path.exists():
            return None
        
        full_executable_path = server_path / executable_path
        if full_executable_path.exists():
            return full_executable_path
        
        return None
    
    def is_git_server_installed(self, server_id: str) -> bool:
        """Check if a git server is already installed."""
        server_path = self.servers_dir / server_id
        return server_path.exists() and server_path.is_dir()


def save_simplified_config(config: Dict[str, Dict[str, Any]], filepath: str = "claude_desktop_simplified.json") -> None:
    """Save simplified configuration to a JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def load_simplified_config(filepath: str = "claude_desktop_simplified.json") -> Dict[str, Dict[str, Any]]:
    """Load simplified configuration from a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        raise RuntimeError(f"Failed to load simplified config: {e}")