#!/bin/bash
# Quick test runner wrapper that ensures venv is activated

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Activate venv
if [ ! -d ".venv" ]; then
    echo -e "${RED}Error: .venv not found. Run 'python -m venv .venv' first${NC}"
    exit 1
fi

source .venv/bin/activate

# Run tests with all arguments passed through
python run_tests.py "$@"
