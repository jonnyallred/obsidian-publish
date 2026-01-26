#!/bin/bash

# Deploy to development environment

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "Deploying to development environment..."

# Pull latest changes
echo "Pulling from Git..."
git pull origin main

# Install/update dependencies
echo "Installing Node dependencies..."
npm install

echo "Installing Python dependencies..."
pip install -q -r backend/requirements.txt

# Build
echo "Building Quartz..."
./scripts/build.sh

# Restart Flask app (if using systemd)
if command -v systemctl &> /dev/null; then
    echo "Restarting blog-dev service..."
    sudo systemctl restart blog-dev || echo "Warning: Could not restart blog-dev service"
fi

echo "✓ Development deployment complete"
