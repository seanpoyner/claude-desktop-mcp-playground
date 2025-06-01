# Testing Guide

Comprehensive testing guide for Claude Desktop MCP Playground.

## 🧪 Test Framework

This project uses **pytest** as the primary testing framework with additional tools for coverage and mocking.

### Test Structure
```
tests/
├── conftest.py                 # Test configuration and fixtures
├── test_cli.py                 # CLI command tests
├── test_config_manager.py      # Configuration management tests
└── test_import_script.py       # Import functionality tests
```

## 🚀 Running Tests

### Basic Test Commands
```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_cli.py

# Run specific test function
pytest tests/test_cli.py::test_version_command

# Run tests matching pattern
pytest -k "config"
```

### Coverage Testing
```bash
# Run tests with coverage
pytest --cov=claude_desktop_mcp

# Generate HTML coverage report
pytest --cov=claude_desktop_mcp --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

### Parallel Testing
```bash
# Install pytest-xdist for parallel testing
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

## 🔍 Test Categories

### Unit Tests
Test individual components in isolation:

```python
def test_server_registry_search():
    """Test server registry search functionality"""
    registry = MCPServerRegistry()
    results = registry.search("database")
    assert len(results) > 0
    assert any("postgres" in r["id"] for r in results)
```

### Integration Tests
Test CLI commands end-to-end:

```python
def test_config_search_command():
    """Test pg config search command"""
    runner = CliRunner()
    result = runner.invoke(cli, ['config', 'search', 'database'])
    assert result.exit_code == 0
    assert "postgres" in result.output
```

### Configuration Tests
Test Claude Desktop config file handling:

```python
def test_config_file_parsing():
    """Test configuration file parsing"""
    config_manager = ConfigManager()
    test_config = {"mcpServers": {"test": {"command": "test"}}}
    
    # Test parsing and validation
    parsed = config_manager.parse_config(test_config)
    assert "test" in parsed
```

## 🛠️ Test Fixtures

### Common Fixtures (conftest.py)
```python
@pytest.fixture
def temp_config_file():
    """Create temporary config file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"mcpServers": {}}, f)
        yield f.name
    os.unlink(f.name)

@pytest.fixture
def mock_registry():
    """Mock server registry for testing"""
    registry = MCPServerRegistry()
    # Add test servers
    registry.servers["test-server"] = {
        "name": "Test Server",
        "description": "Test description",
        "category": "community"
    }
    return registry
```

### CLI Testing Fixtures
```python
@pytest.fixture
def cli_runner():
    """Click CLI test runner"""
    return CliRunner()

@pytest.fixture
def isolated_filesystem():
    """Isolated filesystem for file operations"""
    with CliRunner().isolated_filesystem():
        yield
```

## 🎯 Testing Best Practices

### Test Organization
- **One test per function/behavior**
- **Descriptive test names** that explain what's being tested
- **Arrange-Act-Assert** pattern
- **Test both success and failure cases**

### Example Test Structure
```python
def test_server_installation_with_valid_args():
    """Test successful server installation with valid arguments"""
    # Arrange
    registry = MCPServerRegistry()
    server_id = "filesystem"
    args = {"path": "/test/path"}
    
    # Act
    result = registry.generate_install_command(server_id, args)
    
    # Assert
    assert result is not None
    assert result["server_id"] == server_id
    assert "/test/path" in result["args"]
```

### Mocking External Dependencies
```python
@mock.patch('claude_desktop_mcp.config_manager.Path.exists')
def test_config_file_not_found(mock_exists):
    """Test handling when config file doesn't exist"""
    # Arrange
    mock_exists.return_value = False
    config_manager = ConfigManager()
    
    # Act & Assert
    with pytest.raises(FileNotFoundError):
        config_manager.load_config()
```

## 🔧 Test Configuration

### pytest.ini Configuration
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### Coverage Configuration (.coveragerc)
```ini
[run]
source = claude_desktop_mcp
omit = 
    */tests/*
    */venv/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## 🚦 Continuous Integration

### GitHub Actions Testing
Tests run automatically on:
- **Pull requests** to main branch
- **Pushes** to main branch
- **Multiple Python versions** (3.9, 3.10, 3.11)
- **Multiple platforms** (Ubuntu, Windows, macOS)

### Test Matrix
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ["3.9", "3.10", "3.11"]
```

## 🐛 Debugging Tests

### Running Specific Tests
```bash
# Run only failed tests from last run
pytest --lf

# Stop on first failure
pytest -x

# Drop into debugger on failures
pytest --pdb

# Show local variables in traceback
pytest -l
```

### Test Output and Logging
```bash
# Show print statements
pytest -s

# Show all output
pytest --capture=no

# Set log level
pytest --log-level=DEBUG
```

## 📊 Test Coverage Goals

### Current Coverage Targets
- **Overall**: >85%
- **Core modules**: >90%
- **CLI commands**: >80%
- **Configuration management**: >95%

### Coverage Reports
```bash
# Generate coverage report
pytest --cov=claude_desktop_mcp --cov-report=term-missing

# Check coverage without running tests
coverage report

# Generate HTML report
coverage html
```

## ✅ Pre-commit Testing

### Setup Pre-commit Hooks
```bash
pip install pre-commit
pre-commit install
```

### Pre-commit Configuration (.pre-commit-config.yaml)
```yaml
repos:
  - repo: local
    hooks:
      - id: tests
        name: tests
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

## 🔄 Test Automation

### Test Commands for Development
```bash
# Quick test during development
pytest tests/ -x --tb=short

# Full test suite with coverage
pytest --cov=claude_desktop_mcp --cov-report=html

# Test specific functionality
pytest -k "registry" -v

# Performance testing
pytest --durations=10
```

### Testing Different Scenarios
```bash
# Test with different Python versions
tox

# Test installation process
pytest tests/test_import_script.py -v

# Test CLI commands
pytest tests/test_cli.py -v

# Test configuration handling
pytest tests/test_config_manager.py -v
```

## 📚 Writing New Tests

### Test Checklist
- [ ] Test covers main functionality
- [ ] Test includes error cases
- [ ] Test is isolated (no external dependencies)
- [ ] Test has descriptive name and docstring
- [ ] Test follows AAA pattern (Arrange-Act-Assert)
- [ ] Test uses appropriate fixtures
- [ ] Test mocks external calls
- [ ] Test assertions are specific

### Example New Test
```python
def test_new_feature():
    """Test description of what this test verifies"""
    # Arrange
    setup_test_data()
    
    # Act
    result = function_under_test(test_input)
    
    # Assert
    assert result.is_expected()
    assert result.has_correct_properties()
```

## 🧪 Manual Testing

### Quick Test Commands
```bash
# Test server search functionality
pg config search database

# Test server information display
pg config info filesystem

# Test dry-run installation
pg config install filesystem --dry-run --arg path=/test

# Test configuration management
pg config show
pg config list
```

### Installation Testing
```bash
# Test one-line installer (in safe environment)
curl -sSL https://raw.githubusercontent.com/seanpoyner/claude-desktop-mcp-playground/main/install-full.sh | bash

# Test manual PATH setup
./setup-pg-command.sh

# Verify pg command works globally
pg --version
pg --help
```

### Cross-Platform Testing
- **Linux**: Test with different distributions (Ubuntu, CentOS, Arch)
- **macOS**: Test with/without Homebrew
- **Windows**: Test with PowerShell and Command Prompt

---

**Happy Testing! 🧪**