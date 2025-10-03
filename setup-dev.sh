#!/bin/bash

# Development Environment Setup Script
# This script sets up the development environment with all necessary tools and hooks

set -e

echo "🚀 Setting up development environment for Monopoly Simulator API"
echo ""

HOOK_SRC=".githooks/pre-push"
HOOK_DST=".git/hooks/pre-push"
# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚠️  uv is not installed. Please install it first:${NC}"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo -e "${BLUE}1/4 Installing dependencies...${NC}"
uv sync
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

echo -e "${BLUE}2/4 Installing project in editable mode...${NC}"
uv pip install -e .
echo -e "${GREEN}✓ Project installed${NC}"
echo ""

echo -e "${BLUE}3/4 Setting up pre-push hook...${NC}"
if [ -f "$HOOK_SRC" ]; then
    cp "$HOOK_SRC" "$HOOK_DST"
    chmod +x "$HOOK_DST"
    echo -e "${GREEN}✓ Pre-push hook installed${NC}"
else
    echo -e "${YELLOW}⚠️  No pre-push hook found at $HOOK_SRC${NC}"
fi
echo ""


echo -e "${GREEN}✓ Development environment setup complete!${NC}"
