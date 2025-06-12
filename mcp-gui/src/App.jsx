import React, { useState, useEffect, useMemo } from 'react';
import { Search, Plus, Trash2, Settings, Download, Package, ExternalLink, Filter, RefreshCw, PlayCircle, StopCircle, Info, CheckCircle, XCircle, AlertTriangle, Terminal, FileText, Globe, Bug } from 'lucide-react';

// API service for backend communication
const apiService = {
  baseUrl: 'http://127.0.0.1:8080/api',
  
  async getInstalledServers() {
    try {
      console.log('Fetching installed servers from:', `${this.baseUrl}/servers/installed`);
      const response = await fetch(`${this.baseUrl}/servers/installed`);
      console.log('Installed servers response status:', response.status);
      if (!response.ok) throw new Error('Failed to fetch installed servers');
      const data = await response.json();
      console.log('Installed servers data:', data);
      return data;
    } catch (error) {
      console.error('Error fetching installed servers:', error);
      return [];
    }
  },
  
  async getAvailableServers(category = null) {
    try {
      const url = category ? `${this.baseUrl}/servers/available?category=${category}` : `${this.baseUrl}/servers/available`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch available servers');
      return await response.json();
    } catch (error) {
      console.error('Error fetching available servers:', error);
      return [];
    }
  },
  
  async searchServers(query) {
    try {
      const response = await fetch(`${this.baseUrl}/servers/search?q=${encodeURIComponent(query)}`);
      if (!response.ok) throw new Error('Failed to search servers');
      return await response.json();
    } catch (error) {
      console.error('Error searching servers:', error);
      return [];
    }
  },
  
  async installServer(serverId, config) {
    try {
      const response = await fetch(`${this.baseUrl}/servers/install`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ server_id: serverId, config })
      });
      return await response.json();
    } catch (error) {
      console.error('Error installing server:', error);
      return { success: false, error: error.message };
    }
  },
  
  async removeServer(serverId) {
    try {
      const response = await fetch(`${this.baseUrl}/servers/${serverId}`, {
        method: 'DELETE'
      });
      return await response.json();
    } catch (error) {
      console.error('Error removing server:', error);
      return { success: false, error: error.message };
    }
  },
  
  async getServerErrors(serverId) {
    try {
      const response = await fetch(`${this.baseUrl}/servers/${serverId}/errors`);
      if (!response.ok) throw new Error('Failed to fetch server errors');
      return await response.json();
    } catch (error) {
      console.error('Error fetching server errors:', error);
      return { errors: [] };
    }
  },
  
  async getServerInfo(serverId) {
    try {
      const response = await fetch(`${this.baseUrl}/servers/${serverId}`);
      if (!response.ok) throw new Error('Server not found');
      return await response.json();
    } catch (error) {
      console.error('Error getting server info:', error);
      return null;
    }
  },
  
  async healthCheck() {
    try {
      console.log('Performing health check to:', `${this.baseUrl}/health`);
      const response = await fetch(`${this.baseUrl}/health`);
      console.log('Health check response status:', response.status);
      const data = await response.json();
      console.log('Health check data:', data);
      return data;
    } catch (error) {
      console.error('Backend health check failed:', error);
      return { status: 'error', error: error.message };
    }
  }
};

