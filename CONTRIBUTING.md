# Contributing to Claude Desktop MCP Playground

Thank you for your interest in contributing! This guide will help you get started with contributing to the Claude Desktop MCP Playground project.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/claude-desktop-mcp-playground.git
   cd claude-desktop-mcp-playground
   ```
3. **Set up development environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   
   pip install -e .
   ./setup-pg-command.sh      # or .ps1 on Windows
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🛠️ Development Setup

### Prerequisites
- Python 3.9+ (3.10+ recommended)
- Node.js 16+ (for MCP server testing)
- Git

### Installation
```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

### Testing
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=claude_desktop_mcp

# Run specific test file
pytest tests/test_cli.py -v

# Run tests for specific functionality
pytest -k "test_server_registry"
```

### Code Quality
```bash
# Format code
black .
isort .

# Lint code
flake8 .
mypy .

# All quality checks
black . && isort . && flake8 . && mypy .
```

## 📝 Types of Contributions

### 🐛 Bug Reports
When reporting bugs, please include:
- **Description**: Clear description of the issue
- **Environment**: OS, Python version, Claude Desktop version
- **Steps to reproduce**: Minimal steps to recreate the issue
- **Expected vs actual behavior**
- **Logs**: Any relevant error messages or logs

### ✨ Feature Requests
For new features, please:
- **Check existing issues** to avoid duplicates
- **Describe the use case** and why it's valuable
- **Provide examples** of how it would work
- **Consider implementation** complexity and alternatives

### 🔧 Code Contributions

#### Adding New MCP Servers
To add a new server to the registry:

1. **Research the server**:
   - Verify it's listed in the [official MCP servers repository](https://github.com/modelcontextprotocol/servers)
   - Check installation method (npm, git, etc.)
   - Identify required arguments and environment variables

2. **Update the registry** in `claude_desktop_mcp/server_registry.py`:
   ```python
   "server-id": {
       "name": "Server Name",
       "description": "Brief description of what the server does",
       "category": "official" or "community",
       "package": "npm-package-name or git-repo",
       "install_method": "npm" or "git",
       "command": "npx" or "git",
       "args_template": ["-y", "package-name", "<arg1>"],
       "required_args": ["arg1"],
       "optional_args": [],
       "env_vars": {"ENV_VAR": "Description"},
       "setup_help": "Setup instructions",
       "example_usage": "Example use case",
       "homepage": "https://github.com/..."
   }
   ```

3. **Test the server**:
   ```bash
   pg config search your-server
   pg config info your-server
   pg config install your-server --dry-run
   ```

4. **Add tests**:
   ```python
   def test_new_server_in_registry():
       registry = MCPServerRegistry()
       server = registry.get_server("your-server")
       assert server is not None
       assert server["category"] in ["official", "community"]
   ```

#### Improving CLI Commands
- Follow Click framework conventions
- Add help text and examples
- Include error handling and validation
- Test all command options and edge cases

#### Cross-Platform Compatibility
- Use `pathlib.Path` for file operations
- Test on Windows, macOS, and Linux
- Handle shell differences (.bashrc vs .zshrc vs PowerShell)
- Consider case sensitivity and path separators

## 📚 Documentation

### User Documentation
- Keep README.md updated with new features
- Update CLI help text and examples
- Add troubleshooting sections for common issues

### Developer Documentation
- Update CLAUDE.md for code changes
- Document new functions and classes
- Include type hints and docstrings
- Update architecture documentation for significant changes

## 🔄 Pull Request Process

### Before Submitting
1. **Ensure tests pass**: `pytest tests/`
2. **Check code quality**: `black . && isort . && flake8 .`
3. **Update documentation** as needed
4. **Test on multiple platforms** if possible
5. **Squash commits** into logical units

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Tested on multiple platforms

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process
1. **Automated checks** must pass (tests, linting)
2. **Code review** by maintainers
3. **Testing** on different platforms
4. **Documentation** review
5. **Merge** after approval

## 🎯 Coding Standards

### Python Style
- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Include type hints for all functions
- Write descriptive docstrings

### Commit Messages
Use [Conventional Commits](https://conventionalcommits.org/) format:
```
type(scope): description

feat(registry): add support for new MCP server
fix(cli): handle missing configuration file
docs(readme): update installation instructions
test(config): add tests for edge cases
```

### Testing Guidelines
- Write unit tests for new functions
- Include integration tests for CLI commands
- Test error conditions and edge cases
- Mock external dependencies
- Aim for good test coverage (>80%)

## 🆘 Getting Help

- **Documentation**: Check [docs/](docs/) directory
- **Issues**: Search existing [GitHub issues](https://github.com/seanpoyner/claude-desktop-mcp-playground/issues)
- **Discussions**: Start a [GitHub discussion](https://github.com/seanpoyner/claude-desktop-mcp-playground/discussions)
- **Chat**: Join community discussions (links TBD)

## 🙏 Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md) file
- GitHub contributors list
- Release notes for significant contributions

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License that covers the project.

---

Thank you for contributing to Claude Desktop MCP Playground! 🎉