#!/bin/bash
# Claude Desktop MCP Playground - Full Installation Script
# Supports Linux and macOS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

install_uv() {
    log_info "Installing uv (Python package manager)..."
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        export PATH="$HOME/.local/bin:$PATH"
        log_success "uv installed successfully"
    else
        log_error "Failed to install uv"
        exit 1
    fi
}

install_node_linux() {
    log_info "Installing Node.js..."
    
    # Try different package managers
    if check_command "apt"; then
        sudo apt update
        sudo apt install -y nodejs npm
    elif check_command "dnf"; then
        sudo dnf install -y nodejs npm
    elif check_command "pacman"; then
        sudo pacman -S nodejs npm
    elif check_command "zypper"; then
        sudo zypper install nodejs18 npm18
    else
        log_warning "No supported package manager found. Please install Node.js manually from https://nodejs.org/"
        return 1
    fi
    
    log_success "Node.js installed successfully"
}

install_node_macos() {
    log_info "Installing Node.js..."
    
    if check_command "brew"; then
        brew install node
        log_success "Node.js installed via Homebrew"
    else
        log_warning "Homebrew not found. Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        brew install node
        log_success "Node.js installed via Homebrew"
    fi
}

install_python_linux() {
    log_info "Installing Python 3.9+..."
    
    if check_command "apt"; then
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv
    elif check_command "dnf"; then
        sudo dnf install -y python3 python3-pip
    elif check_command "pacman"; then
        sudo pacman -S python python-pip
    elif check_command "zypper"; then
        sudo zypper install python3 python3-pip
    else
        log_warning "No supported package manager found. Please install Python manually from https://python.org/"
        return 1
    fi
    
    log_success "Python installed successfully"
}

install_python_macos() {
    log_info "Installing Python 3.9+..."
    
    if check_command "brew"; then
        brew install python
        log_success "Python installed via Homebrew"
    else
        log_warning "Homebrew not found. Please install Python from https://python.org/"
        return 1
    fi
}

check_python_version() {
    if check_command "python3"; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
            log_success "Python $PYTHON_VERSION found (✓ 3.9+ required)"
            return 0
        else
            log_warning "Python $PYTHON_VERSION found (✗ 3.9+ required)"
            return 1
        fi
    else
        log_warning "Python 3 not found"
        return 1
    fi
}

check_node_version() {
    if check_command "node"; then
        NODE_VERSION=$(node --version | sed 's/v//')
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
        
        if [ "$NODE_MAJOR" -ge 16 ]; then
            log_success "Node.js $NODE_VERSION found (✓ 16+ required)"
            return 0
        else
            log_warning "Node.js $NODE_VERSION found (✗ 16+ required)"
            return 1
        fi
    else
        log_warning "Node.js not found"
        return 1
    fi
}

clone_repository() {
    log_info "Cloning Claude Desktop MCP Playground repository..."
    
    INSTALL_DIR="$HOME/claude-desktop-mcp-playground"
    
    # Remove existing directory if it exists
    if [ -d "$INSTALL_DIR" ]; then
        log_info "Removing existing installation directory..."
        rm -rf "$INSTALL_DIR"
    fi
    
    if git clone https://github.com/seanpoyner/claude-desktop-mcp-playground.git "$INSTALL_DIR"; then
        log_success "Repository cloned to $INSTALL_DIR"
        cd "$INSTALL_DIR"
        log_info "Changed to project directory: $INSTALL_DIR"
        echo "$INSTALL_DIR"
    else
        log_error "Failed to clone repository"
        log_error "Please ensure Git is installed and you have internet access"
        return 1
    fi
}

