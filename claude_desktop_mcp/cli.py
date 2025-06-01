"""Claude Desktop MCP CLI

Command-line interface for managing Claude Desktop MCP configurations.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

import click

from .config_manager import ClaudeDesktopConfigManager, save_simplified_config, load_simplified_config


@click.group()
@click.version_option()
def main():
    """Claude Desktop MCP Configuration Manager"""
    pass


@main.group()
def config():
    """Manage Claude Desktop MCP configuration"""
    pass


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


if __name__ == '__main__':
    main()