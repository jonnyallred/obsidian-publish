#!/bin/bash

# Build script for Quartz static site

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

CONTENT_REPO="git@github.com:jonnyallred/writings.git"

# Sync content from separate repo
echo "Syncing content..."
if [ -d content/.git ]; then
    git -C content pull
else
    rm -rf content
    git clone "$CONTENT_REPO" content
fi

echo "Building Quartz static site..."
npx quartz build

echo "✓ Build complete"
ls -lh public/index.html
