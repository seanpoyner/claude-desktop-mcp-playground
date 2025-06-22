#!/usr/bin/env python3
"""
Launcher for Registry Manager MCP Server

This script provides a robust way to launch the registry manager server
with proper error handling and dependency management.
"""

import asyncio
import sys
import subprocess
from pathlib import Path

def check_and_install_dependencies():
    """Check if MCP is installed and install if needed."""
    try:
        import mcp
        print("✓ MCP library found", file=sys.stderr)
        return True
    except ImportError:
        print("Installing MCP dependency...", file=sys.stderr)
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "mcp>=1.0.0"
            ], check=True, capture_output=True)
            print("✓ MCP library installed", file=sys.stderr)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install MCP: {e}", file=sys.stderr)
            return False

def main():
    """Main launcher function."""
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    
    # Check dependencies
    if not check_and_install_dependencies():
        sys.exit(1)
    
    try:
        # Import and run the server
        from server import main as server_main
        asyncio.run(server_main())
    except KeyboardInterrupt:
        print("Server stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
