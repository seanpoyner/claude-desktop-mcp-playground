# GUI Application Guide

The Claude Desktop MCP Playground includes a modern desktop GUI application built with Electron and React, providing a visual interface for managing MCP servers.

## 🖥️ Overview

The GUI application provides:
- **Visual Dashboard** - Server status overview and statistics
- **One-Click Installation** - Install servers with guided configuration forms
- **Real-Time Monitoring** - Live server status and error reporting
- **Configuration Editor** - Visual interface for server settings
- **Smart Search** - Find servers by name, description, or category

## 🚀 Getting Started

### Prerequisites

Before running the GUI application, ensure you have:
- **Node.js 16+** installed
- **Python 3.9+** with the CLI tool installed
- **Claude Desktop MCP Playground** base installation completed

### Starting the GUI

#### Development Mode
```bash
# Navigate to GUI directory
cd mcp-gui

# Install dependencies (first time only)
npm install

# Install Python backend dependencies
pip install flask flask-cors

# Start backend API (Terminal 1)
python backend/api.py

# Start React frontend (Terminal 2)
npm run dev

# Start Electron app (Terminal 3)
npm run electron-dev
```

#### Production Mode
```bash
# Build and run
npm run build
npm run electron
```

## 📊 Dashboard Overview

The main dashboard provides a comprehensive overview of your MCP server setup:

### Server Statistics
- **Installed Servers** - Count of configured servers
- **Active Servers** - Currently running servers
- **Error Servers** - Servers with detected issues
- **Available Servers** - Total servers in registry (44+)

### Quick Actions
- **Install New Server** - Browse and install from registry
- **View Configuration** - See current Claude Desktop config
- **Check Logs** - View recent server activity and errors

## 🔍 Server Discovery

### Search Interface
- **Search Bar** - Find servers by name, description, or functionality
- **Category Filter** - Filter between Official (15) and Community (29) servers
- **Server Cards** - Visual representation with key information

### Server Categories
- **Official Servers**: filesystem, memory, puppeteer, github, postgres, etc.
- **Community Servers**: 
  - **Cloud Platforms**: aws, azure, cloudflare, heroku
  - **Databases**: elasticsearch, clickhouse
  - **Development Tools**: jetbrains, xcode, e2b
  - **Web & Automation**: firecrawl, browserbase, screenshotone
  - **Office & Productivity**: excel, office-word, office-powerpoint
  - **Data Analysis**: jupyter-notebook, quickchart
  - **AI & Search**: vectorize, kagi, exa

## ⚡ Server Installation

### Installation Process
1. **Browse Available Servers** - Use search or browse categories
2. **View Server Details** - Click on server cards for detailed information
3. **Configure Installation** - Fill in required parameters in the form
4. **Install Server** - Click install and monitor progress
5. **Verify Installation** - Check dashboard for successful installation

### Configuration Forms
The GUI provides intelligent forms for server configuration:
- **Required Arguments** - Clearly marked mandatory fields
- **Environment Variables** - Secure input for API keys (masked display)
- **Path Selection** - File/directory browsers for path arguments
- **Validation** - Real-time validation of input values
- **Help Text** - Contextual guidance for each parameter

### Example: Installing Filesystem Server
1. Search for "filesystem" in the Available Servers tab
2. Click on the "Filesystem Server" card
3. Fill in the configuration form:
   - **Path**: Select or type the directory path (e.g., `/home/user/projects`)
   - **Server Name**: Optionally customize the server name
4. Click "Install Server"
5. Monitor installation progress in the dashboard

## 🛠️ Server Management

### Installed Servers Tab
View and manage your configured servers:
- **Server Status** - Visual indicators (running, stopped, error)
- **Configuration Details** - View current server settings
- **Server Actions** - Start, stop, configure, remove servers
- **Error Information** - View error messages and logs

### Server Operations
- **Start Server** - Activate a stopped server
- **Stop Server** - Deactivate a running server
- **Configure Server** - Edit server settings
- **Remove Server** - Uninstall and remove from configuration
- **View Logs** - Check server activity and error logs

### Status Indicators
- 🟢 **Running** - Server is active and responsive
- 🟡 **Stopped** - Server is configured but not running
- 🔴 **Error** - Server has encountered an issue
- ⚪ **Unknown** - Server status cannot be determined

## 🔧 Configuration Management

### Configuration Editor
- **Visual JSON Editor** - Edit Claude Desktop configuration directly
- **Syntax Highlighting** - Colored syntax for better readability
- **Validation** - Real-time validation of JSON structure
- **Backup & Restore** - Save and restore configuration snapshots

### Environment Variables
- **Secure Input** - API keys and secrets are masked
- **Variable Management** - Add, edit, and remove environment variables
- **Validation** - Check required variables for each server

