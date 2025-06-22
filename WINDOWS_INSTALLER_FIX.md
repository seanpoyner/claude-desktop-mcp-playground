# Windows Installer Fix Guide

This guide helps you fix the **"ffmpeg.dll was not found"** error when running MCP-Server-Manager.exe on Windows.

## 🚨 Quick Fix (Immediate Solution)

If you need to fix the issue right now:

### Option 1: Run the Fix Script (Recommended)
```batch
# Download and run the fix script
fix-ffmpeg-windows.bat
```

Or if you have PowerShell:
```powershell
# Run PowerShell version (more robust)
.\fix-ffmpeg-windows.ps1
```

### Option 2: Manual Fix
1. Download FFmpeg DLLs from: https://github.com/icedterminal/ffmpeg-dll/raw/main/x64/
2. Download these files:
   - `ffmpeg.dll`
   - `avcodec-60.dll`
   - `avformat-60.dll`
   - `avutil-58.dll`
3. Copy them to the same folder as `MCP-Server-Manager.exe`

## 🔧 Permanent Solution (For Developers)

To build a version that doesn't have this problem:

### 1. Use the Complete Build Script
```bash
python build-windows-complete.py
```

This script:
- ✅ Downloads FFmpeg DLLs automatically
- ✅ Includes them in the build
- ✅ Creates a complete package
- ✅ Sets up proper directory structure

### 2. Update Package Configuration

The `mcp-gui/package.json` has been updated to include FFmpeg handling:

```json
{
  "build": {
    "extraResources": [
      {
        "from": "node_modules/ffmpeg-static",
        "to": "ffmpeg",
        "filter": ["**/*"]
      }
    ],
    "win": {
      "extraFiles": [
        {
          "from": "build-resources/windows",
          "to": ".",
          "filter": ["**/*.dll"]
        }
      ]
    }
  }
}
```

### 3. Manual Build Process

If you prefer to build manually:

```bash
# 1. Navigate to GUI directory
cd mcp-gui

# 2. Create build resources directory
mkdir -p build-resources/windows

# 3. Download FFmpeg DLLs to build-resources/windows/
# (Use fix-ffmpeg-windows script or download manually)

# 4. Install dependencies
npm install

# 5. Build with FFmpeg support
npm run dist:win
```

## 📁 File Structure After Fix

Your distribution should look like this:

```
mcp-server-manager-windows-complete/
├── MCP-Server-Manager.exe          # Main GUI application
├── pg.exe                          # CLI tool
├── ffmpeg.dll                      # Required DLL
├── avcodec-60.dll                  # Required DLL
├── avformat-60.dll                 # Required DLL
├── avutil-58.dll                   # Required DLL
├── swscale-7.dll                   # Optional DLL
├── swresample-4.dll                # Optional DLL
├── gui-resources/                  # Electron resources
│   ├── ffmpeg.dll                  # Backup location
│   └── ...
├── launcher.bat                    # Easy launcher
├── install.bat                     # PATH installer
└── README.md
```

## 🐛 Why This Happens

The error occurs because:

1. **Electron includes Chromium** which uses FFmpeg for media processing
2. **electron-builder** sometimes doesn't include FFmpeg DLLs properly
3. **Windows distribution** needs explicit DLL bundling
4. **Missing dependencies** aren't caught until runtime

## 🔍 Troubleshooting

### Error: "The system cannot execute the specified program"
- Run as Administrator
- Check Windows Defender settings
- Verify all DLLs are in the same directory

### Error: "MSVCP140.dll was not found"
Install Microsoft Visual C++ Redistributable:
- Download from: https://support.microsoft.com/en-us/topic/the-latest-supported-visual-c-downloads-2647da03-1eea-4433-9aff-95f26a218cc0

### Error: "Application failed to start correctly"
- Run `fix-ffmpeg-windows.bat` as Administrator
- Rebuild the project: `python build-windows-complete.py`
- Check antivirus software is not blocking files

### GUI doesn't load properly
1. Check if all DLLs are present
2. Try running from command line to see error messages:
   ```batch
   cd path\to\mcp-server-manager
   MCP-Server-Manager.exe
   ```
3. Check Windows Event Viewer for detailed error information

## 📦 Distribution Checklist

When distributing your Windows build, ensure:

- [ ] All FFmpeg DLLs are included
- [ ] DLLs are in both main directory and gui-resources/
- [ ] launcher.bat script is included
- [ ] README.md with usage instructions
- [ ] Tested on clean Windows machine

## 🚀 Testing Your Fix

To verify the fix worked:

1. **Run the executable**:
   ```batch
   MCP-Server-Manager.exe
   ```

2. **Check for errors**:
   - No "ffmpeg.dll was not found" message
   - GUI loads successfully
   - All features work properly

3. **Test on clean machine**:
   - Copy to different Windows computer
   - Run without installing anything else
   - Verify all functionality works

## 📞 Support

If you're still having issues:

1. **Check the error message** - Look for specific DLL names
2. **Run the fix script** - Try both `.bat` and `.ps1` versions
3. **Rebuild the project** - Use `build-windows-complete.py`
4. **Open an issue** - Include your Windows version and error message

## 🔗 Resources

- [FFmpeg Windows DLLs](https://github.com/icedterminal/ffmpeg-dll)
- [Electron Builder Documentation](https://www.electron.build/)
- [Microsoft Visual C++ Redistributable](https://support.microsoft.com/en-us/topic/the-latest-supported-visual-c-downloads-2647da03-1eea-4433-9aff-95f26a218cc0)
- [Windows DLL Troubleshooting](https://support.microsoft.com/en-us/windows/fix-dll-problems-31d5bf3c-7cf2-9199-9a1f-15c25f34f1c3)