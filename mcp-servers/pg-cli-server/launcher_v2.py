#!/usr/bin/env python3
"""
PG CLI MCP Server Launcher v2
More robust dependency handling with process restart if needed
"""

import subprocess
import sys
import os
from pathlib import Path

def check_mcp_available():
    """Check if MCP is available for import"""
    try:
        import mcp.types
        return True
    except ImportError:
        return False

def install_mcp_dependency():
    """Install the MCP dependency"""
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
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print("✓ MCP dependency installed successfully", file=sys.stderr)
                return True
            else:
                print(f"Command failed with exit code {result.returncode}", file=sys.stderr)
                if result.stderr:
                    print(f"Error: {result.stderr[:200]}", file=sys.stderr)
        except Exception as e:
            print(f"Installation attempt failed: {e}", file=sys.stderr)
            continue
    
    print("✗ Failed to install MCP dependency", file=sys.stderr)
    return False

def main():
    """Main launcher function"""
    print("🚀 PG CLI MCP Server Launcher v2", file=sys.stderr)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("✗ Python 3.9+ required", file=sys.stderr)
        sys.exit(1)
    
    # Check if we're in a restart scenario (MCP was just installed)
    restart_flag = "--restart-after-install" in sys.argv
    
    if not check_mcp_available():
        if restart_flag:
            print("✗ MCP still not available after installation. Please install manually: pip install mcp>=1.0.0", file=sys.stderr)
            sys.exit(1)
        
        # Try to install MCP
        if not install_mcp_dependency():
            sys.exit(1)
        
        # Restart the process to ensure clean import
        print("🔄 Restarting with clean environment...", file=sys.stderr)
        current_script = Path(__file__).resolve()
        restart_cmd = [sys.executable, str(current_script), "--restart-after-install"]
        os.execv(sys.executable, restart_cmd)
    
    print("✓ MCP dependency available", file=sys.stderr)
    
    # Now we can safely import and run the server
    try:
        # Add current directory to path
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        # Import the main server module
        print("✓ Importing server module...", file=sys.stderr)
        from server import main as server_main
        import asyncio
        
        print("✓ Starting PG CLI MCP Server...", file=sys.stderr)
        asyncio.run(server_main())
        
    except ImportError as e:
        print(f"✗ Failed to import server module: {e}", file=sys.stderr)
        print("Make sure server.py is in the same directory", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Server error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()