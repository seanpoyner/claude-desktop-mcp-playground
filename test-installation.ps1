# Test script for Claude Desktop MCP Playground installation (Windows)
# This script helps verify that the installation completed successfully

Write-Host "🧪 Testing Claude Desktop MCP Playground Installation" -ForegroundColor Blue
Write-Host ("=" * 55) -ForegroundColor Blue
Write-Host ""

function Write-Test {
    param([string]$Message)
    Write-Host "🔍 Testing: $Message" -ForegroundColor Blue
}

function Write-Pass {
    param([string]$Message)
    Write-Host "✅ PASS: $Message" -ForegroundColor Green
}

function Write-Fail {
    param([string]$Message)
    Write-Host "❌ FAIL: $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  WARNING: $Message" -ForegroundColor Yellow
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

# Test 1: Check if pg command is available
Write-Test "pg command availability"
if (Test-Command "pg") {
    Write-Pass "pg command found in PATH"
}
else {
    Write-Fail "pg command not found in PATH"
    Write-Host "Please restart your PowerShell terminal for PATH changes to take effect"
}

Write-Host ""

# Test 2: Check if pg command works
Write-Test "pg command execution"
try {
    $version = pg --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Pass "pg command executes successfully"
        Write-Host "Version: $version"
    }
    else {
        Write-Fail "pg command failed to execute"
    }
}
catch {
    Write-Fail "pg command failed to execute: $($_.Exception.Message)"
}

Write-Host ""

# Test 3: Check project directory
Write-Test "Project directory structure"
$projectDir = "$env:USERPROFILE\claude-desktop-mcp-playground"
if (Test-Path $projectDir) {
    Write-Pass "Project directory exists at $projectDir"
    
    if (Test-Path "$projectDir\pyproject.toml") {
        Write-Pass "pyproject.toml found"
    }
    else {
        Write-Fail "pyproject.toml not found"
    }
    
    if (Test-Path "$projectDir\.venv") {
        Write-Pass "Virtual environment exists"
    }
    else {
        Write-Fail "Virtual environment not found"
    }
    
    if (Test-Path "$projectDir\.venv\Scripts\python.exe") {
        Write-Pass "Virtual environment Python found"
    }
    else {
        Write-Fail "Virtual environment Python not found"
    }
}
else {
    Write-Fail "Project directory not found at $projectDir"
}

Write-Host ""

# Test 4: Check MCP servers installation
Write-Test "MCP servers installation"
$mcpServers = @(
    "@modelcontextprotocol/server-filesystem",
    "mcp-server-sqlite-npx",
    "@modelcontextprotocol/server-brave-search",
    "@modelcontextprotocol/server-everything"
)

foreach ($server in $mcpServers) {
    try {
        $result = npm list -g $server 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Pass "$server installed globally"
        }
        else {
            Write-Warning "$server not installed globally"
        }
    }
    catch {
        Write-Warning "$server installation check failed"
    }
}

Write-Host ""

# Test 5: Check Claude Desktop config
Write-Test "Claude Desktop configuration"
$claudeConfig = "$env:APPDATA\Claude\claude_desktop_config.json"

if (Test-Path $claudeConfig) {
    Write-Pass "Claude Desktop config file exists"
    
    try {
        $configContent = Get-Content $claudeConfig -Raw
        if ($configContent -like "*mcpServers*") {
            Write-Pass "MCP servers section found in config"
            
            # Count configured servers (rough estimate)
            $serverMatches = [regex]::Matches($configContent, '"[^"]*"\s*:\s*{')
            if ($serverMatches.Count -gt 1) {  # Subtract 1 for the mcpServers object itself
                Write-Pass "$($serverMatches.Count - 1) MCP server(s) configured"
            }
            else {
                Write-Warning "No MCP servers configured yet"
            }
        }
        else {
            Write-Warning "No MCP servers section found in config"
        }
    }
    catch {
        Write-Warning "Could not parse Claude Desktop config file"
    }
}
else {
    Write-Warning "Claude Desktop config file not found (this is normal if you haven't used Claude Desktop yet)"
}

Write-Host ""

# Test 6: Try basic pg commands
Write-Test "Basic pg commands"
try {
    pg config search filesystem *>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Pass "pg config search works"
    }
    else {
        Write-Fail "pg config search failed"
    }
}
catch {
    Write-Fail "pg config search failed: $($_.Exception.Message)"
}

try {
    pg config show *>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Pass "pg config show works"
    }
    else {
        Write-Warning "pg config show failed (might be normal if no config exists)"
    }
}
catch {
    Write-Warning "pg config show failed (might be normal if no config exists)"
}

Write-Host ""

# Summary
Write-Host "🎯 Test Summary" -ForegroundColor Blue
Write-Host "===============" -ForegroundColor Blue
Write-Host ""
Write-Host "If all tests passed, your installation is complete!"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Restart Claude Desktop"
Write-Host "  2. Try: pg config search database"
Write-Host "  3. Install a server: pg config install filesystem --arg path=C:\path\to\workspace"
Write-Host "  4. Run setup wizard: pg setup"
Write-Host ""
Write-Host "If any tests failed, try running the installer again or check the documentation."
