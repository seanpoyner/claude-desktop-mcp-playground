# MCP Server Manager GUI

A modern, intuitive graphical user interface for managing Claude Desktop's Model Context Protocol (MCP) servers. Built with React, Electron, and integrates seamlessly with your existing `claude-desktop-mcp-playground` CLI tools.

## 🌟 Features

- **📊 Dashboard Overview** - Visual stats of installed, running, and available servers
- **🔍 Smart Search & Filtering** - Find servers by name, description, or category
- **⚡ One-Click Installation** - Install MCP servers with guided configuration
- **🎛️ Server Management** - Start, stop, configure, and remove servers
- **🔄 Real-time Status** - Live monitoring of server states
- **🎨 Modern Glass UI** - Beautiful gradient design with glass morphism effects
- **🔧 Configuration Editor** - Visual interface for server settings
- **📱 Responsive Design** - Works on different screen sizes

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ 
- Python 3.9+
- Your existing `claude-desktop-mcp-playground` installation

### Installation

1. **Navigate to the GUI directory:**
   ```bash
   cd claude-desktop-mcp-playground/mcp-gui
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Install Python backend dependencies:**
   ```bash
   pip install flask flask-cors
   ```

### Development Mode

1. **Start the backend API:**
   ```bash
   python backend/api.py
   ```

2. **In another terminal, start the frontend:**
   ```bash
   npm run dev
   ```

3. **In a third terminal, start Electron:**
   ```bash
   npm run electron-dev
   ```

The application will open in a desktop window with live reloading enabled.

### Production Build

1. **Build the frontend:**
   ```bash
   npm run build
   ```

2. **Package the Electron app:**
   ```bash
   npm run dist
   ```

This creates installers in the `dist/` directory for your platform.

## 🎯 Usage

### Managing Installed Servers

- **View Status**: See which servers are running, stopped, or have issues
- **Start/Stop**: Click the play/stop buttons to control server states  
- **Configure**: Click the settings icon to view and edit server configuration
- **Remove**: Click the trash icon to uninstall servers

### Installing New Servers

1. Switch to the "Available Servers" tab
2. Browse or search for servers
3. Click "Install" on any server
4. Fill in required configuration (API keys, paths, etc.)
5. Click "Install Server" to add it to Claude Desktop

### Search & Discovery

- Use the search bar to find servers by name or description
- Filter by category (Official vs Community servers)
- Click the external link icon to view documentation

## 🏗️ Architecture

```
mcp-gui/
├── src/                    # React frontend
│   ├── App.jsx            # Main application component
│   ├── main.jsx           # React entry point
│   ├── index.css          # Global styles with glass effects
│   ├── main.js            # Electron main process
│   └── preload.js         # Electron preload script
├── backend/               # Python Flask API
│   └── api.py            # REST API for MCP operations
├── dist/                  # Built application
└── package.json          # Dependencies and scripts
```

### Technology Stack

- **Frontend**: React 18, Tailwind CSS, Lucide Icons
- **Desktop**: Electron 27
- **Backend**: Python Flask, integrates with existing CLI tools
- **Build**: Vite, Electron Builder

## 🔌 Integration

The GUI integrates with your existing `claude-desktop-mcp-playground` Python modules:

- **Config Manager**: Reads/writes Claude Desktop configuration
- **Server Registry**: Accesses the 30+ server database
- **CLI Tools**: Leverages existing installation logic

Changes made in the GUI are immediately reflected in:
- Claude Desktop configuration file
- Your `pg` CLI commands
- Server status and availability

## 🎨 Design Features

- **Glass Morphism**: Translucent cards with backdrop blur
- **Gradient Backgrounds**: Dynamic blue-to-slate gradients
- **Status Indicators**: Animated dots for server states
- **Smooth Transitions**: Hover effects and loading states
- **Modern Typography**: Clear hierarchy and readable fonts
- **Responsive Layout**: Adapts to different window sizes

## 🔧 Configuration

### Backend API

The Python backend runs on `http://127.0.0.1:8080` and provides:

- `/api/servers/installed` - List installed servers
- `/api/servers/available` - Browse registry servers  
- `/api/servers/install` - Install new servers
- `/api/servers/{id}` - Server details and management
- `/api/config/validate` - Configuration validation

### Environment Variables

Set these for enhanced functionality:

```bash
NODE_ENV=development     # Enable dev tools
ELECTRON_IS_DEV=1       # Electron development mode
```

## 📦 Building & Distribution

### Development Dependencies

```bash
npm install --save-dev
```

### Build for Distribution

```bash
# Build React app
npm run build

# Create platform-specific installers
npm run dist
```

Supported platforms:
- **Windows**: NSIS installer (`.exe`)
- **macOS**: DMG package (`.dmg`)  
- **Linux**: AppImage (`.AppImage`)

## 🛠️ Troubleshooting

### Common Issues

**Backend not connecting:**
- Ensure Python backend is running on port 8080
- Check that `claude_desktop_mcp` modules are importable
- Verify Flask and flask-cors are installed

**Servers not appearing:**
- Confirm Claude Desktop config file exists
- Check config file permissions
- Validate JSON syntax in config file

**Installation failures:**
- Verify npm/Node.js are available in PATH
- Check network connectivity for package downloads
- Ensure sufficient disk space

### Debug Mode

Run with debugging enabled:

```bash
NODE_ENV=development npm run electron-dev
```

This opens DevTools and enables verbose logging.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Setup

```bash
# Install all dependencies
npm install
pip install flask flask-cors

# Run in development mode
npm run electron-dev
```

## 📄 License

MIT License - see the main project LICENSE.md file for details.

## 🙏 Acknowledgments

- Built on top of `claude-desktop-mcp-playground`
- Integrates with Model Context Protocol ecosystem
- Uses React, Electron, and modern web technologies

---

**Experience the future of MCP server management with a beautiful, intuitive interface! 🚀**
