#!/bin/bash
# Build script for Celery worker to force Python 3.11

set -e

echo "🔧 Installing Python 3.11..."

# Check if Python 3.11 is available, if not, use pyenv or install it
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD=python3.11
    PIP_CMD=python3.11 -m pip
elif command -v python3 &> /dev/null && python3 --version | grep -q "3.11"; then
    PYTHON_CMD=python3
    PIP_CMD=python3 -m pip
else
    echo "⚠️  Python 3.11 not found, using system Python 3"
    PYTHON_CMD=python3
    PIP_CMD=python3 -m pip
fi

echo "✅ Using Python: $($PYTHON_CMD --version)"

# Upgrade pip
echo "📦 Upgrading pip..."
$PIP_CMD install --upgrade pip

# Install requirements
echo "📦 Installing requirements..."
$PIP_CMD install -r requirements.txt

echo "✅ Build complete!"

