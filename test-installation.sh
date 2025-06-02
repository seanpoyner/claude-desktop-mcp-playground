#!/bin/bash
# Test script for Claude Desktop MCP Playground installation
# This script helps verify that the installation completed successfully

set -e

echo "🧪 Testing Claude Desktop MCP Playground Installation"
echo "=" * 55
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_test() {
    echo -e "${BLUE}🔍 Testing: $1${NC}"
}

log_pass() {
    echo -e "${GREEN}✅ PASS: $1${NC}"
}

log_fail() {
    echo -e "${RED}❌ FAIL: $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}"
}

# Test 1: Check if pg command is available
log_test "pg command availability"
if command -v pg >/dev/null 2>&1; then
    log_pass "pg command found in PATH"
else
    log_fail "pg command not found in PATH"
    echo "Please restart your terminal or run: source ~/.bashrc (or ~/.zshrc)"
fi

echo

# Test 2: Check if pg command works
log_test "pg command execution"
if pg --version >/dev/null 2>&1; then
    log_pass "pg command executes successfully"
    echo "Version: $(pg --version)"
else
    log_fail "pg command failed to execute"
fi

echo

# Test 3: Check project directory
log_test "Project directory structure"
PROJECT_DIR="$HOME/claude-desktop-mcp-playground"
if [ -d "$PROJECT_DIR" ]; then
    log_pass "Project directory exists at $PROJECT_DIR"
    
    if [ -f "$PROJECT_DIR/pyproject.toml" ]; then
        log_pass "pyproject.toml found"
    else
        log_fail "pyproject.toml not found"
    fi
    
    if [ -d "$PROJECT_DIR/.venv" ]; then
        log_pass "Virtual environment exists"
    else
        log_fail "Virtual environment not found"
    fi
    
    if [ -f "$PROJECT_DIR/.venv/bin/python" ] || [ -f "$PROJECT_DIR/.venv/Scripts/python.exe" ]; then
        log_pass "Virtual environment Python found"
    else
        log_fail "Virtual environment Python not found"
    fi
else
    log_fail "Project directory not found at $PROJECT_DIR"
fi

echo

# Test 4: Check MCP servers installation
log_test "MCP servers installation"
MCP_SERVERS=(
    "@modelcontextprotocol/server-filesystem"
    "mcp-server-sqlite-npx"
    "@modelcontextprotocol/server-brave-search"
    "@modelcontextprotocol/server-everything"
)

for server in "${MCP_SERVERS[@]}"; do
    if npm list -g "$server" >/dev/null 2>&1; then
        log_pass "$server installed globally"
    else
        log_warning "$server not installed globally"
    fi
done

echo

# Test 5: Check Claude Desktop config
log_test "Claude Desktop configuration"
if [ "$(uname)" = "Darwin" ]; then
    CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [ "$(uname)" = "Linux" ]; then
    CLAUDE_CONFIG="$HOME/.config/Claude/claude_desktop_config.json"
else
    CLAUDE_CONFIG="$APPDATA/Claude/claude_desktop_config.json"
fi

if [ -f "$CLAUDE_CONFIG" ]; then
    log_pass "Claude Desktop config file exists"
    
    if grep -q "mcpServers" "$CLAUDE_CONFIG" 2>/dev/null; then
        log_pass "MCP servers section found in config"
        
        # Count configured servers
        server_count=$(grep -o '"[^"]*"[[:space:]]*:[[:space:]]*{' "$CLAUDE_CONFIG" | wc -l)
        if [ $server_count -gt 0 ]; then
            log_pass "$server_count MCP server(s) configured"
        else
            log_warning "No MCP servers configured yet"
        fi
    else
        log_warning "No MCP servers section found in config"
    fi
else
    log_warning "Claude Desktop config file not found (this is normal if you haven't used Claude Desktop yet)"
fi

echo

# Test 6: Try basic pg commands
log_test "Basic pg commands"
if pg config search filesystem >/dev/null 2>&1; then
    log_pass "pg config search works"
else
    log_fail "pg config search failed"
fi

if pg config show >/dev/null 2>&1; then
    log_pass "pg config show works"
else
    log_warning "pg config show failed (might be normal if no config exists)"
fi

echo

# Summary
echo "🎯 Test Summary"
echo "==============="
echo
echo "If all tests passed, your installation is complete!"
echo
echo "Next steps:"
echo "  1. Restart Claude Desktop"
echo "  2. Try: pg config search database"
echo "  3. Install a server: pg config install filesystem --arg path=/path/to/workspace"
echo "  4. Run setup wizard: pg setup"
echo
echo "If any tests failed, try running the installer again or check the documentation."
