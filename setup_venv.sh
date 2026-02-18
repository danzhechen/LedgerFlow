#!/bin/bash
# Setup script for LedgerFlow virtual environment

set -e

echo "🔧 Setting up LedgerFlow virtual environment..."
echo ""

# Step 1: Create virtual environment
echo "📦 Step 1: Creating virtual environment..."
python3 -m venv .venv
echo "   ✅ Virtual environment created"
echo ""

# Step 2: Activate and upgrade pip
echo "📦 Step 2: Upgrading pip..."
source .venv/bin/activate
pip install --upgrade pip setuptools wheel -q
echo "   ✅ Pip upgraded"
echo ""

# Step 3: Install dependencies
echo "📦 Step 3: Installing dependencies..."
pip install pandas openpyxl pydantic pydantic-settings rule-engine click pyyaml -q
echo "   ✅ Core dependencies installed"
echo ""

# Step 4: Install dev dependencies
echo "📦 Step 4: Installing dev dependencies..."
pip install pytest pytest-cov ruff mypy types-openpyxl -q
echo "   ✅ Dev dependencies installed"
echo ""

# Step 5: Verify installation
echo "📦 Step 5: Verifying installation..."
python -c "import pandas; import pydantic; import click; import rule_engine; print('   ✅ All dependencies verified')"
echo ""

echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To run tests:"
echo "  ./run_tests.sh"
echo "  # or: pytest tests/ -v"








