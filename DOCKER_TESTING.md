# Docker Testing Guide for MCP Server Manager

This guide explains how to use Docker for testing the MCP Server Manager across different environments.

## Quick Start

### Basic Testing Environment
```bash
# Build and run the test container
docker-compose up -d mcp-test

# Enter the container
docker-compose exec mcp-test bash

# Run tests
make test
```

### Windows Compatibility Testing
```bash
# Build and run Wine-based Windows environment
docker-compose up -d mcp-wine-test

# Enter Windows environment
docker-compose exec mcp-wine-test wine cmd
```

## Available Docker Configurations

### 1. Linux Testing Environment (`Dockerfile`)
- Full Python/Node.js development environment
- Includes Wine for basic Windows testing
- Automated test execution
- GUI development dependencies

### 2. Wine-based Windows Testing (`Dockerfile.wine`)
- Windows Python and Node.js via Wine
- Windows file paths and environment variables
- PowerShell script testing
- Windows installer simulation

## Testing Workflows

### CLI Testing
```bash
# In Linux container
docker-compose exec mcp-test bash
pg --help
pg config search database
pg setup --quick

# In Wine container (Windows commands)
docker-compose exec mcp-wine-test wine cmd
python pg --help
python pg config search database
```

### Installation Testing
```bash
# Test Linux installation
docker-compose exec mcp-test bash -c "./install-full.sh"

# Test Windows installation (simulated)
docker-compose exec mcp-wine-test wine powershell -File "install-full.ps1"
```

### Cross-Platform Path Testing
```bash
# Linux paths
docker-compose exec mcp-test python -c "from claude_desktop_mcp.config_manager import get_config_path; print(get_config_path())"

# Windows paths (Wine)
docker-compose exec mcp-wine-test wine python -c "from claude_desktop_mcp.config_manager import get_config_path; print(get_config_path())"
```

## Development Workflow

### Live Code Mounting
The docker-compose.yml mounts your local code:
```yaml
volumes:
  - ./claude_desktop_mcp:/app/claude_desktop_mcp
  - ./tests:/app/tests
```

Changes to your local files are immediately reflected in the container.

### Running Specific Tests
```bash
# Run specific test file
docker-compose exec mcp-test pytest tests/test_cli.py -v

# Run with coverage
docker-compose exec mcp-test pytest --cov=claude_desktop_mcp tests/
```

### GUI Development
```bash
# Start GUI dev server in container
docker-compose exec mcp-test bash -c "cd mcp-gui && npm run dev"

# Access via browser on host at http://localhost:3000
```

## Windows Testing Limitations

### Docker Limitations
- Windows containers require Windows hosts
- Wine provides compatibility layer, not true Windows
- Some Windows-specific features may not work correctly
- Registry operations are simulated

### Recommended Alternatives

#### 1. Windows Virtual Machine (Recommended)
```bash
# Using VirtualBox
1. Download Windows 10/11 ISO
2. Create VM with 4GB RAM, 30GB disk
3. Install Windows
4. Clone repository and test

# Using VMware or Hyper-V
Similar process with respective virtualization software
```

#### 2. GitHub Actions (CI/CD)
```yaml
# .github/workflows/test.yml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
```

#### 3. WSL2 on Windows
For Windows users, WSL2 provides Linux environment:
```bash
# In WSL2
git clone <repository>
./install-full.sh
pg setup
```

## Container Management

### View Logs
```bash
# View container logs
docker-compose logs -f mcp-test

# View specific service
docker-compose logs -f mcp-wine-test
```

### Clean Up
```bash
# Stop containers
docker-compose down

# Remove volumes (reset state)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache
```

### Resource Usage
```bash
# Check container stats
docker stats

# Limit resources in docker-compose.yml
services:
  mcp-test:
    mem_limit: 2g
    cpus: '2.0'
```

## Testing Checklist

### Linux Container Tests
- [ ] CLI commands work (`pg --help`)
- [ ] Server search functions (`pg config search`)
- [ ] Installation completes (`./install-full.sh`)
- [ ] Python tests pass (`pytest`)
- [ ] GUI builds successfully (`npm run build`)

### Wine Container Tests  
- [ ] Windows Python runs (`wine python --version`)
- [ ] CLI works in Wine (`wine python pg --help`)
- [ ] PowerShell scripts execute
- [ ] Windows paths are correct
- [ ] Config file locations match Windows

### Cross-Platform Tests
- [ ] Path handling works on both platforms
- [ ] Configuration files are created correctly
- [ ] Package installation methods work
- [ ] Environment variables are handled properly

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs mcp-test

# Rebuild image
docker-compose build mcp-test
```

### Wine Issues
```bash
# Reset Wine prefix
docker-compose exec mcp-wine-test rm -rf /root/.wine
docker-compose exec mcp-wine-test winecfg
```

### Permission Issues
```bash
# Fix file permissions
docker-compose exec mcp-test chown -R root:root /app
```

### Network Issues
```bash
# Check network
docker network ls
docker network inspect claude-desktop-mcp-playground_mcp-network
```

## Advanced Usage

### Custom Testing Image
```dockerfile
# Dockerfile.test
FROM mcp-server-manager-test
RUN pip install pytest-xdist pytest-timeout
RUN apt-get update && apt-get install -y postgresql-client
```

### Integration Testing
```bash
# Start with dependencies
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
docker-compose exec mcp-test pytest tests/integration/ -v
```

### Performance Testing
```bash
# Run performance benchmarks
docker-compose exec mcp-test python -m pytest tests/performance/ --benchmark-only
```

## Security Considerations

- Don't include sensitive data in images
- Use secrets for API keys
- Scan images for vulnerabilities
- Keep base images updated

## Conclusion

Docker provides a consistent testing environment but has limitations for Windows testing. For production Windows testing, use:
1. Native Windows machines
2. Windows VMs
3. CI/CD with Windows runners

The provided Docker setup is excellent for:
- Linux development and testing
- Basic Windows compatibility checks
- CI/CD pipeline development
- Cross-platform behavior verification