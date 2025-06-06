#!/usr/bin/env python3
"""
PG CLI MCP Server Launcher
Automatically installs dependencies and launches the server
"""

import subprocess
import sys
import os
from pathlib import Path

def install_mcp_dependency():
    """Install the MCP dependency if not available"""
    try:
        import mcp.types
        print("✓ MCP dependency already available", file=sys.stderr)
        return True
    except ImportError:
        print("⚠ MCP dependency not found, installing...", file=sys.stderr)
        
        # Try different installation methods
        install_commands = [
            [sys.executable, "-m", "pip", "install", "mcp>=1.0.0"],
            [sys.executable, "-m", "pip", "install", "--user", "mcp>=1.0.0"],
            [sys.executable, "-m", "pip", "install", "--break-system-packages", "mcp>=1.0.0"]
        ]
        
        for cmd in install_commands:
            try:
                print(f"Trying: {' '.join(cmd)}", file=sys.stderr)
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    print("✓ MCP dependency installed successfully", file=sys.stderr)
                    
                    # Force Python to refresh the module search path
                    import importlib
                    import site
                    importlib.invalidate_caches()
                    site.main()
                    
                    # Test import again
                    try:
                        import mcp.types
                        print("✓ MCP dependency verified", file=sys.stderr)
                        return True
                    except ImportError:
                        print("⚠ MCP installed but still not importable, trying next method...", file=sys.stderr)
                        continue
                else:
                    print(f"Command failed: {result.stderr}", file=sys.stderr)
            except Exception as e:
                print(f"Installation attempt failed: {e}", file=sys.stderr)
                continue
        
        print("✗ Failed to install MCP dependency", file=sys.stderr)
        print("Please manually run: pip install mcp>=1.0.0", file=sys.stderr)
        return False

def main():
    """Main launcher function"""
    print("🚀 PG CLI MCP Server Launcher", file=sys.stderr)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("✗ Python 3.9+ required", file=sys.stderr)
        sys.exit(1)
    
    # Install MCP dependency if needed
    if not install_mcp_dependency():
        sys.exit(1)
    
    # Import and run the actual server
    try:
        # Add current directory to path
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        # Import the main server module
        from server import main as server_main
        import asyncio
        
        print("✓ Starting PG CLI MCP Server...", file=sys.stderr)
        asyncio.run(server_main())
        
    except ImportError as e:
        print(f"✗ Failed to import server module: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Server error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()