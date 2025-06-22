#!/usr/bin/env python3
"""
Documentation Analyzer MCP Server

This MCP server can examine publicly available MCP server documentation from HTTP URLs,
extract the necessary information, and either register the server automatically or
provide the structured data needed for manual registration via the registry manager.
"""

import asyncio
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import aiohttp

import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.lowlevel.server import NotificationOptions
from mcp.server.stdio import stdio_server

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("doc-analyzer-server")

class DocumentationAnalyzer:
    """Analyzes MCP server documentation and extracts registration information."""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_documentation(self, url: str) -> Tuple[str, str]:
        """Fetch documentation content from URL."""
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: {response.reason}")
                
                content_type = response.headers.get('content-type', '').lower()
                content = await response.text()
                
                return content, content_type
                
        except Exception as e:
            raise Exception(f"Failed to fetch documentation: {str(e)}")
    
    def extract_server_info_from_markdown(self, content: str, url: str) -> Dict[str, Any]:
        """Extract server information from Markdown documentation."""
        info = {
            "name": "",
            "description": "",
            "install_method": "",
            "package": "",
            "repository": "",
            "command": "",
            "args_template": [],
            "env_vars": {},
            "setup_help": "",
            "example_usage": "",
            "homepage": url,
            "category": "community"
        }
        
        # Extract title/name (first # heading)
        title_match = re.search(r'^#\s+(.+?)(?:\n|$)', content, re.MULTILINE)
        if title_match:
            raw_title = title_match.group(1).strip()
            # Clean up common patterns
            info["name"] = re.sub(r'\s*(MCP\s*)?Server\s*$', ' Server', raw_title).strip()
        
        # Extract description (first paragraph after title or explicit description section)
        desc_patterns = [
            r'(?:^|\n)##?\s*(?:Description|About|Overview)\s*\n\s*(.+?)(?:\n\s*\n|\n\s*#)',
            r'^#[^#\n]*\n\s*(.+?)(?:\n\s*\n|\n\s*#)',
        ]
        for pattern in desc_patterns:
            desc_match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if desc_match:
                info["description"] = desc_match.group(1).strip()[:200]  # Limit length
                break
        
        # Detect installation method and package info
        npm_patterns = [
            r'npm\s+install\s+(?:-g\s+)?([^\s\n]+)',
            r'npx\s+([^\s\n]+)',
            r'"([^"]*mcp[^"]*)":\s*"[^"]*"',  # package.json style
        ]
        
        git_patterns = [
            r'git\s+clone\s+([^\s\n]+)',
            r'https://github\.com/([^\s\n/]+/[^\s\n/]+)',
        ]
        
        uvx_patterns = [
            r'uvx\s+([^\s\n]+)',
            r'pip\s+install\s+([^\s\n]+)',
        ]
        
        docker_patterns = [
            r'docker\s+(?:run|pull)\s+[^\s]*\s*([^\s\n]+)',
        ]
        
        # Check for NPM
        for pattern in npm_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                info["install_method"] = "npm"
                info["package"] = match.group(1)
                info["command"] = "npx"
                info["args_template"] = ["-y", match.group(1)]
                break
        
        # Check for Git if NPM not found
        if not info["install_method"]:
            for pattern in git_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    info["install_method"] = "git"
                    if match.group(1).startswith('http'):
                        info["repository"] = match.group(1)
                    else:
                        info["repository"] = f"https://github.com/{match.group(1)}"
                    info["command"] = "node"  # Common default
                    break
        
        # Check for Python/uvx
        if not info["install_method"]:
            for pattern in uvx_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match and 'mcp' in match.group(1).lower():
                    info["install_method"] = "uvx"
                    info["package"] = match.group(1)
                    info["command"] = "uvx"
                    info["args_template"] = [match.group(1)]
                    break
        
        # Check for Docker
        if not info["install_method"]:
            for pattern in docker_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    info["install_method"] = "docker"
                    info["package"] = match.group(1)
                    info["command"] = "docker"
                    info["args_template"] = ["run", "-i", "--rm", match.group(1)]
                    break
        
        # Extract environment variables
        env_section_pattern = r'##?\s*(?:Environment|Config|Setup|Variables)\s*\n(.*?)(?:\n\s*##?|\Z)'
        env_match = re.search(env_section_pattern, content, re.DOTALL | re.IGNORECASE)
        if env_match:
            env_content = env_match.group(1)
            # Look for KEY=value or KEY: description patterns
            env_patterns = [
                r'([A-Z_]+)[:=]\s*([^\n]+)',
                r'`([A-Z_]+)`[:\s]*([^\n]+)',
                r'\$\{?([A-Z_]+)\}?[:\s]*([^\n]+)',
            ]
            for pattern in env_patterns:
                for match in re.finditer(pattern, env_content):
                    key = match.group(1)
                    desc = match.group(2).strip()
                    # Clean up description
                    desc = re.sub(r'^[:\-\s]*', '', desc)
                    desc = re.sub(r'[`"\']', '', desc)
                    info["env_vars"][key] = desc[:100]  # Limit length
        
        # Extract setup instructions
        setup_patterns = [
            r'##?\s*(?:Setup|Installation|Getting Started|Configuration)\s*\n(.*?)(?:\n\s*##?|\Z)',
            r'##?\s*(?:Usage|Example)\s*\n(.*?)(?:\n\s*##?|\Z)',
        ]
        for pattern in setup_patterns:
            setup_match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if setup_match:
                setup_text = setup_match.group(1).strip()
                # Clean up and limit length
                setup_text = re.sub(r'```[^`]*```', '', setup_text)  # Remove code blocks
                setup_text = re.sub(r'\n\s*\n', ' ', setup_text)  # Collapse whitespace
                info["setup_help"] = setup_text[:300]
                break
        
        # Extract example usage
        example_patterns = [
            r'##?\s*(?:Example|Usage|Use Cases?)\s*\n(.*?)(?:\n\s*##?|\Z)',
        ]
        for pattern in example_patterns:
            example_match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if example_match:
                example_text = example_match.group(1).strip()
                example_text = re.sub(r'```[^`]*```', '', example_text)
                example_text = re.sub(r'\n\s*\n', ' ', example_text)
                info["example_usage"] = example_text[:200]
                break
        
        return info
    
    def extract_server_info_from_html(self, content: str, url: str) -> Dict[str, Any]:
        """Extract server information from HTML documentation."""
        # Simple HTML parsing - look for common patterns
        info = {
            "name": "",
            "description": "",
            "install_method": "",
            "package": "",
            "repository": url,
            "command": "",
            "args_template": [],
            "env_vars": {},
            "setup_help": "",
            "example_usage": "",
            "homepage": url,
            "category": "community"
        }
        
        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
        if title_match:
            info["name"] = title_match.group(1).strip()
        
        # Extract description from meta tag
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)', content, re.IGNORECASE)
        if desc_match:
            info["description"] = desc_match.group(1).strip()
        
        # Look for common installation patterns in text
        text_content = re.sub(r'<[^>]+>', ' ', content)  # Strip HTML tags
        
        # Check for npm
        npm_match = re.search(r'npm\s+install[^a-zA-Z]+([^\s\n]+)', text_content, re.IGNORECASE)
        if npm_match:
            info["install_method"] = "npm"
            info["package"] = npm_match.group(1)
            info["command"] = "npx"
            info["args_template"] = ["-y", npm_match.group(1)]
        
        return info
    
    def detect_github_repo_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract information if the URL is a GitHub repository."""
        github_pattern = r'https://github\.com/([^/]+)/([^/?#]+)'
        match = re.match(github_pattern, url)
        if not match:
            return None
        
        owner, repo = match.groups()
        return {
            "repository": url,
            "install_method": "git",
            "command": "node",  # Default assumption
            "args_template": [f"<repo_path>/dist/index.js"],  # Common pattern
            "setup_help": f"Repository will be cloned from {url}",
            "homepage": url
        }
    
    def validate_extracted_info(self, info: Dict[str, Any]) -> List[str]:
        """Validate extracted server information."""
        errors = []
        
        if not info.get("name"):
            errors.append("Could not extract server name")
        
        if not info.get("description"):
            errors.append("Could not extract server description")
        
        if not info.get("install_method"):
            errors.append("Could not determine installation method")
        
        if info.get("install_method") == "npm" and not info.get("package"):
            errors.append("NPM installation method requires package name")
        
        if info.get("install_method") == "git" and not info.get("repository"):
            errors.append("Git installation method requires repository URL")
        
        if not info.get("command"):
            errors.append("Could not determine command to run server")
        
        return errors
    
    def generate_server_id(self, info: Dict[str, Any], url: str) -> str:
        """Generate a server ID from the extracted information."""
        # Try to create ID from name
        if info.get("name"):
            # Clean name and make it ID-friendly
            name = info["name"].lower()
            name = re.sub(r'\s*(mcp\s*)?server\s*', '', name)
            name = re.sub(r'[^a-z0-9\-]', '-', name)
            name = re.sub(r'-+', '-', name).strip('-')
            if name and len(name) > 2:
                return name
        
        # Try to extract from package name
        if info.get("package"):
            package = info["package"].lower()
            package = re.sub(r'[^a-z0-9\-]', '-', package)
            return package
        
        # Try to extract from URL
        parsed = urlparse(url)
        if parsed.path:
            path_parts = [p for p in parsed.path.split('/') if p]
            if path_parts:
                return path_parts[-1].lower()
        
        # Fallback
        return "custom-server"

class DocAnalyzerServer:
    def __init__(self):
        self.server = Server("doc-analyzer")
        self._setup_handlers()
    
    def _setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available documentation analysis tools."""
            return [
                types.Tool(
                    name="analyze_mcp_documentation",
                    description="Analyze MCP server documentation from a URL and extract registration information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "HTTP URL to the MCP server documentation (README, GitHub repo, etc.)"
                            },
                            "suggested_id": {
                                "type": "string",
                                "description": "Optional custom server ID (will auto-generate if not provided)"
                            }
                        },
                        "required": ["url"]
                    }
                ),
                types.Tool(
                    name="extract_server_definition",
                    description="Extract a complete server definition from documentation URL for registry manager",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "HTTP URL to the MCP server documentation"
                            },
                            "server_id": {
                                "type": "string",
                                "description": "Custom server ID for registration"
                            },
                            "override_info": {
                                "type": "object",
                                "description": "Optional overrides for extracted information",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "install_method": {"type": "string"},
                                    "package": {"type": "string"},
                                    "command": {"type": "string"}
                                }
                            }
                        },
                        "required": ["url", "server_id"]
                    }
                ),
                types.Tool(
                    name="preview_registration",
                    description="Preview what would be registered without actually registering",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "HTTP URL to analyze"
                            },
                            "server_id": {
                                "type": "string",
                                "description": "Server ID to use"
                            }
                        },
                        "required": ["url"]
                    }
                ),
                types.Tool(
                    name="batch_analyze_urls",
                    description="Analyze multiple MCP server documentation URLs at once",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "urls": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of documentation URLs to analyze"
                            },
                            "auto_generate_ids": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to auto-generate server IDs"
                            }
                        },
                        "required": ["urls"]
                    }
                ),
                types.Tool(
                    name="generate_registry_commands",
                    description="Generate ready-to-use commands for the registry manager",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "Documentation URL to analyze"
                            },
                            "server_id": {
                                "type": "string",
                                "description": "Server ID for registration"
                            }
                        },
                        "required": ["url", "server_id"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
            """Handle tool calls for documentation analysis."""
            logger.info(f"Tool call received: {name} with arguments keys: {list(arguments.keys())}")
            
            try:
                if name == "analyze_mcp_documentation":
                    result = await self._analyze_documentation(arguments)
                elif name == "extract_server_definition":
                    result = await self._extract_server_definition(arguments)
                elif name == "preview_registration":
                    result = await self._preview_registration(arguments)
                elif name == "batch_analyze_urls":
                    result = await self._batch_analyze_urls(arguments)
                elif name == "generate_registry_commands":
                    result = await self._generate_registry_commands(arguments)
                else:
                    result = f"Error: Unknown tool '{name}'"
                
                logger.info(f"Tool call completed: {name}")
                return [types.TextContent(type="text", text=result)]
                
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}", exc_info=True)
                error_msg = f"Error: {str(e)}"
                return [types.TextContent(type="text", text=error_msg)]

    async def _analyze_documentation(self, arguments: dict[str, Any]) -> str:
        """Analyze MCP server documentation from a URL."""
        url = arguments["url"]
        suggested_id = arguments.get("suggested_id")
        
        async with DocumentationAnalyzer() as analyzer:
            try:
                # Fetch documentation
                content, content_type = await analyzer.fetch_documentation(url)
                
                # Determine format and extract info
                if 'html' in content_type:
                    info = analyzer.extract_server_info_from_html(content, url)
                else:
                    # Assume markdown or plain text
                    info = analyzer.extract_server_info_from_markdown(content, url)
                
                # Check if it's a GitHub repo for additional context
                github_info = analyzer.detect_github_repo_info(url)
                if github_info:
                    # Merge GitHub-specific info
                    for key, value in github_info.items():
                        if not info.get(key):
                            info[key] = value
                
                # Generate server ID
                server_id = suggested_id or analyzer.generate_server_id(info, url)
                
                # Validate extracted information
                errors = analyzer.validate_extracted_info(info)
                
                # Format results
                result = f"📄 **Documentation Analysis Results**\n\n"
                result += f"🌐 **Source URL:** {url}\n"
                result += f"📝 **Content Type:** {content_type}\n"
                result += f"🆔 **Generated Server ID:** `{server_id}`\n\n"
                
                result += "## 📋 Extracted Information\n\n"
                result += f"**Name:** {info.get('name', 'Not found')}\n"
                result += f"**Description:** {info.get('description', 'Not found')}\n"
                result += f"**Install Method:** {info.get('install_method', 'Not detected')}\n"
                
                if info.get('package'):
                    result += f"**Package:** {info['package']}\n"
                if info.get('repository'):
                    result += f"**Repository:** {info['repository']}\n"
                
                result += f"**Command:** {info.get('command', 'Not detected')}\n"
                
                if info.get('args_template'):
                    result += f"**Args Template:** {info['args_template']}\n"
                
                if info.get('env_vars'):
                    result += f"**Environment Variables:** {len(info['env_vars'])} found\n"
                    for key, desc in info['env_vars'].items():
                        result += f"  • `{key}`: {desc}\n"
                
                if info.get('setup_help'):
                    result += f"**Setup Help:** {info['setup_help'][:100]}...\n"
                
                if info.get('example_usage'):
                    result += f"**Example Usage:** {info['example_usage'][:100]}...\n"
                
                # Show validation results
                if errors:
                    result += f"\n## ⚠️ Validation Issues\n\n"
                    for error in errors:
                        result += f"• {error}\n"
                    result += f"\n💡 **Recommendation:** Manual review and correction needed before registration.\n"
                else:
                    result += f"\n## ✅ Validation Passed\n\n"
                    result += f"The extracted information appears complete and ready for registration.\n"
                
                # Provide next steps
                result += f"\n## 🚀 Next Steps\n\n"
                result += f"1. **Preview registration:** Use `preview_registration` tool\n"
                result += f"2. **Generate commands:** Use `generate_registry_commands` tool  \n"
                result += f"3. **Extract definition:** Use `extract_server_definition` tool\n"
                result += f"4. **Register server:** Use the registry manager with extracted data\n"
                
                return result
                
            except Exception as e:
                return f"❌ **Analysis failed:** {str(e)}\n\n" \
                       f"**Troubleshooting:**\n" \
                       f"• Check that the URL is accessible\n" \
                       f"• Verify the URL contains MCP server documentation\n" \
                       f"• Try a direct link to README.md or documentation page"

    async def _extract_server_definition(self, arguments: dict[str, Any]) -> str:
        """Extract a complete server definition for registry manager."""
        url = arguments["url"]
        server_id = arguments["server_id"]
        overrides = arguments.get("override_info", {})
        
        async with DocumentationAnalyzer() as analyzer:
            try:
                content, content_type = await analyzer.fetch_documentation(url)
                
                if 'html' in content_type:
                    info = analyzer.extract_server_info_from_html(content, url)
                else:
                    info = analyzer.extract_server_info_from_markdown(content, url)
                
                # Apply GitHub repo detection
                github_info = analyzer.detect_github_repo_info(url)
                if github_info:
                    for key, value in github_info.items():
                        if not info.get(key):
                            info[key] = value
                
                # Apply user overrides
                info.update(overrides)
                
                # Ensure required fields have defaults
                if not info.get("name"):
                    info["name"] = server_id.replace('-', ' ').title() + " Server"
                if not info.get("description"):
                    info["description"] = f"MCP server extracted from {url}"
                if not info.get("category"):
                    info["category"] = "community"
                
                # Clean up the definition for registry manager
                server_def = {
                    "name": info["name"],
                    "description": info["description"],
                    "category": info["category"],
                    "install_method": info.get("install_method", "manual"),
                    "command": info.get("command", "node"),
                    "args_template": info.get("args_template", []),
                    "homepage": info.get("homepage", url)
                }
                
                # Add optional fields if present
                if info.get("package"):
                    server_def["package"] = info["package"]
                if info.get("repository"):
                    server_def["repository"] = info["repository"]
                if info.get("env_vars"):
                    server_def["env_vars"] = info["env_vars"]
                if info.get("setup_help"):
                    server_def["setup_help"] = info["setup_help"]
                if info.get("example_usage"):
                    server_def["example_usage"] = info["example_usage"]
                
                # Format as JSON for easy copy-paste
                json_def = json.dumps(server_def, indent=2, ensure_ascii=False)
                
                result = f"📦 **Server Definition for Registry Manager**\n\n"
                result += f"**Server ID:** `{server_id}`\n\n"
                result += f"**Ready-to-use definition:**\n\n"
                result += f"```json\n{json_def}\n```\n\n"
                
                result += f"## 🔧 Registry Manager Command\n\n"
                result += f"Use the `add_custom_server` tool with:\n\n"
                result += f"```\nserver_id: \"{server_id}\"\n"
                result += f"server_definition: {json_def}\n```\n\n"
                
                # Validate
                errors = analyzer.validate_extracted_info(info)
                if errors:
                    result += f"## ⚠️ Validation Warnings\n\n"
                    for error in errors:
                        result += f"• {error}\n"
                    result += f"\n**Note:** You may need to manually complete missing information.\n"
                else:
                    result += f"## ✅ Definition Complete\n\n"
                    result += f"The server definition is ready for registration!\n"
                
                return result
                
            except Exception as e:
                return f"❌ **Failed to extract server definition:** {str(e)}"

    async def _preview_registration(self, arguments: dict[str, Any]) -> str:
        """Preview what would be registered without actually registering."""
        url = arguments["url"]
        server_id = arguments.get("server_id")
        
        async with DocumentationAnalyzer() as analyzer:
            try:
                content, content_type = await analyzer.fetch_documentation(url)
                
                if 'html' in content_type:
                    info = analyzer.extract_server_info_from_html(content, url)
                else:
                    info = analyzer.extract_server_info_from_markdown(content, url)
                
                github_info = analyzer.detect_github_repo_info(url)
                if github_info:
                    for key, value in github_info.items():
                        if not info.get(key):
                            info[key] = value
                
                if not server_id:
                    server_id = analyzer.generate_server_id(info, url)
                
                result = f"👀 **Registration Preview**\n\n"
                result += f"**Server ID:** `{server_id}`\n"
                result += f"**Source:** {url}\n\n"
                
                result += f"## 📋 What Will Be Registered\n\n"
                result += f"**Name:** {info.get('name', '❌ Missing')}\n"
                result += f"**Description:** {info.get('description', '❌ Missing')}\n"
                result += f"**Category:** community\n"
                result += f"**Install Method:** {info.get('install_method', '❌ Missing')}\n"
                result += f"**Command:** {info.get('command', '❌ Missing')}\n"
                
                if info.get('package'):
                    result += f"**Package:** {info['package']}\n"
                if info.get('repository'):
                    result += f"**Repository:** {info['repository']}\n"
                if info.get('args_template'):
                    result += f"**Arguments:** {info['args_template']}\n"
                
                result += f"\n## 🔍 After Registration\n\n"
                result += f"You'll be able to:\n"
                result += f"• Search: `pg config search {server_id}`\n"
                result += f"• Get info: `pg config info {server_id}`\n"
                result += f"• Install: `pg config install {server_id}`\n"
                
                # Check completeness
                errors = analyzer.validate_extracted_info(info)
                if errors:
                    result += f"\n## ⚠️ Issues to Address\n\n"
                    for error in errors:
                        result += f"• {error}\n"
                    result += f"\n**Recommendation:** Fix these issues before registering.\n"
                else:
                    result += f"\n## ✅ Ready for Registration\n\n"
                    result += f"All required information has been extracted successfully!\n"
                
                return result
                
            except Exception as e:
                return f"❌ **Preview failed:** {str(e)}"

    async def _batch_analyze_urls(self, arguments: dict[str, Any]) -> str:
        """Analyze multiple URLs at once."""
        urls = arguments["urls"]
        auto_generate_ids = arguments.get("auto_generate_ids", True)
        
        if len(urls) > 10:
            return "❌ **Too many URLs.** Maximum 10 URLs per batch to avoid timeouts."
        
        results = []
        async with DocumentationAnalyzer() as analyzer:
            for i, url in enumerate(urls, 1):
                try:
                    content, content_type = await analyzer.fetch_documentation(url)
                    
                    if 'html' in content_type:
                        info = analyzer.extract_server_info_from_html(content, url)
                    else:
                        info = analyzer.extract_server_info_from_markdown(content, url)
                    
                    github_info = analyzer.detect_github_repo_info(url)
                    if github_info:
                        for key, value in github_info.items():
                            if not info.get(key):
                                info[key] = value
                    
                    if auto_generate_ids:
                        server_id = analyzer.generate_server_id(info, url)
                    else:
                        server_id = f"server-{i}"
                    
                    errors = analyzer.validate_extracted_info(info)
                    status = "✅ Ready" if not errors else f"⚠️ {len(errors)} issues"
                    
                    results.append({
                        "url": url,
                        "server_id": server_id,
                        "name": info.get("name", "Unknown"),
                        "install_method": info.get("install_method", "Unknown"),
                        "status": status,
                        "errors": errors
                    })
                    
                except Exception as e:
                    results.append({
                        "url": url,
                        "server_id": f"failed-{i}",
                        "name": "Failed to analyze",
                        "install_method": "Unknown",
                        "status": f"❌ Error: {str(e)[:50]}...",
                        "errors": [str(e)]
                    })
        
        # Format results
        result = f"📊 **Batch Analysis Results** ({len(urls)} URLs)\n\n"
        
        for i, res in enumerate(results, 1):
            result += f"## {i}. {res['name']}\n"
            result += f"**URL:** {res['url']}\n"
            result += f"**Server ID:** `{res['server_id']}`\n"
            result += f"**Install Method:** {res['install_method']}\n"
            result += f"**Status:** {res['status']}\n"
            if res['errors']:
                result += f"**Issues:** {', '.join(res['errors'][:2])}\n"
            result += "\n"
        
        # Summary
        ready_count = sum(1 for r in results if r['status'].startswith('✅'))
        result += f"## 📈 Summary\n\n"
        result += f"• **Ready for registration:** {ready_count}/{len(results)}\n"
        result += f"• **Need manual review:** {len(results) - ready_count}/{len(results)}\n\n"
        
        if ready_count > 0:
            result += f"💡 **Next step:** Use `extract_server_definition` for each ready server.\n"
        
        return result

    async def _generate_registry_commands(self, arguments: dict[str, Any]) -> str:
        """Generate ready-to-use commands for the registry manager."""
        url = arguments["url"]
        server_id = arguments["server_id"]
        
        async with DocumentationAnalyzer() as analyzer:
            try:
                content, content_type = await analyzer.fetch_documentation(url)
                
                if 'html' in content_type:
                    info = analyzer.extract_server_info_from_html(content, url)
                else:
                    info = analyzer.extract_server_info_from_markdown(content, url)
                
                github_info = analyzer.detect_github_repo_info(url)
                if github_info:
                    for key, value in github_info.items():
                        if not info.get(key):
                            info[key] = value
                
                # Build server definition
                server_def = {
                    "name": info.get("name", f"{server_id.replace('-', ' ').title()} Server"),
                    "description": info.get("description", f"MCP server from {url}"),
                    "category": "community",
                    "install_method": info.get("install_method", "manual"),
                    "command": info.get("command", "node"),
                    "args_template": info.get("args_template", []),
                    "homepage": url
                }
                
                # Add optional fields
                for field in ["package", "repository", "env_vars", "setup_help", "example_usage"]:
                    if info.get(field):
                        server_def[field] = info[field]
                
                result = f"🛠️ **Registry Manager Commands**\n\n"
                result += f"Copy and paste these commands to register the server:\n\n"
                
                # Command for add_custom_server tool
                result += f"## 1. Add Custom Server\n\n"
                result += f"**Tool:** `add_custom_server`\n\n"
                result += f"**Arguments:**\n"
                result += f"```json\n"
                result += f"{{\n"
                result += f'  "server_id": "{server_id}",\n'
                result += f'  "server_definition": {json.dumps(server_def, indent=4)}\n'
                result += f"}}\n"
                result += f"```\n\n"
                
                # Command for pg CLI (alternative)
                result += f"## 2. Alternative: PG CLI Commands\n\n"
                result += f"After registration, you can use these commands:\n\n"
                result += f"```bash\n"
                result += f"# Search for the server\n"
                result += f"pg config search {server_id}\n\n"
                result += f"# Get detailed information\n"
                result += f"pg config info {server_id}\n\n"
                result += f"# Install the server\n"
                result += f"pg config install {server_id}\n"
                
                # Add environment variables if needed
                if info.get("env_vars"):
                    for env_key in info["env_vars"].keys():
                        result += f" --env {env_key}=<your_value>"
                
                result += f"\n```\n\n"
                
                # Validation status
                errors = analyzer.validate_extracted_info(info)
                if errors:
                    result += f"## ⚠️ Pre-Registration Checklist\n\n"
                    result += f"Please verify/fix these items before registration:\n\n"
                    for error in errors:
                        result += f"• [ ] {error}\n"
                    result += f"\n"
                
                result += f"## 🎯 Expected Outcome\n\n"
                result += f"After successful registration:\n"
                result += f"• Server `{server_id}` will be discoverable via `pg config search`\n"
                result += f"• You can install it with `pg config install {server_id}`\n"
                result += f"• It will appear in your Claude Desktop MCP server list\n"
                
                return result
                
            except Exception as e:
                return f"❌ **Failed to generate commands:** {str(e)}"

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="doc-analyzer",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

async def main():
    """Main entry point."""
    server = DocAnalyzerServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
