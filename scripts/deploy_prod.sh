#!/bin/bash

# Deploy to production server

# Configuration
PROD_SERVER="your-prod-server.com"
PROD_USER="jonny"
PROD_PATH="/home/jonny/projects/obsidian-writings"
PROD_SERVICE="blog"

if [ -z "$PROD_SERVER" ] || [ "$PROD_SERVER" = "your-prod-server.com" ]; then
    echo "Error: Configure PROD_SERVER in this script first"
    exit 1
fi

echo "Deploying to production server: $PROD_SERVER"

ssh "$PROD_USER@$PROD_SERVER" << 'EOF'
set -e

echo "Pulling latest changes..."
cd "$PROD_PATH"
git pull origin main

echo "Installing dependencies..."
npm install
pip install -q -r backend/requirements.txt

echo "Building static site..."
npx quartz build

echo "Restarting Flask app..."
sudo systemctl restart "$PROD_SERVICE"

echo "✓ Production deployment complete"
EOF

if [ $? -eq 0 ]; then
    echo "✓ Deployment to production successful"
else
    echo "✗ Deployment failed"
    exit 1
fi
