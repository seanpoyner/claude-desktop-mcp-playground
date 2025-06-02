"""Tests for Claude Desktop CLI"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner

from claude_desktop_mcp.cli import main, config
from claude_desktop_mcp.config_manager import ClaudeDesktopConfigManager


class TestCLI(unittest.TestCase):
    """Test cases for CLI commands"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "claude_desktop_config.json"
        self.simplified_path = Path(self.temp_dir) / "claude_desktop_simplified.json"
        
    def tearDown(self):
        """Clean up test fixtures"""
        for file_path in [self.config_path, self.simplified_path]:
            if file_path.exists():
                file_path.unlink()
        os.rmdir(self.temp_dir)
    
    def create_test_config(self):
        """Create a test configuration file"""
        test_config = {
            "mcpServers": {
                "test-server": {
                    "command": "python",
                    "args": ["-m", "test"],
                    "env": {"TEST_VAR": "value"}
                },
                "another-server": {
                    "command": "node",
                    "args": ["server.js"],
                    "env": {}
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        return test_config
    
    def create_test_simplified_config(self):
        """Create a test simplified configuration file"""
        simplified_config = {
            "test-server": {
                "command": "python",
                "args": ["-m", "test"],
                "env": {"TEST_VAR": "value"},
                "enabled": True
            },
            "disabled-server": {
                "command": "go",
                "args": ["run", "main.go"],
                "env": {},
                "enabled": False
            }
        }
        
        with open(self.simplified_path, 'w') as f:
            json.dump(simplified_config, f)
        
        return simplified_config
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_import_config_success(self, mock_get_path):
        """Test successful config import"""
        mock_get_path.return_value = self.config_path
        self.create_test_config()
        
        result = self.runner.invoke(config, ['import', '--output', str(self.simplified_path)])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Imported 2 MCP servers", result.output)
        self.assertTrue(self.simplified_path.exists())
        
        # Verify simplified config content
        with open(self.simplified_path) as f:
            simplified = json.load(f)
        
        self.assertIn("test-server", simplified)
        self.assertIn("another-server", simplified)
        self.assertTrue(simplified["test-server"]["enabled"])
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_import_config_no_file(self, mock_get_path):
        """Test import when config file doesn't exist"""
        mock_get_path.return_value = self.config_path
        
        result = self.runner.invoke(config, ['import'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Claude Desktop config not found", result.output)
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_show_config_success(self, mock_get_path):
        """Test successful config show"""
        mock_get_path.return_value = self.config_path
        self.create_test_config()
        
        result = self.runner.invoke(config, ['show'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Found 2 MCP server(s)", result.output)
        self.assertIn("test-server", result.output)
        self.assertIn("another-server", result.output)
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_show_config_json_format(self, mock_get_path):
        """Test config show with JSON format"""
        mock_get_path.return_value = self.config_path
        self.create_test_config()
        
        result = self.runner.invoke(config, ['show', '--format', 'json'])
        
        self.assertEqual(result.exit_code, 0)
        # Should be valid JSON
        try:
            json.loads(result.output)
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_show_config_no_servers(self, mock_get_path):
        """Test show when no servers are configured"""
        mock_get_path.return_value = self.config_path
        
        # Create empty config
        with open(self.config_path, 'w') as f:
            json.dump({"mcpServers": {}}, f)
        
        result = self.runner.invoke(config, ['show'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("No MCP servers configured", result.output)
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_add_server_success(self, mock_get_path):
        """Test successful server addition"""
        mock_get_path.return_value = self.config_path
        
        result = self.runner.invoke(config, [
            'add', 'new-server', 'python',
            '--args', '-m', '--args', 'newserver',
            '--env', 'KEY=value', '--env', 'KEY2=value2'
        ])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Added MCP server 'new-server'", result.output)
        
        # Verify server was added
        with open(self.config_path) as f:
            config_data = json.load(f)
        
        self.assertIn("new-server", config_data["mcpServers"])
        server_config = config_data["mcpServers"]["new-server"]
        self.assertEqual(server_config["command"], "python")
        self.assertEqual(server_config["args"], ["-m", "newserver"])
        self.assertEqual(server_config["env"], {"KEY": "value", "KEY2": "value2"})
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_add_server_invalid_env(self, mock_get_path):
        """Test adding server with invalid environment variable format"""
        mock_get_path.return_value = self.config_path
        
        result = self.runner.invoke(config, [
            'add', 'new-server', 'python',
            '--env', 'invalid-format'
        ])
        
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Invalid environment variable format", result.output)
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_add_server_overwrite_existing(self, mock_get_path):
        """Test adding server that overwrites existing one"""
        mock_get_path.return_value = self.config_path
        self.create_test_config()
        
        # Try to add server with existing name, but decline overwrite
        result = self.runner.invoke(config, [
            'add', 'test-server', 'go'
        ], input='n\n')
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Cancelled", result.output)
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_remove_server_success(self, mock_get_path):
        """Test successful server removal"""
        mock_get_path.return_value = self.config_path
        self.create_test_config()
        
        result = self.runner.invoke(config, [
            'remove', 'test-server'
        ], input='y\n')
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Removed MCP server 'test-server'", result.output)
        
        # Verify server was removed
        with open(self.config_path) as f:
            config_data = json.load(f)
        
        self.assertNotIn("test-server", config_data["mcpServers"])
        self.assertIn("another-server", config_data["mcpServers"])
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_remove_server_with_confirm_flag(self, mock_get_path):
        """Test server removal with --confirm flag"""
        mock_get_path.return_value = self.config_path
        self.create_test_config()
        
        result = self.runner.invoke(config, [
            'remove', 'test-server', '--confirm'
        ])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Removed MCP server 'test-server'", result.output)
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_remove_nonexistent_server(self, mock_get_path):
        """Test removing a server that doesn't exist"""
        mock_get_path.return_value = self.config_path
        self.create_test_config()
        
        result = self.runner.invoke(config, [
            'remove', 'nonexistent-server', '--confirm'
        ])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Server 'nonexistent-server' not found", result.output)
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_validate_config_valid(self, mock_get_path):
        """Test validating a valid configuration"""
        mock_get_path.return_value = self.config_path
        self.create_test_config()
        
        result = self.runner.invoke(config, ['validate'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Configuration is valid", result.output)
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_validate_config_invalid(self, mock_get_path):
        """Test validating an invalid configuration"""
        mock_get_path.return_value = self.config_path
        
        # Create invalid config (missing command)
        invalid_config = {
            "mcpServers": {
                "bad-server": {
                    "args": ["-m", "test"],
                    "env": {}
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(invalid_config, f)
        
        result = self.runner.invoke(config, ['validate'])
        
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Configuration has errors", result.output)
        self.assertIn("missing 'command' field", result.output)
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_apply_config_success(self, mock_get_path):
        """Test successful config application"""
        mock_get_path.return_value = self.config_path
        simplified_config = self.create_test_simplified_config()
        
        result = self.runner.invoke(config, [
            'apply', str(self.simplified_path)
        ], input='y\n')
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Configuration applied successfully", result.output)
        self.assertIn("Will apply 1 MCP server(s)", result.output)  # Only enabled ones
        
        # Verify config was applied correctly
        with open(self.config_path) as f:
            config_data = json.load(f)
        
        # Should only contain enabled servers
        self.assertIn("test-server", config_data["mcpServers"])
        self.assertNotIn("disabled-server", config_data["mcpServers"])
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_apply_config_nonexistent_file(self, mock_get_path):
        """Test applying config from nonexistent file"""
        mock_get_path.return_value = self.config_path
        
        result = self.runner.invoke(config, [
            'apply', 'nonexistent.json'
        ])
        
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Input file not found", result.output)
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_apply_config_cancelled(self, mock_get_path):
        """Test applying config but cancelling at confirmation"""
        mock_get_path.return_value = self.config_path
        self.create_test_simplified_config()
        
        result = self.runner.invoke(config, [
            'apply', str(self.simplified_path)
        ], input='n\n')
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Cancelled", result.output)


class TestMainCLI(unittest.TestCase):
    """Test cases for main CLI entry point"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.runner = CliRunner()
    
    def test_main_help(self):
        """Test main CLI help"""
        result = self.runner.invoke(main, ['--help'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Claude Desktop MCP Configuration Manager", result.output)
    
    def test_config_help(self):
        """Test config subcommand help"""
        result = self.runner.invoke(main, ['config', '--help'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Manage Claude Desktop MCP configuration", result.output)
    
    def test_version(self):
        """Test version display"""
        result = self.runner.invoke(main, ['--version'])
        
        self.assertEqual(result.exit_code, 0)


if __name__ == '__main__':
    unittest.main()