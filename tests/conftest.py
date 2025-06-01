"""Pytest configuration and shared fixtures for Claude Desktop MCP tests"""

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    
    # Cleanup
    for file in Path(temp_dir).glob("*"):
        if file.is_file():
            file.unlink()
    os.rmdir(temp_dir)


@pytest.fixture
def mock_config_path(temp_dir):
    """Create a mock Claude Desktop config path"""
    return temp_dir / "claude_desktop_config.json"


@pytest.fixture
def sample_claude_config():
    """Sample Claude Desktop configuration for testing"""
    return {
        "mcpServers": {
            "test-server": {
                "command": "python",
                "args": ["-m", "test_server"],
                "env": {
                    "TEST_VAR": "test_value",
                    "DEBUG": "true"
                }
            },
            "node-server": {
                "command": "node",
                "args": ["server.js", "--port", "3000"],
                "env": {
                    "NODE_ENV": "development",
                    "PORT": "3000"
                }
            },
            "go-server": {
                "command": "/usr/local/bin/go-server",
                "args": ["--config", "/etc/go-server.conf"],
                "env": {}
            }
        }
    }


@pytest.fixture
def sample_simplified_config():
    """Sample simplified configuration for testing"""
    return {
        "test-server": {
            "command": "python",
            "args": ["-m", "test_server"],
            "env": {
                "TEST_VAR": "test_value",
                "DEBUG": "true"
            },
            "enabled": True
        },
        "node-server": {
            "command": "node",
            "args": ["server.js", "--port", "3000"],
            "env": {
                "NODE_ENV": "development",
                "PORT": "3000"
            },
            "enabled": True
        },
        "disabled-server": {
            "command": "disabled-command",
            "args": [],
            "env": {},
            "enabled": False
        },
        "go-server": {
            "command": "/usr/local/bin/go-server",
            "args": ["--config", "/etc/go-server.conf"],
            "env": {},
            "enabled": True
        }
    }


@pytest.fixture
def create_config_file(mock_config_path):
    """Fixture factory to create config files with given content"""
    def _create_file(config_data: Dict[str, Any]):
        with open(mock_config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        return mock_config_path
    
    return _create_file


@pytest.fixture
def empty_claude_config():
    """Empty Claude Desktop configuration"""
    return {"mcpServers": {}}


@pytest.fixture
def invalid_claude_config():
    """Invalid Claude Desktop configuration for testing error handling"""
    return {
        "mcpServers": {
            "bad-server-1": {
                "args": ["-m", "test"],  # Missing command
                "env": {}
            },
            "bad-server-2": "not-a-dict",  # Server config is not a dict
            "good-server": {
                "command": "python",
                "args": [],
                "env": {}
            }
        }
    }


@pytest.fixture
def claude_config_with_env_only():
    """Configuration with only environment variables"""
    return {
        "mcpServers": {
            "env-server": {
                "command": "env-command",
                "args": [],
                "env": {
                    "API_KEY": "secret-key",
                    "DATABASE_URL": "postgresql://localhost/test",
                    "LOG_LEVEL": "debug"
                }
            }
        }
    }


@pytest.fixture
def claude_config_minimal():
    """Minimal valid configuration"""
    return {
        "mcpServers": {
            "minimal-server": {
                "command": "echo"
            }
        }
    }


# Test data constants
TEST_SERVERS = {
    "python-server": {
        "command": "python",
        "args": ["-m", "test_module"],
        "env": {"PYTHONPATH": "/custom/path"}
    },
    "node-server": {
        "command": "node",
        "args": ["app.js"],
        "env": {"NODE_ENV": "test"}
    },
    "binary-server": {
        "command": "/usr/bin/custom-server",
        "args": ["--verbose", "--config=/etc/server.conf"],
        "env": {}
    }
}


@pytest.fixture(params=TEST_SERVERS.keys())
def server_config(request):
    """Parameterized fixture for different server configurations"""
    server_name = request.param
    return server_name, TEST_SERVERS[server_name]