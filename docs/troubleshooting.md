# Troubleshooting Guide

Common issues and solutions for Claude Desktop MCP Playground.

## 🚨 Quick Diagnostics

Before diving into specific issues, run these commands to check your setup:

```bash
# Check if pg command is available
pg --version

# Check dependencies
pg setup --deps-only

# Validate configuration
pg config validate

# Show current setup
pg config show
```

## 🔧 Installation Issues

### "Command not found: pg"

**Problem**: The `pg` command is not available in your PATH.

**Solutions**:

1. **Reload shell configuration**:
   ```bash
   source ~/.bashrc    # Bash
   source ~/.zshrc     # Zsh
   ```

2. **Restart your terminal** completely

3. **Re-run PATH setup**:
   ```bash
   # Linux/macOS
   ./setup-pg-command.sh
   
   # Windows
   .\setup-pg-command.ps1
   ```

4. **Check PATH manually**:
   ```bash
   echo $PATH | grep -o ~/.local/bin    # Linux/macOS
   echo $env:PATH | Select-String Scripts    # Windows
   ```

5. **Use absolute path temporarily**:
   ```bash
   ~/.local/bin/pg --version    # Linux/macOS
   %USERPROFILE%\Scripts\pg.cmd --version    # Windows
   ```

### Installation Script Fails

**Problem**: One-line installer fails with errors.

**Common causes and solutions**:

1. **Permission denied**:
   ```bash
   # Linux/macOS: Check if you have write permissions
   ls -la ~/.local/bin/
   
   # Windows: Run PowerShell as Administrator
   ```

2. **Network issues**:
   ```bash
   # Test connectivity
   curl -I https://github.com
   
   # Use manual installation instead
   git clone https://github.com/seanpoyner/claude-desktop-mcp-playground.git
   ```

3. **Python/Node.js missing**:
   ```bash
   # Check versions
   python --version
   node --version
   
   # Install missing dependencies manually
   ```

### Dependencies Not Found

**Problem**: Missing Python, Node.js, or other dependencies.

**Solutions by platform**:

