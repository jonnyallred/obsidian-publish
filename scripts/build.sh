#!/bin/bash

# Build script for Quartz static site

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "Building Quartz static site..."
npx quartz build

echo "✓ Build complete"
ls -lh public/index.html
