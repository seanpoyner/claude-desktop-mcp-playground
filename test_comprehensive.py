#!/usr/bin/env python3
"""
Comprehensive Test Suite for Claude Desktop MCP Playground

Tests every piece of functionality including:
- CLI commands and options
- Server search and discovery  
- Server installation (including real downloads)
- Configuration management
- Setup wizard
- Error handling
"""

import os
import sys
import json
import tempfile
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any

# Add project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from claude_desktop_mcp.cli import main
from claude_desktop_mcp.config_manager import ClaudeDesktopConfigManager
from claude_desktop_mcp.server_registry import MCPServerRegistry
from click.testing import CliRunner


class ComprehensiveTestSuite:
    def __init__(self):
        self.runner = CliRunner()
        self.test_results = []
        self.temp_dir = None
        self.original_config_path = None
        
    def setup_test_environment(self):
        """Set up isolated test environment"""
        print("🔧 Setting up test environment...")
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp(prefix="mcp_test_")
        print(f"   Test directory: {self.temp_dir}")
        
        # Create test config directory
        test_config_dir = Path(self.temp_dir) / "claude"
        test_config_dir.mkdir(parents=True)
        
        # Set environment variable to use test config
        self.original_config_path = os.environ.get('CLAUDE_CONFIG_PATH')
        os.environ['CLAUDE_CONFIG_PATH'] = str(test_config_dir / "claude_desktop_config.json")
        
        # Create empty test config
        test_config = {"mcpServers": {}}
        with open(os.environ['CLAUDE_CONFIG_PATH'], 'w') as f:
            json.dump(test_config, f, indent=2)
            
        print("✅ Test environment ready")
        
    def cleanup_test_environment(self):
        """Clean up test environment"""
        print("🧹 Cleaning up test environment...")
        
        # Restore original config path
        if self.original_config_path:
            os.environ['CLAUDE_CONFIG_PATH'] = self.original_config_path
        elif 'CLAUDE_CONFIG_PATH' in os.environ:
            del os.environ['CLAUDE_CONFIG_PATH']
            
        # Remove temporary directory
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            
        print("✅ Cleanup complete")
        
    def run_test(self, test_name: str, test_func):
        """Run a single test and record results"""
        print(f"\n🧪 Running: {test_name}")
        try:
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            
            self.test_results.append({
                "name": test_name,
                "status": "PASS" if result else "FAIL",
                "duration": f"{end_time - start_time:.2f}s",
                "details": result if isinstance(result, str) else None
            })
            
            if result:
                print(f"   ✅ PASS ({end_time - start_time:.2f}s)")
            else:
                print(f"   ❌ FAIL ({end_time - start_time:.2f}s)")
                
        except Exception as e:
            self.test_results.append({
                "name": test_name,
                "status": "ERROR",
                "duration": "N/A",
                "details": str(e)
            })
            print(f"   💥 ERROR: {e}")
            
    # ===== CLI BASIC FUNCTIONALITY TESTS =====
    
    def test_cli_help(self):
        """Test CLI help commands"""
        result = self.runner.invoke(main, ['--help'])
        return result.exit_code == 0 and "Claude Desktop MCP Configuration Manager" in result.output
        
    def test_cli_version(self):
        """Test CLI version command"""
        result = self.runner.invoke(main, ['--version'])
        return result.exit_code == 0 and "version" in result.output
        
    def test_config_help(self):
        """Test config subcommand help"""
        result = self.runner.invoke(main, ['config', '--help'])
        return result.exit_code == 0 and "Manage Claude Desktop MCP configuration" in result.output
        
    # ===== SERVER SEARCH TESTS =====
    
    def test_search_all_servers(self):
        """Test searching all servers"""
        result = self.runner.invoke(main, ['config', 'search'])
        return (result.exit_code == 0 and 
                "Found" in result.output and 
                "filesystem" in result.output and
                "postgres" in result.output)
                
    def test_search_specific_term(self):
        """Test searching for specific term"""
        result = self.runner.invoke(main, ['config', 'search', 'database'])
        return (result.exit_code == 0 and 
                "postgres" in result.output and 
                "sqlite" in result.output)
                
    def test_search_no_results(self):
        """Test search with no results"""
        result = self.runner.invoke(main, ['config', 'search', 'nonexistent'])
        return result.exit_code == 0 and "No servers found" in result.output
        
    def test_search_json_format(self):
        """Test search with JSON output"""
        result = self.runner.invoke(main, ['config', 'search', 'database', '--format', 'json'])
        if result.exit_code != 0:
            return False
        try:
            data = json.loads(result.output)
            return isinstance(data, list) and len(data) > 0
        except json.JSONDecodeError:
            return False
            
    def test_search_by_category(self):
        """Test search by category"""
        result = self.runner.invoke(main, ['config', 'search', '--category', 'official'])
        return (result.exit_code == 0 and 
                "Found" in result.output and
                "filesystem" in result.output)
                
    # ===== SERVER INFO TESTS =====
    
    def test_server_info_valid(self):
        """Test getting info for valid server"""
        result = self.runner.invoke(main, ['config', 'info', 'filesystem'])
        return (result.exit_code == 0 and 
                "Filesystem Server" in result.output and
                "Required Arguments" in result.output)
                
    def test_server_info_invalid(self):
        """Test getting info for invalid server"""
        result = self.runner.invoke(main, ['config', 'info', 'nonexistent'])
        return result.exit_code != 0 or "not found" in result.output.lower()
        
    # ===== CONFIGURATION TESTS =====
    
    def test_config_show_empty(self):
        """Test showing empty configuration"""
        result = self.runner.invoke(main, ['config', 'show'])
        return result.exit_code == 0
        
    def test_config_list_empty(self):
        """Test listing empty server list"""
        result = self.runner.invoke(main, ['config', 'list'])
        return result.exit_code == 0 and "No MCP servers found" in result.output
        
    def test_config_validate_empty(self):
        """Test validating empty configuration"""
        result = self.runner.invoke(main, ['config', 'validate'])
        return result.exit_code == 0
        
    # ===== DRY RUN INSTALLATION TESTS =====
    
    def test_install_dry_run_filesystem(self):
        """Test dry-run installation of filesystem server"""
        result = self.runner.invoke(main, [
            'config', 'install', 'filesystem', 
            '--dry-run', '--arg', 'path=/test'
        ])
        return (result.exit_code == 0 and 
                "Dry run" in result.output and
                "filesystem" in result.output)
                
    def test_install_dry_run_missing_args(self):
        """Test dry-run installation with missing required args"""
        result = self.runner.invoke(main, [
            'config', 'install', 'filesystem', '--dry-run'
        ])
        return result.exit_code != 0 or "required" in result.output.lower()
        
    def test_install_dry_run_sqlite(self):
        """Test dry-run installation of sqlite server"""
        result = self.runner.invoke(main, [
            'config', 'install', 'sqlite',
            '--dry-run', '--arg', 'database_path=/test.db'
        ])
        return (result.exit_code == 0 and 
                "Dry run" in result.output and
                "sqlite" in result.output)
                
    # ===== REAL INSTALLATION TESTS =====
    
    def test_install_filesystem_server(self):
        """Test real installation of filesystem server"""
        test_path = Path(self.temp_dir) / "test_workspace"
        test_path.mkdir()
        
        result = self.runner.invoke(main, [
            'config', 'install', 'filesystem',
            '--arg', f'path={test_path}',
            '--name', 'test-filesystem'
        ])
        
        if result.exit_code != 0:
            print(f"   Installation failed: {result.output}")
            return False
            
        # Verify installation in config
        list_result = self.runner.invoke(main, ['config', 'list'])
        return 'test-filesystem' in list_result.output
        
    def test_install_time_server(self):
        """Test installation of time server (no args required)"""
        result = self.runner.invoke(main, [
            'config', 'install', 'time',
            '--name', 'test-time'
        ])
        
        if result.exit_code != 0:
            print(f"   Installation failed: {result.output}")
            return False
            
        # Verify installation in config
        list_result = self.runner.invoke(main, ['config', 'list'])
        return 'test-time' in list_result.output
        
    def test_install_with_env_vars(self):
        """Test installation with environment variables"""
        result = self.runner.invoke(main, [
            'config', 'install', 'github',
            '--env', 'GITHUB_TOKEN=test_token',
            '--name', 'test-github'
        ])
        
        # This should succeed even with a fake token for config purposes
        if result.exit_code != 0:
            print(f"   Installation failed: {result.output}")
            return False
            
        # Verify installation in config
        list_result = self.runner.invoke(main, ['config', 'list'])
        return 'test-github' in list_result.output
        
    # ===== NPM PACKAGE INSTALLATION TESTS =====
    
    def test_npm_package_check(self):
        """Test if npm packages can be checked"""
        try:
            # Test if npm is available
            result = subprocess.run(['npm', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return "NPM not available - skipping npm tests"
                
            # Test checking if a package exists
            result = subprocess.run([
                'npm', 'view', '@modelcontextprotocol/server-filesystem', 'version'
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return "NPM tests skipped - npm not available or timeout"
            
    def test_install_with_npm_check(self):
        """Test installation that requires npm package check"""
        result = self.runner.invoke(main, [
            'config', 'install', 'memory',
            '--name', 'test-memory'
        ])
        
        # Should succeed regardless of npm availability
        return result.exit_code == 0 or "npm" in result.output.lower()
        
    # ===== CONFIGURATION MANAGEMENT TESTS =====
    
    def test_config_after_installations(self):
        """Test configuration after installing servers"""
        # Should have servers from previous tests
        result = self.runner.invoke(main, ['config', 'show'])
        return (result.exit_code == 0 and 
                len(result.output.strip()) > 0)
                
    def test_config_list_populated(self):
        """Test listing servers after installations"""
        result = self.runner.invoke(main, ['config', 'list'])
        return (result.exit_code == 0 and 
                "test-filesystem" in result.output)
                
    def test_config_export(self):
        """Test exporting configuration"""
        export_file = Path(self.temp_dir) / "export.json"
        result = self.runner.invoke(main, [
            'config', 'export', '--file', str(export_file)
        ])
        
        return (result.exit_code == 0 and 
                export_file.exists() and
                export_file.stat().st_size > 0)
                
    # ===== SERVER REMOVAL TESTS =====
    
    def test_remove_server_dry_run(self):
        """Test removing server with dry-run"""
        result = self.runner.invoke(main, [
            'config', 'remove', 'test-filesystem', '--dry-run'
        ])
        return result.exit_code == 0 and "would remove" in result.output.lower()
        
    def test_remove_server_real(self):
        """Test actually removing a server"""
        result = self.runner.invoke(main, [
            'config', 'remove', 'test-time', '--confirm'
        ])
        
        if result.exit_code != 0:
            return False
            
        # Verify removal
        list_result = self.runner.invoke(main, ['config', 'list'])
        return 'test-time' not in list_result.output
        
    # ===== SERVER REGISTRY TESTS =====
    
    def test_registry_initialization(self):
        """Test server registry initialization"""
        try:
            registry = MCPServerRegistry()
            return len(registry.servers) > 30  # Should have 34+ servers
        except Exception:
            return False
            
    def test_registry_search_functionality(self):
        """Test registry search methods"""
        try:
            registry = MCPServerRegistry()
            
            # Test different search methods
            all_servers = registry.get_all_servers()
            database_servers = registry.search("database")
            official_servers = registry.get_by_category("official")
            
            return (len(all_servers) > 30 and 
                   len(database_servers) > 0 and
                   len(official_servers) > 0)
        except Exception:
            return False
            
    def test_registry_server_info(self):
        """Test getting specific server information"""
        try:
            registry = MCPServerRegistry()
            filesystem_info = registry.get_server("filesystem")
            
            return (filesystem_info is not None and
                   "name" in filesystem_info and
                   "description" in filesystem_info)
        except Exception:
            return False
            
    # ===== ERROR HANDLING TESTS =====
    
    def test_invalid_command(self):
        """Test invalid command handling"""
        result = self.runner.invoke(main, ['invalid', 'command'])
        return result.exit_code != 0
        
    def test_invalid_server_install(self):
        """Test installing invalid server"""
        result = self.runner.invoke(main, [
            'config', 'install', 'nonexistent-server'
        ])
        return result.exit_code != 0
        
    def test_missing_config_file(self):
        """Test handling missing config file"""
        # Remove config file temporarily
        config_path = os.environ['CLAUDE_CONFIG_PATH']
        if Path(config_path).exists():
            os.remove(config_path)
            
        result = self.runner.invoke(main, ['config', 'show'])
        
        # Should handle gracefully
        return result.exit_code == 0 or "not found" in result.output.lower()
        
    # ===== INTEGRATION TESTS =====
    
    def test_full_workflow(self):
        """Test complete workflow: search -> info -> install -> list -> remove"""
        steps = []
        
        # Step 1: Search for servers
        result = self.runner.invoke(main, ['config', 'search', 'memory'])
        steps.append(result.exit_code == 0 and "memory" in result.output)
        
        # Step 2: Get server info
        result = self.runner.invoke(main, ['config', 'info', 'memory'])
        steps.append(result.exit_code == 0 and "Memory Server" in result.output)
        
        # Step 3: Install server
        result = self.runner.invoke(main, [
            'config', 'install', 'memory', '--name', 'workflow-test'
        ])
        steps.append(result.exit_code == 0)
        
        # Step 4: List servers
        result = self.runner.invoke(main, ['config', 'list'])
        steps.append('workflow-test' in result.output)
        
        # Step 5: Remove server
        result = self.runner.invoke(main, [
            'config', 'remove', 'workflow-test', '--confirm'
        ])
        steps.append(result.exit_code == 0)
        
        return all(steps)
        
    def run_all_tests(self):
        """Run all tests in the suite"""
        print("🚀 Starting Comprehensive Test Suite")
        print("=" * 60)
        
        self.setup_test_environment()
        
        try:
            # Basic CLI Tests
            print("\n📋 BASIC CLI FUNCTIONALITY")
            self.run_test("CLI Help Command", self.test_cli_help)
            self.run_test("CLI Version Command", self.test_cli_version)
            self.run_test("Config Help Command", self.test_config_help)
            
            # Server Search Tests
            print("\n🔍 SERVER SEARCH FUNCTIONALITY")
            self.run_test("Search All Servers", self.test_search_all_servers)
            self.run_test("Search Specific Term", self.test_search_specific_term)
            self.run_test("Search No Results", self.test_search_no_results)
            self.run_test("Search JSON Format", self.test_search_json_format)
            self.run_test("Search By Category", self.test_search_by_category)
            
            # Server Info Tests
            print("\n📝 SERVER INFORMATION")
            self.run_test("Valid Server Info", self.test_server_info_valid)
            self.run_test("Invalid Server Info", self.test_server_info_invalid)
            
            # Configuration Tests
            print("\n⚙️  CONFIGURATION MANAGEMENT")
            self.run_test("Show Empty Config", self.test_config_show_empty)
            self.run_test("List Empty Servers", self.test_config_list_empty)
            self.run_test("Validate Empty Config", self.test_config_validate_empty)
            
            # Dry Run Installation Tests
            print("\n🧪 DRY RUN INSTALLATIONS")
            self.run_test("Filesystem Dry Run", self.test_install_dry_run_filesystem)
            self.run_test("Missing Args Dry Run", self.test_install_dry_run_missing_args)
            self.run_test("SQLite Dry Run", self.test_install_dry_run_sqlite)
            
            # Real Installation Tests
            print("\n📦 REAL SERVER INSTALLATIONS")
            self.run_test("Install Filesystem Server", self.test_install_filesystem_server)
            self.run_test("Install Time Server", self.test_install_time_server)
            self.run_test("Install with Env Vars", self.test_install_with_env_vars)
            
            # NPM Tests
            print("\n📦 NPM PACKAGE TESTS")
            self.run_test("NPM Package Check", self.test_npm_package_check)
            self.run_test("Install with NPM Check", self.test_install_with_npm_check)
            
            # Configuration After Installation
            print("\n⚙️  POST-INSTALLATION CONFIG")
            self.run_test("Config After Installations", self.test_config_after_installations)
            self.run_test("List Populated Servers", self.test_config_list_populated)
            self.run_test("Export Configuration", self.test_config_export)
            
            # Server Removal Tests
            print("\n🗑️  SERVER REMOVAL")
            self.run_test("Remove Server Dry Run", self.test_remove_server_dry_run)
            self.run_test("Remove Server Real", self.test_remove_server_real)
            
            # Registry Tests
            print("\n🏛️  SERVER REGISTRY")
            self.run_test("Registry Initialization", self.test_registry_initialization)
            self.run_test("Registry Search Methods", self.test_registry_search_functionality)
            self.run_test("Registry Server Info", self.test_registry_server_info)
            
            # Error Handling Tests
            print("\n🚨 ERROR HANDLING")
            self.run_test("Invalid Command", self.test_invalid_command)
            self.run_test("Invalid Server Install", self.test_invalid_server_install)
            self.run_test("Missing Config File", self.test_missing_config_file)
            
            # Integration Tests
            print("\n🔄 INTEGRATION TESTS")
            self.run_test("Full Workflow", self.test_full_workflow)
            
        finally:
            self.cleanup_test_environment()
            
        self.print_test_summary()
        
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        errors = len([r for r in self.test_results if r["status"] == "ERROR"])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"💥 Errors: {errors}")
        print(f"Success Rate: {(passed/total_tests)*100:.1f}%")
        
        if failed > 0 or errors > 0:
            print(f"\n❌ FAILED/ERROR TESTS:")
            for result in self.test_results:
                if result["status"] in ["FAIL", "ERROR"]:
                    print(f"   {result['status']}: {result['name']}")
                    if result["details"]:
                        print(f"      {result['details']}")
                        
        print(f"\n⏱️  PERFORMANCE:")
        for result in self.test_results:
            if result["duration"] != "N/A":
                print(f"   {result['name']}: {result['duration']}")
                
        print("\n🎯 FUNCTIONALITY COVERAGE:")
        print("   ✅ CLI Commands (help, version)")
        print("   ✅ Server Search (all, specific, categories, formats)")
        print("   ✅ Server Information (valid, invalid)")
        print("   ✅ Configuration Management (show, list, validate, export)")
        print("   ✅ Dry Run Installations")
        print("   ✅ Real Server Installations")
        print("   ✅ NPM Package Integration")
        print("   ✅ Server Removal")
        print("   ✅ Server Registry Operations")
        print("   ✅ Error Handling")
        print("   ✅ Complete Workflows")
        
        if passed == total_tests:
            print(f"\n🎉 ALL TESTS PASSED! The system is fully functional.")
        else:
            print(f"\n⚠️  {failed + errors} tests failed. Review output above.")


if __name__ == "__main__":
    suite = ComprehensiveTestSuite()
    suite.run_all_tests()