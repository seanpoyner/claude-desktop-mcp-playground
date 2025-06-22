# MCP Server Manager - Packaging Guide

## Package Types Available

### 1. Source Packages (Recommended for Linux/macOS)
**Command:** `python build-simple.py` or `make build-simple`

Creates self-contained source packages that work on any system with Python 3.9+:
- ✅ No PyInstaller required
- ✅ Works in externally-managed Python environments  
- ✅ Includes installation scripts
- ✅ Smaller package size
- ✅ Cross-platform compatible

**Output:**
- `mcp-server-manager-{platform}-{arch}-source.tar.gz` (Linux/macOS)
- `mcp-server-manager-{platform}-{arch}-source.zip` (Windows)

### 2. Compiled Packages (When PyInstaller Available)
**Command:** `python build-unix.py` or `python build-windows.py`

Creates standalone executables:
- ✅ No Python installation required
- ✅ Single executable files
- ❌ Requires PyInstaller
- ❌ Larger package size
- ❌ May have compatibility issues

### 3. GUI-Only Packages
**Command:** `cd mcp-gui && npm run dist`

Creates native desktop applications:
- ✅ Standalone GUI app
- ✅ Native installers (NSIS, DMG, AppImage)
- ✅ Desktop integration
- ❌ GUI only (no CLI)

## Quick Start

### Build Source Packages (Works Everywhere)
```bash
# Test build system
python test-build.py

# Create source packages
python build-simple.py

# Or use Make
make build-simple
```

### Install from Source Package
```bash
# Extract package
tar -xzf mcp-server-manager-linux-x64-source.tar.gz
cd mcp-server-manager-linux-x64-source/

# Run installation script
./install.sh

# Or run directly
python -m claude_desktop_mcp.cli --help
```

## Package Contents

### Source Package Structure
```
mcp-server-manager-{platform}-{arch}-source/
├── claude_desktop_mcp/          # Source code
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Package configuration
├── pg                          # CLI wrapper script
├── install.sh                  # Installation script
├── README.md                   # Usage instructions
└── mcp-server-manager          # GUI app (if built)
```

### Installation Script Features
- ✅ Checks Python version (3.9+ required)
- ✅ Installs dependencies with `--user` flag
- ✅ Creates wrapper scripts in `~/.local/bin/`
- ✅ Creates desktop entries for GUI
- ✅ Provides PATH setup instructions

## Environment Compatibility

### ✅ Works With
- Externally-managed Python environments (Debian/Ubuntu)
- Virtual environments
- User installs (`pip install --user`)
- pipx installations
- System Python installations

### ❌ Limitations
- PyInstaller requires write access to system packages
- Some Linux distributions restrict system package installation
- GUI packages require Node.js for building

## Build System Commands

### Make Targets
```bash
make help           # Show all available targets
make install        # Install development dependencies
make build-simple   # Create source packages (recommended)
make build-gui      # Build GUI packages only
make test           # Run tests
make clean          # Clean build artifacts
```

### Manual Commands
```bash
# Source packages (no PyInstaller needed)
python build-simple.py

# Compiled packages (requires PyInstaller)
python build-unix.py        # Linux/macOS
python build-windows.py     # Windows

# Cross-platform (experimental)
python build-standalone.py

# Test build system
python test-build.py
```

## Distribution

### For End Users
1. **Recommended:** Use source packages
   - Download `mcp-server-manager-{platform}-{arch}-source.tar.gz`
   - Extract and run `install.sh`
   - Or run directly with Python

2. **GUI Users:** Download platform-specific GUI packages
   - Windows: `.exe` installer from `mcp-gui/dist/`
   - macOS: `.dmg` from `mcp-gui/dist/`
   - Linux: `.AppImage` from `mcp-gui/dist/`

### For Developers
```bash
# Development setup
git clone <repository>
cd claude-desktop-mcp-playground
make install           # Install dependencies
make dev-cli          # Install CLI in development mode
make dev-gui          # Start GUI development server
```

## Troubleshooting

### PyInstaller Issues
If PyInstaller fails:
1. Use `python build-simple.py` instead
2. Or create virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install pyinstaller
   python build-unix.py
   ```

### GUI Build Issues
```bash
# Clear npm cache
cd mcp-gui && rm -rf node_modules/.cache/

# Reinstall dependencies
cd mcp-gui && rm -rf node_modules && npm install

# Check Electron version compatibility
cd mcp-gui && npm ls electron
```

### Permission Issues
```bash
# Make scripts executable
chmod +x dist/pg
chmod +x install.sh

# Check Python installation permissions
python -m pip install --user --dry-run pyinstaller
```

## Platform-Specific Notes

### Linux
- Use source packages for maximum compatibility
- AppImage provides portable GUI option
- Consider creating .deb packages for Debian-based systems

### macOS
- Source packages work on all macOS versions
- DMG provides native installer experience
- Code signing required for distribution outside App Store

### Windows
- Source packages require Python installation
- Use GUI installer for non-technical users
- Consider creating MSI packages for enterprise deployment

## Security Considerations

### Source Packages
- ✅ Full source code visibility
- ✅ Uses standard Python packaging
- ✅ No binary executables to scan
- ✅ Dependencies installed from PyPI

### Compiled Packages
- ❌ Antivirus may flag PyInstaller executables
- ❌ Code signing recommended for distribution
- ✅ Self-contained (no dependency confusion)

## Performance

### Package Sizes
- Source packages: ~100KB
- Compiled packages: ~50-100MB
- GUI packages: ~100-200MB

### Startup Times
- Source packages: ~1-2 seconds (Python import time)
- Compiled packages: ~0.5-1 seconds
- GUI packages: ~2-3 seconds (Electron startup)

## Future Improvements

### Planned Features
- [ ] Automatic updates for GUI packages
- [ ] Docker containers for consistent builds
- [ ] GitHub Actions for automated releases
- [ ] Package signing and verification
- [ ] Conda packages for data science users

### Build System Enhancements
- [ ] Cross-compilation support
- [ ] Dependency bundling optimization
- [ ] Build caching for faster iterations
- [ ] Multi-architecture support (ARM64, etc.)

## Conclusion

The source package approach (`build-simple.py`) is recommended for most users as it:
- Works in all Python environments
- Provides full transparency
- Has minimal dependencies
- Offers the best compatibility

Use compiled packages only when you need to distribute to systems without Python, and use GUI packages for users who prefer graphical interfaces.