# MCP Server Manager Testing Environment
# This provides a testing environment for the Claude Desktop MCP Playground
# Note: For true Windows testing, a Windows VM is recommended

FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    make \
    build-essential \
    nodejs \
    npm \
    # Wine for basic Windows compatibility testing
    wine \
    wine64 \
    && rm -rf /var/lib/apt/lists/*

# Install UV for Python package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/seanpoyner/claude-desktop-mcp-playground.git .

# Install Python dependencies
RUN pip install -r requirements.txt
RUN pip install -e .

# Install Node dependencies for GUI
WORKDIR /app/mcp-gui
RUN npm install

# Back to main directory
WORKDIR /app

# Create test configuration directory
RUN mkdir -p /root/.config/Claude

# Set up environment for testing
ENV CLAUDE_DESKTOP_CONFIG_PATH=/root/.config/Claude/claude_desktop_config.json
ENV PYTHONPATH=/app:$PYTHONPATH

# Create startup script
RUN echo '#!/bin/bash\n\
echo "MCP Server Manager Testing Environment"\n\
echo "======================================"\n\
echo ""\n\
echo "Available commands:"\n\
echo "  pg --help                 # CLI help"\n\
echo "  pg config search          # Search servers"\n\
echo "  pg setup                  # Run setup wizard"\n\
echo "  make test                 # Run tests"\n\
echo "  python -m pytest tests/   # Run specific tests"\n\
echo ""\n\
echo "For Windows-specific testing:"\n\
echo "  wine cmd                  # Windows command prompt"\n\
echo "  wine python              # Python in Wine"\n\
echo ""\n\
bash' > /app/start.sh && chmod +x /app/start.sh

# Default command
CMD ["/app/start.sh"]