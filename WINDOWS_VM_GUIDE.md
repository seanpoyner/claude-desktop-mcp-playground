# Windows Virtual Machine Testing Guide

Since Docker containers for Windows require a Windows host, here's how to set up a Windows VM for testing the MCP Server Manager.

## Option 1: VirtualBox (Free, Cross-Platform)

### 1. Download and Install VirtualBox
- Download from: https://www.virtualbox.org/
- Install on your host system (Windows/Mac/Linux)

### 2. Get Windows ISO
- Download Windows 10/11 ISO from Microsoft:
  - Windows 10: https://www.microsoft.com/software-download/windows10
  - Windows 11: https://www.microsoft.com/software-download/windows11

### 3. Create Virtual Machine
```
1. Open VirtualBox
2. Click "New"
3. Name: "Windows-MCP-Test"
4. Type: Microsoft Windows
5. Version: Windows 10/11 (64-bit)
6. Memory: 4096 MB (minimum)
7. Create virtual hard disk: 30 GB (minimum)
```

### 4. Configure VM Settings
```
- System → Processor: 2 CPUs minimum
- Display → Video Memory: 128 MB
- Network → Adapter 1: NAT (for internet access)
```

### 5. Install Windows
1. Start VM and select Windows ISO
2. Follow Windows installation
3. Skip product key (for testing)

## Option 2: VMware (Better Performance)

### VMware Workstation Player (Free for Personal Use)
- Download: https://www.vmware.com/products/workstation-player.html
- Similar setup process as VirtualBox
- Generally better performance

### VMware Workstation Pro (Paid)
- Advanced features
- Better snapshot management
- Enhanced networking options

## Option 3: Hyper-V (Windows Pro/Enterprise)

### Enable Hyper-V
```powershell
# Run as Administrator
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

### Create VM
1. Open Hyper-V Manager
2. Action → New → Virtual Machine
3. Follow wizard with similar specs

## Setting Up the Test Environment

### 1. Install Prerequisites in VM
```powershell
# Install Chocolatey (package manager)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install dependencies
choco install python nodejs git -y

# Install UV
irm https://astral.sh/uv/install.ps1 | iex
```

### 2. Clone and Test Repository
```powershell
# Clone repository
git clone https://github.com/seanpoyner/claude-desktop-mcp-playground.git
cd claude-desktop-mcp-playground

# Test installation script
.\install-full.ps1

# Test CLI
pg --help
pg config search
```

### 3. Test Configuration Paths
```powershell
# Check Windows config location
echo $env:APPDATA\Claude\claude_desktop_config.json

# Test path handling
python -c "from claude_desktop_mcp.config_manager import get_config_path; print(get_config_path())"
```

## Automated Testing Script

Create `test-windows.ps1` in the VM:

```powershell
# Windows Testing Script
Write-Host "MCP Server Manager Windows Testing" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# Test 1: Installation
Write-Host "`nTest 1: Running installer..." -ForegroundColor Yellow
.\install-full.ps1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Installation successful" -ForegroundColor Green
} else {
    Write-Host "✗ Installation failed" -ForegroundColor Red
}

# Test 2: CLI Commands
Write-Host "`nTest 2: Testing CLI..." -ForegroundColor Yellow
pg --version
pg config search database
pg config list

# Test 3: Configuration
Write-Host "`nTest 3: Checking configuration..." -ForegroundColor Yellow
if (Test-Path "$env:APPDATA\Claude\claude_desktop_config.json") {
    Write-Host "✓ Config file exists" -ForegroundColor Green
} else {
    Write-Host "✗ Config file missing" -ForegroundColor Red
}

# Test 4: Python Import
Write-Host "`nTest 4: Testing Python import..." -ForegroundColor Yellow
python -c "import claude_desktop_mcp; print('✓ Import successful')"

# Test 5: GUI (if applicable)
Write-Host "`nTest 5: Testing GUI build..." -ForegroundColor Yellow
cd mcp-gui
npm install
npm run build
```

## VM Snapshots for Testing

### Create Clean Snapshots
1. After Windows installation: "Clean Windows"
2. After prerequisites: "Dev Environment"
3. After first successful install: "Working State"

### Restore Points
- Before major changes
- After successful configurations
- Before testing destructive operations

## Remote Access Options

### 1. RDP (Remote Desktop)
- Enable in Windows Settings
- Connect from host: `mstsc /v:VM_IP`

### 2. SSH (OpenSSH)
```powershell
# Install OpenSSH
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Start service
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'
```

### 3. PowerShell Remoting
```powershell
# Enable on VM
Enable-PSRemoting -Force

# Connect from host
Enter-PSSession -ComputerName VM_IP -Credential (Get-Credential)
```

## Performance Tips

### VM Optimization
- Disable Windows animations
- Disable unnecessary services
- Use fixed-size virtual disk
- Allocate sufficient RAM

### Testing Efficiency
- Use snapshots liberally
- Script repetitive tasks
- Keep base image clean
- Document test results

## Alternative: Cloud VMs

### Azure
```bash
# Create Windows VM
az vm create \
  --resource-group MCP-Test \
  --name MCP-Win-Test \
  --image Win2019Datacenter \
  --admin-username testuser \
  --admin-password 'YourPassword123!'
```

### AWS EC2
```bash
# Launch Windows instance
aws ec2 run-instances \
  --image-id ami-windows-latest \
  --instance-type t3.medium \
  --key-name your-key-pair
```

### Google Cloud
```bash
# Create Windows VM
gcloud compute instances create mcp-test-windows \
  --image-family=windows-2019 \
  --image-project=windows-cloud \
  --machine-type=n1-standard-2
```

## Troubleshooting

### Common Issues

1. **Slow Performance**
   - Increase RAM allocation
   - Enable virtualization extensions
   - Use SSD for VM storage

2. **Network Issues**
   - Check VM network adapter settings
   - Verify Windows Firewall rules
   - Test with simple ping/curl

3. **Installation Failures**
   - Run PowerShell as Administrator
   - Check execution policy
   - Verify internet connectivity

### Debug Commands
```powershell
# System info
systeminfo

# Network test
Test-NetConnection github.com -Port 443

# Python/Node versions
python --version
node --version
npm --version

# Environment variables
$env:Path -split ';'
```

## Conclusion

A Windows VM provides the most accurate testing environment for Windows-specific features. Key benefits:
- True Windows file paths and permissions
- Native PowerShell testing
- Accurate GUI behavior
- Real Windows registry access

For CI/CD, consider using GitHub Actions with Windows runners for automated testing.