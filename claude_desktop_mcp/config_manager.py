"""Claude Desktop Configuration Manager

Handles importing, exporting, and managing Claude Desktop MCP server configurations.
"""

import json
import os
import platform
from pathlib import Path
from typing import Dict, Any, Optional


class ClaudeDesktopConfigManager:
    """Manages Claude Desktop configuration files across platforms."""
    
    def __init__(self):
        self.config_path = self._get_config_path()
    
    def _get_config_path(self) -> Path:
        """Get the Claude Desktop config file path for the current platform."""
        system = platform.system()
        
        if system == "Darwin":  # macOS
            base_path = Path.home() / "Library" / "Application Support" / "Claude"
        elif system == "Windows":
            base_path = Path(os.environ.get("APPDATA", "")) / "Claude"
        else:  # Linux and others
            base_path = Path.home() / ".config" / "Claude"
        
        return base_path / "claude_desktop_config.json"
    
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
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
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