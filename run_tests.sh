#!/bin/bash
# Script to run all tests for veritas-accounting
# Make sure dependencies are installed first: pip install -e ".[dev]"

set -e

echo "🧪 Running veritas-accounting test suite..."
echo ""

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing dependencies..."
    pip install -e ".[dev]"
fi

# Run all tests with verbose output
echo "Running unit tests..."
pytest tests/unit/ -v --tb=short

echo ""
echo "Running integration tests..."
pytest tests/integration/ -v --tb=short

echo ""
echo "Running full test suite..."
pytest tests/ -v --tb=short --cov=src/veritas_accounting --cov-report=term-missing

echo ""
echo "✅ All tests completed!"