### Configuration File Locations
The GUI automatically detects your platform and manages the correct configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

## 📈 Monitoring and Logs

### Real-Time Monitoring
- **Server Health Checks** - Continuous monitoring of server status
- **Auto-Refresh** - Dashboard updates automatically
- **Error Detection** - Automatic detection of server issues

### Log Analysis
- **Claude Desktop Logs** - Read and analyze Claude Desktop log files
- **Error Extraction** - Identify MCP server-related errors
- **Log Filtering** - Filter logs by server or error type

### Error Reporting
- **Bug Reports** - Integrated GitHub issue creation
- **Error Details** - Comprehensive error information
- **Diagnostic Information** - System and configuration details

## 🎨 User Interface Features

### Modern Design
- **Glass Morphism** - Translucent cards with backdrop blur effects
- **Dark Theme** - Easy on the eyes for extended use
- **Responsive Layout** - Adapts to different window sizes
- **Smooth Animations** - Polished transitions and interactions

### Accessibility
- **Keyboard Navigation** - Full keyboard support
- **High Contrast** - Clear visual hierarchy
- **Screen Reader Support** - Accessible markup and labels

### Customization
- **Window Size** - Resizable window with minimum dimensions
- **Panel Layout** - Collapsible panels and adjustable layouts
- **Theme Options** - Light and dark theme variants (future feature)

## 🔒 Security Considerations

### Secure Credential Handling
- **Masked Input** - API keys and secrets are hidden during input
- **Local Storage** - Credentials stored securely in Claude Desktop config
- **No Network Transmission** - Credentials never sent over network

### Permission Management
- **File System Access** - Limited to configured directories
- **Server Permissions** - Servers run with user permissions only
- **Network Access** - Controlled by individual server configurations

## 🚀 Advanced Features

### Bulk Operations
- **Multiple Server Installation** - Install several servers at once
- **Batch Configuration** - Apply settings to multiple servers
- **Export/Import** - Save and share server configurations

### Integration Features
- **External Links** - Open server documentation in browser
- **Copy Configuration** - Copy server settings to clipboard
- **Share Configurations** - Export server setups for sharing

### Development Tools
- **Debug Mode** - Enhanced logging and error information
- **API Testing** - Test server connections and responses
- **Configuration Validation** - Comprehensive config file checking

## 🆘 Troubleshooting

### Common Issues

#### GUI Won't Start
```bash
# Check Node.js version
node --version  # Should be 16+

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check Python backend
python backend/api.py
```

#### Server Installation Fails
1. **Check Internet Connection** - Required for downloading packages
2. **Verify Permissions** - Ensure write access to config directory
3. **Check Dependencies** - Some servers require specific tools (Node.js, Python)
4. **Review Error Messages** - Check console output for specific errors

#### Configuration Not Saving
1. **Check File Permissions** - Ensure write access to Claude Desktop config
2. **Verify Claude Desktop Location** - Confirm config file path is correct
3. **Restart Claude Desktop** - Changes may require restart to take effect

#### Server Status Not Updating
1. **Refresh Dashboard** - Click refresh button or restart GUI
2. **Check Server Logs** - Review logs for error messages
3. **Restart Backend** - Stop and restart the Python backend API

### Debug Mode
Enable debug mode for enhanced troubleshooting:
```bash
# Set debug environment variable
export DEBUG=true
npm run electron-dev
```

### Log Files
Check these locations for additional debugging information:
- **GUI Logs**: Check browser developer console (F12)
- **Backend Logs**: Python backend console output
- **Claude Desktop Logs**: Platform-specific log directories

## 📚 Tips and Best Practices

### Efficient Workflow
1. **Use Search** - Quickly find servers with the search functionality
2. **Check Requirements** - Review server requirements before installation
3. **Test Configuration** - Use dry-run mode when available
4. **Monitor Status** - Keep an eye on server health indicators

### Server Organization
- **Naming Convention** - Use descriptive names for multiple similar servers
- **Category Grouping** - Organize servers by function or project
- **Regular Cleanup** - Remove unused servers to keep config clean

### Performance Optimization
- **Limited Active Servers** - Only run servers you actively need
- **Resource Monitoring** - Monitor system resources with many servers
- **Regular Updates** - Keep servers and GUI updated for best performance

## 🔗 Related Documentation

- **[Quick Start Guide](quick-start.md)** - Get started with CLI and GUI
- **[CLI Reference](cli-reference.md)** - Complete command reference
- **[Installation Guide](installation.md)** - Installation instructions
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

---

**Ready to dive deeper?** Check out the [CLI Reference](cli-reference.md) for advanced command-line usage!