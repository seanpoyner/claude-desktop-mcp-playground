#!/usr/bin/env python3
"""
Standalone script to import Claude Desktop configuration and save to simplified format.

This script can be run independently to quickly import your current Claude Desktop
MCP server configuration and save it in a simplified JSON format for easy editing.
"""

import json
import sys
from pathlib import Path

from claude_desktop_mcp.config_manager import ClaudeDesktopConfigManager, save_simplified_config


def main():
    """Import Claude Desktop config and save to simplified format."""
    print("Claude Desktop Configuration Importer")
    print("=" * 40)
    
    manager = ClaudeDesktopConfigManager()
    
    # Check if config exists
    print(f"Looking for config at: {manager.config_path}")
    
    if not manager.config_exists():
        print("❌ Claude Desktop config file not found.")
        print("\nThis is normal if you haven't configured any MCP servers yet.")
        print(f"Expected location: {manager.config_path}")
        return 1
    
    try:
        # Import to simplified format
        print("📥 Importing configuration...")
        simplified = manager.import_to_simplified()
        
        # Save simplified config
        output_file = "claude_desktop_simplified.json"
        save_simplified_config(simplified, output_file)
        
        print(f"✅ Successfully imported {len(simplified)} MCP server(s)")
        print(f"📄 Saved simplified configuration to: {output_file}")
        
        if simplified:
            print("\n📋 Configured servers:")
            for name, config in simplified.items():
                status = "✅ enabled" if config.get("enabled", True) else "❌ disabled"
                command = config.get("command", "no command")
                print(f"  • {name} ({command}) - {status}")
        else:
            print("\n📝 No MCP servers are currently configured.")
        
        # Show simplified structure
        print(f"\n📖 Simplified configuration structure:")
        print(json.dumps(simplified, indent=2))
        
        print(f"\n💡 You can now edit '{output_file}' and use the CLI to apply changes:")
        print("   claude-desktop-mcp config apply claude_desktop_simplified.json")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error importing configuration: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())