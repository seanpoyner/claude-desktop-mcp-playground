# MCP Server Manager - Build Guide

This guide explains how to build standalone packages for the MCP Server Manager, including both CLI and GUI components.

## Overview

The MCP Server Manager can be packaged as:
- **Windows**: `.exe` installer, portable `.zip`
- **Linux**: `.tar.gz`, `.deb`, AppImage
- **macOS**: `.tar.gz`, `.dmg`

All packages include both the command-line interface (`pg`) and the graphical user interface.

## Quick Start

### Using Make (Recommended)

```bash
# Install dependencies
make install

# Build for current platform
make build

# Build for specific platforms
make build-windows    # Windows packages
make build-linux      # Linux packages
make build-macos      # macOS packages

# Build everything (requires appropriate build environments)
make build-all
```

### Manual Build

```bash
# For Windows
python build-windows.py

# For Linux/macOS
python build-unix.py

# Cross-platform (experimental)
python build-standalone.py
```

## Prerequisites

### All Platforms
- Python 3.9+
- Node.js 18+
- Git

### Platform-Specific

#### Windows
```bash
# Install PyInstaller and electron-builder
pip install pyinstaller
cd mcp-gui && npm install
```

#### Linux
```bash
# Install build tools
sudo apt-get install build-essential

# For .deb packages
sudo apt-get install dpkg-dev

# Install PyInstaller
pip install pyinstaller
cd mcp-gui && npm install
```

#### macOS
```bash
# Install Xcode command line tools
xcode-select --install

# Install PyInstaller
pip install pyinstaller
cd mcp-gui && npm install
```

## Build Scripts

### `build-windows.py`
Creates Windows-specific packages:
- `pg.exe` - Standalone CLI executable
- `MCP-Server-Manager.exe` - GUI installer (NSIS)
- `mcp-server-manager-windows-portable.zip` - Portable package

Features:
- Custom launcher with ASCII art
- Desktop shortcuts
- Start menu integration
- Both 32-bit and 64-bit support

### `build-unix.py`
Creates Unix packages:
- `pg` - Standalone CLI executable
- `mcp-server-manager-{platform}-{arch}.tar.gz` - Portable package
- `mcp-server-manager.deb` - Debian package (Linux only)
- AppImage or DMG (platform-specific)

Features:
- Installation script included
- Desktop entry creation
- PATH integration helper

### `build-standalone.py`
Cross-platform build script (experimental):
- Attempts to build for current platform
- Creates combined packages
- Includes launcher scripts

## Package Contents

### CLI Component (`pg`)
- Standalone executable (no Python required)
- Full MCP server registry
- Configuration management
- Interactive setup wizard

### GUI Component
- Electron-based desktop application
- Native window decorations
- System tray integration (planned)
- Auto-updater support (planned)

## Build Outputs

### Windows
```
mcp-server-manager-setup.exe              # NSIS installer
mcp-server-manager-windows-portable.zip   # Portable package
├── pg.exe                                 # CLI executable
├── MCP-Server-Manager.exe                 # GUI executable  
├── launcher.bat                           # Launcher script
└── README.txt                             # Usage instructions
```

### Linux
```
mcp-server-manager-linux-x64.tar.gz       # Portable package
├── pg                                     # CLI executable
├── mcp-server-manager                     # GUI executable (AppImage)
├── install.sh                             # Installation script
└── README.md                              # Usage instructions

mcp-server-manager_1.0.0_amd64.deb        # Debian package
```

### macOS
```
mcp-server-manager-darwin-x64.tar.gz      # Portable package
├── pg                                     # CLI executable
├── MCP Server Manager.app/                # GUI app bundle
├── install.sh                             # Installation script
└── README.md                              # Usage instructions

MCP-Server-Manager.dmg                     # DMG installer
```

## Advanced Configuration

### PyInstaller Customization

