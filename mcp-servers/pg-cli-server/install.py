#!/usr/bin/env python3
"""
Installation script for PG CLI MCP Server
Handles dependency installation and path setup
"""

import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    try:
        # Try to install mcp using pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp>=1.0.0"])
        print("✓ MCP dependency installed successfully")
        return True
    except subprocess.CalledProcessError:
        try:
            # Try with --user flag
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "mcp>=1.0.0"])
            print("✓ MCP dependency installed successfully (user install)")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install MCP dependency")
            print("Please run: pip install mcp>=1.0.0")
            return False

def check_pg_command():
    """Check if pg command is available"""
    try:
        result = subprocess.run(["pg", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ pg command found (version: {result.stdout.strip()})")
            return True
        else:
            print("✗ pg command not working properly")
            return False
    except FileNotFoundError:
        print("✗ pg command not found in PATH")
        print("Please install Claude Desktop MCP Playground first")
        return False

def main():
    """Main installation function"""
    print("🚀 Installing PG CLI MCP Server...\n")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("✗ Python 3.9+ required")
        return False
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check pg command
    if not check_pg_command():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Test server import
    try:
        current_dir = Path(__file__).parent
        server_path = current_dir / "server.py"
        
        # Add current directory to Python path for testing
        sys.path.insert(0, str(current_dir))
        
        # Try to import required modules
        import mcp.types
        import mcp.server
        print("✓ MCP modules available")
        
        print(f"\n✅ Installation complete!")
        print(f"Server path: {server_path}")
        print(f"\nAdd this to your Claude Desktop configuration:")
        print(f'"pg-cli-server": {{')
        print(f'  "command": "python",')
        print(f'  "args": ["{server_path}"]')
        print(f'}}')
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)