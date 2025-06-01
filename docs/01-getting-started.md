# Getting Started with Claude Desktop MCP Playground

## Introduction

Claude Desktop MCP Playground is a Python framework for creating AI-powered productivity workflows using Claude Desktop's Model Context Protocol (MCP) servers. This guide will help you get started with managing your Claude Desktop configuration and building powerful AI workflows.

## Prerequisites

Before beginning, ensure you have:
- **Claude Desktop application** installed and running
- **Python 3.9+** (3.10+ recommended)
- Basic understanding of command-line interfaces
- Administrative privileges to install packages
- Required dependencies:
  - pip or uv package manager
  - Virtual environment support

## What You'll Learn

This guide covers:
- Installing the Claude Desktop MCP configuration CLI
- Managing MCP servers with simple commands
- Converting between configuration formats
- Setting up your first AI workflow

## Key Concepts

### What is Claude Desktop MCP?

Model Context Protocol (MCP) is Claude Desktop's system for connecting with external tools and services. This playground provides:

- **Configuration Management**: Easy CLI for managing MCP server configurations
- **Simplified Workflows**: Convert complex JSON configs to readable key-value pairs
- **Cross-Platform Support**: Works on macOS, Windows, and Linux
- **Extensible Framework**: Build custom productivity workflows

### Core Components

1. **Configuration Manager**: Handles Claude Desktop MCP server configs across platforms
2. **CLI Tool**: Command-line interface for configuration management  
3. **Simplified Format**: Easy-to-edit JSON structure with enable/disable flags
4. **Import/Export System**: Convert between Claude Desktop and simplified formats

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/seanpoyner/pg-playground.git
cd pg-playground
```

### 2. Create Virtual Environment

```bash
# Using Python venv
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or using uv (recommended)
uv venv
source .venv/bin/activate
```

### 3. Install the Package

```bash
pip install -e .
```

### 4. Verify Installation

```bash
playground --help
# or use the short form:
pg --help
```

### 5. Import Your Current Configuration

```bash
# Import current Claude Desktop config to simplified format
pg config import

# View what's configured
pg config show
```

## Next Steps

- [Proceed to Installation Guide](02-installation.md)
- [Learn about Basic Configuration](03-basic-configuration.md)

## Troubleshooting

If you encounter any issues during setup, refer to our [Troubleshooting Guide](07-troubleshooting.md).
