# Claude Desktop MCP Installation Guide

## Supported Platforms

- Windows 10/11 (64-bit)
- macOS 11.0+ (Big Sur and later)
- Linux (Ubuntu 20.04+, Fedora 33+)

## Installation Methods

### 1. Pip Installation

```bash
# Recommended for most users
pip install claude-desktop-mcp

# For development version
pip install git+https://github.com/your-org/claude-desktop-mcp.git
```

### 2. Local Development Setup

1. Clone the repository
   ```bash
   git clone https://github.com/your-org/claude-desktop-mcp.git
   cd claude-desktop-mcp
   ```

2. Create virtual environment
   ```bash
   python -m venv mcp-env
   source mcp-env/bin/activate  # Activation varies by OS
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in editable mode
   ```

## Configuration Requirements

### API Credentials

1. Obtain Anthropic API key from [Anthropic Console](https://console.anthropic.com)
2. Set environment variable
   ```bash
   # Linux/macOS
   export ANTHROPIC_API_KEY='your-api-key-here'

   # Windows (PowerShell)
   $env:ANTHROPIC_API_KEY = 'your-api-key-here'
   ```

3. Alternatively, create a `.env` file in the project root
   ```
   ANTHROPIC_API_KEY=your-api-key-here
   ```

## Verification

Verify installation by running:
```bash
claude-desktop-mcp --version
claude-desktop-mcp doctor  # Checks system compatibility
```

## Potential Installation Issues

- Ensure Python 3.8+ is installed
- Check pip is up to date: `pip install --upgrade pip`
- Verify virtual environment activation
- Resolve any dependency conflicts

## System Requirements

- Minimum 8GB RAM
- 20GB free disk space
- Stable internet connection
- Python 3.8-3.11 recommended

## Next Steps

- [Configure Basic Settings](03-basic-configuration.md)
- [Explore Productivity Workflows](05-productivity-workflows.md)