Edit the spec files (`pg-windows.spec`, `pg-unix.spec`) to customize:
- Hidden imports
- Excluded modules
- Icon files
- Version information

### Electron Builder Customization

Edit `mcp-gui/package.json` build section to customize:
- Application metadata
- Installer options
- Code signing
- Auto-updater configuration

### Build Optimization

#### Reducing Package Size
```bash
# Exclude development dependencies
cd mcp-gui && npm ci --production

# Enable UPX compression (if available)
pip install upx-ucl-binary
```

#### Faster Builds
```bash
# Use build cache
export ELECTRON_CACHE=/tmp/electron-cache

# Parallel builds
make -j4 build-all
```

## Testing Packages

### Automated Testing
```bash
# Test CLI functionality
./dist/pg --version
./dist/pg config list

# Test GUI (headless)
cd mcp-gui && npm run test:e2e
```

### Manual Testing Checklist

#### CLI Tests
- [ ] `pg --help` shows help
- [ ] `pg config search filesystem` finds results
- [ ] `pg setup` runs interactive setup
- [ ] Configuration file is created/updated correctly

#### GUI Tests  
- [ ] Application launches without errors
- [ ] Server list loads correctly
- [ ] Server installation works
- [ ] Configuration is persisted

### Cross-Platform Testing

Use virtual machines or CI/CD for testing on different platforms:

```yaml
# GitHub Actions example
strategy:
  matrix:
    os: [windows-latest, ubuntu-latest, macos-latest]
    node-version: [18, 20]
    python-version: [3.9, 3.10, 3.11]
```

## Troubleshooting

### Common Issues

#### PyInstaller Import Errors
```bash
# Add hidden imports to spec file
hiddenimports=[
    'your_missing_module',
    'another_module'
]
```

#### Electron Build Failures
```bash
# Clear cache
cd mcp-gui && rm -rf node_modules/.cache/

# Rebuild native modules
cd mcp-gui && npm rebuild
```

#### Permission Errors (Unix)
```bash
# Make executables
chmod +x dist/pg
chmod +x install.sh
```

### Platform-Specific Issues

#### Windows
- Antivirus may flag PyInstaller executables
- Use code signing for production releases
- Test on both Windows 10 and 11

#### Linux
- Different distributions may need different packages
- Test AppImage on multiple distros
- Consider Flatpak/Snap packages for broader compatibility

#### macOS
- Code signing required for distribution
- Notarization needed for Gatekeeper
- Test on both Intel and Apple Silicon

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Build Packages

on:
  push:
    tags: ['v*']

jobs:
  build:
    strategy:
      matrix:
        os: [windows-latest, ubuntu-latest, macos-latest]
    
    runs-on: ${{ matrix.os }}
    
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - uses: actions/setup-node@v4
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: make install
    
    - name: Build packages
      run: make build
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v4
      with:
        name: packages-${{ matrix.os }}
        path: |
          *.exe
          *.zip
          *.tar.gz
          *.deb
          *.dmg
          *.AppImage
```

## Distribution

### Release Process
1. Update version numbers in `package.json` and `pyproject.toml`
2. Create git tag: `git tag v1.0.0`
3. Push tag: `git push origin v1.0.0`
4. Build packages for all platforms
5. Create GitHub release with packages
6. Update distribution channels (optional)

### Package Verification
Before releasing, verify packages on clean systems:
- Fresh OS installations
- Different user accounts
- Various system configurations

## Security Considerations

- Code sign all executables for production
- Scan packages with antivirus before distribution
- Use HTTPS for all download links
- Verify package integrity with checksums
- Consider reproducible builds for transparency

## Performance Optimization

### Build Time Optimization
- Use build caches
- Parallel builds where possible
- Incremental builds for development

### Package Size Optimization
- Remove unnecessary dependencies
- Use UPX compression (with caution)
- Optimize asset files
- Consider modular packages

### Runtime Performance
- Pre-compile templates
- Optimize startup time
- Consider lazy loading for GUI components