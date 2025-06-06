#!/usr/bin/env python3
"""
Test PG command execution in the MCP server
"""

import sys
import asyncio
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

async def test_pg_execution():
    """Test executing pg commands through the server"""
    try:
        from server import PGCLIServer
        
        server = PGCLIServer()
        print("✓ Server initialized")
        
        # Test pg_config_search
        print("\n🔍 Testing pg_config_search...")
        result = await server._execute_pg_command("pg_config_search", {"query": "filesystem"})
        print(f"Result: {result[:200]}{'...' if len(result) > 200 else ''}")
        
        # Test pg_config_show
        print("\n📋 Testing pg_config_show...")
        result = await server._execute_pg_command("pg_config_show", {})
        print(f"Result: {result[:200]}{'...' if len(result) > 200 else ''}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🧪 Testing PG Command Execution...\n")
    
    success = await test_pg_execution()
    
    if success:
        print("\n🎉 PG command execution working correctly!")
    else:
        print("\n❌ PG command execution failed")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)