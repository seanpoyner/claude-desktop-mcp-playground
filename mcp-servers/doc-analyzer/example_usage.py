#!/usr/bin/env python3
"""
Example: Using Documentation Analyzer with Registry Manager
This script demonstrates the workflow of analyzing documentation and registering servers.
"""

import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from server import DocumentationAnalyzer

async def example_workflow():
    """Demonstrate the complete workflow"""
    print("=" * 60)
    print("Documentation Analyzer + Registry Manager Workflow Example")
    print("=" * 60)
    
    # Example URL to analyze
    test_url = "https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search"
    
    async with DocumentationAnalyzer() as analyzer:
        print(f"\n1. Analyzing documentation from: {test_url}")
        print("-" * 50)
        
        try:
            # Fetch and analyze
            content, content_type = await analyzer.fetch_documentation(test_url)
            info = analyzer.extract_server_info_from_markdown(content, test_url)
            
            # Generate server ID
            server_id = analyzer.generate_server_id(info, test_url)
            
            print(f"✅ Successfully analyzed!")
            print(f"   Server Name: {info.get('name', 'Unknown')}")
            print(f"   Install Method: {info.get('install_method', 'Unknown')}")
            print(f"   Package: {info.get('package', 'Unknown')}")
            print(f"   Generated ID: {server_id}")
            
            # Validate
            errors = analyzer.validate_extracted_info(info)
            if errors:
                print(f"\n⚠️  Validation Issues:")
                for error in errors:
                    print(f"   - {error}")
            else:
                print(f"\n✅ Validation passed!")
            
            # Create server definition
            print(f"\n2. Creating Server Definition")
            print("-" * 50)
            
            server_def = {
                "name": info.get("name", f"{server_id} Server"),
                "description": info.get("description", f"MCP server from {test_url}"),
                "category": "community",
                "install_method": info.get("install_method", "manual"),
                "command": info.get("command", "node"),
                "args_template": info.get("args_template", []),
                "homepage": test_url
            }
            
            # Add optional fields
            if info.get("package"):
                server_def["package"] = info["package"]
            if info.get("repository"):
                server_def["repository"] = info["repository"]
            if info.get("env_vars"):
                server_def["env_vars"] = info["env_vars"]
            if info.get("setup_help"):
                server_def["setup_help"] = info["setup_help"]
            if info.get("example_usage"):
                server_def["example_usage"] = info["example_usage"]
            
            print("Server definition created!")
            print(json.dumps(server_def, indent=2))
            
            # Show registry manager commands
            print(f"\n3. Registry Manager Commands")
            print("-" * 50)
            print(f"\nTo register this server, use the Registry Manager's add_custom_server tool:")
            print(f"\nserver_id: \"{server_id}\"")
            print(f"server_definition: {json.dumps(server_def, indent=2)}")
            
            print(f"\n4. After Registration")
            print("-" * 50)
            print(f"\nOnce registered, you can:")
            print(f"• Search: pg config search {server_id}")
            print(f"• Get info: pg config info {server_id}")
            print(f"• Install: pg config install {server_id}")
            
            if info.get("env_vars"):
                print(f"\nEnvironment variables needed:")
                for key, desc in info["env_vars"].items():
                    print(f"• {key}: {desc}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")

async def analyze_multiple_urls():
    """Example of batch analysis"""
    print("\n\n" + "=" * 60)
    print("Batch Analysis Example")
    print("=" * 60)
    
    urls = [
        "https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem",
        "https://github.com/modelcontextprotocol/servers/tree/main/src/memory",
        "https://www.npmjs.com/package/@modelcontextprotocol/server-puppeteer"
    ]
    
    results = []
    async with DocumentationAnalyzer() as analyzer:
        for url in urls:
            print(f"\nAnalyzing: {url}")
            try:
                content, content_type = await analyzer.fetch_documentation(url)
                
                if 'html' in content_type:
                    info = analyzer.extract_server_info_from_html(content, url)
                else:
                    info = analyzer.extract_server_info_from_markdown(content, url)
                
                server_id = analyzer.generate_server_id(info, url)
                errors = analyzer.validate_extracted_info(info)
                
                results.append({
                    "url": url,
                    "server_id": server_id,
                    "name": info.get("name", "Unknown"),
                    "valid": len(errors) == 0,
                    "errors": errors
                })
                print(f"✅ Analyzed: {info.get('name', 'Unknown')} (ID: {server_id})")
                
            except Exception as e:
                print(f"❌ Failed: {str(e)}")
    
    # Summary
    print(f"\n📊 Batch Analysis Summary")
    print("-" * 50)
    valid_count = sum(1 for r in results if r["valid"])
    print(f"Total analyzed: {len(results)}")
    print(f"Ready for registration: {valid_count}")
    print(f"Need manual review: {len(results) - valid_count}")
    
    print(f"\nResults:")
    for r in results:
        status = "✅" if r["valid"] else "⚠️"
        print(f"{status} {r['name']} (ID: {r['server_id']})")
        if r["errors"]:
            for error in r["errors"]:
                print(f"   - {error}")

async def main():
    """Run examples"""
    # Run single URL analysis
    await example_workflow()
    
    # Uncomment to run batch analysis
    # await analyze_multiple_urls()

if __name__ == "__main__":
    asyncio.run(main())
