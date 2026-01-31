#!/bin/bash
# =============================================================================
# ABIOGENESIS - Scarlet Setup Script
# Modulo 1: Foundation Setup
# =============================================================================
#
# This script sets up the development environment for Scarlet.
# Run from the scarlet/ directory.
#
# Usage: ./scripts/setup.sh
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ABIOGENESIS - Scarlet Setup${NC}"
echo -e "${BLUE}  Modulo 1: Foundation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}Project directory: $PROJECT_DIR${NC}"
echo ""

# =============================================================================
# Step 1: Check Prerequisites
# =============================================================================
echo -e "${BLUE}[1/5] Checking prerequisites...${NC}"

# Check Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}ERROR: Python not found. Please install Python 3.10+${NC}"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} Python: $(python --version)"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker not found. Please install Docker${NC}"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} Docker: $(docker --version)"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠${NC} docker-compose not found, checking docker compose v2..."
    if ! docker compose version &> /dev/null; then
        echo -e "${RED}ERROR: Neither docker-compose nor docker compose found${NC}"
        exit 1
    fi
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi
echo -e "  ${GREEN}✓${NC} Docker Compose: $DOCKER_COMPOSE"

# =============================================================================
# Step 2: Create Virtual Environment
# =============================================================================
echo ""
echo -e "${BLUE}[2/5] Setting up Python environment...${NC}"

VENV_DIR="$PROJECT_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
    python -m venv "$VENV_DIR"
    echo -e "  ${GREEN}✓${NC} Created virtual environment"
else
    echo -e "  ${YELLOW}⚠${NC} Virtual environment already exists"
fi

# Activate venv and install dependencies
source "$VENV_DIR/bin/activate" 2>/dev/null || source "$VENV_DIR/Scripts/activate" 2>/dev/null || true

echo -e "  Installing dependencies..."

# Install basic dependencies
pip install --quiet --upgrade pip
pip install --quiet python-dotenv
pip install --quiet letta-client 2>/dev/null || echo -e "  ${YELLOW}⚠${NC} letta-client install failed (will retry later)"

echo -e "  ${GREEN}✓${NC} Dependencies installed"

# =============================================================================
# Step 3: Configure Environment
# =============================================================================
echo ""
echo -e "${BLUE}[3/5] Configuring environment...${NC}"

ENV_FILE="$PROJECT_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo -e "  ${YELLOW}⚠${NC} .env file not found, creating from template..."
    cat > "$ENV_FILE" << 'EOF'
# ABIOGENESIS - Scarlet Configuration
# Modulo 1: Foundation Setup

# ============================================
# LLM Configuration - MiniMax M2.1
# ============================================
MINIMAX_API_KEY=your_minimax_api_key_here
MINIMAX_BASE_URL=https://api.minimax.chat/v1/text/chatcompletion_v2

# ============================================
# Letta Server Configuration
# ============================================
LETTA_SERVER_URL=http://localhost:8283
LETTA_MODEL=minimax/MiniMax-M2.1

# ============================================
# Database Configuration
# ============================================
POSTGRES_PASSWORD=scarlet_secure_password_change_this_in_production

# ============================================
# Application Settings
# ============================================
SCARLET_NAME=Scarlet
SCARLET_VERSION=0.1.0
DEBUG=false
EOF
    echo -e "  ${GREEN}✓${NC} Created .env template"
    echo -e "  ${YELLOW}⚠${NC} Please edit .env and add your MINIMAX_API_KEY"
else
    echo -e "  ${GREEN}✓${NC} .env file exists"

    # Check if API key is set
    if grep -q "your_minimax_api_key_here" "$ENV_FILE"; then
        echo -e "  ${YELLOW}⚠${NC} WARNING: MINIMAX_API_KEY not configured!"
        echo -e "      Please edit $ENV_FILE and add your API key"
    fi
fi

# =============================================================================
# Step 4: Initialize Docker Services
# =============================================================================
echo ""
echo -e "${BLUE}[4/5] Starting Docker services...${NC}"

cd "$PROJECT_DIR"

echo "  Starting Letta, PostgreSQL, and Redis..."

# Check if containers are already running
if $DOCKER_COMPOSE ps | grep -q "Up"; then
    echo -e "  ${YELLOW}⚠${NC} Containers already running"
else
    $DOCKER_COMPOSE up -d
    echo -e "  ${GREEN}✓${NC} Containers started"

    # Wait for services to be healthy
    echo "  Waiting for services to be ready..."
    sleep 5
fi

# Check service health
echo ""
echo "  Service Status:"
$DOCKER_COMPOSE ps

# =============================================================================
# Step 5: Final Setup
# =============================================================================
echo ""
echo -e "${BLUE}[5/5] Finalizing setup...${NC}"

# Create required directories if missing
mkdir -p "$PROJECT_DIR/data"
mkdir -p "$PROJECT_DIR/logs"

# Test Python import
python -c "from src.scarlet_agent import ScarletAgent" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} Python imports working"
else
    echo -e "  ${YELLOW}⚠${NC} Python imports failed (may need pip install letta-client)"
fi

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your MINIMAX_API_KEY"
echo "  2. Run: python src/scarlet_agent.py"
echo ""
echo "Useful commands:"
echo "  Start services:  docker-compose up -d"
echo "  Stop services:   docker-compose down"
echo "  View logs:       docker-compose logs -f"
echo "  Enter shell:     docker-compose exec letta-server bash"
echo ""
echo -e "${BLUE}========================================${NC}"
