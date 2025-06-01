"""Claude Desktop MCP CLI

Command-line interface for managing Claude Desktop MCP configurations.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

import click

from .config_manager import ClaudeDesktopConfigManager, save_simplified_config, load_simplified_config
from .setup_wizard import setup
from .server_registry import MCPServerRegistry


@click.group()
@click.version_option(version="0.1.0", prog_name="pg")
def main():
    """Claude Desktop MCP Configuration Manager"""
    pass


@main.group()
def config():
    """Manage Claude Desktop MCP configuration"""
    pass


# Add setup command to main group
main.add_command(setup)


@config.command()
@click.option('--output', '-o', default='claude_desktop_simplified.json', 
              help='Output file for simplified configuration')
@click.option('--format', 'output_format', default='simplified', 
              type=click.Choice(['simplified', 'original']),
              help='Output format')
def import_config(output: str, output_format: str):
    """Import current Claude Desktop configuration"""
    manager = ClaudeDesktopConfigManager()
    
    if not manager.config_exists():
        click.echo(f"Claude Desktop config not found at: {manager.config_path}")
        click.echo("This is normal if you haven't configured any MCP servers yet.")
        return
    
    try:
        if output_format == 'simplified':
            simplified = manager.import_to_simplified()
            save_simplified_config(simplified, output)
            click.echo(f"✓ Imported {len(simplified)} MCP servers to {output}")
            
            if simplified:
                click.echo("\nConfigured servers:")
                for name, config in simplified.items():
                    status = "enabled" if config.get("enabled", True) else "disabled"
                    click.echo(f"  • {name} ({config.get('command', 'no command')}) - {status}")
        else:
            original = manager.load_config()
            with open(output.replace('.json', '_original.json'), 'w') as f:
                json.dump(original, f, indent=2)
            click.echo(f"✓ Exported original configuration to {output.replace('.json', '_original.json')}")
            
    except Exception as e:
        click.echo(f"✗ Error importing configuration: {e}", err=True)
        sys.exit(1)


@config.command()
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json']),
              help='Output format')
def show(output_format: str):
    """Show current MCP servers configuration"""
    manager = ClaudeDesktopConfigManager()
    
    if not manager.config_exists():
        click.echo("No Claude Desktop configuration found.")
        return
    
    try:
        servers = manager.list_servers()
        
        if not servers:
            click.echo("No MCP servers configured.")
            return
        
        if output_format == 'json':
            click.echo(json.dumps(servers, indent=2))
        else:
            click.echo(f"Found {len(servers)} MCP server(s):\n")
            for name, config in servers.items():
                click.echo(f"Server: {name}")
                click.echo(f"  Command: {config.get('command', 'Not set')}")
                if config.get('args'):
                    click.echo(f"  Args: {' '.join(config['args'])}")
                if config.get('env'):
                    click.echo(f"  Environment: {len(config['env'])} variable(s)")
                click.echo()
                
    except Exception as e:
        click.echo(f"✗ Error reading configuration: {e}", err=True)
        sys.exit(1)


@config.command()
@click.argument('name')
@click.argument('command')
@click.option('--args', multiple=True, help='Command arguments')
@click.option('--env', multiple=True, help='Environment variables (KEY=VALUE)')
def add(name: str, command: str, args: tuple, env: tuple):
    """Add a new MCP server"""
    manager = ClaudeDesktopConfigManager()
    
    # Parse environment variables
    env_dict = {}
    for env_var in env:
        if '=' not in env_var:
            click.echo(f"✗ Invalid environment variable format: {env_var}", err=True)
            click.echo("Use format: KEY=VALUE", err=True)
            sys.exit(1)
        key, value = env_var.split('=', 1)
        env_dict[key] = value
    
    try:
        # Check if server already exists
        existing_servers = manager.list_servers()
        if name in existing_servers:
            if not click.confirm(f"Server '{name}' already exists. Overwrite?"):
                click.echo("Cancelled.")
                return
        
        manager.add_server(name, command, list(args), env_dict)
        click.echo(f"✓ Added MCP server '{name}'")
        
    except Exception as e:
        click.echo(f"✗ Error adding server: {e}", err=True)
        sys.exit(1)


@config.command()
@click.argument('name')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
def remove(name: str, confirm: bool):
    """Remove an MCP server"""
    manager = ClaudeDesktopConfigManager()
    
    try:
        servers = manager.list_servers()
        if name not in servers:
            click.echo(f"✗ Server '{name}' not found.")
            return
        
        if not confirm and not click.confirm(f"Remove server '{name}'?"):
            click.echo("Cancelled.")
            return
        
        if manager.remove_server(name):
            click.echo(f"✓ Removed MCP server '{name}'")
        else:
            click.echo(f"✗ Failed to remove server '{name}'")
            
    except Exception as e:
        click.echo(f"✗ Error removing server: {e}", err=True)
        sys.exit(1)


@config.command()
def validate():
    """Validate Claude Desktop configuration"""
    manager = ClaudeDesktopConfigManager()
    
    try:
        result = manager.validate_config()
        
        if result["valid"]:
            click.echo("✓ Configuration is valid")
        else:
            click.echo("✗ Configuration has errors:")
            for error in result["errors"]:
                click.echo(f"  • {error}")
        
        if result["warnings"]:
            click.echo("\nWarnings:")
            for warning in result["warnings"]:
                click.echo(f"  • {warning}")
        
        if not result["valid"]:
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"✗ Error validating configuration: {e}", err=True)
        sys.exit(1)


@config.command()
@click.argument('input_file', default='claude_desktop_simplified.json')
def apply(input_file: str):
    """Apply simplified configuration to Claude Desktop"""
    manager = ClaudeDesktopConfigManager()
    
    if not Path(input_file).exists():
        click.echo(f"✗ Input file not found: {input_file}")
        sys.exit(1)
    
    try:
        simplified = load_simplified_config(input_file)
        claude_config = manager.export_from_simplified(simplified)
        
        # Show what will be applied
        enabled_servers = [name for name, config in simplified.items() 
                          if config.get("enabled", True)]
        
        click.echo(f"Will apply {len(enabled_servers)} MCP server(s):")
        for name in enabled_servers:
            click.echo(f"  • {name}")
        
        if not click.confirm("Apply this configuration?"):
            click.echo("Cancelled.")
            return
        
        manager.save_config(claude_config)
        click.echo("✓ Configuration applied successfully")
        click.echo("Restart Claude Desktop for changes to take effect.")
        
    except Exception as e:
        click.echo(f"✗ Error applying configuration: {e}", err=True)
        sys.exit(1)


@config.command()
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json', 'simple']),
              help='Output format')
@click.option('--status', is_flag=True, help='Show server status (running/stopped)')
@click.option('--npm-global', is_flag=True, help='Also list globally installed npm MCP packages')
def list(output_format: str, status: bool, npm_global: bool):
    """List all installed MCP servers"""
    manager = ClaudeDesktopConfigManager()
    
    try:
        # Get configured servers from Claude Desktop
        servers = manager.list_servers()
        
        # Get npm global packages if requested
        npm_packages = []
        if npm_global:
            npm_packages = get_npm_mcp_packages()
        
        if output_format == 'json':
            output_data = {
                "configured_servers": servers,
                "npm_packages": npm_packages if npm_global else []
            }
            click.echo(json.dumps(output_data, indent=2))
            
        elif output_format == 'simple':
            if servers:
                for name in servers.keys():
                    click.echo(name)
            if npm_global and npm_packages:
                for pkg in npm_packages:
                    click.echo(f"npm:{pkg['name']}")
                    
        else:  # table format
            display_servers_table(servers, npm_packages if npm_global else [], status)
            
    except Exception as e:
        click.echo(f"✗ Error listing servers: {e}", err=True)
        sys.exit(1)


def get_npm_mcp_packages():
    """Get globally installed npm MCP packages"""
    import subprocess
    
    try:
        # Get global npm packages
        result = subprocess.run(
            ["npm", "list", "-g", "--depth=0", "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return []
        
        npm_data = json.loads(result.stdout)
        dependencies = npm_data.get("dependencies", {})
        
        # Filter for MCP packages
        mcp_packages = []
        for pkg_name, pkg_info in dependencies.items():
            if "modelcontextprotocol" in pkg_name or "mcp" in pkg_name.lower():
                mcp_packages.append({
                    "name": pkg_name,
                    "version": pkg_info.get("version", "unknown"),
                    "path": pkg_info.get("path", "")
                })
        
        return mcp_packages
        
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        return []


def check_server_status(command: str, args: list) -> str:
    """Check if a server process is running"""
    import subprocess
    
    try:
        import psutil
        
        # Look for processes matching the command
        full_command = [command] + args
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and len(cmdline) >= len(full_command):
                    # Check if the command matches
                    if cmdline[:len(full_command)] == full_command:
                        return "🟢 Running"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return "🔴 Stopped"
        
    except ImportError:
        # psutil not available, try simple approach
        try:
            # For npm-based servers, check if process exists
            if command == "npx" or command == "node":
                result = subprocess.run(
                    ["pgrep", "-f", " ".join([command] + args[:2])],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return "🟢 Running" if result.returncode == 0 else "🔴 Stopped"
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        return "❓ Unknown"
    except Exception:
        return "❓ Unknown"


def display_servers_table(servers: dict, npm_packages: list, show_status: bool):
    """Display servers in a formatted table"""
    if not servers and not npm_packages:
        click.echo("No MCP servers found.")
        return
    
    click.echo("📋 Installed MCP Servers")
    click.echo("=" * 50)
    
    if servers:
        click.echo("\n🔧 Configured in Claude Desktop:")
        click.echo("-" * 30)
        
        for name, config in servers.items():
            command = config.get('command', 'Unknown')
            args = config.get('args', [])
            env_count = len(config.get('env', {}))
            
            # Status indicator
            status_text = ""
            if show_status:
                status = check_server_status(command, args)
                status_text = f" {status}"
            
            click.echo(f"  📦 {name}{status_text}")
            click.echo(f"     Command: {command}")
            
            if args:
                args_str = " ".join(args)
                if len(args_str) > 60:
                    args_str = args_str[:57] + "..."
                click.echo(f"     Args: {args_str}")
            
            if env_count > 0:
                click.echo(f"     Environment: {env_count} variable(s)")
            
            click.echo()
    
    if npm_packages:
        click.echo("📦 NPM Global Packages:")
        click.echo("-" * 30)
        
        for pkg in npm_packages:
            click.echo(f"  🌐 {pkg['name']} (v{pkg['version']})")
            if pkg.get('path'):
                click.echo(f"     Path: {pkg['path']}")
            click.echo()
    
    # Summary
    total_configured = len(servers)
    total_npm = len(npm_packages)
    
    click.echo("📊 Summary:")
    click.echo(f"  • Configured servers: {total_configured}")
    if npm_packages:
        click.echo(f"  • NPM packages: {total_npm}")
    
    if show_status and servers:
        running_count = sum(1 for config in servers.values() 
                          if "🟢" in check_server_status(config.get('command', ''), config.get('args', [])))
        click.echo(f"  • Running servers: {running_count}/{total_configured}")


@config.command()
@click.argument('query', required=False)
@click.option('--category', help='Filter by category (official, community)')
@click.option('--format', 'output_format', default='table',
              type=click.Choice(['table', 'json', 'simple']),
              help='Output format')
def search(query: str, category: str, output_format: str):
    """Search for available MCP servers in the registry"""
    registry = MCPServerRegistry()
    
    try:
        if query:
            results = registry.search(query)
        elif category:
            results = registry.get_by_category(category)
        else:
            results = registry.get_all_servers()
        
        if not results:
            if query:
                click.echo(f"No servers found matching '{query}'")
            else:
                click.echo("No servers found")
            return
        
        if output_format == 'json':
            click.echo(json.dumps(results, indent=2))
        elif output_format == 'simple':
            for server in results:
                click.echo(server['id'])
        else:
            display_search_results(results)
            
    except Exception as e:
        click.echo(f"✗ Error searching servers: {e}", err=True)
        sys.exit(1)


@config.command()
@click.argument('server_id')
def info(server_id: str):
    """Show detailed information about a specific server"""
    registry = MCPServerRegistry()
    
    try:
        server = registry.get_server(server_id)
        if not server:
            click.echo(f"✗ Server '{server_id}' not found in registry")
            click.echo("Use 'pg config search' to find available servers")
            return
        
        display_server_info(server)
        
    except Exception as e:
        click.echo(f"✗ Error getting server info: {e}", err=True)
        sys.exit(1)


@config.command()
@click.argument('server_id')
@click.option('--name', help='Custom name for the server instance')
@click.option('--arg', 'args', multiple=True, help='Server arguments (key=value)')
@click.option('--env', 'env_vars', multiple=True, help='Environment variables (key=value)')
@click.option('--auto-install', is_flag=True, help='Automatically install npm package if needed')
@click.option('--dry-run', is_flag=True, help='Show what would be installed without doing it')
def install(server_id: str, name: str, args: tuple, env_vars: tuple, auto_install: bool, dry_run: bool):
    """Install an MCP server from the registry"""
    registry = MCPServerRegistry()
    manager = ClaudeDesktopConfigManager()
    
    try:
        server = registry.get_server(server_id)
        if not server:
            click.echo(f"✗ Server '{server_id}' not found in registry")
            click.echo("Use 'pg config search' to find available servers")
            return
        
        # Display server information
        click.echo(f"📦 Installing: {server['name']}")
        click.echo(f"📝 Description: {server['description']}")
        click.echo()
        
        # Parse user arguments
        user_args = {}
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                user_args[key] = value
            else:
                click.echo(f"✗ Invalid argument format: {arg}")
                click.echo("Use format: key=value")
                return
        
        # Parse environment variables
        for env_var in env_vars:
            if '=' in env_var:
                key, value = env_var.split('=', 1)
                user_args[key] = value
            else:
                click.echo(f"✗ Invalid environment variable format: {env_var}")
                click.echo("Use format: KEY=VALUE")
                return
        
        # Check for required arguments
        missing_args = []
        for required_arg in server.get('required_args', []):
            if required_arg not in user_args:
                missing_args.append(required_arg)
        
        # Check for required environment variables
        for env_key in server.get('env_vars', {}):
            if env_key not in user_args:
                missing_args.append(env_key)
        
        # Interactive prompts for missing arguments
        if missing_args:
            click.echo("📋 Required configuration:")
            for missing_arg in missing_args:
                if missing_arg in server.get('env_vars', {}):
                    prompt_text = f"{missing_arg} ({server['env_vars'][missing_arg]})"
                    hide_input = any(secret in missing_arg.lower() for secret in ['key', 'token', 'password', 'secret'])
                    value = click.prompt(prompt_text, hide_input=hide_input)
                    user_args[missing_arg] = value
                else:
                    prompt_text = f"{missing_arg}"
                    if server.get('setup_help'):
                        prompt_text += f" ({server['setup_help']})"
                    value = click.prompt(prompt_text)
                    user_args[missing_arg] = value
        
        # Generate install command
        install_config = registry.generate_install_command(server_id, user_args)
        if not install_config:
            click.echo("✗ Failed to generate install configuration")
            return
        
        # Use custom name if provided
        instance_name = name or server_id
        
        if dry_run:
            click.echo("🔍 Dry run - would install:")
            click.echo(f"  Name: {instance_name}")
            click.echo(f"  Command: {install_config['command']}")
            click.echo(f"  Args: {' '.join(install_config['args'])}")
            if install_config['env']:
                click.echo(f"  Environment: {len(install_config['env'])} variable(s)")
            return
        
        # Install npm package if needed
        if auto_install and server.get('install_method') == 'npm' and server.get('package'):
            click.echo(f"📦 Installing npm package: {server['package']}")
            try:
                import subprocess
                result = subprocess.run(
                    ["npm", "install", "-g", server['package']],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    click.echo("✅ npm package installed successfully")
                else:
                    click.echo(f"⚠️  npm install warning: {result.stderr[:100]}")
            except Exception as e:
                click.echo(f"⚠️  Failed to install npm package: {e}")
                click.echo("You may need to install it manually")
        
        # Check if server already exists
        existing_servers = manager.list_servers()
        if instance_name in existing_servers:
            if not click.confirm(f"Server '{instance_name}' already exists. Overwrite?"):
                click.echo("Cancelled.")
                return
        
        # Add server to configuration
        manager.add_server(
            instance_name,
            install_config['command'],
            install_config['args'],
            install_config['env']
        )
        
        click.echo(f"✅ Successfully installed '{instance_name}'")
        click.echo("🔄 Restart Claude Desktop for changes to take effect")
        
        # Show usage example
        if server.get('example_usage'):
            click.echo(f"\n💡 Example usage: {server['example_usage']}")
        
    except Exception as e:
        click.echo(f"✗ Error installing server: {e}", err=True)
        sys.exit(1)


def display_search_results(results: List[Dict[str, Any]]):
    """Display search results in a formatted table"""
    click.echo(f"🔍 Found {len(results)} MCP server(s):")
    click.echo("=" * 50)
    
    for server in results:
        category_emoji = "🏛️" if server['category'] == 'official' else "🌟"
        click.echo(f"\n{category_emoji} {server['id']} - {server['name']}")
        click.echo(f"   {server['description']}")
        
        if server.get('package'):
            click.echo(f"   📦 Package: {server['package']}")
        
        # Show platform requirement if any
        if server.get('platform'):
            click.echo(f"   🖥️  Platform: {server['platform']}")
    
    click.echo(f"\n💡 Use 'pg config info <server_id>' for detailed information")
    click.echo("💡 Use 'pg config install <server_id>' to install a server")


def display_server_info(server: Dict[str, Any]):
    """Display detailed information about a server"""
    category_emoji = "🏛️" if server['category'] == 'official' else "🌟"
    
    click.echo(f"{category_emoji} {server['name']}")
    click.echo("=" * 50)
    click.echo(f"ID: {server['id']}")
    click.echo(f"Category: {server['category']}")
    click.echo(f"Description: {server['description']}")
    
    if server.get('package'):
        click.echo(f"Package: {server['package']}")
    
    if server.get('homepage'):
        click.echo(f"Homepage: {server['homepage']}")
    
    if server.get('platform'):
        click.echo(f"Platform: {server['platform']}")
    
    click.echo(f"\nInstallation:")
    click.echo(f"  Method: {server.get('install_method', 'manual')}")
    click.echo(f"  Command: {server['command']}")
    
    if server.get('required_args'):
        click.echo(f"\nRequired Arguments:")
        for arg in server['required_args']:
            click.echo(f"  • {arg}")
    
    if server.get('env_vars'):
        click.echo(f"\nEnvironment Variables:")
        for env_key, env_desc in server['env_vars'].items():
            click.echo(f"  • {env_key}: {env_desc}")
    
    if server.get('setup_help'):
        click.echo(f"\nSetup Help:")
        click.echo(f"  {server['setup_help']}")
    
    if server.get('example_usage'):
        click.echo(f"\nExample Usage:")
        click.echo(f"  {server['example_usage']}")
    
    click.echo(f"\n💡 Install with: pg config install {server['id']}")


if __name__ == '__main__':
    main()