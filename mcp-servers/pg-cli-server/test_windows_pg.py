#!/usr/bin/env python3
"""
Test Windows pg.bat execution
"""

import subprocess
import sys
from pathlib import Path

def test_windows_pg():
    """Test if the Windows pg.bat works"""
    
    # Test the Windows batch file
    pg_bat_path = "C:\\Users\\seanp\\claude-desktop-mcp-playground\\mcp-server-manager-windows-complete\\pg.bat"
    
    print(f"Testing Windows pg.bat at: {pg_bat_path}")
    
    try:
        # Convert Windows path to WSL path for testing
        wsl_path = "/mnt/c/Users/seanp/claude-desktop-mcp-playground/mcp-server-manager-windows-complete/pg.bat"
        
        # Check if file exists
        if not Path(wsl_path).exists():
            print(f"✗ File not found: {wsl_path}")
            return False
            
        print(f"✓ File exists: {wsl_path}")
        
        # Test execution (in WSL, we can test the batch file logic)
        # The batch file runs: python -m claude_desktop_mcp.cli
        test_cmd = ["python", "-m", "claude_desktop_mcp.cli", "--version"]
        
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10, 
                              cwd="/mnt/c/Users/seanp/claude-desktop-mcp-playground")
        
        if result.returncode == 0:
            print(f"✓ Command works: {result.stdout.strip()}")
            return True
        else:
            print(f"✗ Command failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Windows pg.bat compatibility...\n")
    success = test_windows_pg()
    print(f"\n{'🎉 Success!' if success else '❌ Failed'}")
    sys.exit(0 if success else 1)