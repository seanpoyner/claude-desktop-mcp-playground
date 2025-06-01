# Contributing to Claude Desktop MCP Playground

## Welcome Contributors!

We appreciate your interest in contributing to the Claude Desktop Model Context Protocol (MCP) Playground. This document provides guidelines for contributing to the project.

## Code of Conduct

Our project is committed to providing a welcoming and inspiring community for all. All participants are expected to adhere to our Code of Conduct.

## How to Contribute

### 1. Reporting Issues

- Use GitHub Issues to report bugs
- Provide a clear and descriptive title
- Include steps to reproduce the issue
- Specify your environment (OS, Python version, etc.)
- Add error messages or screenshots if applicable

### 2. Feature Requests

- Open a GitHub Issue
- Describe the feature in detail
- Explain the use case and potential benefits
- Discuss potential implementation approaches

### 3. Development Process

#### Setting Up Development Environment

1. Fork the repository
2. Clone your fork
   ```bash
   git clone https://github.com/your-username/claude-desktop-mcp-playground.git
   cd claude-desktop-mcp-playground
   ```

3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
   or by using uv:
   ```bash
   uv venv
   source .venv/bin/activate
   ```

4. Install development dependencies
   ```bash
   pip install -r requirements.txt
   ```

#### Creating a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
```

#### Coding Guidelines

- Follow PEP 8 style guide
- Write clear, commented code
- Include type hints
- Write unit tests for new functionality
- Ensure all tests pass before submitting

#### Commit Messages

- Use clear and descriptive commit messages
- Follow conventional commit format:
  ```
  type(scope): description
  
  Optional detailed explanation
  ```
- Example types: feat, fix, docs, test, chore

### 4. Pull Request Process

1. Ensure your code passes all tests
2. Update documentation as needed
3. Submit a pull request with:
   - Clear title
   - Description of changes
   - Reference any related issues

### 5. Code Review Process

- All submissions require review
- Maintainers may request changes
- Be open to feedback and collaboration

## Development Setup

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test module
pytest tests/test_agent_framework.py

# Generate coverage report
pytest --cov=claude_desktop_mcp
```

### Documentation

- Update README and docs for any changes
- Use docstrings for all functions and classes
- Generate documentation using Sphinx

## Questions?

If you have any questions about contributing, please open an issue with the "question" label.

## License

By contributing, you agree that your contributions will be licensed under the project's license.
