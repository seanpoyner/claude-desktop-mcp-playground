"""Tests for the standalone import script"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open
from io import StringIO

# Add the project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import import_claude_config
from claude_desktop_mcp.config_manager import ClaudeDesktopConfigManager


class TestImportScript(unittest.TestCase):
    """Test cases for the standalone import script"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "claude_desktop_config.json"
        self.simplified_path = Path(self.temp_dir) / "claude_desktop_simplified.json"
        
        # Store original stdout to restore later
        self.original_stdout = sys.stdout
        
    def tearDown(self):
        """Clean up test fixtures"""
        sys.stdout = self.original_stdout
        
        for file_path in [self.config_path, self.simplified_path]:
            if file_path.exists():
                file_path.unlink()
        
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def create_test_config(self):
        """Create a test Claude Desktop configuration"""
        test_config = {
            "mcpServers": {
                "test-server": {
                    "command": "python",
                    "args": ["-m", "test_server"],
                    "env": {
                        "TEST_VAR": "test_value",
                        "ANOTHER_VAR": "another_value"
                    }
                },
                "node-server": {
                    "command": "node",
                    "args": ["server.js", "--port", "3000"],
                    "env": {
                        "NODE_ENV": "development"
                    }
                },
                "simple-server": {
                    "command": "/usr/local/bin/simple-server",
                    "args": [],
                    "env": {}
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f, indent=2)
        
        return test_config
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    @patch('import_claude_config.save_simplified_config')
    def test_main_success(self, mock_save, mock_get_path):
        """Test successful import script execution"""
        mock_get_path.return_value = self.config_path
        self.create_test_config()
        
        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run main function
        result = import_claude_config.main()
        
        # Restore stdout
        sys.stdout = self.original_stdout
        output = captured_output.getvalue()
        
        # Check return code
        self.assertEqual(result, 0)
        
        # Check output contains expected messages
        self.assertIn("Claude Desktop Configuration Importer", output)
        self.assertIn("Successfully imported 3 MCP server(s)", output)
        self.assertIn("test-server", output)
        self.assertIn("node-server", output)
        self.assertIn("simple-server", output)
        self.assertIn("enabled", output)
        
        # Verify save_simplified_config was called
        mock_save.assert_called_once()
        args, kwargs = mock_save.call_args
        simplified_config = args[0]
        
        # Check simplified config structure
        self.assertIn("test-server", simplified_config)
        self.assertIn("node-server", simplified_config)
        self.assertIn("simple-server", simplified_config)
        
        # Check that all servers are enabled by default
        for server_name, server_config in simplified_config.items():
            self.assertTrue(server_config.get("enabled", False))
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_main_no_config_file(self, mock_get_path):
        """Test import script when config file doesn't exist"""
        mock_get_path.return_value = self.config_path
        # Don't create the config file
        
        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run main function
        result = import_claude_config.main()
        
        # Restore stdout
        sys.stdout = self.original_stdout
        output = captured_output.getvalue()
        
        # Check return code
        self.assertEqual(result, 1)
        
        # Check output contains expected messages
        self.assertIn("Claude Desktop config file not found", output)
        self.assertIn("This is normal if you haven't configured", output)
        self.assertIn(str(self.config_path), output)
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_main_empty_config(self, mock_get_path):
        """Test import script with empty configuration"""
        mock_get_path.return_value = self.config_path
        
        # Create empty config
        empty_config = {"mcpServers": {}}
        with open(self.config_path, 'w') as f:
            json.dump(empty_config, f)
        
        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run main function
        result = import_claude_config.main()
        
        # Restore stdout
        sys.stdout = self.original_stdout
        output = captured_output.getvalue()
        
        # Check return code
        self.assertEqual(result, 0)
        
        # Check output contains expected messages
        self.assertIn("Successfully imported 0 MCP server(s)", output)
        self.assertIn("No MCP servers are currently configured", output)
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_main_invalid_json(self, mock_get_path):
        """Test import script with invalid JSON configuration"""
        mock_get_path.return_value = self.config_path
        
        # Create invalid JSON file
        with open(self.config_path, 'w') as f:
            f.write("invalid json content {")
        
        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run main function
        result = import_claude_config.main()
        
        # Restore stdout
        sys.stdout = self.original_stdout
        output = captured_output.getvalue()
        
        # Check return code
        self.assertEqual(result, 1)
        
        # Check output contains error message
        self.assertIn("Error importing configuration", output)
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    @patch('import_claude_config.save_simplified_config')
    def test_main_save_error(self, mock_save, mock_get_path):
        """Test import script when save operation fails"""
        mock_get_path.return_value = self.config_path
        self.create_test_config()
        
        # Make save_simplified_config raise an exception
        mock_save.side_effect = IOError("Permission denied")
        
        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run main function
        result = import_claude_config.main()
        
        # Restore stdout
        sys.stdout = self.original_stdout
        output = captured_output.getvalue()
        
        # Check return code
        self.assertEqual(result, 1)
        
        # Check output contains error message
        self.assertIn("Error importing configuration", output)
        self.assertIn("Permission denied", output)
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_main_output_format(self, mock_get_path):
        """Test that the output format is user-friendly"""
        mock_get_path.return_value = self.config_path
        test_config = self.create_test_config()
        
        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run main function
        result = import_claude_config.main()
        
        # Restore stdout
        sys.stdout = self.original_stdout
        output = captured_output.getvalue()
        
        # Check return code
        self.assertEqual(result, 0)
        
        # Check output formatting
        lines = output.split('\n')
        
        # Should have header with separators
        self.assertIn("=" * 40, output)
        
        # Should show each server with status
        self.assertIn("test-server (python) - ✅ enabled", output)
        self.assertIn("node-server (node) - ✅ enabled", output)
        self.assertIn("simple-server (/usr/local/bin/simple-server) - ✅ enabled", output)
        
        # Should show next steps
        self.assertIn("pg config apply", output)
        
        # Should show JSON structure
        self.assertIn("Simplified configuration structure:", output)


class TestImportScriptIntegration(unittest.TestCase):
    """Integration tests for the import script"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        # Clean up temp files
        for file in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        os.rmdir(self.temp_dir)
    
    @patch.object(ClaudeDesktopConfigManager, '_get_config_path')
    def test_creates_simplified_config_file(self, mock_get_path):
        """Test that the script creates the simplified config file"""
        config_path = Path(self.temp_dir) / "claude_desktop_config.json"
        mock_get_path.return_value = config_path
        
        # Create test config
        test_config = {
            "mcpServers": {
                "test-server": {
                    "command": "python",
                    "args": ["-m", "test"],
                    "env": {"TEST": "value"}
                }
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(test_config, f)
        
        # Run import script (suppress output)
        with patch('sys.stdout', StringIO()):
            result = import_claude_config.main()
        
        self.assertEqual(result, 0)
        
        # Check that simplified config file was created
        simplified_path = Path("claude_desktop_simplified.json")
        self.assertTrue(simplified_path.exists())
        
        # Verify content
        with open(simplified_path) as f:
            simplified = json.load(f)
        
        self.assertIn("test-server", simplified)
        self.assertEqual(simplified["test-server"]["command"], "python")
        self.assertEqual(simplified["test-server"]["args"], ["-m", "test"])
        self.assertEqual(simplified["test-server"]["env"], {"TEST": "value"})
        self.assertTrue(simplified["test-server"]["enabled"])


if __name__ == '__main__':
    unittest.main()