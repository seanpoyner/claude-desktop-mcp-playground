# MCP Server Manager - Build System
# ================================

.PHONY: help install build build-simple build-gui build-cli build-windows build-linux build-macos build-all clean test lint format

# Default target
help:
	@echo "MCP Server Manager Build System"
	@echo "==============================="
	@echo ""
	@echo "Available targets:"
	@echo "  install       - Install development dependencies"
	@echo "  build         - Build for current platform"
	@echo "  build-simple  - Build source packages (no PyInstaller required)"
	@echo "  build-gui     - Build GUI application only"
	@echo "  build-cli     - Build CLI application only"
	@echo "  build-windows - Build Windows packages (.exe, .zip)"
	@echo "  build-linux   - Build Linux packages (.tar.gz, .deb, .AppImage)"
	@echo "  build-macos   - Build macOS packages (.tar.gz, .dmg)"
	@echo "  build-all     - Build for all platforms"
	@echo "  test          - Run all tests"
	@echo "  lint          - Run code linting"
	@echo "  format        - Format code"
	@echo "  clean         - Clean build artifacts"
	@echo ""

# Install development dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	pip install pyinstaller
	@echo "Installing GUI dependencies..."
	cd mcp-gui && npm install
	@echo "✓ Dependencies installed"

# Build for current platform
build:
	@echo "Building for current platform..."
	python build-standalone.py

# Build simple source packages (no PyInstaller required)
build-simple:
	@echo "Building simple source packages..."
	python build-simple.py

# Build GUI application only
build-gui:
	@echo "Building GUI application..."
	cd mcp-gui && npm install && npm run build && npm run dist

# Build CLI application only
build-cli:
	@echo "Building CLI application..."
	pip install pyinstaller
	pyinstaller --onefile --name pg claude_desktop_mcp/cli.py

# Build Windows packages
build-windows:
	@echo "Building Windows packages..."
	python build-windows-simple.py

# Build Linux packages
build-linux:
	@echo "Building Linux packages..."
	python build-unix.py

# Build macOS packages
build-macos:
	@echo "Building macOS packages..."
	python build-unix.py

# Build for all platforms (requires appropriate environments)
build-all: build-windows build-linux build-macos
	@echo "✅ All platform builds completed"

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ -v
	cd mcp-gui && npm test

# Run linting
lint:
	@echo "Running Python linting..."
	flake8 claude_desktop_mcp/ tests/
	mypy claude_desktop_mcp/
	@echo "Running JavaScript linting..."
	cd mcp-gui && npm run lint

# Format code
format:
	@echo "Formatting Python code..."
	black claude_desktop_mcp/ tests/
	isort claude_desktop_mcp/ tests/
	@echo "Formatting JavaScript code..."
	cd mcp-gui && npm run format

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist/
	rm -rf build/
	rm -rf *.spec
	rm -rf portable/
	rm -rf mcp-server-manager-*/
	rm -rf *.tar.gz *.zip *.deb *.exe *.dmg *.AppImage
	rm -rf version_info.txt
	cd mcp-gui && rm -rf dist/ node_modules/.vite/
	@echo "✓ Clean completed"

# Development helpers
dev-gui:
	@echo "Starting GUI development server..."
	cd mcp-gui && npm run electron-dev

dev-cli:
	@echo "Installing CLI in development mode..."
	pip install -e .

# Package verification
verify:
	@echo "Verifying packages..."
	@python -c "
import subprocess
import sys
from pathlib import Path

packages = []
for p in Path('.').glob('mcp-server-manager-*'):
    packages.append(str(p))

for p in Path('.').glob('*.tar.gz'):
    if 'mcp-server-manager' in str(p):
        packages.append(str(p))

if packages:
    print('Found packages:')
    for pkg in packages:
        print(f'  ✓ {pkg}')
else:
    print('No packages found. Run make build first.')
    sys.exit(1)
"

# Quick start for development
dev-setup:
	@echo "Setting up development environment..."
	python -m venv .venv
	@echo "Virtual environment created. Activate it with:"
	@echo "  source .venv/bin/activate  # Linux/Mac"
	@echo "  .venv\\Scripts\\activate     # Windows"
	@echo "Then run: make install"