install_mcp_servers() {
    log_info "Installing common MCP servers..."
    
    # Fixed server list with correct package names
    MCP_SERVERS=(
        "@modelcontextprotocol/server-filesystem"
        "mcp-server-sqlite-npx"
        "@modelcontextprotocol/server-brave-search"
        "@modelcontextprotocol/server-everything"
    )
    
    SUCCESS_COUNT=0
    TOTAL_COUNT=${#MCP_SERVERS[@]}
    
    for server in "${MCP_SERVERS[@]}"; do
        log_info "Installing $server..."
        if npm install -g "$server" 2>/dev/null; then
            log_success "$server installed"
            ((SUCCESS_COUNT++))
        else
            log_warning "Failed to install $server"
        fi
    done
    
    log_info "Installation summary: $SUCCESS_COUNT/$TOTAL_COUNT packages installed successfully"
}

setup_playground() {
    local project_dir="$1"
    
    log_info "Setting up Claude Desktop MCP Playground..."
    
    # Ensure we're in the project directory
    if [ ! -f "pyproject.toml" ]; then
        log_error "Not in project directory. pyproject.toml not found."
        log_error "Current location: $(pwd)"
        return 1
    fi
    
    # Create virtual environment
    log_info "Creating virtual environment..."
    python3 -m venv .venv
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    source .venv/bin/activate
    
    # Install with uv if available, otherwise pip
    log_info "Installing Claude Desktop MCP Playground..."
    if check_command "uv"; then
        uv pip install -e .
    else
        pip install -e .
    fi
    
    log_success "Claude Desktop MCP Playground installed"
    
    # Add pg command to PATH
    setup_pg_command "$project_dir"
    
    # Run setup wizard
    log_info "Running setup wizard..."
    ./.venv/bin/python -m claude_desktop_mcp.cli setup --quick
}

setup_pg_command() {
    local project_dir="$1"
    log_info "Setting up 'pg' command..."
    
    INSTALL_DIR="$HOME/.local/bin"
    PG_SCRIPT="$INSTALL_DIR/pg"
    
    # Create .local/bin directory if it doesn't exist
    mkdir -p "$INSTALL_DIR"
    
    # Create the pg script that uses the virtual environment Python
    cat > "$PG_SCRIPT" << EOF
#!/bin/bash
# Claude Desktop MCP Playground CLI wrapper

PROJECT_DIR="$project_dir"
VENV_PYTHON="\$PROJECT_DIR/.venv/bin/python"

if [ ! -f "\$VENV_PYTHON" ]; then
    echo "ERROR: Virtual environment Python not found at: \$VENV_PYTHON"
    echo "Please ensure the virtual environment is set up correctly."
    exit 1
fi

# Run the CLI using the virtual environment Python
"\$VENV_PYTHON" -c "
import sys
from pathlib import Path
sys.path.insert(0, r'$project_dir')
try:
    from claude_desktop_mcp.cli import main
    main()
except ImportError as e:
    print('Error: Claude Desktop MCP Playground not found.')
    print(f'Import error: {e}')
    print('Please run installation again.')
    sys.exit(1)
"
EOF
    
    # Make it executable
    chmod +x "$PG_SCRIPT"
    
    # Add to PATH in shell profiles
    add_to_path "$INSTALL_DIR"
    
    log_success "pg command installed to $PG_SCRIPT"
}

add_to_path() {
    local bin_dir="$1"
    local path_line="export PATH=\"\$HOME/.local/bin:\$PATH\""
    
    # Shell profile files to update
    local shell_files=(
        "$HOME/.bashrc"
        "$HOME/.zshrc"
        "$HOME/.profile"
    )
    
    for file in "${shell_files[@]}"; do
        if [[ -f "$file" ]]; then
            # Check if the PATH is already added
            if ! grep -q "\$HOME/.local/bin" "$file"; then
                echo "" >> "$file"
                echo "# Added by Claude Desktop MCP Playground installer" >> "$file"
                echo "$path_line" >> "$file"
                log_info "Updated $file"
            fi
        fi
    done
    
    # Also add to current session
    export PATH="$bin_dir:$PATH"
    
    log_info "Added $bin_dir to PATH"
    log_warning "Please restart your terminal or run: source ~/.bashrc (or ~/.zshrc)"
}

main() {
    echo "🎉 Claude Desktop MCP Playground - Full Installation"
    echo "=" * 55
    echo
    
    # Detect OS
    OS=$(uname -s)
    case "$OS" in
        Linux*)
            PLATFORM="Linux"
            ;;
        Darwin*)
            PLATFORM="macOS"
            ;;
        *)
            log_error "Unsupported operating system: $OS"
            exit 1
            ;;
    esac
    
    log_info "Detected platform: $PLATFORM"
    echo
    
    # Check and install dependencies
    log_info "Checking dependencies..."
    
    # Check Python
    if ! check_python_version; then
        if [ "$PLATFORM" = "Linux" ]; then
            install_python_linux
        else
            install_python_macos
        fi
    fi
    
    # Check Node.js
    if ! check_node_version; then
        if [ "$PLATFORM" = "Linux" ]; then
            install_node_linux
        else
            install_node_macos
        fi
    fi
    
    # Check Git (needed for cloning)
    if ! check_command "git"; then
        log_warning "Git not found. Installing..."
        if [ "$PLATFORM" = "Linux" ]; then
            if check_command "apt"; then
                sudo apt update && sudo apt install -y git
            elif check_command "dnf"; then
                sudo dnf install -y git
            fi
        else
            # macOS
            if check_command "brew"; then
                brew install git
            else
                log_error "Please install Git manually or install Homebrew first"
                exit 1
            fi
        fi
    else
        log_success "Git found"
    fi
    
    # Check uv
    if ! check_command "uv"; then
        install_uv
    else
        log_success "uv found"
    fi
    
    # Clone the repository
    project_dir=$(clone_repository)
    if [ $? -ne 0 ]; then
        log_error "Failed to clone repository. Installation aborted."
        exit 1
    fi
    
    # Install MCP servers
    install_mcp_servers
    
    # Setup playground
    setup_playground "$project_dir"
    
    echo
    log_success "Installation complete! 🎊"
    echo
    echo "Next steps:"
    echo "  1. Restart Claude Desktop"
    echo "  2. Try: pg config show"
    echo "  3. Edit configurations with: pg setup"
    echo
}

# Run main function
main "$@"