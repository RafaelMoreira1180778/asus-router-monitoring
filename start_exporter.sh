#!/bin/bash

# ASUS Router Prometheus Exporter Startup Script
# This script provides an easy way to start the exporter with configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 ASUS Router Prometheus Exporter${NC}"
echo "=================================================="

# Check if Python is available
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}❌ Error: Python 3.12+ is required but not installed${NC}"
    exit 1
fi

# Check Python version (3.12+)
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.12"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}❌ Error: Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $PYTHON_VERSION detected${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
source .venv/bin/activate

# Install/upgrade requirements
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}📦 Installing/updating dependencies...${NC}"
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    echo -e "${GREEN}✅ Dependencies installed${NC}"
fi

# Check for configuration
if [ -z "$ASUS_PASSWORD" ] && [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: No configuration found${NC}"
    echo ""
    echo "Please either:"
    echo "1. Set environment variables:"
    echo "   export ASUS_HOSTNAME=192.168.1.1"
    echo "   export ASUS_USERNAME=admin"
    echo "   export ASUS_PASSWORD=your_password"
    echo ""
    echo "2. Or create a .env file (copy from .env.example):"
    echo "   cp .env.example .env"
    echo "   # Edit .env with your router credentials"
    echo ""
    exit 1
fi

# Load .env file if it exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}📄 Loading configuration from .env file...${NC}"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Validate required configuration
if [ -z "$ASUS_PASSWORD" ]; then
    echo -e "${RED}❌ Error: ASUS_PASSWORD is required${NC}"
    exit 1
fi

# Display configuration
echo -e "${GREEN}📋 Configuration:${NC}"
echo "   Hostname: ${ASUS_HOSTNAME:-192.168.1.1}"
echo "   Username: ${ASUS_USERNAME:-admin}"
echo "   Use SSL: ${ASUS_USE_SSL:-false}"
echo "   Port: ${EXPORTER_PORT:-8000}"
echo ""

# Test connection first
echo -e "${YELLOW}🧪 Testing router connection...${NC}"
if python3 test_connection.py; then
    echo -e "${GREEN}✅ Connection test passed!${NC}"
    echo ""
    echo -e "${YELLOW}🎯 Starting Prometheus exporter...${NC}"
    echo "Press Ctrl+C to stop"
    echo ""

    # Start the exporter
    python3 asus_exporter.py
else
    echo -e "${RED}❌ Connection test failed!${NC}"
    echo "Please check your router configuration and try again."
    exit 1
fi
