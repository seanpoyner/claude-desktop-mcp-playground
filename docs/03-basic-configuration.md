# Basic Configuration for Claude Desktop MCP

## Configuration Overview

The Claude Desktop MCP uses a flexible configuration system to customize your workflow and agent environments.

## Configuration File Location

Configurations are managed through:
- Global configuration: `~/.claude-desktop-mcp/config.yaml`
- Project-specific: `./mcp-config.yaml`

## Core Configuration Sections

### 1. API Settings

```yaml
api:
  provider: anthropic
  model: claude-3-5-sonnet-20240620
  max_tokens: 4096
  temperature: 0.7
  timeout: 60
```

### 2. Agent Defaults

```yaml
agent_defaults:
  max_iterations: 10
  memory_size: 5
  verbose: false
  logging:
    level: INFO
    path: ./logs
```

### 3. Workflow Configurations

```yaml
workflows:
  default_timeout: 3600  # 1 hour max per workflow
  retry_attempts: 3
  error_handling: 
    mode: graceful
    notification: email
```

## Environment Setup

Create a `.env` file or use environment variables:

```bash
# API Configuration
CLAUDE_MCP_API_KEY=your_anthropic_api_key
CLAUDE_MCP_WORKSPACE=/path/to/workspace

# Logging Configuration
CLAUDE_MCP_LOG_LEVEL=INFO
CLAUDE_MCP_LOG_PATH=./logs
```

## Customization Example

Full configuration example:

```yaml
# ~/.claude-desktop-mcp/config.yaml
version: 1.0

api:
  provider: anthropic
  model: claude-3-5-sonnet-20240620
  max_tokens: 4096
  temperature: 0.7

agent_defaults:
  max_iterations: 10
  memory_size: 5
  verbose: false
  logging:
    level: INFO
    path: ./logs

workflows:
  default_timeout: 3600
  retry_attempts: 3
  error_handling:
    mode: graceful
    notification: email

plugins:
  enabled:
    - productivity_tracker
    - code_assistant
    - research_helper

security:
  encryption: true
  api_key_protection: true
```

## Configuration Management Commands

```bash
# Validate configuration
claude-desktop-mcp config validate

# View current configuration
claude-desktop-mcp config show

# Reset to default configuration
claude-desktop-mcp config reset
```

## Best Practices

- Keep API keys secure and out of version control
- Use environment-specific configurations
- Regularly update and review your settings
- Use encryption for sensitive configurations

## Troubleshooting

- Ensure YAML syntax is correct
- Check file permissions
- Verify API credentials
- Validate configuration with provided commands

## Next Steps

- [Advanced Server Setup](04-advanced-setup.md)
- [Productivity Workflows](05-productivity-workflows.md)