function App() {
  const [activeTab, setActiveTab] = useState('installed');
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [installedServers, setInstalledServers] = useState([]);
  const [availableServers, setAvailableServers] = useState([]);
  const [selectedServer, setSelectedServer] = useState(null);
  const [showInstallModal, setShowInstallModal] = useState(false);
  const [installFormData, setInstallFormData] = useState({});
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [showBugReportModal, setShowBugReportModal] = useState(false);
  const [bugReportData, setBugReportData] = useState({
    title: '',
    description: '',
    steps: '',
    expected: '',
    actual: '',
    severity: 'medium'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState(null);
  const [error, setError] = useState(null);

  // Load data on component mount
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    console.log('Starting loadInitialData...');
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Checking backend health...');
      // Check backend health
      const health = await apiService.healthCheck();
      console.log('Health check result:', health);
      setBackendStatus(health);
      
      if (health.status === 'error') {
        console.log('Backend health check failed');
        setError('Backend API is not available. Please ensure the Python backend is running on port 8080.');
        return;
      }
      
      console.log('Loading servers...');
      // Load servers - try to continue even if one fails
      try {
        await loadInstalledServers();
        console.log('Installed servers loaded successfully');
      } catch (error) {
        console.error('Failed to load installed servers:', error);
        setInstalledServers([]); // Set empty array to continue
      }
      
      try {
        await loadAvailableServers();
        console.log('Available servers loaded successfully');
      } catch (error) {
        console.error('Failed to load available servers:', error);
        setAvailableServers([]); // Set empty array to continue
      }
      
      console.log('Server loading complete');
      
    } catch (error) {
      console.error('Error in loadInitialData:', error);
      setError('Failed to connect to backend API. Please check that the Python backend is running.');
      console.error('Error loading initial data:', error);
    } finally {
      console.log('loadInitialData complete, setting loading to false');
      setIsLoading(false);
    }
  };

  const loadInstalledServers = async () => {
    try {
      console.log('Loading installed servers...');
      const servers = await apiService.getInstalledServers();
      console.log('Raw installed servers:', servers);
      // Map the actual server data to include proper names and descriptions
      const mappedServers = servers.map(server => ({
        ...server,
        name: getServerDisplayName(server.id),
        description: getServerDescription(server.id),
        category: 'installed'
      }));
      console.log('Mapped installed servers:', mappedServers);
      setInstalledServers(mappedServers);
    } catch (error) {
      console.error('Error loading installed servers:', error);
    }
  };

  const loadAvailableServers = async () => {
    try {
      console.log('Loading available servers...');
      const servers = await apiService.getAvailableServers(categoryFilter === 'all' ? null : categoryFilter);
      console.log('Available servers loaded:', servers.length);
      setAvailableServers(servers);
    } catch (error) {
      console.error('Error loading available servers:', error);
    }
  };

  // Helper function to get display names for servers
  const getServerDisplayName = (serverId) => {
    const nameMap = {
      'filesystem': 'Filesystem Server',
      'code-sandbox-mcp': 'Code Sandbox Server',
      'fetch': 'Fetch Server',
      'brave-search': 'Brave Search Server',
      'github': 'GitHub Server',
      'memory': 'Memory Server',
      'sequential-thinking': 'Sequential Thinking Server',
      'puppeteer': 'Puppeteer Server',
      'everything': 'Everything Server',
      'time': 'Time Server',
      'computer-control': 'Computer Control Server',
      'github-docker': 'GitHub Docker Server'
    };
    return nameMap[serverId] || serverId.replace(/[-_]/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  // Helper function to get descriptions for servers
  const getServerDescription = (serverId) => {
    const descMap = {
      'filesystem': 'Secure file operations with configurable access controls',
      'code-sandbox-mcp': 'Safe code execution in isolated sandbox environments',
      'fetch': 'Web content fetching and conversion for efficient LLM usage',
      'brave-search': 'Web search capabilities using Brave Search API',
      'github': 'Access GitHub repositories, issues, PRs, and code',
      'memory': 'Knowledge graph-based persistent memory system',
      'sequential-thinking': 'Dynamic and reflective problem-solving through thought sequences',
      'puppeteer': 'Browser automation and web scraping using Puppeteer',
      'everything': 'Reference/test server that exercises all MCP protocol features',
      'time': 'Time and timezone utilities with conversion capabilities',
      'computer-control': 'Control computer operations and automation through MCP interface',
      'github-docker': 'Docker-based GitHub server with containerized execution'
    };
    return descMap[serverId] || `MCP Server: ${serverId}`;
  };

  // Filter and search logic
  const filteredAvailableServers = useMemo(() => {
    return availableServers.filter(server => {
      const matchesSearch = !searchTerm || 
        server.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        server.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        server.id.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesCategory = categoryFilter === 'all' || server.category === categoryFilter;
      
      return matchesSearch && matchesCategory;
    });
  }, [availableServers, searchTerm, categoryFilter]);

  const filteredInstalledServers = useMemo(() => {
    return installedServers.filter(server => {
      return !searchTerm || 
        server.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        server.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        server.id.toLowerCase().includes(searchTerm.toLowerCase());
    });
  }, [installedServers, searchTerm]);


  const handleRemoveServer = async (serverId) => {
    if (confirm('Are you sure you want to remove this server? This will delete it from your Claude Desktop configuration.')) {
      setIsLoading(true);
      try {
        const result = await apiService.removeServer(serverId);
        if (result.success) {
          await loadInstalledServers();
        } else {
          setError(result.error || 'Failed to remove server');
        }
      } catch (error) {
        setError('Failed to remove server');
        console.error('Remove server error:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleInstallServer = async (server) => {
    const serverInfo = await apiService.getServerInfo(server.id);
    setSelectedServer(serverInfo || server);
    setInstallFormData({
      name: server.id,
      ...Object.keys(serverInfo?.env_vars || {}).reduce((acc, key) => {
        acc[key] = '';
        return acc;
      }, {}),
      ...serverInfo?.required_args?.reduce((acc, arg) => {
        acc[arg] = '';
        return acc;
      }, {}) || {},
      ...serverInfo?.optional_args?.reduce((acc, arg) => {
        acc[arg] = '';
        return acc;
      }, {}) || {}
    });
    setShowInstallModal(true);
  };

  const submitInstall = async () => {
    setIsLoading(true);
    try {
      const result = await apiService.installServer(selectedServer.id, installFormData);
      if (result.success) {
        await loadInstalledServers();
        setShowInstallModal(false);
        setSelectedServer(null);
        setInstallFormData({});
      } else {
        setError(result.error || 'Installation failed');
      }
    } catch (error) {
      setError('Installation failed');
      console.error('Install error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const openConfigModal = (server) => {
    setSelectedServer(server);
    setShowConfigModal(true);
  };

  const handleRefresh = async () => {
    await loadInitialData();
  };

  const handleBugReport = () => {
    setShowBugReportModal(true);
  };

  const submitBugReport = () => {
    // Collect system information
    const systemInfo = {
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString(),
      installedServers: installedServers.length,
      backendStatus: backendStatus?.status || 'unknown',
      ...bugReportData
    };

    // Create GitHub issue URL with pre-filled data
    const issueTitle = encodeURIComponent(`Bug Report: ${bugReportData.title}`);
    const issueBody = encodeURIComponent(`## Bug Description
${bugReportData.description}

## Steps to Reproduce
${bugReportData.steps}

## Expected Behavior
${bugReportData.expected}

## Actual Behavior
${bugReportData.actual}

## Severity
${bugReportData.severity}

## System Information
- User Agent: ${navigator.userAgent}
- Timestamp: ${systemInfo.timestamp}
- Installed Servers: ${systemInfo.installedServers}
- Backend Status: ${systemInfo.backendStatus}

## Additional Context
Please provide any additional context or screenshots that might help us understand the issue.`);

    const githubUrl = `https://github.com/seanpoyner/claude-desktop-mcp-playground/issues/new?title=${issueTitle}&body=${issueBody}&labels=bug`;
    
    // Open GitHub in new tab
    window.open(githubUrl, '_blank');
    
    // Reset form and close modal
    setBugReportData({
      title: '',
      description: '',
      steps: '',
      expected: '',
      actual: '',
      severity: 'medium'
    });
    setShowBugReportModal(false);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'configured':
        return <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
          <span className="text-blue-400 text-sm">Configured</span>
        </div>;
      case 'error':
        return <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
          <span className="text-red-400 text-sm">Error</span>
        </div>;
      default:
        return <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
          <span className="text-blue-400 text-sm">Configured</span>
        </div>;
    }
  };

  const getCategoryBadge = (category) => {
    const colors = {
      official: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
      community: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
      installed: 'bg-green-500/20 text-green-300 border-green-500/30'
    };
    
    const labels = {
      official: '🏛️ Official',
      community: '🌟 Community',
      installed: '✅ Installed'
    };
    
    return (
      <span className={`px-3 py-1 text-xs font-medium rounded-full border ${colors[category] || 'bg-gray-500/20 text-gray-300 border-gray-500/30'}`}>
        {labels[category] || category}
      </span>
    );
  };

  const stats = {
    total: installedServers.length,
    configured: installedServers.filter(s => s.status === 'configured').length,
    errors: installedServers.filter(s => s.status === 'error').length,
    available: availableServers.length
  };

  // Show error state if backend is not available
  if (error && !backendStatus) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="glass-card rounded-xl p-8 max-w-md text-center">
          <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-white mb-2">Backend Not Available</h2>
          <p className="text-slate-300 mb-4">{error}</p>
          <button onClick={loadInitialData} className="btn-primary">
            <RefreshCw className="w-4 h-4 mr-2" />
            Retry Connection
          </button>
          <div className="mt-4 text-sm text-slate-400">
            <p>Make sure to start the backend with:</p>
            <code className="block mt-2 p-2 bg-black/20 rounded">python backend/api.py</code>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Loading Overlay */}
      {isLoading && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="glass-card rounded-xl p-6">
            <div className="flex items-center gap-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-400"></div>
              <span className="text-white">Processing...</span>
            </div>
          </div>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="bg-red-500/20 border border-red-500/30 rounded-lg p-4 m-6 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <span className="text-red-300">{error}</span>
          <button 
            onClick={() => setError(null)}
            className="ml-auto text-red-400 hover:text-red-300"
          >
            <XCircle className="w-4 h-4" />
          </button>
        </div>
      )}
      
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <Terminal className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">MCP Server Manager</h1>
              <p className="text-slate-300">Manage your Claude Desktop Model Context Protocol servers</p>
              {backendStatus && (
                <div className="flex items-center gap-2 mt-1">
                  <div className={`w-2 h-2 rounded-full ${backendStatus.status === 'healthy' ? 'bg-green-400' : 'bg-red-400'}`}></div>
                  <span className="text-xs text-slate-400">
                    Backend {backendStatus.status} • Config: {backendStatus.config_exists ? 'Found' : 'Not Found'}
                  </span>
                </div>
              )}
            </div>
          </div>
          
          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="glass-card rounded-xl p-4">
              <div className="flex items-center gap-3">
                <Package className="w-5 h-5 text-blue-400" />
                <div>
                  <p className="text-2xl font-bold text-white">{stats.total}</p>
                  <p className="text-slate-400 text-sm">Installed</p>
                </div>
              </div>
            </div>
            
            <div className="glass-card rounded-xl p-4">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-blue-400" />
                <div>
                  <p className="text-2xl font-bold text-white">{stats.configured}</p>
                  <p className="text-slate-400 text-sm">Configured</p>
                </div>
              </div>
            </div>
            
            <div className="glass-card rounded-xl p-4">
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-5 h-5 text-red-400" />
                <div>
                  <p className="text-2xl font-bold text-white">{stats.errors}</p>
                  <p className="text-slate-400 text-sm">Errors</p>
                </div>
              </div>
            </div>
            
            <div className="glass-card rounded-xl p-4">
              <div className="flex items-center gap-3">
                <Download className="w-5 h-5 text-purple-400" />
                <div>
                  <p className="text-2xl font-bold text-white">{stats.available}</p>
                  <p className="text-slate-400 text-sm">Available</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="glass-card rounded-xl p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search servers..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20 transition-all"
              />
            </div>
            
            <div className="flex gap-3">
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white focus:outline-none focus:border-blue-400 transition-all"
              >
                <option value="all">All Categories</option>
                <option value="official">Official</option>
                <option value="community">Community</option>
              </select>
              
              <button onClick={handleRefresh} className="btn-primary flex items-center gap-2">
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
              
              <button onClick={handleBugReport} className="btn-secondary flex items-center gap-2">
                <Bug className="w-4 h-4" />
                Report Bug
              </button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="flex space-x-1 glass-card rounded-lg p-1">
            <button
              onClick={() => setActiveTab('installed')}
              className={`flex-1 py-3 px-4 rounded-md text-sm font-medium transition-all ${
                activeTab === 'installed'
                  ? 'bg-white text-slate-900 shadow-lg'
                  : 'text-slate-300 hover:text-white hover:bg-white/10'
              }`}
            >
              Installed Servers ({installedServers.length})
            </button>
            <button
              onClick={() => setActiveTab('available')}
              className={`flex-1 py-3 px-4 rounded-md text-sm font-medium transition-all ${
                activeTab === 'available'
                  ? 'bg-white text-slate-900 shadow-lg'
                  : 'text-slate-300 hover:text-white hover:bg-white/10'
              }`}
            >
              Available Servers ({availableServers.length})
            </button>
          </div>
        </div>

        {/* Content */}
        {activeTab === 'installed' ? (
          <div className="grid gap-4">
            {filteredInstalledServers.length === 0 ? (
              <div className="glass-card rounded-xl p-8 text-center">
                <Package className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-white mb-2">No Installed Servers</h3>
                <p className="text-slate-400 mb-4">Get started by installing some MCP servers</p>
                <button
                  onClick={() => setActiveTab('available')}
                  className="btn-primary"
                >
                  Browse Available Servers
                </button>
              </div>
            ) : (
              filteredInstalledServers.map((server) => (
                <div key={server.id} className="glass-card rounded-xl p-6 hover:border-white/30 transition-all card-enter">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <h3 className="text-xl font-semibold text-white">{server.name}</h3>
                        {getCategoryBadge(server.category)}
                        {getStatusIcon(server.status)}
                      </div>
                      <p className="text-slate-300 mb-4">{server.description}</p>
                      
                      <div className="space-y-3 text-sm">
                        <div className="flex items-center gap-2">
                          <Terminal className="w-4 h-4 text-slate-400" />
                          <span className="text-slate-400">Command:</span>
                          <code className="bg-black/20 px-2 py-1 rounded text-slate-200 font-mono text-xs">
                            {server.command} {server.args?.join(' ')}
                          </code>
                        </div>
                        
                        {Object.keys(server.env || {}).length > 0 && (
                          <div className="flex items-center gap-2">
                            <Settings className="w-4 h-4 text-slate-400" />
                            <span className="text-slate-400">Environment:</span>
                            <span className="text-slate-200">{Object.keys(server.env).length} variable(s) configured</span>
                          </div>
                        )}
                        
                        {server.errors && server.errors.length > 0 && (
                          <div className="mt-3 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                            <div className="flex items-center gap-2 mb-2">
                              <AlertTriangle className="w-4 h-4 text-red-400" />
                              <span className="text-red-400 text-sm font-medium">Recent Errors:</span>
                            </div>
                            <div className="space-y-1">
                              {server.errors.slice(0, 3).map((error, index) => (
                                <div key={index} className="text-xs text-red-300 font-mono bg-black/20 p-2 rounded">
                                  {error.length > 100 ? `${error.substring(0, 100)}...` : error}
                                </div>
                              ))}
                              {server.errors.length > 3 && (
                                <div className="text-xs text-red-400">+ {server.errors.length - 3} more errors</div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={() => openConfigModal(server)}
                        className="btn-secondary p-2"
                        title="Configure Server"
                      >
                        <Settings className="w-4 h-4" />
                      </button>
                      
                      <button
                        onClick={() => handleRemoveServer(server.id)}
                        className="btn-danger p-2"
                        title="Remove Server"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        ) : (
          <div className="grid gap-4">
            {filteredAvailableServers.map((server) => (
              <div key={server.id} className="glass-card rounded-xl p-6 hover:border-white/30 transition-all card-enter">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <Package className="w-5 h-5 text-slate-400" />
                      <h3 className="text-xl font-semibold text-white">{server.name}</h3>
                      {getCategoryBadge(server.category)}
                    </div>
                    <p className="text-slate-300 mb-4">{server.description}</p>
                    
                    <div className="space-y-3 text-sm">
                      <div className="flex items-center gap-2">
                        <Package className="w-4 h-4 text-slate-400" />
                        <span className="text-slate-400">Package:</span>
                        <code className="bg-black/20 px-2 py-1 rounded text-slate-200 font-mono text-xs">{server.package}</code>
                      </div>
                      
                      {server.required_args && server.required_args.length > 0 && (
                        <div className="flex items-center gap-2">
                          <AlertTriangle className="w-4 h-4 text-yellow-400" />
                          <span className="text-slate-400">Required Args:</span>
                          <span className="text-yellow-300">{server.required_args.join(', ')}</span>
                        </div>
                      )}
                      
                      {server.optional_args && server.optional_args.length > 0 && (
                        <div className="flex items-center gap-2">
                          <Info className="w-4 h-4 text-blue-400" />
                          <span className="text-slate-400">Optional Args:</span>
                          <span className="text-blue-300">{server.optional_args.join(', ')}</span>
                        </div>
                      )}
                      
                      {Object.keys(server.env_vars || {}).length > 0 && (
                        <div className="flex items-center gap-2">
                          <Settings className="w-4 h-4 text-purple-400" />
                          <span className="text-slate-400">Environment:</span>
                          <span className="text-purple-300">{Object.keys(server.env_vars).length} variable(s) required</span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 ml-4">
                    {server.homepage && (
                      <a
                        href={server.homepage}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn-secondary p-2"
                        title="View Documentation"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    )}
                    
                    <button
                      onClick={() => handleInstallServer(server)}
                      className="btn-primary flex items-center gap-2"
                    >
                      <Download className="w-4 h-4" />
                      Install
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Install Modal */}
        {showInstallModal && selectedServer && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-slate-800 rounded-xl border border-slate-600 w-full max-w-md max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-slate-600">
                <h2 className="text-xl font-bold text-white mb-2">Install {selectedServer.name}</h2>
                <p className="text-slate-300 text-sm">{selectedServer.description}</p>
              </div>
              
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Server Name
                  </label>
                  <input
                    type="text"
                    value={installFormData.name || selectedServer.id}
                    onChange={(e) => setInstallFormData(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-400"
                  />
                </div>

                {selectedServer.required_args?.map(arg => (
                  <div key={arg}>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      {arg} <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="text"
                      value={installFormData[arg] || ''}
                      onChange={(e) => setInstallFormData(prev => ({ ...prev, [arg]: e.target.value }))}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-400"
                      placeholder={`Enter ${arg}`}
                    />
                  </div>
                ))}

                {selectedServer.optional_args?.map(arg => (
                  <div key={arg}>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      {arg} <span className="text-slate-500">(optional)</span>
                    </label>
                    <input
                      type="text"
                      value={installFormData[arg] || ''}
                      onChange={(e) => setInstallFormData(prev => ({ ...prev, [arg]: e.target.value }))}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-400"
                      placeholder={`Enter ${arg} (optional)`}
                    />
                  </div>
                ))}

                {Object.entries(selectedServer.env_vars || {}).map(([key, description]) => (
                  <div key={key}>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      {key} <span className="text-red-400">*</span>
                    </label>
                    <input
                      type={key.toLowerCase().includes('token') || key.toLowerCase().includes('key') || key.toLowerCase().includes('password') ? 'password' : 'text'}
                      value={installFormData[key] || ''}
                      onChange={(e) => setInstallFormData(prev => ({ ...prev, [key]: e.target.value }))}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-400"
                      placeholder={description}
                    />
                  </div>
                ))}
              </div>
              
              <div className="p-6 border-t border-slate-600 flex justify-end gap-3">
                <button
                  onClick={() => setShowInstallModal(false)}
                  className="px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={submitInstall}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Install Server
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Config Modal */}
        {showConfigModal && selectedServer && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-slate-800 rounded-xl border border-slate-600 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-slate-600">
                <h2 className="text-xl font-bold text-white mb-2">Configure {selectedServer.name}</h2>
                <p className="text-slate-300 text-sm">{selectedServer.description}</p>
              </div>
              
              <div className="p-6 space-y-6">
                {/* Server Status */}
                <div className="glass-card rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-white mb-3">Server Status</h3>
                  <div className="flex items-center justify-between">
                    {getStatusIcon(selectedServer.status)}
                    <div className="text-sm text-slate-400">
                      {selectedServer.status === 'error' ? 
                        'Server has recent errors - check logs below' :
                        'MCP servers are managed by Claude Desktop'}
                    </div>
                  </div>
                </div>

                {/* Command Configuration */}
                <div className="glass-card rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-white mb-3">Command Configuration</h3>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Command</label>
                      <code className="block w-full p-3 bg-black/20 border border-slate-600 rounded text-slate-200 font-mono text-sm">
                        {selectedServer.command}
                      </code>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Arguments</label>
                      <code className="block w-full p-3 bg-black/20 border border-slate-600 rounded text-slate-200 font-mono text-sm">
                        {selectedServer.args?.join(' ') || 'No arguments'}
                      </code>
                    </div>
                  </div>
                </div>

                {/* Environment Variables */}
                {Object.keys(selectedServer.env || {}).length > 0 && (
                  <div className="glass-card rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-3">Environment Variables</h3>
                    <div className="space-y-2">
                      {Object.entries(selectedServer.env).map(([key, value]) => (
                        <div key={key} className="flex items-center justify-between p-2 bg-black/20 rounded">
                          <span className="text-slate-300 font-mono text-sm">{key}</span>
                          <span className="text-slate-500 text-xs">
                            {key.toLowerCase().includes('token') || key.toLowerCase().includes('key') ? '***' : value}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Server Errors */}
                {selectedServer.errors && selectedServer.errors.length > 0 && (
                  <div className="glass-card rounded-lg p-4 border border-red-500/30">
                    <h3 className="text-lg font-semibold text-red-400 mb-3 flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5" />
                      Recent Errors
                    </h3>
                    <div className="space-y-3 max-h-64 overflow-y-auto">
                      {selectedServer.errors.map((error, index) => (
                        <div key={index} className="p-3 bg-red-500/10 border border-red-500/20 rounded text-red-300 text-sm font-mono">
                          {error}
                        </div>
                      ))}
                    </div>
                    <div className="mt-3 text-xs text-slate-400">
                      Check Claude Desktop logs for more details
                    </div>
                  </div>
                )}
              </div>
              
              <div className="p-6 border-t border-slate-600 flex justify-end gap-3">
                <button
                  onClick={() => setShowConfigModal(false)}
                  className="px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white rounded-lg transition-colors"
                >
                  Close
                </button>
                <button
                  onClick={() => {
                    setShowConfigModal(false);
                    handleRemoveServer(selectedServer.id);
                  }}
                  className="btn-danger"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Remove Server
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Bug Report Modal */}
        {showBugReportModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-slate-800 rounded-xl border border-slate-600 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-slate-600">
                <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                  <Bug className="w-5 h-5 text-red-400" />
                  Report a Bug
                </h2>
                <p className="text-slate-300 text-sm">Help us improve the MCP Server Manager by reporting issues you encounter.</p>
              </div>
              
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Bug Title <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    value={bugReportData.title}
                    onChange={(e) => setBugReportData(prev => ({ ...prev, title: e.target.value }))}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-400"
                    placeholder="Brief description of the issue"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Description <span className="text-red-400">*</span>
                  </label>
                  <textarea
                    value={bugReportData.description}
                    onChange={(e) => setBugReportData(prev => ({ ...prev, description: e.target.value }))}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-400 h-24"
                    placeholder="Detailed description of what went wrong"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Steps to Reproduce
                  </label>
                  <textarea
                    value={bugReportData.steps}
                    onChange={(e) => setBugReportData(prev => ({ ...prev, steps: e.target.value }))}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-400 h-24"
                    placeholder="1. Go to...&#10;2. Click on...&#10;3. See error..."
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Expected Behavior
                    </label>
                    <textarea
                      value={bugReportData.expected}
                      onChange={(e) => setBugReportData(prev => ({ ...prev, expected: e.target.value }))}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-400 h-20"
                      placeholder="What should have happened?"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Actual Behavior
                    </label>
                    <textarea
                      value={bugReportData.actual}
                      onChange={(e) => setBugReportData(prev => ({ ...prev, actual: e.target.value }))}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-400 h-20"
                      placeholder="What actually happened?"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Severity
                  </label>
                  <select
                    value={bugReportData.severity}
                    onChange={(e) => setBugReportData(prev => ({ ...prev, severity: e.target.value }))}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-400"
                  >
                    <option value="low">Low - Minor inconvenience</option>
                    <option value="medium">Medium - Affects functionality</option>
                    <option value="high">High - Major issue or blocks usage</option>
                    <option value="critical">Critical - App is unusable</option>
                  </select>
                </div>

                <div className="bg-slate-700/50 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-slate-300 mb-2">System Information (Auto-collected)</h3>
                  <div className="text-xs text-slate-400 space-y-1">
                    <div>• Browser: {navigator.userAgent.split('(')[0].trim()}</div>
                    <div>• Installed Servers: {installedServers.length}</div>
                    <div>• Backend Status: {backendStatus?.status || 'unknown'}</div>
                  </div>
                </div>
              </div>
              
              <div className="p-6 border-t border-slate-600 flex justify-end gap-3">
                <button
                  onClick={() => setShowBugReportModal(false)}
                  className="px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={submitBugReport}
                  disabled={!bugReportData.title || !bugReportData.description}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center gap-2"
                >
                  <Bug className="w-4 h-4" />
                  Submit Bug Report
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;