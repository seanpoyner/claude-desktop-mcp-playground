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
        # Start with hardcoded servers
        servers = {
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
            "pg-cli-server": {
                "name": "PG CLI Server",
                "description": "MCP server that exposes pg (Claude Desktop MCP Playground) commands as tools. Manage MCP servers directly from Claude Desktop.",
                "category": "community",
                "package": "pg-cli-mcp-server",
                "install_method": "script",
                "command": "auto_detect",
                "args_template": [],
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Automatically detects the server path. Requires Python 3.9+ and the 'pg' command in PATH. MCP dependency will be installed automatically if needed.",
                "example_usage": "Search, install, and manage MCP servers directly through Claude Desktop chat",
                "homepage": "https://github.com/seanpoyner/claude-desktop-mcp-playground/tree/main/mcp-servers/pg-cli-server",
                "platform_config": {
                    "windows": {
                        "command": "python",
                        "args_template": ["{executable_path}"],
                        "executable_patterns": [
                            "C:\\Users\\*\\claude-desktop-mcp-playground\\mcp-servers\\pg-cli-server\\launcher_v2.py",
                            "{USERPROFILE}\\claude-desktop-mcp-playground\\mcp-servers\\pg-cli-server\\launcher_v2.py",
                            "{USERPROFILE}\\Desktop\\claude-desktop-mcp-playground\\mcp-servers\\pg-cli-server\\launcher_v2.py"
                        ]
                    },
                    "macos": {
                        "command": "python3",
                        "args_template": ["{executable_path}"],
                        "executable_patterns": [
                            "~/claude-desktop-mcp-playground/mcp-servers/pg-cli-server/launcher_v2.py",
                            "~/Desktop/claude-desktop-mcp-playground/mcp-servers/pg-cli-server/launcher_v2.py",
                            "/Users/*/claude-desktop-mcp-playground/mcp-servers/pg-cli-server/launcher_v2.py"
                        ]
                    },
                    "linux": {
                        "command": "python3",
                        "args_template": ["{executable_path}"],
                        "executable_patterns": [
                            "~/claude-desktop-mcp-playground/mcp-servers/pg-cli-server/launcher_v2.py",
                            "~/Desktop/claude-desktop-mcp-playground/mcp-servers/pg-cli-server/launcher_v2.py",
                            "/home/*/claude-desktop-mcp-playground/mcp-servers/pg-cli-server/launcher_v2.py",
                            "/mnt/c/Users/*/claude-desktop-mcp-playground/mcp-servers/pg-cli-server/launcher_v2.py"
                        ]
                    }
                }
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
                "package": "@azure/mcp",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "@azure/mcp@latest", "server", "start"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {
                    "AZURE_TENANT_ID": "Your Azure tenant ID",
                    "AZURE_CLIENT_ID": "Your Azure client ID", 
                    "AZURE_CLIENT_SECRET": "Your Azure client secret"
                },
                "setup_help": "Configure Azure credentials via environment variables or use Azure CLI authentication",
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
            },
            "office-powerpoint": {
                "name": "Office PowerPoint Server",
                "description": "PowerPoint manipulation using python-pptx. Create, edit, and manipulate PowerPoint presentations through MCP protocol.",
                "category": "community",
                "package": "office-powerpoint-mcp-server",
                "install_method": "uvx",
                "command": "uvx",
                "args_template": ["--from", "office-powerpoint-mcp-server", "ppt_mcp_server.exe"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Requires uvx (pip install uvx) for Python package management. Installs and runs the server from PyPI.",
                "example_usage": "Create presentations, add slides, insert charts, tables, images, and text",
                "homepage": "https://github.com/GongRzhe/Office-PowerPoint-MCP-Server"
            },
            "office-word": {
                "name": "Office Word Server",
                "description": "Microsoft Word document manipulation using python-docx. Create, read, and edit Word documents with rich formatting capabilities.",
                "category": "community",
                "package": "office-word-mcp-server",
                "install_method": "uvx",
                "command": "uvx",
                "args_template": ["--from", "office-word-mcp-server", "word_mcp_server"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Requires uvx (pip install uvx) for Python package management. Installs and runs the server from PyPI.",
                "example_usage": "Create documents, add headings/paragraphs, insert tables/images, format text, convert to PDF",
                "homepage": "https://github.com/GongRzhe/Office-Word-MCP-Server"
            },
            "excel": {
                "name": "Excel MCP Server",
                "description": "Excel file manipulation without Microsoft Excel. Create, read, modify workbooks, apply formatting, create charts and pivot tables.",
                "category": "community",
                "package": "excel-mcp-server",
                "install_method": "uvx",
                "command": "uvx",
                "args_template": ["excel-mcp-server", "stdio"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Requires uvx (pip install uvx) for Python package management. Uses stdio transport for local file manipulation.",
                "example_usage": "Create workbooks, read/write data, apply formatting, create charts, generate pivot tables",
                "homepage": "https://github.com/haris-musa/excel-mcp-server"
            },
            "short-video-maker": {
                "name": "Short Video Maker",
                "description": "Automated short-form video creation with text-to-speech, captions, background videos from Pexels, and music. Creates TikTok/Instagram/YouTube Shorts.",
                "category": "community",
                "package": "short-video-maker",
                "install_method": "docker",
                "command": "docker",
                "args_template": ["run", "--rm", "--name", "short-video-maker", "-p", "3123:3123", "-e", "PEXELS_API_KEY=<pexels_api_key>", "-e", "LOG_LEVEL=error", "gyoridavid/short-video-maker:latest-tiny"],
                "required_args": ["pexels_api_key"],
                "optional_args": [],
                "env_vars": {"PEXELS_API_KEY": "Your free Pexels API key from https://www.pexels.com/api/"},
                "setup_help": "Requires Docker and a free Pexels API key. Server runs on localhost:3123 with both REST API and MCP endpoints. For MCP: use URL http://localhost:3123/mcp/sse. Requires ≥3GB RAM, ≥2 vCPU, ≥5GB disk space.",
                "example_usage": "Create short videos with AI narration, automatic captions, background footage, and music",
                "homepage": "https://github.com/gyoridavid/short-video-maker"
            },
            "vectorize": {
                "name": "Vectorize MCP Server",
                "description": "Advanced vector retrieval and text extraction using Vectorize. Perform semantic search, extract text from documents, and generate research reports.",
                "category": "community",
                "package": "@vectorize-io/vectorize-mcp-server",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "@vectorize-io/vectorize-mcp-server@latest"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {
                    "VECTORIZE_ORG_ID": "Your Vectorize Organization ID",
                    "VECTORIZE_TOKEN": "Your Vectorize API token",
                    "VECTORIZE_PIPELINE_ID": "Your Vectorize Pipeline ID"
                },
                "setup_help": "Get credentials from Vectorize dashboard. Provides vector search, document extraction, and deep research capabilities.",
                "example_usage": "Semantic document search, text extraction from PDFs, generate research reports",
                "homepage": "https://github.com/vectorize-io/vectorize-mcp-server"
            },
            "quickchart": {
                "name": "QuickChart Server",
                "description": "Chart generation using QuickChart.io. Create various chart types (bar, line, pie, doughnut, radar) with Chart.js configurations.",
                "category": "community",
                "package": "@gongrzhe/quickchart-mcp-server",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "@gongrzhe/quickchart-mcp-server"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "No additional setup required. Uses QuickChart.io service for chart generation.",
                "example_usage": "Generate bar/line/pie charts, create URLs for chart images, download chart files",
                "homepage": "https://github.com/GongRzhe/Quickchart-MCP-Server"
            },
            "jupyter-notebook": {
                "name": "Jupyter Notebook MCP",
                "description": "Connect Claude AI to Jupyter Notebook v6.x through WebSocket. Execute cells, manipulate notebooks, run data analysis.",
                "category": "community",
                "package": "jupyter-notebook-mcp",
                "install_method": "git",
                "command": "uv",
                "args_template": ["--directory", "<repo_path>/src", "run", "jupyter_mcp_server.py"],
                "required_args": ["repo_path"],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Requires uv package manager and Jupyter Notebook v6.x (NOT JupyterLab/v7). Clone repository, install kernel with 'uv run python -m ipykernel install --name jupyter-mcp', then start WebSocket server in notebook.",
                "example_usage": "Execute notebook cells, insert/edit cells, save notebooks, run data analysis, create presentations",
                "homepage": "https://github.com/jjsantos01/jupyter-notebook-mcp"
            },
            "screenshotone": {
                "name": "ScreenshotOne Server",
                "description": "Website screenshot capture using ScreenshotOne API. Render high-quality screenshots of websites and web pages.",
                "category": "community",
                "package": "screenshotone-mcp",
                "install_method": "git",
                "command": "node",
                "args_template": ["build/index.js"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {"SCREENSHOTONE_API_KEY": "Your ScreenshotOne API key"},
                "setup_help": "Get API key from ScreenshotOne.com. Repository will be cloned and built automatically.",
                "example_usage": "Capture website screenshots, generate page images for documentation, visual testing",
                "homepage": "https://github.com/screenshotone/mcp",
                "git_config": {
                    "url": "https://github.com/screenshotone/mcp",
                    "executable_path": "build/index.js",
                    "build_commands": ["npm install", "npm run build"]
                }
            },
            "obsidian": {
                "name": "Obsidian MCP Server (Direct File Access)",
                "description": "Direct file system access to Obsidian vaults. Read, create, edit and manage notes and tags through direct file operations.",
                "category": "community",
                "package": "mcp-obsidian",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["-y", "mcp-obsidian", "<vault_path>"],
                "required_args": ["vault_path"],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Provide the absolute path to your Obsidian vault directory as a command line argument. IMPORTANT: Backup your vault before use as this server has read/write access.",
                "example_usage": "Read/create/edit notes, search vault contents, manage tags, move/delete notes via direct file system access",
                "homepage": "https://github.com/StevenStavrakis/obsidian-mcp"
            },
            "obsidian-mcp-server": {
                "name": "Obsidian MCP Server (REST API)",
                "description": "Advanced Obsidian vault integration using the Local REST API plugin. Provides comprehensive note management, frontmatter editing, tag operations, and search capabilities with atomic operations and caching.",
                "category": "community",
                "package": "obsidian-mcp-server",
                "install_method": "npm",
                "command": "npx",
                "args_template": ["obsidian-mcp-server"],
                "required_args": [],
                "optional_args": [],
                "env_vars": {
                    "OBSIDIAN_API_KEY": "API key from Obsidian Local REST API plugin settings",
                    "OBSIDIAN_BASE_URL": "Base URL for Obsidian API (default: http://127.0.0.1:27123)",
                    "OBSIDIAN_VERIFY_SSL": "Whether to verify SSL certificates (default: false)",
                    "OBSIDIAN_ENABLE_CACHE": "Enable vault caching for performance (default: true)"
                },
                "setup_help": "1. Install 'Local REST API' plugin in Obsidian from Community plugins. 2. Enable the plugin and copy the API key from plugin settings. 3. Configure OBSIDIAN_API_KEY environment variable. 4. Optionally set OBSIDIAN_BASE_URL if using HTTPS (https://localhost:27124). Default uses HTTP on port 27123.",
                "example_usage": "Advanced note operations, atomic frontmatter editing, comprehensive search, tag management, directory operations with caching",
                "homepage": "https://github.com/cyanheads/obsidian-mcp-server"
            },
            "registry-manager": {
                "name": "Registry Manager",
                "description": "Dynamically add, manage, and organize custom MCP servers in the registry. Custom servers become discoverable via pg commands.",
                "category": "community",
                "package": "registry-manager-mcp-server",
                "install_method": "script",
                "command": "auto_detect",
                "args_template": [],
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Automatically detects the server path. Requires Python 3.9+ and MCP dependency will be installed automatically if needed.",
                "example_usage": "Add custom MCP servers, manage registry, import/export server definitions",
                "homepage": "https://github.com/seanpoyner/claude-desktop-mcp-playground/tree/main/mcp-servers/registry-manager",
                "platform_config": {
                    "windows": {
                        "command": "python",
                        "args_template": ["{executable_path}"],
                        "executable_patterns": [
                            "C:\\Users\\*\\claude-desktop-mcp-playground\\mcp-servers\\registry-manager\\launcher.py",
                            "{USERPROFILE}\\claude-desktop-mcp-playground\\mcp-servers\\registry-manager\\launcher.py",
                            "{USERPROFILE}\\Desktop\\claude-desktop-mcp-playground\\mcp-servers\\registry-manager\\launcher.py"
                        ]
                    },
                    "macos": {
                        "command": "python3",
                        "args_template": ["{executable_path}"],
                        "executable_patterns": [
                            "~/claude-desktop-mcp-playground/mcp-servers/registry-manager/launcher.py",
                            "~/Desktop/claude-desktop-mcp-playground/mcp-servers/registry-manager/launcher.py",
                            "/Users/*/claude-desktop-mcp-playground/mcp-servers/registry-manager/launcher.py"
                        ]
                    },
                    "linux": {
                        "command": "python3",
                        "args_template": ["{executable_path}"],
                        "executable_patterns": [
                            "~/claude-desktop-mcp-playground/mcp-servers/registry-manager/launcher.py",
                            "~/Desktop/claude-desktop-mcp-playground/mcp-servers/registry-manager/launcher.py",
                            "/home/*/claude-desktop-mcp-playground/mcp-servers/registry-manager/launcher.py",
                            "/mnt/c/Users/*/claude-desktop-mcp-playground/mcp-servers/registry-manager/launcher.py"
                        ]
                    }
                }
            },
            "doc-analyzer": {
                "name": "Documentation Analyzer",
                "description": "Analyze MCP server documentation from HTTP URLs to extract registration information. Automates the discovery and registration of new MCP servers.",
                "category": "community",
                "package": "doc-analyzer-mcp-server",
                "install_method": "script",
                "command": "auto_detect",
                "args_template": [],
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "setup_help": "Automatically detects the server path. Requires Python 3.9+ and aiohttp. Dependencies will be installed automatically if needed.",
                "example_usage": "Analyze documentation URLs, extract server definitions, generate registry commands",
                "homepage": "https://github.com/seanpoyner/claude-desktop-mcp-playground/tree/main/mcp-servers/doc-analyzer",
                "platform_config": {
                    "windows": {
                        "command": "python",
                        "args_template": ["{executable_path}"],
                        "executable_patterns": [
                            "C:\\Users\\*\\claude-desktop-mcp-playground\\mcp-servers\\doc-analyzer\\launcher.py",
                            "{USERPROFILE}\\claude-desktop-mcp-playground\\mcp-servers\\doc-analyzer\\launcher.py",
                            "{USERPROFILE}\\Desktop\\claude-desktop-mcp-playground\\mcp-servers\\doc-analyzer\\launcher.py"
                        ]
                    },
                    "macos": {
                        "command": "python3",
                        "args_template": ["{executable_path}"],
                        "executable_patterns": [
                            "~/claude-desktop-mcp-playground/mcp-servers/doc-analyzer/launcher.py",
                            "~/Desktop/claude-desktop-mcp-playground/mcp-servers/doc-analyzer/launcher.py",
                            "/Users/*/claude-desktop-mcp-playground/mcp-servers/doc-analyzer/launcher.py"
                        ]
                    },
                    "linux": {
                        "command": "python3",
                        "args_template": ["{executable_path}"],
                        "executable_patterns": [
                            "~/claude-desktop-mcp-playground/mcp-servers/doc-analyzer/launcher.py",
                            "~/Desktop/claude-desktop-mcp-playground/mcp-servers/doc-analyzer/launcher.py",
                            "/home/*/claude-desktop-mcp-playground/mcp-servers/doc-analyzer/launcher.py",
                            "/mnt/c/Users/*/claude-desktop-mcp-playground/mcp-servers/doc-analyzer/launcher.py"
                        ]
                    }
                }
            }
        }
        
        # Load custom servers from custom_registry.json if it exists
        custom_registry_path = Path(__file__).parent.parent / "custom_registry.json"
        if custom_registry_path.exists():
            try:
                with open(custom_registry_path, 'r') as f:
                    custom_servers = json.load(f)
                    # Merge custom servers into the registry
                    servers.update(custom_servers)
            except Exception as e:
                # Log error but continue with hardcoded servers
                print(f"Warning: Failed to load custom_registry.json: {e}")
        
        return servers
    
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
            return "macos"
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
        if "{USERPROFILE}" in path:
            path = path.replace("{USERPROFILE}", os.environ.get("USERPROFILE", str(Path.home())))
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
        
        # Check default_paths (existing functionality)
        default_paths = platform_info.get("default_paths", [])
        for path in default_paths:
            expanded_path = self._expand_env_vars(path)
            if Path(expanded_path).exists():
                return expanded_path
        
        # Check executable_patterns (new functionality for pg-cli-server)
        executable_patterns = platform_info.get("executable_patterns", [])
        for pattern in executable_patterns:
            expanded_pattern = self._expand_env_vars(pattern)
            
            # Handle wildcard patterns
            if "*" in expanded_pattern:
                import glob
                matches = glob.glob(expanded_pattern)
                for match in matches:
                    if Path(match).exists():
                        return match
            else:
                # Handle ~ expansion for Unix-like paths
                if expanded_pattern.startswith("~"):
                    expanded_pattern = str(Path(expanded_pattern).expanduser())
                
                if Path(expanded_pattern).exists():
                    return expanded_pattern
        
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
            if "{executable_path}" in arg_template:
                # Replace executable path placeholder
                expanded_arg = arg_template.replace("{executable_path}", executable_path)
                args.append(expanded_arg)
            elif "{" in arg_template and "}" in arg_template:
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
        
        # Handle git-based servers with automated installation
        if server.get("install_method") == "git" and "git_config" in server:
            git_config = server["git_config"]
            
            # Build environment variables
            env_vars = {}
            for env_key, env_description in server["env_vars"].items():
                if env_key in user_args:
                    env_vars[env_key] = user_args[env_key]
            
            return {
                "server_id": server_id,
                "name": server["name"],
                "command": server["command"],
                "args": server["args_template"],
                "env": env_vars,
                "package": server.get("package", ""),
                "install_method": "git",
                "git_config": git_config
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
                    # Check if this is a required argument
                    required_args = server.get("required_args", [])
                    if placeholder in required_args:
                        # Required argument missing
                        return None
                    # Optional argument missing - skip it
                    continue
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

            # Custom servers (managed by registry-manager)
            "wikidata":   "name": "Wikidata MCP Server",
                "description": "A server implementation for Wikidata API using the Model Context Protocol (MCP). Provides tools to interact with Wikidata, such as searching identifiers (entity and property), extracting metadata (label and description) and executing SPARQL queries.",
                "category": "community",
                "install_method": "uvx",
                "command": "uvx",
                "args_template": [
                                "@zzaebok/mcp-wikidata"
                ],
                "required_args": [],
                "optional_args": [],
                "env_vars": {},
                "homepage": "https://github.com/zzaebok/mcp-wikidata",
                "package": "@zzaebok/mcp-wikidata",
                "repository": "https://github.com/zzaebok/mcp-wikidata",
                "setup_help": "Install via uvx with package @zzaebok/mcp-wikidata",
                "example_usage": "Use this server to search Wikidata entities and properties, retrieve metadata, and execute SPARQL queries. Available tools: search_entity, search_property, get_properties, execute_sparql, get_metadata"
},
            "spotify": {
                "name": "Spotify MCP",
                "description": "MCP server to connect Claude with Spotify. Features include playback control (start, pause, skip), search for tracks/albums/artists/playlists, get info about media, manage Spotify queue, and manage/create/update playlists. Requires Spotify Premium account.",
                "category": "community",
                "install_method": "git",
                "command": "uv",
                "args_template": [
                                "--directory",
                                "<repo_path>",
                                "run",
                                "spotify-mcp"
                ],
                "homepage": "https://github.com/varunneal/spotify-mcp",
                "repository": "https://github.com/varunneal/spotify-mcp",
                "env_vars": {
                                "SPOTIFY_CLIENT_ID": "Your Spotify app client ID from developer.spotify.com",
                                "SPOTIFY_CLIENT_SECRET": "Your Spotify app client secret",
                                "SPOTIFY_REDIRECT_URI": "Redirect URI (e.g., http://127.0.0.1:8080/callback)"
                },
                "required_args": [],
                "setup_help": "1. Create a Spotify app at https://developer.spotify.com/dashboard\n2. Set redirect URI to http://127.0.0.1:8080/callback\n3. Requires Spotify Premium account\n4. Requires uv version >=0.54\n5. May need to restart Claude Desktop once or twice on first use",
                "platform": null
            },
            "protonmail-mcp": {
                "name": "ProtonMail MCP Server",
                "description": "Email sending functionality using Protonmail's SMTP service. Allows both Claude Desktop and Cline VSCode extension to send emails with support for CC/BCC, HTML content, and comprehensive error handling.",
                "homepage": "https://github.com/amotivv/protonmail-mcp",
                "repository": "https://github.com/amotivv/protonmail-mcp",
                "install_method": "git",
                "command": "node",
                "args_template": [
                                "<repository_path>/dist/index.js"
                ],
                "category": "custom",
                "env_vars": {
                                "PROTONMAIL_USERNAME": "Your Protonmail email address",
                                "PROTONMAIL_PASSWORD": "Your Protonmail SMTP password (not your regular login password)",
                                "PROTONMAIL_HOST": "SMTP server hostname (default: smtp.protonmail.ch)",
                                "PROTONMAIL_PORT": "SMTP server port (default: 587 for STARTTLS, 465 for SSL/TLS)",
                                "PROTONMAIL_SECURE": "Whether to use a secure connection (default: 'false' for port 587, 'true' for port 465)",
                                "DEBUG": "Enable debug logging (set to 'true' to see detailed logs, 'false' to hide them)"
                },
                "setup_help": "1. Clone the repository: git clone https://github.com/amotivv/protonmail-mcp.git\n2. Install dependencies: npm install\n3. Build the project: npm run build\n4. Configure environment variables with your ProtonMail SMTP credentials\n5. Get your SMTP password from ProtonMail settings (not your regular login password)\n6. Reference: https://proton.me/support/smtp-submission",
                "example_usage": "Send emails with support for multiple recipients, CC/BCC, plain text or HTML content. Example: send_email tool with parameters: to, subject, body, isHtml (optional), cc (optional), bcc (optional)"
            }
        }
        
        # Load custom servers from external JSON files
        custom_servers = self._load_custom_servers()
        servers.update(custom_servers)
        
        return servers
    
    def _load_custom_servers(self) -> Dict[str, Dict[str, Any]]:
        """Load custom server configurations from JSON files"""
        custom_servers = {}
        
        # Look for custom server JSON files
        custom_paths = [
            Path.home() / ".config" / "claude-mcp" / "servers",
            Path("/etc/claude-mcp/servers"),
            Path("./mcp-servers")
        ]
        
        for base_path in custom_paths:
            if base_path.exists() and base_path.is_dir():
                for json_file in base_path.glob("*.json"):
                    try:
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                            if isinstance(data, dict):
                                # Single server definition
                                if "name" in data and "command" in data:
                                    server_id = json_file.stem
                                    custom_servers[server_id] = data
                                # Multiple server definitions
                                else:
                                    for server_id, server_data in data.items():
                                        if isinstance(server_data, dict):
                                            custom_servers[server_id] = server_data
                    except (json.JSONDecodeError, IOError) as e:
                        print(f"Warning: Failed to load {json_file}: {e}")
        
        return custom_servers
    
    def search(self, query: str = "") -> List[Dict[str, Any]]:
        """Search for servers by name or description"""
        if not query:
            return list(self.servers.values())
        
        query_lower = query.lower()
        results = []
        
        for server_id, server_info in self.servers.items():
            if (query_lower in server_info.get("name", "").lower() or
                query_lower in server_info.get("description", "").lower() or
                query_lower in server_id.lower()):
                results.append({**server_info, "id": server_id})
        
        return results
    
    def get_server(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific server by ID"""
        return self.servers.get(server_id)
    
    def get_install_command(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get installation command details for a server"""
        server = self.get_server(server_id)
        if not server:
            return None
        
        return {
            "method": server.get("install_method", "npm"),
            "package": server.get("package", server_id),
            "command": server.get("command", "npx"),
            "args_template": server.get("args_template", []),
            "required_args": server.get("required_args", []),
            "optional_args": server.get("optional_args", []),
            "env_vars": server.get("env_vars", {}),
            "platform": server.get("platform")
        }