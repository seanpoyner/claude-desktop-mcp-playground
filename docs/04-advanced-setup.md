# Advanced Claude Desktop MCP Setup

## Advanced Configuration Management

### Custom MCP Server Development

Create your own MCP servers for specialized workflows:

```python
# example_server.py
from mcp.server import Server
from mcp.types import Tool

server = Server("my-custom-server")

@server.tool()
def process_data(input_data: str) -> str:
    """Custom data processing tool"""
    return f"Processed: {input_data}"

if __name__ == "__main__":
    server.run()
```

Then add to your configuration:
```bash
pg config add my-custom-server "python" \
  --args "example_server.py" \
  --env "LOG_LEVEL=DEBUG"
```

## Advanced Configuration Patterns

### Environment-Specific Configurations

Manage different environments with separate simplified configs:

```bash
# Development environment
pg config import --output dev_config.json

# Production environment  
pg config import --output prod_config.json

# Apply specific environment
pg config apply dev_config.json
```

### Conditional Server Enablement

Edit your simplified config to enable servers based on context:

```json
{
  "development-tools": {
    "command": "python",
    "args": ["-m", "dev_tools"],
    "env": {"ENV": "development"},
    "enabled": true
  },
  "production-monitor": {
    "command": "python", 
    "args": ["-m", "prod_monitor"],
    "env": {"ENV": "production"},
    "enabled": false
  }
}
```

## Complex MCP Server Configurations

### Multi-Service Server Setup

```bash
# Database integration
pg config add database-server "python" \
  --args "-m" --args "database_mcp.server" \
  --env "DB_HOST=localhost" \
  --env "DB_PORT=5432" \
  --env "DB_NAME=workspace"

# API integration
pg config add api-gateway "node" \
  --args "api_server.js" \
  --env "API_KEY_FILE=/secure/api.key" \
  --env "RATE_LIMIT=1000"

# File processing service
pg config add file-processor "go" \
  --args "run" --args "./cmd/processor" \
  --env "WORKSPACE_DIR=/workspace" \
  --env "MAX_FILE_SIZE=10MB"
```

### Server Health Monitoring

Create a monitoring configuration:

```json
{
  "health-monitor": {
    "command": "python",
    "args": ["-m", "health_check"],
    "env": {
      "CHECK_INTERVAL": "30",
      "ALERT_WEBHOOK": "https://hooks.slack.com/..."
    },
    "enabled": true
  }
}
```

## Server Development Best Practices

### Error Handling

```python
# robust_server.py
import logging
from mcp.server import Server
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = Server("robust-server")

@server.tool()
def safe_operation(data: str) -> str:
    try:
        # Your processing logic here
        result = process_data(data)
        logger.info(f"Successfully processed: {data}")
        return result
    except Exception as e:
        logger.error(f"Error processing {data}: {e}")
        return f"Error: {str(e)}"
```

### Configuration Validation

```bash
# Always validate before applying
pg config validate

# Test individual servers
python -m my_server --test

# Check server connectivity
curl -f http://localhost:8000/health || echo "Server not responding"
```

## Backup and Recovery

### Configuration Backup Strategy

```bash
# Create timestamped backup
DATE=$(date +%Y%m%d_%H%M%S)
pg config import --output "backup_${DATE}.json"

# Restore from backup
pg config apply backup_20241201_143022.json

# Version control your configs
git add *.json
git commit -m "Update MCP server configuration"
```

## Security Considerations

### Secure Environment Variables

```bash
# Use secure credential storage
pg config add secure-server "python" \
  --args "-m" --args "secure_server" \
  --env "CREDENTIAL_FILE=/secure/creds.enc" \
  --env "KEY_ROTATION_INTERVAL=86400"
```

### Network Security

```json
{
  "secure-api-server": {
    "command": "python",
    "args": ["-m", "api_server"],
    "env": {
      "BIND_HOST": "127.0.0.1",
      "TLS_CERT": "/certs/server.crt",
      "TLS_KEY": "/certs/server.key",
      "ALLOWED_ORIGINS": "https://trusted-domain.com"
    },
    "enabled": true
  }
}
```

## Performance Optimization

### Resource Management

Monitor and optimize your MCP servers:

```bash
# Monitor server resource usage
pg config add resource-monitor "python" \
  --args "-m" --args "resource_monitor" \
  --env "MEMORY_LIMIT=1GB" \
  --env "CPU_LIMIT=80"
```

### Load Balancing

For high-throughput scenarios:

```json
{
  "load-balancer": {
    "command": "nginx",
    "args": ["-c", "/etc/nginx/mcp.conf"],
    "env": {
      "UPSTREAM_SERVERS": "server1:8001,server2:8002,server3:8003"
    },
    "enabled": true
  }
}
```

## Testing and Debugging

### Development Workflow

```bash
# Test configuration without applying
pg config validate

# Enable debug logging
pg config add debug-server "python" \
  --args "-m" --args "my_server" \
  --env "LOG_LEVEL=DEBUG" \
  --env "DEBUG_MODE=true"

# Monitor logs in real-time
tail -f ~/.config/Claude/logs/mcp-server.log
```

### Integration Testing

```python
# test_integration.py
import subprocess
import json

def test_mcp_server():
    # Start server
    process = subprocess.Popen(["python", "-m", "my_server"])
    
    try:
        # Test server functionality
        result = subprocess.run(
            ["pg", "config", "validate"],
            capture_output=True, text=True
        )
        assert result.returncode == 0
    finally:
        process.terminate()
```

## Next Steps

- [Explore Productivity Workflows](05-productivity-workflows.md)
- [Learn Agentic Experimentation](06-agentic-experimentation.md)
- [Troubleshooting Guide](07-troubleshooting.md)