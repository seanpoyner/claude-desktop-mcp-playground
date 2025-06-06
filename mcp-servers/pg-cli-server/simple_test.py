#!/usr/bin/env python3
"""
Simple test to validate the PG CLI MCP Server structure
"""

import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_server_import():
    """Test that the server can be imported without errors"""
    try:
        from server import PGCLIServer
        print("✓ Server module imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import server: {e}")
        return False

def test_server_initialization():
    """Test that the server can be initialized"""
    try:
        from server import PGCLIServer
        server = PGCLIServer()
        print("✓ Server initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize server: {e}")
        return False

def test_mcp_dependencies():
    """Test that MCP dependencies are available"""
    try:
        import mcp.types as types
        import mcp.server
        from mcp.server.models import InitializationOptions
        from mcp.server.stdio import stdio_server
        print("✓ All MCP dependencies available")
        return True
    except Exception as e:
        print(f"✗ MCP dependencies missing: {e}")
        return False

def test_pg_command():
    """Test that pg command is available"""
    import subprocess
    try:
        result = subprocess.run(["pg", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ pg command available (version: {result.stdout.strip()})")
            return True
        else:
            print("✗ pg command not working")
            return False
    except FileNotFoundError:
        print("✗ pg command not found")
        return False
    except Exception as e:
        print(f"✗ Error checking pg command: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing PG CLI MCP Server Components...\n")
    
    tests = [
        ("MCP Dependencies", test_mcp_dependencies),
        ("Server Import", test_server_import),
        ("Server Initialization", test_server_initialization),
        ("PG Command", test_pg_command),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        success = test_func()
        results.append(success)
        print()
    
    total_tests = len(tests)
    passed_tests = sum(results)
    
    print(f"📊 Test Results: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Server should work correctly in Claude Desktop.")
    else:
        print("⚠️  Some tests failed. Server may not work properly.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)