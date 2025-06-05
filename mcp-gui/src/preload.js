const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // MCP Server Management
  getInstalledServers: () => ipcRenderer.invoke('get-installed-servers'),
  installServer: (serverData) => ipcRenderer.invoke('install-server', serverData),
  removeServer: (serverId) => ipcRenderer.invoke('remove-server', serverId),
  checkServerStatus: (serverId) => ipcRenderer.invoke('check-server-status', serverId),
  
  // System operations
  runCommand: (command, args) => ipcRenderer.invoke('run-command', command, args),
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  showMessageBox: (options) => ipcRenderer.invoke('show-message-box', options),
  getAppPath: () => ipcRenderer.invoke('get-app-path'),
  
  // Platform info
  platform: process.platform,
  
  // Events
  onServerStatusChanged: (callback) => {
    ipcRenderer.on('server-status-changed', callback);
    return () => ipcRenderer.removeListener('server-status-changed', callback);
  }
});

// Expose a simple API for renderer to check if running in Electron
contextBridge.exposeInMainWorld('isElectron', true);