**Linux (Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm git curl
```

**Linux (CentOS/RHEL)**:
```bash
sudo dnf install python3 python3-pip nodejs npm git curl
```

**macOS**:
```bash
# With Homebrew
brew install python node git

# Without Homebrew - download from official sites
# python.org, nodejs.org
```

**Windows**:
```powershell
# With winget
winget install Python.Python.3.11
winget install OpenJS.NodeJS
winget install Git.Git

# Or download manually from official sites
```

## 🔧 Configuration Issues

### Claude Desktop Config Not Found

**Problem**: Cannot find Claude Desktop configuration file.

**Check file locations**:
```bash
# macOS
ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
ls -la ~/.config/Claude/claude_desktop_config.json

# Windows (PowerShell)
ls $env:APPDATA\Claude\claude_desktop_config.json
```

**Solutions**:

1. **Create directory if missing**:
   ```bash
   # macOS
   mkdir -p ~/Library/Application\ Support/Claude/
   
   # Linux
   mkdir -p ~/.config/Claude/
   
   # Windows
   mkdir $env:APPDATA\Claude\
   ```

2. **Create empty config file**:
   ```bash
   echo '{"mcpServers": {}}' > path/to/claude_desktop_config.json
   ```

3. **Check if Claude Desktop is installed**:
   - Download from [claude.ai/download](https://claude.ai/download)
   - Run Claude Desktop at least once to create config directory

### Invalid Configuration

**Problem**: Configuration file has syntax errors or invalid structure.

**Diagnosis**:
```bash
# Check configuration validity
pg config validate

# Show current configuration
pg config show --raw
```

**Common fixes**:

1. **JSON syntax errors**:
   ```bash
   # Backup current config
   cp claude_desktop_config.json claude_desktop_config.json.backup
   
   # Fix JSON syntax (use online JSON validator)
   # Or restore from backup
   ```

2. **Missing required fields**:
   ```bash
   # Import a clean configuration
   pg config import
   ```

3. **Corrupted config file**:
   ```bash
   # Reset to empty configuration
   echo '{"mcpServers": {}}' > path/to/claude_desktop_config.json
   pg config validate
   ```

### Permission Errors

**Problem**: Cannot write to configuration file.

**Solutions**:

1. **Check file permissions**:
   ```bash
   ls -la path/to/claude_desktop_config.json
   ```

2. **Fix permissions**:
   ```bash
   chmod 644 path/to/claude_desktop_config.json
   ```

3. **Check directory permissions**:
   ```bash
   ls -la path/to/Claude/
   chmod 755 path/to/Claude/
   ```

## 🚀 Server Issues

### Server Installation Fails

**Problem**: MCP server installation fails with errors.

**Common solutions**:

1. **Check npm/node availability**:
   ```bash
   node --version
   npm --version
   ```

2. **Clear npm cache**:
   ```bash
   npm cache clean --force
   ```

3. **Update npm**:
   ```bash
   npm install -g npm@latest
   ```

4. **Try manual installation**:
   ```bash
   npm install -g @modelcontextprotocol/server-filesystem
   ```

5. **Check network connectivity**:
   ```bash
   npm ping
   ```

### Server Not Working in Claude Desktop

**Problem**: Installed server doesn't appear in Claude Desktop.

**Troubleshooting steps**:

1. **Restart Claude Desktop** completely

2. **Check server configuration**:
   ```bash
   pg config list
   pg config show
   ```

3. **Validate configuration**:
   ```bash
   pg config validate
   ```

4. **Check environment variables**:
   ```bash
   # Show environment variables
   env | grep -i github    # Example for GitHub token
   ```

5. **Test server manually**:
   ```bash
   # Test if server command works
   npx @modelcontextprotocol/server-filesystem /test/path
   ```

6. **Check Claude Desktop logs**:
   - macOS: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\logs\`
   - Linux: `~/.config/Claude/logs/`

### Environment Variables Not Set

**Problem**: Server requires environment variables that aren't configured.

**Solutions**:

1. **Check required variables**:
   ```bash
   pg config info server-name
   ```

2. **Set variables temporarily**:
   ```bash
   export GITHUB_TOKEN="your_token_here"
   export BRAVE_API_KEY="your_api_key_here"
   ```

3. **Set variables permanently**:
   ```bash
   # Add to shell profile
   echo 'export GITHUB_TOKEN="your_token"' >> ~/.bashrc
   source ~/.bashrc
   ```

4. **Set for specific installation**:
   ```bash
   pg config install github --env GITHUB_TOKEN=your_token
   ```

## 🔍 Search and Registry Issues

### "No servers found"

**Problem**: Search returns no results for expected servers.

**Solutions**:

1. **Check spelling and try different terms**:
   ```bash
   pg config search database
   pg config search db
   pg config search sql
   ```

2. **List all servers**:
   ```bash
   pg config search
   ```

3. **Try different categories**:
   ```bash
   pg config search --category official
   pg config search --category community
   ```

4. **Update registry** (if using custom registry):
   ```bash
   # Use default registry
   unset PG_REGISTRY_URL
   ```

### Server Info Not Available

**Problem**: `pg config info` doesn't work for a server.

**Check if server exists**:
```bash
# Search for the server first
pg config search server-name

# List all available servers
pg config search
```

## 🖥️ Platform-Specific Issues

### Windows Issues

**PowerShell Execution Policy**:
```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy to allow scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**PATH not updating**:
```powershell
# Refresh environment variables
refreshenv

# Or restart PowerShell
```

**Long path issues**:
```powershell
# Enable long paths in Windows 10+
# Run as Administrator
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

### macOS Issues

**Command Line Tools missing**:
```bash
xcode-select --install
```

**Homebrew issues**:
```bash
# Update Homebrew
brew update

# Fix permissions
sudo chown -R $(whoami) $(brew --prefix)/*
```

### Linux Issues

**Package manager differences**:
```bash
# Ubuntu/Debian
sudo apt install python3-venv

# CentOS/RHEL
sudo dnf install python3-venv

# Arch
sudo pacman -S python-venv
```

**AppImage/Snap Claude Desktop**:
- Configuration path might be different
- Check: `~/.var/app/com.anthropic.claude/config/Claude/`

## 🔄 Reset and Recovery

### Complete Reset

If everything is broken, start fresh:

```bash
# 1. Remove pg command
rm -f ~/.local/bin/pg    # Linux/macOS
rm -f $env:USERPROFILE\Scripts\pg.cmd    # Windows

# 2. Remove virtual environment
rm -rf .venv

# 3. Clean git repository
git clean -fdx

# 4. Reinstall
pip install -e .
./setup-pg-command.sh

# 5. Restart shell
exec $SHELL
```

### Backup and Restore

**Create backup**:
```bash
# Backup configuration
pg config export --file backup.json
cp path/to/claude_desktop_config.json backup_claude_config.json
```

**Restore from backup**:
```bash
# Restore configuration
pg config import --file backup.json
cp backup_claude_config.json path/to/claude_desktop_config.json
```

### Factory Reset Configuration

```bash
# Reset Claude Desktop config to empty
echo '{"mcpServers": {}}' > path/to/claude_desktop_config.json
pg config validate
```

## 📝 Debugging and Logs

### Enable Debug Mode

```bash
# Set debug logging
export PG_LOG_LEVEL=DEBUG

# Run commands with verbose output
pg config install filesystem --arg path=/test --verbose --debug
```

### Check System Information

```bash
# System information
uname -a                    # OS info
python --version           # Python version
node --version             # Node.js version
npm --version              # npm version

# pg information
pg --version               # pg version
which pg                   # pg location
```

### Log Files

Check log files for detailed error information:
- **Claude Desktop logs**: Look in Claude app data directory
- **npm logs**: `~/.npm/_logs/`
- **Python logs**: Set `PG_LOG_FILE` environment variable

## 🆘 Getting Help

If you're still stuck:

1. **Search existing issues**: [GitHub Issues](https://github.com/seanpoyner/claude-desktop-mcp-playground/issues)

2. **Create a new issue** with:
   - Operating system and version
   - Python and Node.js versions
   - Complete error message
   - Steps to reproduce
   - Output of `pg setup --deps-only`

3. **Include diagnostic information**:
   ```bash
   # Gather diagnostic info
   echo "=== System Info ==="
   uname -a
   python --version
   node --version
   
   echo "=== pg Info ==="
   pg --version
   which pg
   
   echo "=== Configuration ==="
   pg config validate
   ```

## 📚 Additional Resources

- **[Installation Guide](installation.md)** - Complete installation instructions
- **[CLI Reference](cli-reference.md)** - Complete command documentation  
- **[Examples](examples.md)** - Working examples and use cases
- **[GitHub Issues](https://github.com/seanpoyner/claude-desktop-mcp-playground/issues)** - Known issues and solutions