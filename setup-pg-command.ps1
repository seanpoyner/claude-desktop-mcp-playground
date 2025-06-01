# Setup 'pg' command for Claude Desktop MCP Playground (Windows)

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

# Get current directory (project root)
$projectDir = (Get-Location).Path

Write-Log "Setting up 'pg' command for Claude Desktop MCP Playground"
Write-Log "Project directory: $projectDir"

# Create Scripts directory in user profile
$scriptsDir = "$env:USERPROFILE\Scripts"
$pgScript = "$scriptsDir\pg.cmd"

# Create directory if it doesn't exist
if (-not (Test-Path $scriptsDir)) {
    New-Item -ItemType Directory -Path $scriptsDir -Force | Out-Null
}

# Create a Python launcher script first
$pythonScript = "$scriptsDir\pg_launcher.py"
$pythonContent = @"
import sys
import os
from pathlib import Path

# Add project directory to Python path
project_dir = r'$projectDir'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

try:
    from claude_desktop_mcp.cli import main
    main()
except ImportError as e:
    print('Error: Claude Desktop MCP Playground not found.')
    print(f'Project directory: {project_dir}')
    print('Please ensure you are in the correct directory and run this script again.')
    print(f'Import error: {e}')
    sys.exit(1)
"@

Set-Content -Path $pythonScript -Value $pythonContent

# Create the pg.cmd script that calls the Python launcher
$scriptContent = @"
@echo off
python "$pythonScript" %*
"@

Set-Content -Path $pgScript -Value $scriptContent

Write-Success "pg command created at $pgScript"

# Add to PATH
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")

if ($currentPath -notlike "*$scriptsDir*") {
    # Add to user PATH
    $newPath = "$scriptsDir;$currentPath"
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    
    # Update current session PATH
    $env:PATH = "$scriptsDir;$env:PATH"
    
    Write-Success "Added $scriptsDir to PATH"
    Write-Warning "Please restart your terminal/PowerShell for PATH changes to take effect"
}
else {
    Write-Log "$scriptsDir already in PATH"
}

Write-Success "Setup complete!"
Write-Host ""
Write-Host "You can now use 'pg' from anywhere:"
Write-Host "  pg config search database"
Write-Host "  pg config list" 
Write-Host "  pg setup"
Write-Host ""
Write-Warning "Note: You may need to restart your terminal for the PATH changes to take effect."