#!/usr/bin/env python3
"""
MCP Server Manager Backend API

This module provides a REST API for the MCP Server Manager GUI to interact
with the existing Python CLI functionality.
"""

import os
import sys
import json
import subprocess
import glob
import platform
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add the parent directory to Python path to import claude_desktop_mcp modules
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from claude_desktop_mcp.config_manager import ClaudeDesktopConfigManager
    from claude_desktop_mcp.server_registry import MCPServerRegistry
except ImportError as e:
    print(f"Error importing claude_desktop_mcp modules: {e}")
    print("Make sure you're running this from the correct directory")
    sys.exit(1)

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize managers
config_manager = ClaudeDesktopConfigManager()
registry = MCPServerRegistry()


class MCPBackendAPI:
    """Backend API for MCP Server Manager"""
    
    def __init__(self):
        self.config_manager = config_manager
        self.registry = registry
    
    def get_installed_servers(self) -> List[Dict[str, Any]]:
        """Get list of currently installed MCP servers"""
        try:
            print(f"Starting get_installed_servers...")
            servers = self.config_manager.list_servers()
            print(f"Found {len(servers)} servers in config")
            result = []
            
            for server_id, config in servers.items():
                print(f"Processing server: {server_id}")
                try:
                    # Get enhanced server info first (fast operation)
                    enhanced_info = self._get_enhanced_server_info(server_id)
                    
                    # Skip expensive log checking for now - just mark as configured
                    # TODO: Implement async/faster log checking
                    status = 'configured'
                    errors = []
                    
                    server_info = {
                        'id': server_id,
                        'name': enhanced_info.get('name', server_id.replace('_', ' ').replace('-', ' ').title()),
                        'description': enhanced_info.get('description', f'MCP Server: {server_id}'),
                        'category': enhanced_info.get('category', 'installed'),
                        'status': status,
                        'command': config.get('command', ''),
                        'args': config.get('args', []),
                        'env': self._sanitize_env_vars(config.get('env', {})),
                        'package': self._get_package_name(config),
                        'config': config,
                        'errors': errors
                    }
                    result.append(server_info)
                    print(f"Successfully processed server: {server_id}")
                except Exception as e:
                    print(f"Error processing server {server_id}: {e}")
                    continue
            
            print(f"Completed get_installed_servers, returning {len(result)} servers")
            return result
        except Exception as e:
            print(f"Error getting installed servers: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_enhanced_server_info(self, server_id: str) -> Dict[str, Any]:
        """Get enhanced information for known servers"""
        server_info_map = {
            'filesystem': {
                'name': 'Filesystem Server',
                'description': 'Secure file operations with configurable access controls. Read, write, and manage files and directories.',
                'category': 'official'
            },
            'code-sandbox-mcp': {
                'name': 'Code Sandbox Server',
                'description': 'Safe code execution in isolated sandbox environments. Run code snippets and test applications.',
                'category': 'community'
            },
            'fetch': {
                'name': 'Fetch Server',
                'description': 'Web content fetching and conversion for efficient LLM usage. Fetch and process web pages.',
                'category': 'official'
            },
            'brave-search': {
                'name': 'Brave Search Server',
                'description': 'Web search capabilities using Brave Search API. Get search results with privacy focus.',
                'category': 'official'
            },
            'github': {
                'name': 'GitHub Server',
                'description': 'Access GitHub repositories, issues, PRs, and code. Search repositories and manage GitHub resources.',
                'category': 'official'
            },
            'memory': {
                'name': 'Memory Server',
                'description': 'Knowledge graph-based persistent memory system. Store and retrieve information across conversations.',
                'category': 'official'
            },
            'sequential-thinking': {
                'name': 'Sequential Thinking Server',
                'description': 'Dynamic and reflective problem-solving through thought sequences. Advanced reasoning capabilities.',
                'category': 'official'
            },
            'puppeteer': {
                'name': 'Puppeteer Server',
                'description': 'Browser automation and web scraping using Puppeteer. Interact with web pages programmatically.',
                'category': 'official'
            },
            'everything': {
                'name': 'Everything Server',
                'description': 'Reference/test server that exercises all MCP protocol features. Includes prompts, resources, and tools.',
                'category': 'official'
            },
            'time': {
                'name': 'Time Server',
                'description': 'Time and timezone utilities. Get current time, convert between timezones, format dates.',
                'category': 'official'
            },
            'computer-control': {
                'name': 'Computer Control Server',
                'description': 'Control computer operations and automation through MCP interface. Interact with desktop applications.',
                'category': 'community'
            },
            'github-docker': {
                'name': 'GitHub Docker Server',
                'description': 'Docker-based GitHub server with containerized execution. Enhanced security and isolation.',
                'category': 'official'
            }
        }
        
        return server_info_map.get(server_id, {
            'name': server_id.replace('_', ' ').replace('-', ' ').title(),
            'description': f'MCP Server: {server_id}',
            'category': 'installed'
        })
    
    def _get_package_name(self, config: Dict[str, Any]) -> str:
        """Extract package name from server configuration"""
        command = config.get('command', '')
        args = config.get('args', [])
        
        if command == 'npx' and len(args) >= 2 and args[0] == '-y':
            return args[1]
        elif command == 'uvx' and len(args) >= 1:
            return args[0]
        elif command == 'docker' and 'mcp/' in ' '.join(args):
            for arg in args:
                if arg.startswith('mcp/'):
                    return arg
        
        return command or 'unknown'
    
    def get_available_servers(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available servers from registry"""
        try:
            if category:
                servers = self.registry.get_by_category(category)
            else:
                servers = self.registry.get_all_servers()
            
            return servers
        except Exception as e:
            print(f"Error getting available servers: {e}")
            return []
    
    def search_servers(self, query: str) -> List[Dict[str, Any]]:
        """Search for servers in registry"""
        try:
            return self.registry.search(query)
        except Exception as e:
            print(f"Error searching servers: {e}")
            return []
    
    def install_server(self, server_id: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Install a new MCP server"""
        try:
            # Get server info from registry
            server = self.registry.get_server(server_id)
            if not server:
                return {'success': False, 'error': f'Server {server_id} not found in registry'}
            
            # Generate install configuration
            install_config = self.registry.generate_install_command(server_id, config_data)
            if not install_config:
                return {'success': False, 'error': 'Failed to generate install configuration'}
            
            # Use custom name if provided
            instance_name = config_data.get('name', server_id)
            
            # Install the server
            self.config_manager.add_server(
                instance_name,
                install_config['command'],
                install_config['args'],
                install_config['env']
            )
            
            # Try to install npm package if needed
            if server.get('install_method') == 'npm' and server.get('package'):
                try:
                    result = subprocess.run(
                        ['npm', 'install', '-g', server['package']],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    if result.returncode != 0:
                        print(f"Warning: npm install failed: {result.stderr}")
                except Exception as e:
                    print(f"Warning: Failed to install npm package: {e}")
            
            return {'success': True, 'message': f'Successfully installed {instance_name}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def remove_server(self, server_id: str) -> Dict[str, Any]:
        """Remove an installed MCP server"""
        try:
            success = self.config_manager.remove_server(server_id)
            if success:
                return {'success': True, 'message': f'Successfully removed {server_id}'}
            else:
                return {'success': False, 'error': f'Server {server_id} not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_server_info(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a server"""
        try:
            return self.registry.get_server(server_id)
        except Exception as e:
            print(f"Error getting server info: {e}")
            return None
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate Claude Desktop configuration"""
        try:
            return self.config_manager.validate_config()
        except Exception as e:
            return {
                'valid': False,
                'errors': [str(e)],
                'warnings': []
            }
    
    def _check_server_status(self, server_id: str, config: Dict[str, Any]) -> str:
        """Check server status by examining Claude Desktop logs"""
        try:
            # Check for errors in log files first
            if self._has_server_errors(server_id):
                return 'error'
            
            # If no errors found, server is configured
            return 'configured'
        except Exception as e:
            print(f"Error checking server status for {server_id}: {e}")
            return 'configured'  # Default to configured if we can't check logs
    
    def _sanitize_env_vars(self, env_vars: Dict[str, str]) -> Dict[str, str]:
        """Sanitize environment variables for display"""
        sanitized = {}
        for key, value in env_vars.items():
            if any(secret in key.lower() for secret in ['token', 'key', 'password', 'secret']):
                sanitized[key] = '***'
            else:
                sanitized[key] = value
        return sanitized
    
    def _get_claude_logs_path(self) -> Path:
        """Get Claude Desktop logs directory based on platform"""
        system = platform.system().lower()
        
        if system == 'darwin':  # macOS
            return Path.home() / 'Library' / 'Logs' / 'Claude'
        elif system == 'windows':
            appdata = os.environ.get('APPDATA', '')
            if appdata:
                return Path(appdata) / 'Claude' / 'logs'
            return Path.home() / 'AppData' / 'Roaming' / 'Claude' / 'logs'
        else:  # Linux and others
            return Path.home() / '.config' / 'Claude' / 'logs'
    
    def _has_server_errors(self, server_id: str) -> bool:
        """Check if server has recent errors in Claude Desktop logs"""
        try:
            logs_path = self._get_claude_logs_path()
            if not logs_path.exists():
                return False
            
            # Look for recent log files (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            # Search for log files
            log_patterns = ['*.log', '*.txt']
            recent_errors = []
            
            for pattern in log_patterns:
                for log_file in logs_path.glob(pattern):
                    try:
                        # Check if file is recent enough
                        if log_file.stat().st_mtime < cutoff_time.timestamp():
                            continue
                        
                        # Read file and search for server-related errors
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            # Look for server-specific errors
                            error_patterns = [
                                f'error.*{server_id}',
                                f'failed.*{server_id}',
                                f'{server_id}.*error',
                                f'{server_id}.*failed',
                                f'mcp.*{server_id}.*error'
                            ]
                            
                            for pattern in error_patterns:
                                import re
                                if re.search(pattern, content, re.IGNORECASE):
                                    recent_errors.append(log_file.name)
                                    break
                    except Exception:
                        continue
            
            return len(recent_errors) > 0
            
        except Exception as e:
            print(f"Error checking logs for {server_id}: {e}")
            return False
    
    def get_server_errors(self, server_id: str) -> List[str]:
        """Get recent error messages for a server from Claude Desktop logs"""
        try:
            logs_path = self._get_claude_logs_path()
            if not logs_path.exists():
                return []
            
            cutoff_time = datetime.now() - timedelta(hours=24)
            errors = []
            
            log_patterns = ['*.log', '*.txt']
            
            for pattern in log_patterns:
                for log_file in logs_path.glob(pattern):
                    try:
                        if log_file.stat().st_mtime < cutoff_time.timestamp():
                            continue
                        
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            
                            for line in lines:
                                # Look for error lines mentioning this server
                                if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception']):
                                    if server_id.lower() in line.lower():
                                        # Clean up the error message
                                        error = line.strip()
                                        if error and error not in errors:
                                            errors.append(error)
                    except Exception:
                        continue
            
            return errors[:10]  # Return at most 10 recent errors
            
        except Exception as e:
            print(f"Error getting server errors for {server_id}: {e}")
            return []


# Initialize API instance
api = MCPBackendAPI()

# API Routes
@app.route('/api/servers/installed', methods=['GET'])
def get_installed_servers():
    """Get list of installed servers"""
    servers = api.get_installed_servers()
    return jsonify(servers)

@app.route('/api/servers/available', methods=['GET'])
def get_available_servers():
    """Get list of available servers"""
    category = request.args.get('category')
    servers = api.get_available_servers(category)
    return jsonify(servers)

@app.route('/api/servers/search', methods=['GET'])
def search_servers():
    """Search for servers"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    servers = api.search_servers(query)
    return jsonify(servers)

@app.route('/api/servers/<server_id>', methods=['GET'])
def get_server_info(server_id):
    """Get detailed server information"""
    server = api.get_server_info(server_id)
    if server:
        return jsonify(server)
    else:
        return jsonify({'error': 'Server not found'}), 404

@app.route('/api/servers/install', methods=['POST'])
def install_server():
    """Install a new server"""
    data = request.get_json()
    if not data or 'server_id' not in data:
        return jsonify({'error': 'Missing server_id'}), 400
    
    server_id = data['server_id']
    config_data = data.get('config', {})
    
    result = api.install_server(server_id, config_data)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@app.route('/api/servers/<server_id>', methods=['DELETE'])
def remove_server(server_id):
    """Remove an installed server"""
    result = api.remove_server(server_id)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@app.route('/api/servers/<server_id>/errors', methods=['GET'])
def get_server_errors(server_id):
    """Get recent errors for a server"""
    errors = api.get_server_errors(server_id)
    return jsonify({'errors': errors})

@app.route('/api/config/validate', methods=['GET'])
def validate_config():
    """Validate configuration"""
    result = api.validate_config()
    return jsonify(result)

@app.route('/api/config/path', methods=['GET'])
def get_config_path():
    """Get Claude Desktop config file path"""
    return jsonify({'path': str(api.config_manager.config_path)})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'config_exists': api.config_manager.config_exists(),
        'config_path': str(api.config_manager.config_path),
        'registry_loaded': len(api.registry.servers) > 0,
        'installed_servers': len(api.config_manager.list_servers()) if api.config_manager.config_exists() else 0
    })

if __name__ == '__main__':
    print("Starting MCP Server Manager Backend API...")
    print(f"Claude Desktop config path: {config_manager.config_path}")
    print(f"Config exists: {config_manager.config_exists()}")
    
    if config_manager.config_exists():
        try:
            servers = config_manager.list_servers()
            print(f"Found {len(servers)} installed servers:")
            for server_id in servers.keys():
                print(f"  - {server_id}")
        except Exception as e:
            print(f"Error reading config: {e}")
    
    print(f"Registry has {len(registry.servers)} available servers")
    print("API server starting on http://127.0.0.1:8080")
    
    # Run the Flask app
    app.run(host='127.0.0.1', port=8080, debug=True)