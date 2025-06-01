# Claude Desktop MCP Playground - Full Installation Script for Windows
# Requires PowerShell 5.1+ and Admin privileges for some installations

param(
    [switch]$SkipDeps,
    [switch]$Quick
)

# Colors for output
$colors = @{
    Red = "Red"
    Green = "Green" 
    Yellow = "Yellow"
    Blue = "Blue"
    White = "White"
}

function Write-Log {
    param([string]$Message, [string]$Color = "White", [string]$Prefix = "INFO")
    Write-Host "$Prefix $Message" -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-Log $Message -Color Green -Prefix "SUCCESS"
}

function Write-Warning {
    param([string]$Message)
    Write-Log $Message -Color Yellow -Prefix "WARNING"
}

function Write-Error {
    param([string]$Message)
    Write-Log $Message -Color Red -Prefix "ERROR"
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Test-AdminPrivileges {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-Winget {
    Write-Log "Installing winget package manager..."
    try {
        # Check if winget is already installed
        if (Test-Command "winget") {
            Write-Success "winget already installed"
            return $true
        }
        
        # Install App Installer (includes winget)
        $uri = "https://aka.ms/getwinget"
        $tempFile = "$env:TEMP\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
        
        Invoke-WebRequest -Uri $uri -OutFile $tempFile
        Add-AppxPackage -Path $tempFile
        
        Write-Success "winget installed successfully"
        return $true
    }
    catch {
        Write-Warning "Failed to install winget automatically"
        Write-Log "Please install winget manually from Microsoft Store (App Installer)"
        return $false
    }
}

function Install-Node {
    Write-Log "Installing Node.js..."
    
    if (Test-Command "winget") {
        try {
            winget install OpenJS.NodeJS --accept-source-agreements --accept-package-agreements
            Write-Success "Node.js installed via winget"
            
            # Refresh PATH
            $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
            
            return $true
        }
        catch {
            Write-Warning "winget installation failed"
        }
    }
    
    Write-Log "Please install Node.js manually from https://nodejs.org/"
    Write-Log "Download the Windows Installer (.msi) and run it"
    return $false
}

function Install-Python {
    Write-Log "Installing Python..."
    
    if (Test-Command "winget") {
        try {
            winget install Python.Python.3.11 --accept-source-agreements --accept-package-agreements
            Write-Success "Python installed via winget"
            
            # Refresh PATH
            $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
            
            return $true
        }
        catch {
            Write-Warning "winget installation failed"
        }
    }
    
    Write-Log "Please install Python manually from https://python.org/"
    Write-Log "Download Python 3.9+ and make sure to check 'Add Python to PATH'"
    return $false
}

function Install-UV {
    Write-Log "Installing uv (Python package manager)..."
    try {
        powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
        
        # Add to PATH for current session
        $uvPath = "$env:USERPROFILE\.local\bin"
        if (Test-Path $uvPath) {
            $env:PATH = "$uvPath;$env:PATH"
        }
        
        Write-Success "uv installed successfully"
        return $true
    }
    catch {
        Write-Warning "Failed to install uv"
        return $false
    }
}

function Test-PythonVersion {
    if (Test-Command "python") {
        try {
            $version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
            $major, $minor = $version.Split('.')
            
            if ([int]$major -eq 3 -and [int]$minor -ge 9) {
                Write-Success "Python $version found (✓ 3.9+ required)"
                return $true
            }
            else {
                Write-Warning "Python $version found (✗ 3.9+ required)"
                return $false
            }
        }
        catch {
            Write-Warning "Could not determine Python version"
            return $false
        }
    }
    else {
        Write-Warning "Python not found"
        return $false
    }
}

function Test-NodeVersion {
    if (Test-Command "node") {
        try {
            $version = node --version
            $major = [int]($version -replace 'v', '' -split '\.')[0]
            
            if ($major -ge 16) {
                Write-Success "Node.js $version found (✓ 16+ required)"
                return $true
            }
            else {
                Write-Warning "Node.js $version found (✗ 16+ required)"
                return $false
            }
        }
        catch {
            Write-Warning "Could not determine Node.js version"
            return $false
        }
    }
    else {
        Write-Warning "Node.js not found"
        return $false
    }
}

function Install-MCPServers {
    Write-Log "Installing common MCP servers..."
    
    $mcpServers = @(
        "@modelcontextprotocol/server-filesystem",
        "@modelcontextprotocol/server-sqlite",
        "@modelcontextprotocol/server-brave-search",
        "@modelcontextprotocol/server-everything"
    )
    
    foreach ($server in $mcpServers) {
        Write-Log "Installing $server..."
        try {
            npm install -g $server
            Write-Success "$server installed"
        }
        catch {
            Write-Warning "Failed to install $server"
        }
    }
}

function Setup-Playground {
    Write-Log "Setting up Claude Desktop MCP Playground..."
    
    # Create virtual environment
    python -m venv .venv
    
    # Activate virtual environment
    & ".\.venv\Scripts\Activate.ps1"
    
    # Install with uv if available, otherwise pip
    if (Test-Command "uv") {
        uv pip install -e .
    }
    else {
        pip install -e .
    }
    
    Write-Success "Claude Desktop MCP Playground installed"
    
    # Add pg command to PATH
    Setup-PGCommand
    
    # Run setup wizard
    Write-Log "Running setup wizard..."
    if ($Quick) {
        pg setup --quick
    }
    else {
        pg setup
    }
}

function Setup-PGCommand {
    Write-Log "Setting up 'pg' command..."
    
    # Create Scripts directory in user profile
    $scriptsDir = "$env:USERPROFILE\Scripts"
    $pgScript = "$scriptsDir\pg.cmd"
    
    # Create directory if it doesn't exist
    if (-not (Test-Path $scriptsDir)) {
        New-Item -ItemType Directory -Path $scriptsDir -Force | Out-Null
    }
    
    # Get current directory for project path
    $projectDir = (Get-Location).Path
    
    # Create the pg.cmd script
    $scriptContent = @"
@echo off
python -c "
import sys
from pathlib import Path
sys.path.insert(0, r'$projectDir')
try:
    from claude_desktop_mcp.cli import main
    main()
except ImportError:
    print('Error: Claude Desktop MCP Playground not found. Please run installation again.')
    sys.exit(1)
"
"@
    
    Set-Content -Path $pgScript -Value $scriptContent
    
    # Add to PATH
    Add-ToPath $scriptsDir
    
    Write-Success "pg command installed to $pgScript"
}

function Add-ToPath {
    param([string]$Directory)
    
    # Get current user PATH
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    
    # Check if directory is already in PATH
    if ($currentPath -notlike "*$Directory*") {
        # Add to user PATH
        $newPath = "$Directory;$currentPath"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        
        # Update current session PATH
        $env:PATH = "$Directory;$env:PATH"
        
        Write-Log "Added $Directory to PATH"
        Write-Warning "Please restart your terminal/PowerShell for PATH changes to take effect"
    }
    else {
        Write-Log "$Directory already in PATH"
    }
}

function Main {
    Write-Host "🎉 Claude Desktop MCP Playground - Full Installation" -ForegroundColor Blue
    Write-Host ("=" * 55) -ForegroundColor Blue
    Write-Host ""
    
    Write-Log "Detected platform: Windows"
    Write-Host ""
    
    if (-not $SkipDeps) {
        Write-Log "Checking dependencies..."
        
        # Check if running as admin for installations
        $isAdmin = Test-AdminPrivileges
        if (-not $isAdmin) {
            Write-Warning "Not running as Administrator. Some installations may fail."
            Write-Log "Consider running PowerShell as Administrator for automatic installations."
            Write-Host ""
        }
        
        # Install winget if needed
        if (-not (Test-Command "winget")) {
            Install-Winget
        }
        
        # Check Python
        if (-not (Test-PythonVersion)) {
            Install-Python
        }
        
        # Check Node.js  
        if (-not (Test-NodeVersion)) {
            Install-Node
        }
        
        # Check uv
        if (-not (Test-Command "uv")) {
            Install-UV
        }
        else {
            Write-Success "uv found"
        }
        
        # Install MCP servers
        Install-MCPServers
    }
    
    # Setup playground
    Setup-Playground
    
    Write-Host ""
    Write-Success "Installation complete! 🎊"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Restart Claude Desktop"
    Write-Host "  2. Try: pg config show"
    Write-Host "  3. Edit configurations with: pg setup"
    Write-Host ""
    Write-Host "Note: You may need to restart your terminal/PowerShell session"
    Write-Host "for PATH changes to take effect."
}

# Run main function
Main