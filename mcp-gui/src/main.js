const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');
const fs = require('fs').promises;
const os = require('os');

// Keep a global reference of the window object
let mainWindow;

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'assets', 'icon.png'), // Add an icon if you have one
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    show: false // Don't show until ready
  });

  // Load the app
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

// This method will be called when Electron has finished initialization
app.whenReady().then(createWindow);

// Quit when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// Security: Prevent new window creation
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    event.preventDefault();
    shell.openExternal(navigationUrl);
  });
});

// Get Claude Desktop config path based on platform
function getClaudeConfigPath() {
  const platform = process.platform;
  let configPath;

  if (platform === 'darwin') {
    configPath = path.join(os.homedir(), 'Library', 'Application Support', 'Claude', 'claude_desktop_config.json');
  } else if (platform === 'win32') {
    configPath = path.join(process.env.APPDATA || '', 'Claude', 'claude_desktop_config.json');
  } else {
    configPath = path.join(os.homedir(), '.config', 'Claude', 'claude_desktop_config.json');
  }

  return configPath;
}

// IPC Handlers for MCP server management
ipcMain.handle('get-installed-servers', async () => {
  try {
    const configPath = getClaudeConfigPath();
    const configData = await fs.readFile(configPath, 'utf8');
    const config = JSON.parse(configData);
    
    const servers = [];
    const mcpServers = config.mcpServers || {};
    
    for (const [id, serverConfig] of Object.entries(mcpServers)) {
      servers.push({
        id,
        name: id, // You might want to enhance this with a proper name mapping
        description: `MCP Server: ${id}`,
        category: 'installed',
        status: 'stopped', // You'd need to implement actual status checking
        command: serverConfig.command || '',
        args: serverConfig.args || [],
        env: serverConfig.env || {},
        package: serverConfig.command || ''
      });
    }
    
    return servers;
  } catch (error) {
    console.error('Error reading Claude config:', error);
    return [];
  }
});

ipcMain.handle('install-server', async (event, serverData) => {
  try {
    const configPath = getClaudeConfigPath();
    let config = {};
    
    try {
      const configData = await fs.readFile(configPath, 'utf8');
      config = JSON.parse(configData);
    } catch (error) {
      // File doesn't exist, create new config
      config = { mcpServers: {} };
    }
    
    if (!config.mcpServers) {
      config.mcpServers = {};
    }
    
    // Add the new server
    config.mcpServers[serverData.id] = {
      command: serverData.command,
      args: serverData.args,
      env: serverData.env
    };
    
    // Ensure directory exists
    await fs.mkdir(path.dirname(configPath), { recursive: true });
    
    // Write updated config
    await fs.writeFile(configPath, JSON.stringify(config, null, 2));
    
    return { success: true };
  } catch (error) {
    console.error('Error installing server:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('remove-server', async (event, serverId) => {
  try {
    const configPath = getClaudeConfigPath();
    const configData = await fs.readFile(configPath, 'utf8');
    const config = JSON.parse(configData);
    
    if (config.mcpServers && config.mcpServers[serverId]) {
      delete config.mcpServers[serverId];
      await fs.writeFile(configPath, JSON.stringify(config, null, 2));
      return { success: true };
    }
    
    return { success: false, error: 'Server not found' };
  } catch (error) {
    console.error('Error removing server:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('run-command', async (event, command, args = []) => {
  return new Promise((resolve) => {
    const child = spawn(command, args, { stdio: 'pipe' });
    
    let stdout = '';
    let stderr = '';
    
    child.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    child.on('close', (code) => {
      resolve({
        success: code === 0,
        stdout,
        stderr,
        code
      });
    });
    
    child.on('error', (error) => {
      resolve({
        success: false,
        error: error.message
      });
    });
  });
});

ipcMain.handle('check-server-status', async (event, serverId) => {
  // This is a simplified status check - you'd want to implement proper process monitoring
  try {
    const result = await new Promise((resolve) => {
      exec('tasklist', (error, stdout) => {
        if (error) {
          resolve({ running: false });
          return;
        }
        
        // Simple check for node/npx processes
        const isRunning = stdout.toLowerCase().includes('node.exe') || 
                         stdout.toLowerCase().includes('npx');
        resolve({ running: isRunning });
      });
    });
    
    return result;
  } catch (error) {
    return { running: false };
  }
});

ipcMain.handle('open-external', async (event, url) => {
  shell.openExternal(url);
});

ipcMain.handle('show-message-box', async (event, options) => {
  const result = await dialog.showMessageBox(mainWindow, options);
  return result;
});

ipcMain.handle('get-app-path', async () => {
  return {
    userData: app.getPath('userData'),
    documents: app.getPath('documents'),
    downloads: app.getPath('downloads')
  };
});
