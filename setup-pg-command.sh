#!/bin/bash
# Setup 'pg' command for Claude Desktop MCP Playground

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Get the current directory (project root)
PROJECT_DIR="$(pwd)"

log_info "Setting up 'pg' command for Claude Desktop MCP Playground"
log_info "Project directory: $PROJECT_DIR"

# Create ~/.local/bin if it doesn't exist
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# Create the pg script
PG_SCRIPT="$INSTALL_DIR/pg"

cat > "$PG_SCRIPT" << EOF
#!/usr/bin/env python3
"""Playground CLI wrapper script"""
import sys
import os
from pathlib import Path

# Add the project directory to Python path
project_dir = Path("$PROJECT_DIR")
if project_dir.exists():
    sys.path.insert(0, str(project_dir))

    # Import and run the CLI
    try:
        from claude_desktop_mcp.cli import main
        main()
    except ImportError:
        print("Error: Claude Desktop MCP Playground not found.")
        print(f"Project directory: {project_dir}")
        print("Please ensure you're in the correct directory and run this script again.")
        sys.exit(1)
else:
    print("Error: Could not find Claude Desktop MCP Playground installation.")
    print(f"Expected at: {project_dir}")
    sys.exit(1)
EOF

# Make it executable
chmod +x "$PG_SCRIPT"

log_success "pg command created at $PG_SCRIPT"

# Add to PATH in shell profiles
PATH_LINE="export PATH=\"\$HOME/.local/bin:\$PATH\""

# Shell profile files to update
SHELL_FILES=(
    "$HOME/.bashrc"
    "$HOME/.zshrc" 
    "$HOME/.profile"
)

UPDATED_FILES=()

for file in "${SHELL_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        # Check if the PATH is already added
        if ! grep -q "\$HOME/.local/bin" "$file"; then
            echo "" >> "$file"
            echo "# Added by Claude Desktop MCP Playground" >> "$file"
            echo "$PATH_LINE" >> "$file"
            UPDATED_FILES+=("$file")
        fi
    fi
done

if [ ${#UPDATED_FILES[@]} -gt 0 ]; then
    log_success "Updated shell profiles: ${UPDATED_FILES[*]}"
    log_warning "Please restart your terminal or run: source ~/.bashrc (or ~/.zshrc)"
else
    log_info "Shell profiles already configured"
fi

# Also add to current session
export PATH="$INSTALL_DIR:$PATH"

log_success "Setup complete!"
echo
echo "You can now use 'pg' from anywhere:"
echo "  pg config search database"
echo "  pg config list"
echo "  pg setup"
echo
log_warning "Note: You may need to restart your terminal for the PATH changes to take effect."