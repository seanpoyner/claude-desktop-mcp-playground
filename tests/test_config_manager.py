"""Tests for Claude Desktop Configuration Manager"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

from claude_desktop_mcp.config_manager import (
    ClaudeDesktopConfigManager,
    save_simplified_config,
    load_simplified_config
)


class TestClaudeDesktopConfigManager(unittest.TestCase):
    """Test cases for ClaudeDesktopConfigManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "claude_desktop_config.json"
        
    def tearDown(self):
        """Clean up test fixtures"""
        if self.config_path.exists():
            self.config_path.unlink()
        os.rmdir(self.temp_dir)
    
    @patch('claude_desktop_mcp.config_manager.platform.system')
    def test_get_config_path_macos(self, mock_system):
        """Test config path detection on macOS"""
        mock_system.return_value = "Darwin"
        manager = ClaudeDesktopConfigManager()
        
        expected_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        self.assertEqual(manager.config_path, expected_path)
    
    @patch('claude_desktop_mcp.config_manager.platform.system')
    @patch.dict(os.environ, {'APPDATA': '/Users/test/AppData/Roaming'})
    def test_get_config_path_windows(self, mock_system):
        """Test config path detection on Windows"""
        mock_system.return_value = "Windows"
        manager = ClaudeDesktopConfigManager()
        
        expected_path = Path("/Users/test/AppData/Roaming") / "Claude" / "claude_desktop_config.json"
        self.assertEqual(manager.config_path, expected_path)
    
    @patch('claude_desktop_mcp.config_manager.platform.system')
    def test_get_config_path_linux(self, mock_system):
        """Test config path detection on Linux"""
        mock_system.return_value = "Linux"
        manager = ClaudeDesktopConfigManager()
        
        expected_path = Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
        self.assertEqual(manager.config_path, expected_path)
    
    def test_config_exists_false(self):
        """Test config_exists when file doesn't exist"""
        with patch.object(ClaudeDesktopConfigManager, '_get_config_path', return_value=self.config_path):
            manager = ClaudeDesktopConfigManager()
            self.assertFalse(manager.config_exists())
    
    def test_config_exists_true(self):
        """Test config_exists when file exists"""
        self.config_path.touch()
        
        with patch.object(ClaudeDesktopConfigManager, '_get_config_path', return_value=self.config_path):
            manager = ClaudeDesktopConfigManager()
            self.assertTrue(manager.config_exists())
    
    def test_load_config_nonexistent(self):
        """Test loading config when file doesn't exist"""
        with patch.object(ClaudeDesktopConfigManager, '_get_config_path', return_value=self.config_path):
            manager = ClaudeDesktopConfigManager()
            config = manager.load_config()
            self.assertEqual(config, {"mcpServers": {}})
    
    def test_load_config_valid(self):
        """Test loading valid configuration"""
        test_config = {
            "mcpServers": {
                "test-server": {
                    "command": "python",
                    "args": ["-m", "test"],
                    "env": {"TEST_VAR": "value"}
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        with patch.object(ClaudeDesktopConfigManager, '_get_config_path', return_value=self.config_path):
            manager = ClaudeDesktopConfigManager()
            config = manager.load_config()
            self.assertEqual(config, test_config)
    
    def test_load_config_invalid_json(self):
        """Test loading invalid JSON configuration"""
        with open(self.config_path, 'w') as f:
            f.write("invalid json {")
        
        with patch.object(ClaudeDesktopConfigManager, '_get_config_path', return_value=self.config_path):
            manager = ClaudeDesktopConfigManager()
            with self.assertRaises(RuntimeError):
                manager.load_config()
    
    def test_save_config(self):
        """Test saving configuration"""
        test_config = {
            "mcpServers": {
                "new-server": {
                    "command": "node",
                    "args": ["server.js"],
                    "env": {}
                }
            }
        }
        
        with patch.object(ClaudeDesktopConfigManager, '_get_config_path', return_value=self.config_path):
            manager = ClaudeDesktopConfigManager()
            manager.save_config(test_config)
        
        # Verify file was created and content is correct
        self.assertTrue(self.config_path.exists())
        with open(self.config_path) as f:
            saved_config = json.load(f)
        self.assertEqual(saved_config, test_config)
    
    def test_import_to_simplified(self):
        """Test importing to simplified format"""
        test_config = {
            "mcpServers": {
                "server1": {
                    "command": "python",
                    "args": ["-m", "server1"],
                    "env": {"VAR1": "value1"}
                },
                "server2": {
                    "command": "node",
                    "args": ["server2.js"],
                    "env": {}
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        with patch.object(ClaudeDesktopConfigManager, '_get_config_path', return_value=self.config_path):
            manager = ClaudeDesktopConfigManager()
            simplified = manager.import_to_simplified()
        
        expected_simplified = {
            "server1": {
                "command": "python",
                "args": ["-m", "server1"],
                "env": {"VAR1": "value1"},
                "enabled": True
            },
            "server2": {
                "command": "node",
                "args": ["server2.js"],
                "env": {},
                "enabled": True
            }
        }
        
        self.assertEqual(simplified, expected_simplified)
    
    def test_export_from_simplified(self):
        """Test exporting from simplified format"""
        simplified_config = {
            "server1": {
                "command": "python",
                "args": ["-m", "server1"],
                "env": {"VAR1": "value1"},
                "enabled": True
            },
            "server2": {
                "command": "node",
                "args": ["server2.js"],
                "env": {},
                "enabled": False  # Disabled server
            },
            "server3": {
                "command": "go",
                "args": ["run", "main.go"],
                "env": {},
                "enabled": True
            }
        }
        
        with patch.object(ClaudeDesktopConfigManager, '_get_config_path', return_value=self.config_path):
            manager = ClaudeDesktopConfigManager()
            claude_config = manager.export_from_simplified(simplified_config)
        
        # Only enabled servers should be included
        expected_config = {
            "mcpServers": {
                "server1": {
                    "command": "python",
                    "args": ["-m", "server1"],
                    "env": {"VAR1": "value1"}
                },
                "server3": {
                    "command": "go",
                    "args": ["run", "main.go"],
                    "env": {}
                }
            }
        }
        
        self.assertEqual(claude_config, expected_config)
    
    def test_add_server(self):
        """Test adding a new server"""
        with patch.object(ClaudeDesktopConfigManager, '_get_config_path', return_value=self.config_path):
            manager = ClaudeDesktopConfigManager()
            manager.add_server("test-server", "python", ["-m", "test"], {"TEST": "value"})
        
        # Verify server was added
        with open(self.config_path) as f:
            config = json.load(f)
        
        expected_server = {
            "command": "python",
            "args": ["-m", "test"],
            "env": {"TEST": "value"}
        }
        
        self.assertIn("test-server", config["mcpServers"])
        self.assertEqual(config["mcpServers"]["test-server"], expected_server)
    
    def test_remove_server(self):
        """Test removing a server"""
        initial_config = {
            "mcpServers": {
                "server1": {"command": "python", "args": [], "env": {}},
                "server2": {"command": "node", "args": [], "env": {}}
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(initial_config, f)
        
        with patch.object(ClaudeDesktopConfigManager, '_get_config_path', return_value=self.config_path):
            manager = ClaudeDesktopConfigManager()
            result = manager.remove_server("server1")
        
        self.assertTrue(result)
        
        # Verify server was removed
        with open(self.config_path) as f:
            config = json.load(f)
        
        self.assertNotIn("server1", config["mcpServers"])
        self.assertIn("server2", config["mcpServers"])
    
    def test_remove_nonexistent_server(self):
        """Test removing a server that doesn't exist"""
        with patch.object(ClaudeDesktopConfigManager, '_get_config_path', return_value=self.config_path):
            manager = ClaudeDesktopConfigManager()
            result = manager.remove_server("nonexistent")
        
        self.assertFalse(result)
    
    def test_validate_config_valid(self):
        """Test validating a valid configuration"""
        valid_config = {
            "mcpServers": {
                "test-server": {
                    "command": "python",
                    "args": ["-m", "test"],
                    "env": {}
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(valid_config, f)
        
        with patch.object(ClaudeDesktopConfigManager, '_get_config_path', return_value=self.config_path):
            manager = ClaudeDesktopConfigManager()
            result = manager.validate_config()
        
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)
    
    def test_validate_config_missing_command(self):
        """Test validating configuration with missing command"""
        invalid_config = {
            "mcpServers": {
                "test-server": {
                    "args": ["-m", "test"],
                    "env": {}
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(invalid_config, f)
        
        with patch.object(ClaudeDesktopConfigManager, '_get_config_path', return_value=self.config_path):
            manager = ClaudeDesktopConfigManager()
            result = manager.validate_config()
        
        self.assertFalse(result["valid"])
        self.assertIn("missing 'command' field", result["errors"][0])


class TestSimplifiedConfigHelpers(unittest.TestCase):
    """Test cases for simplified config helper functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.temp_path = self.temp_file.name
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_path):
            os.unlink(self.temp_path)
    
    def test_save_load_simplified_config(self):
        """Test saving and loading simplified configuration"""
        test_config = {
            "server1": {
                "command": "python",
                "args": ["-m", "server1"],
                "env": {"VAR": "value"},
                "enabled": True
            },
            "server2": {
                "command": "node",
                "args": ["server.js"],
                "env": {},
                "enabled": False
            }
        }
        
        # Save config
        save_simplified_config(test_config, self.temp_path)
        
        # Load config
        loaded_config = load_simplified_config(self.temp_path)
        
        self.assertEqual(loaded_config, test_config)
    
    def test_load_simplified_config_invalid(self):
        """Test loading invalid simplified configuration"""
        with open(self.temp_path, 'w') as f:
            f.write("invalid json")
        
        with self.assertRaises(RuntimeError):
            load_simplified_config(self.temp_path)
    
    def test_load_simplified_config_nonexistent(self):
        """Test loading nonexistent simplified configuration"""
        os.unlink(self.temp_path)
        
        with self.assertRaises(RuntimeError):
            load_simplified_config(self.temp_path)


if __name__ == '__main__':
    unittest.main()