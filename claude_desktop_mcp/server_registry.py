"""MCP Server Registry

Registry of available MCP servers with installation and configuration information.
"""

from typing import Dict, List, Optional, Any
import json
import re
import os
import platform
from pathlib import Path


class MCPServerRegistry:
    """Registry of available MCP servers"""
    
    def __init__(self):
        self.servers = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Dict[str, Any]]:
        """Load the MCP server registry"""
        return {
            # Current official @modelcontextprotocol servers (in main repo)
            "filesystem": {
                "name": "Filesystem Server",
                "description": "Secure file operations with configurable access controls. Read, write, and manage files and directories.",
                "category": "official",
                "package": "@modelcontextprotocol/server-filesystem",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "@modelcontextprotocol/server-filesystem", "<path>"],
                "required_args": ["path"],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Provide a path to the directory you want Claude to access",
                "example_usage": "Access files in your workspace directory",
                "homepage": "https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem"
            },
            "memory": {
                "name": "Memory Server",
                "description": "Knowledge graph-based persistent memory system. Store and retrieve information across conversations.",
                "category": "official",
                "package": "@modelcontextprotocol/server-memory",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "@modelcontextprotocol/server-memory"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "No additional setup required",
                "example_usage": "Remember information between conversations",
                "homepage": "https://github.com/modelcontextprotocol/servers/tree/main/src/memory"
            },
            "puppeteer": {
                "name": "Puppeteer Server",
                "description": "Browser automation and web scraping using Puppeteer. Interact with web pages programmatically.",
                "category": "official",
                "package": "@modelcontextprotocol/server-puppeteer",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "@modelcontextprotocol/server-puppeteer"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Requires Chrome/Chromium browser",
                "example_usage": "Automate browser interactions and scraping",
                "homepage": "https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer"
            },
            "everything": {
                "name": "Everything Server",
                "description": "Reference/test server that exercises all MCP protocol features. Includes prompts, resources, and tools.",
                "category": "official", 
                "package": "@modelcontextprotocol/server-everything",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "@modelcontextprotocol/server-everything"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "No additional setup required",
                "example_usage": "Test all MCP protocol features",
                "homepage": "https://github.com/modelcontextprotocol/servers/tree/main/src/everything"
            },
            "sequential-thinking": {
                "name": "Sequential Thinking Server",
                "description": "Dynamic and reflective problem-solving through thought sequences. Advanced reasoning capabilities.",
                "category": "official",
                "package": "@modelcontextprotocol/server-sequential-thinking",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "No additional setup required",
                "example_usage": "Enhanced reasoning and problem-solving",
                "homepage": "https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking"
            },
            
            # Archived official servers (still available as packages)
            "fetch": {
                "name": "Fetch Server",
                "description": "Web content fetching and conversion for efficient LLM usage. Fetch and process web pages.",
                "category": "official",
                "package": "mcp-server-fetch",
                "install_method": "uvx",
                "command": "uvx",
                "args_template": ["mcp-server-fetch"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Requires uvx (pip install uvx) for Python package management",
                "example_usage": "Fetch and analyze web content",
                "homepage": "https://github.com/modelcontextprotocol/servers/tree/main/src/fetch"
            },
            "brave-search": {
                "name": "Brave Search Server",
                "description": "Web search capabilities using Brave Search API. Get search results with privacy focus.",
                "category": "official",
                "package": "@modelcontextprotocol/server-brave-search",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "@modelcontextprotocol/server-brave-search"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"BRAVE_API_KEY": "Your Brave Search API key"},
                "setup_help": "Get API key from https://brave.com/search/api/",
                "example_usage": "Search the web for current information",
                "homepage": "https://github.com/modelcontextprotocol/servers"
            },
            "github": {
                "name": "GitHub Server",
                "description": "Access GitHub repositories, issues, PRs, and code. Search repositories and manage GitHub resources.",
                "category": "official",
                "package": "@modelcontextprotocol/server-github",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "@modelcontextprotocol/server-github"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"GITHUB_TOKEN": "Your GitHub personal access token"},
                "setup_help": "Create a GitHub token at https://github.com/settings/tokens",
                "example_usage": "Search code, manage issues, analyze repositories",
                "homepage": "https://github.com/modelcontextprotocol/servers"
            },
            "gitlab": {
                "name": "GitLab Server",
                "description": "Access GitLab repositories, issues, merge requests, and code. Manage GitLab resources.",
                "category": "official",
                "package": "@modelcontextprotocol/server-gitlab",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "@modelcontextprotocol/server-gitlab"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"GITLAB_TOKEN": "Your GitLab personal access token"},
                "setup_help": "Create a GitLab token in your account settings",
                "example_usage": "Search code, manage issues, analyze GitLab repositories",
                "homepage": "https://github.com/modelcontextprotocol/servers"
            },
            "github-docker": {
                "name": "GitHub Server (Docker)",
                "description": "Access GitHub repositories using Docker-based deployment. Alternative to npm-based GitHub server with containerized execution.",
                "category": "community",
                "package": "mcp/github",
                "install_method": "docker",
                "command": "docker",
                "args_template": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "mcp/github"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"GITHUB_PERSONAL_ACCESS_TOKEN": "Your GitHub personal access token"},
                "setup_help": "Requires Docker installed and running. Create a GitHub token at https://github.com/settings/tokens",
                "example_usage": "Search code, manage issues, analyze repositories via Docker",
                "homepage": "https://github.com/ckreiling/mcp-server-docker"
            },
            "postgres": {
                "name": "PostgreSQL Server",
                "description": "Connect to PostgreSQL databases. Execute queries, manage schemas, and analyze data.",
                "category": "official",
                "package": "@modelcontextprotocol/server-postgres",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "@modelcontextprotocol/server-postgres"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {
                    "POSTGRES_URL": "PostgreSQL connection string",
                    "POSTGRES_HOST": "Database host (alternative)",
                    "POSTGRES_PORT": "Database port (alternative)",
                    "POSTGRES_DB": "Database name (alternative)",
                    "POSTGRES_USER": "Username (alternative)",
                    "POSTGRES_PASSWORD": "Password (alternative)"
                },
                "setup_help": "Provide PostgreSQL connection details",
                "example_usage": "Query your PostgreSQL database",
                "homepage": "https://github.com/modelcontextprotocol/servers"
            },
            "slack": {
                "name": "Slack Server",
                "description": "Interact with Slack workspaces. Send messages, read channels, manage Slack resources.",
                "category": "official",
                "package": "@modelcontextprotocol/server-slack",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "@modelcontextprotocol/server-slack"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {
                    "SLACK_BOT_TOKEN": "Slack bot token (xoxb-...)",
                    "SLACK_APP_TOKEN": "Slack app token (xapp-...)"
                },
                "setup_help": "Create a Slack app at https://api.slack.com/apps",
                "example_usage": "Send messages and read Slack channels",
                "homepage": "https://github.com/modelcontextprotocol/servers"
            },
            "google-drive": {
                "name": "Google Drive Server",
                "description": "Access Google Drive files and folders. Read, write, and manage Google Drive content.",
                "category": "official",
                "package": "@modelcontextprotocol/server-gdrive",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "@modelcontextprotocol/server-gdrive"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {
                    "GOOGLE_DRIVE_CREDENTIALS": "Google service account JSON",
                    "GOOGLE_DRIVE_TOKEN": "OAuth token (alternative)"
                },
                "setup_help": "Set up Google Drive API credentials",
                "example_usage": "Access and manage Google Drive files",
                "homepage": "https://github.com/modelcontextprotocol/servers"
            },
            "google-maps": {
                "name": "Google Maps Server",
                "description": "Access Google Maps API for location data, directions, and place information.",
                "category": "official",
                "package": "@modelcontextprotocol/server-google-maps",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "@modelcontextprotocol/server-google-maps"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"GOOGLE_MAPS_API_KEY": "Your Google Maps API key"},
                "setup_help": "Get API key from Google Cloud Console",
                "example_usage": "Get directions, search places, location data",
                "homepage": "https://github.com/modelcontextprotocol/servers"
            },
            "sqlite": {
                "name": "SQLite Server",
                "description": "Query and manage SQLite databases. Execute SQL queries, create tables, and manage database schemas.",
                "category": "official",
                "package": "mcp-server-sqlite-npx",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "mcp-server-sqlite-npx", "<database_path>"],
                "required_args": ["database_path"],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Provide path to your SQLite database file (.db or .sqlite)",
                "example_usage": "Query your application database or analyze data",
                "homepage": "https://github.com/modelcontextprotocol/servers"
            },
            "time": {
                "name": "Time Server",
                "description": "Time and timezone utilities. Get current time, convert between timezones, format dates.",
                "category": "official",
                "package": "mcp-server-time",
                "install_method": "uvx",
                "command": "uvx",
                "args_template": ["mcp-server-time", "--local-timezone", "<timezone>"],
                "required_args": ["timezone"],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Requires uvx (pip install uvx) for Python package management. Provide timezone in IANA format (e.g., America/New_York, Europe/London, UTC)",
                "example_usage": "Handle time-based operations and conversions",
                "homepage": "https://github.com/modelcontextprotocol/servers/tree/main/src/time"
            },
            "computer-control": {
                "name": "Computer Control Server",
                "description": "Control computer operations and automation through MCP interface. Interact with desktop applications and system functions.",
                "category": "community",
                "package": "computer-control-mcp",
                "install_method": "uvx",
                "command": "uvx",
                "args_template": ["computer-control-mcp@latest"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Requires uvx (pip install uvx) for Python package management. WARNING: Initial startup may take 60+ seconds due to large dependencies (OpenCV, ONNX runtime). May require additional system permissions for computer control.",
                "example_usage": "Automate desktop tasks and control computer operations",
                "homepage": "https://pypi.org/project/computer-control-mcp/"
            },
            "mcp-server-docker": {
                "name": "Docker MCP Server",
                "description": "Manage Docker with natural language. Compose containers, introspect running containers, and manage volumes, networks, and images.",
                "category": "community",
                "package": "mcp-server-docker",
                "install_method": "uvx",
                "command": "uvx",
                "args_template": ["mcp-server-docker"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {
                    "DOCKER_HOST": "Docker host URL (optional, e.g., ssh://user@host.com for remote Docker)"
                },
                "setup_help": "Requires Docker installed. For remote Docker access, set DOCKER_HOST environment variable to ssh://username@hostname",
                "example_usage": "Deploy WordPress with MySQL, manage containers with natural language",
                "homepage": "https://github.com/ckreiling/mcp-server-docker"
            },
            
            # Third-party community servers (selection from 500+ available)
            "aws-third-party": {
                "name": "AWS MCP Server",
                "description": "Specialized MCP servers that bring AWS best practices directly to your development workflow.",
                "category": "community",
                "package": "aws-mcp",
                "install_method": "git",
                "command": "git",
                "args_template": ["clone", "https://github.com/awslabs/mcp"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"AWS_ACCESS_KEY_ID": "AWS access key", "AWS_SECRET_ACCESS_KEY": "AWS secret key"},
                "setup_help": "Clone repository and follow setup instructions",
                "example_usage": "Manage AWS resources through AI agents",
                "homepage": "https://github.com/awslabs/mcp"
            },
            "azure": {
                "name": "Microsoft Azure Server",
                "description": "Access key Azure services and tools like Azure Storage, Cosmos DB, the Azure CLI, and more.",
                "category": "community",
                "package": "azure-mcp",
                "install_method": "git",
                "command": "git",
                "args_template": ["clone", "https://github.com/Azure/azure-mcp"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"AZURE_SUBSCRIPTION_ID": "Azure subscription ID"},
                "setup_help": "Clone repository and configure Azure credentials",
                "example_usage": "Manage Azure resources and services",
                "homepage": "https://github.com/Azure/azure-mcp"
            },
            "elasticsearch": {
                "name": "Elasticsearch Server",
                "description": "Query your data in Elasticsearch with natural language.",
                "category": "community",
                "package": "elasticsearch-mcp",
                "install_method": "git",
                "command": "git",
                "args_template": ["clone", "https://github.com/elastic/mcp-server-elasticsearch"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"ELASTICSEARCH_URL": "Elasticsearch cluster URL"},
                "setup_help": "Clone repository and configure Elasticsearch connection",
                "example_usage": "Search and analyze Elasticsearch data",
                "homepage": "https://github.com/elastic/mcp-server-elasticsearch"
            },
            "clickhouse": {
                "name": "ClickHouse Server",
                "description": "Query your ClickHouse database server with AI assistance.",
                "category": "community",
                "package": "clickhouse-mcp",
                "install_method": "git",
                "command": "git",
                "args_template": ["clone", "https://github.com/ClickHouse/mcp-clickhouse"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"CLICKHOUSE_URL": "ClickHouse server URL"},
                "setup_help": "Clone repository and configure ClickHouse connection",
                "example_usage": "Query and analyze ClickHouse databases",
                "homepage": "https://github.com/ClickHouse/mcp-clickhouse"
            },
            "cloudflare": {
                "name": "Cloudflare Server",
                "description": "Deploy, configure & interrogate your resources on the Cloudflare developer platform.",
                "category": "community",
                "package": "cloudflare-mcp",
                "install_method": "git",
                "command": "git",
                "args_template": ["clone", "https://github.com/cloudflare/mcp-server-cloudflare"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"CLOUDFLARE_API_TOKEN": "Cloudflare API token"},
                "setup_help": "Clone repository and configure Cloudflare credentials",
                "example_usage": "Manage Workers, KV, R2, D1 resources",
                "homepage": "https://github.com/cloudflare/mcp-server-cloudflare"
            },
            "linear": {
                "name": "Linear Server",
                "description": "Search, create, and update Linear issues, projects, and comments.",
                "category": "community",
                "package": "linear-mcp",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["linear-app/mcp"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"LINEAR_API_KEY": "Linear API key"},
                "setup_help": "Get API key from Linear settings",
                "example_usage": "Manage Linear issues and projects",
                "homepage": "https://linear.app/docs/mcp"
            },
            "hubspot": {
                "name": "HubSpot Server",
                "description": "Connect, manage, and interact with HubSpot CRM data.",
                "category": "community",
                "package": "hubspot-mcp",
                "install_method": "git",
                "command": "git",
                "args_template": ["clone", "https://github.com/HubSpot/mcp-server-hubspot"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"HUBSPOT_ACCESS_TOKEN": "HubSpot access token"},
                "setup_help": "Configure HubSpot API credentials",
                "example_usage": "Manage HubSpot CRM data and contacts",
                "homepage": "https://developer.hubspot.com/mcp"
            },
            "grafana": {
                "name": "Grafana Server",
                "description": "Search dashboards, investigate incidents and query datasources in your Grafana instance.",
                "category": "community",
                "package": "grafana-mcp",
                "install_method": "git",
                "command": "git",
                "args_template": ["clone", "https://github.com/grafana/mcp-grafana"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"GRAFANA_URL": "Grafana instance URL", "GRAFANA_API_KEY": "Grafana API key"},
                "setup_help": "Configure Grafana instance and API key",
                "example_usage": "Monitor dashboards and investigate incidents",
                "homepage": "https://github.com/grafana/mcp-grafana"
            },
            "confluence": {
                "name": "Confluence Server",
                "description": "Interact with Confluence Kafka and Confluent Cloud REST APIs.",
                "category": "community",
                "package": "confluent-mcp",
                "install_method": "git",
                "command": "git",
                "args_template": ["clone", "https://github.com/confluentinc/mcp-confluent"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"CONFLUENT_API_KEY": "Confluent API key"},
                "setup_help": "Configure Confluent Cloud credentials",
                "example_usage": "Manage Kafka clusters and topics",
                "homepage": "https://github.com/confluentinc/mcp-confluent"
            },
            "browserbase": {
                "name": "Browserbase Server",
                "description": "Automate browser interactions in the cloud (web navigation, data extraction, form filling).",
                "category": "community",
                "package": "browserbase-mcp",
                "install_method": "git",
                "command": "git",
                "args_template": ["clone", "https://github.com/browserbase/mcp-server-browserbase"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"BROWSERBASE_API_KEY": "Browserbase API key"},
                "setup_help": "Get API key from Browserbase dashboard",
                "example_usage": "Automate web browsing and data extraction",
                "homepage": "https://github.com/browserbase/mcp-server-browserbase"
            },
            "firecrawl": {
                "name": "Firecrawl Server",
                "description": "Extract web data with Firecrawl's powerful web scraping capabilities.",
                "category": "community",
                "package": "firecrawl-mcp",
                "install_method": "git",
                "command": "git",
                "args_template": ["clone", "https://github.com/mendableai/firecrawl-mcp-server"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"FIRECRAWL_API_KEY": "Firecrawl API key"},
                "setup_help": "Get API key from Firecrawl dashboard",
                "example_usage": "Scrape and extract web content",
                "homepage": "https://github.com/mendableai/firecrawl-mcp-server"
            },
            "exa": {
                "name": "Exa Search Server",
                "description": "Search Engine made for AIs by Exa - high-quality web search results.",
                "category": "community",
                "package": "exa-mcp",
                "install_method": "git",
                "command": "git",
                "args_template": ["clone", "https://github.com/exa-labs/exa-mcp-server"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"EXA_API_KEY": "Exa API key"},
                "setup_help": "Get API key from Exa dashboard",
                "example_usage": "Perform AI-optimized web searches",
                "homepage": "https://github.com/exa-labs/exa-mcp-server"
            },
            "kagi": {
                "name": "Kagi Search Server",
                "description": "Search the web using Kagi's search API for high-quality results.",
                "category": "community",
                "package": "kagi-mcp",
                "install_method": "git",
                "command": "git",
                "args_template": ["clone", "https://github.com/kagisearch/kagimcp"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"KAGI_API_KEY": "Kagi API key"},
                "setup_help": "Get API key from Kagi account settings",
                "example_usage": "Perform private web searches",
                "homepage": "https://github.com/kagisearch/kagimcp"
            },
            "jetbrains": {
                "name": "JetBrains IDEs Server",
                "description": "Work on your Java, Kotlin, Python, and other code with JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm) through AI assistance.",
                "category": "community",
                "package": "jetbrains-mcp",
                "install_method": "git",
                "command": "git",
                "args_template": ["clone", "https://github.com/JetBrains/mcp-jetbrains"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Requires JetBrains IDE installation",
                "example_usage": "AI-assisted coding in IntelliJ, PyCharm, etc.",
                "homepage": "https://github.com/JetBrains/mcp-jetbrains"
            },
            "heroku": {
                "name": "Heroku Server",
                "description": "Interact with the Heroku Platform for managing apps, add-ons, dynos, databases, and more.",
                "category": "community",
                "package": "heroku-mcp",
                "install_method": "git",
                "command": "git",
                "args_template": ["clone", "https://github.com/heroku/heroku-mcp-server"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"HEROKU_API_KEY": "Heroku API key"},
                "setup_help": "Get API key from Heroku account settings",
                "example_usage": "Deploy and manage Heroku applications",
                "homepage": "https://github.com/heroku/heroku-mcp-server"
            },
            "e2b": {
                "name": "E2B Code Sandbox Server",
                "description": "Run code in secure sandboxes hosted by E2B for safe code execution.",
                "category": "community",
                "package": "e2b-mcp",
                "install_method": "git",
                "command": "git",
                "args_template": ["clone", "https://github.com/e2b-dev/mcp-server"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"E2B_API_KEY": "E2B API key"},
                "setup_help": "Get API key from E2B dashboard",
                "example_usage": "Execute code safely in isolated environments",
                "homepage": "https://github.com/e2b-dev/mcp-server"
            },
            "xcode": {
                "name": "Xcode Build Server",
                "description": "XcodeBuildMCP provides tools for Xcode project management, simulator management, and app utilities.",
                "category": "community",
                "package": "xcodebuildmcp",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "xcodebuildmcp"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Requires Xcode and macOS",
                "example_usage": "Build iOS/macOS apps, manage simulators",
                "homepage": "https://github.com/cameroncooke/XcodeBuildMCP",
                "platform": "macos"
            },
            "figma": {
                "name": "Figma Server",
                "description": "ModelContextProtocol server for Figma design files and collaboration.",
                "category": "community",
                "package": "figma-mcp",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "figma-mcp"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"FIGMA_TOKEN": "Your Figma API token"},
                "setup_help": "Get API token from Figma account settings",
                "example_usage": "Access Figma designs and collaborate",
                "homepage": "https://www.npmjs.com/package/figma-mcp"
            },
            "code-sandbox-mcp": {
                "name": "Code Sandbox MCP Server",
                "description": "Secure code execution environment for running code snippets and testing applications.",
                "category": "community",
                "package": "code-sandbox-mcp",
                "install_method": "script",
                "command": "auto_detect",
                "args_template": "auto_detect",
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Install using: curl -fsSL https://raw.githubusercontent.com/Automata-Labs-team/code-sandbox-mcp/main/install.sh | bash (Linux) or irm https://raw.githubusercontent.com/Automata-Labs-team/code-sandbox-mcp/main/install.ps1 | iex (Windows). Will auto-detect installed location.",
                "example_usage": "Execute code safely in isolated sandbox environments",
                "homepage": "https://github.com/Automata-Labs-team/code-sandbox-mcp",
                "platform_config": {
                    "windows": {
                        "command": "cmd",
                        "args_template": ["/c", "{LOCALAPPDATA}\\code-sandbox-mcp\\code-sandbox-mcp.exe"],
                        "default_paths": [
                            "{LOCALAPPDATA}\\code-sandbox-mcp\\code-sandbox-mcp.exe",
                            "{APPDATA}\\code-sandbox-mcp\\code-sandbox-mcp.exe"
                        ]
                    },
                    "linux": {
                        "command": "sh",
                        "args_template": ["-c", "{HOME}/.local/bin/code-sandbox-mcp"],
                        "default_paths": [
                            "{HOME}/.local/bin/code-sandbox-mcp",
                            "/usr/local/bin/code-sandbox-mcp"
                        ]
                    },
                    "darwin": {
                        "command": "sh", 
                        "args_template": ["-c", "{HOME}/.local/bin/code-sandbox-mcp"],
                        "default_paths": [
                            "{HOME}/.local/bin/code-sandbox-mcp",
                            "/usr/local/bin/code-sandbox-mcp"
                        ]
                    }
                }
            }
        }
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for servers matching the query"""
        query = query.lower()
        results = []
        
        for server_id, server_info in self.servers.items():
            # Search in server ID, name, description, and category
            searchable_text = f"{server_id} {server_info['name']} {server_info['description']} {server_info['category']}".lower()
            
            if query in searchable_text:
                results.append({
                    "id": server_id,
                    **server_info
                })
        
        # Sort by relevance (exact matches first, then partial matches)
        def relevance_score(server):
            score = 0
            server_text = f"{server['id']} {server['name']}".lower()
            
            if query == server['id']:
                score += 100
            elif query in server['id']:
                score += 50
            elif query in server['name'].lower():
                score += 30
            elif query in server['description'].lower():
                score += 10
            
            return score
        
        results.sort(key=relevance_score, reverse=True)
        return results
    
    def get_server(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific server"""
        server_info = self.servers.get(server_id)
        if server_info:
            return {
                "id": server_id,
                **server_info
            }
        return None
    
    def list_categories(self) -> List[str]:
        """Get all available categories"""
        categories = set()
        for server in self.servers.values():
            categories.add(server["category"])
        return sorted(list(categories))
    
    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all servers in a specific category"""
        results = []
        for server_id, server_info in self.servers.items():
            if server_info["category"] == category:
                results.append({
                    "id": server_id,
                    **server_info
                })
        return results
    
    def get_all_servers(self) -> List[Dict[str, Any]]:
        """Get all servers in the registry"""
        results = []
        for server_id, server_info in self.servers.items():
            results.append({
                "id": server_id,
                **server_info
            })
        return results
    
    def _get_platform_key(self) -> str:
        """Get platform key for configuration"""
        system = platform.system().lower()
        if system == "darwin":
            return "darwin"
        elif system == "windows":
            return "windows"
        else:
            return "linux"
    
    def _expand_env_vars(self, path: str) -> str:
        """Expand environment variables in path string"""
        # Handle common environment variables
        if "{LOCALAPPDATA}" in path:
            path = path.replace("{LOCALAPPDATA}", os.environ.get("LOCALAPPDATA", ""))
        if "{APPDATA}" in path:
            path = path.replace("{APPDATA}", os.environ.get("APPDATA", ""))
        if "{HOME}" in path:
            path = path.replace("{HOME}", str(Path.home()))
        return path
    
    def _find_executable(self, server: Dict[str, Any]) -> Optional[str]:
        """Find the executable path for a server with platform config"""
        platform_config = server.get("platform_config", {})
        current_platform = self._get_platform_key()
        
        if current_platform not in platform_config:
            return None
        
        platform_info = platform_config[current_platform]
        default_paths = platform_info.get("default_paths", [])
        
        for path in default_paths:
            expanded_path = self._expand_env_vars(path)
            if Path(expanded_path).exists():
                return expanded_path
        
        return None
    
    def _configure_platform_specific(self, server: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Configure platform-specific command and args for auto_detect servers"""
        if server.get("command") != "auto_detect":
            return None
        
        platform_config = server.get("platform_config", {})
        current_platform = self._get_platform_key()
        
        if current_platform not in platform_config:
            return None
        
        platform_info = platform_config[current_platform]
        executable_path = self._find_executable(server)
        
        if not executable_path:
            return None
        
        # Build args from template, replacing executable path
        args = []
        for arg_template in platform_info.get("args_template", []):
            if "{" in arg_template and "}" in arg_template:
                # This contains environment variables, expand them
                expanded_arg = self._expand_env_vars(arg_template)
                args.append(expanded_arg)
            else:
                args.append(arg_template)
        
        return {
            "command": platform_info.get("command"),
            "args": args,
            "executable_path": executable_path
        }

    def generate_install_command(self, server_id: str, user_args: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Generate installation command for a server with user-provided arguments"""
        server = self.get_server(server_id)
        if not server:
            return None
        
        # Handle platform-specific auto-detection
        if server.get("command") == "auto_detect":
            platform_config = self._configure_platform_specific(server)
            if not platform_config:
                return None
            
            return {
                "server_id": server_id,
                "name": server["name"],
                "command": platform_config["command"],
                "args": platform_config["args"],
                "env": {},
                "package": server.get("package", ""),
                "install_method": server.get("install_method", "npm"),
                "executable_path": platform_config["executable_path"]
            }
        
        # Build command arguments for regular servers
        args = []
        for arg_template in server["args_template"]:
            if arg_template.startswith("<") and arg_template.endswith(">"):
                # This is a placeholder, replace with user input
                placeholder = arg_template[1:-1]  # Remove < >
                if placeholder in user_args:
                    args.append(user_args[placeholder])
                else:
                    # Required argument missing
                    return None
            else:
                # Static argument
                args.append(arg_template)
        
        # Build environment variables
        env_vars = {}
        for env_key, env_description in server["env_vars"].items():
            if env_key in user_args:
                env_vars[env_key] = user_args[env_key]
        
        return {
            "server_id": server_id,
            "name": server["name"],
            "command": server["command"],
            "args": args,
            "env": env_vars,
            "package": server.get("package", ""),
            "install_method": server.get("install_method", "npm")
        }