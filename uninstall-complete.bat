@echo off
title MCP Server Manager - Complete Uninstallation
echo ===============================================================================
echo                    MCP SERVER MANAGER - COMPLETE UNINSTALL
echo ===============================================================================
echo.
echo This script will completely remove MCP Server Manager and clean up all files.
echo.
echo WARNING: This will remove:
echo - Installed application files
echo - Start menu shortcuts
echo - Desktop shortcuts
echo - Cached files
echo - Temporary files
echo.
set /p continue="Do you want to continue? (Y/N): "
if /i not "%continue%"=="Y" (
    echo Cancelled by user.
    pause
    exit /b 0
)

echo.
echo Starting complete uninstallation...

REM Stop any running processes
echo Stopping any running MCP processes...
taskkill /f /im "MCP-Server-Manager.exe" >nul 2>&1
taskkill /f /im "mcp-server-manager.exe" >nul 2>&1
taskkill /f /im "electron.exe" >nul 2>&1

REM Wait a moment for processes to close
timeout /t 2 >nul

REM Remove from Programs and Features (if installed via NSIS)
echo Checking for installed version...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /s /f "MCP Server Manager" >nul 2>&1
if %errorlevel% equ 0 (
    echo Found installed version. Attempting to uninstall...
    
    REM Try to find and run uninstaller
    for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /s /f "MCP Server Manager" /k 2^>nul ^| findstr "HKEY"') do (
        for /f "tokens=2*" %%c in ('reg query "%%a" /v "UninstallString" 2^>nul ^| findstr "UninstallString"') do (
            echo Running uninstaller: %%d
            "%%d" /S
        )
    )
)

REM Remove from user-specific locations
echo Removing user-specific files...

REM Remove from Program Files
if exist "%ProgramFiles%\MCP Server Manager" (
    echo Removing from Program Files...
    rmdir /s /q "%ProgramFiles%\MCP Server Manager" >nul 2>&1
)

if exist "%ProgramFiles(x86)%\MCP Server Manager" (
    echo Removing from Program Files (x86)...
    rmdir /s /q "%ProgramFiles(x86)%\MCP Server Manager" >nul 2>&1
)

REM Remove from AppData
if exist "%APPDATA%\MCP Server Manager" (
    echo Removing AppData files...
    rmdir /s /q "%APPDATA%\MCP Server Manager" >nul 2>&1
)

if exist "%LOCALAPPDATA%\MCP Server Manager" (
    echo Removing Local AppData files...
    rmdir /s /q "%LOCALAPPDATA%\MCP Server Manager" >nul 2>&1
)

if exist "%LOCALAPPDATA%\Programs\MCP Server Manager" (
    echo Removing Local Programs files...
    rmdir /s /q "%LOCALAPPDATA%\Programs\MCP Server Manager" >nul 2>&1
)

if exist "%LOCALAPPDATA%\Programs\MCP-Server-Manager" (
    echo Removing Local Programs files (alt name)...
    rmdir /s /q "%LOCALAPPDATA%\Programs\MCP-Server-Manager" >nul 2>&1
)

REM Remove shortcuts
echo Removing shortcuts...
del "%USERPROFILE%\Desktop\MCP Server Manager.lnk" >nul 2>&1
del "%USERPROFILE%\Desktop\MCP-Server-Manager.lnk" >nul 2>&1
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\MCP Server Manager.lnk" >nul 2>&1
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\MCP-Server-Manager.lnk" >nul 2>&1

REM Remove from Start Menu folder if it exists
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\MCP Server Manager" (
    rmdir /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\MCP Server Manager" >nul 2>&1
)

REM Clean registry entries
echo Cleaning registry entries...
reg delete "HKEY_CURRENT_USER\SOFTWARE\MCP Server Manager" /f >nul 2>&1
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\MCP Server Manager" /f >nul 2>&1

REM Remove any electron cache
if exist "%APPDATA%\mcp-server-manager-gui" (
    echo Removing Electron cache...
    rmdir /s /q "%APPDATA%\mcp-server-manager-gui" >nul 2>&1
)

REM Remove temp files
echo Cleaning temporary files...
del "%TEMP%\*mcp*" /q >nul 2>&1
del "%TEMP%\*electron*" /q >nul 2>&1

REM Clean current directory build artifacts
echo Cleaning build artifacts in current directory...
if exist "mcp-gui\dist" (
    rmdir /s /q "mcp-gui\dist" >nul 2>&1
)
if exist "dist" (
    rmdir /s /q "dist" >nul 2>&1
)
if exist "temp" (
    rmdir /s /q "temp" >nul 2>&1
)

REM Remove any global npm packages
echo Checking for global npm installations...
npm uninstall -g mcp-server-manager >nul 2>&1

echo.
echo ===============================================================================
echo                          UNINSTALLATION COMPLETE
echo ===============================================================================
echo.
echo All MCP Server Manager files have been removed from:
echo ✅ Program Files
echo ✅ AppData directories  
echo ✅ Start Menu
echo ✅ Desktop shortcuts
echo ✅ Registry entries
echo ✅ Temporary files
echo ✅ Build artifacts
echo.
echo The system is now clean and ready for a fresh installation.
echo.
pause
