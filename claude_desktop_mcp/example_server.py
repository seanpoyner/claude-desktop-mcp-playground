"""Example Python MCP Server

A simple example server demonstrating MCP protocol implementation.
"""

import json
import sys
from typing import Any, Dict

def create_server_response(id: str, result: Any = None, error: str = None) -> Dict:
    """Create a JSON-RPC response"""
    response = {"jsonrpc": "2.0", "id": id}
    if error:
        response["error"] = {"code": -1, "message": error}
    else:
        response["result"] = result
    return response

def handle_initialize(params: Dict) -> Dict:
    """Handle initialize request"""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "example-server",
            "version": "0.1.0"
        }
    }

def handle_tools_list() -> Dict:
    """Handle tools/list request"""
    return {
        "tools": [
            {
                "name": "echo",
                "description": "Echo back the input text",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to echo back"
                        }
                    },
                    "required": ["text"]
                }
            }
        ]
    }

def handle_tools_call(params: Dict) -> Dict:
    """Handle tools/call request"""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    if tool_name == "echo":
        text = arguments.get("text", "")
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Echo: {text}"
                }
            ]
        }
    else:
        raise ValueError(f"Unknown tool: {tool_name}")

def main():
    """Main server loop"""
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            method = request.get("method")
            params = request.get("params", {})
            id = request.get("id")
            
            if method == "initialize":
                result = handle_initialize(params)
                response = create_server_response(id, result)
            elif method == "tools/list":
                result = handle_tools_list()
                response = create_server_response(id, result)
            elif method == "tools/call":
                result = handle_tools_call(params)
                response = create_server_response(id, result)
            else:
                response = create_server_response(id, error=f"Unknown method: {method}")
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except Exception as e:
            error_response = create_server_response(
                request.get("id") if "request" in locals() else None,
                error=str(e)
            )
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
