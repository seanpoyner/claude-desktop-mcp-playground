#!/usr/bin/env python3
"""
Launcher for Documentation Analyzer MCP Server
Handles dependency checks and starts the server
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_and_install_dependencies():
    """Check and install required dependencies."""
    required_packages = {
        'mcp': 'mcp>=0.1.0',
        'aiohttp': 'aiohttp>=3.8.0'
    }
    
    missing_packages = []
    for package, spec in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(spec)
    
    if missing_packages:
        print("Installing missing dependencies...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--quiet", *missing_packages
        ])
        print("Dependencies installed successfully!")

def main():
    """Main launcher function."""
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check dependencies
    try:
        check_and_install_dependencies()
    except Exception as e:
        print(f"Error installing dependencies: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run the server
    try:
        from server import main as server_main
        import asyncio
        asyncio.run(server_main())
    except KeyboardInterrupt:
        print("\nShutting down Documentation Analyzer server...")
    except Exception as e:
        print(f"Error running server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
