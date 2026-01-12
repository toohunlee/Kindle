#!/bin/bash

# Setup macOS Scheduler for Daily News Delivery
# This script installs the launchd plist file to run the news delivery daily

PLIST_NAME="com.kindle.news.delivery.plist"
PLIST_SOURCE="/Users/seo/kindle-news-delivery/$PLIST_NAME"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "================================================"
echo "Setting up Daily News Delivery Scheduler"
echo "================================================"

# Create logs directory
mkdir -p /Users/seo/kindle-news-delivery/logs
echo "✓ Created logs directory"

# Copy plist to LaunchAgents
echo "Installing launchd configuration..."
cp "$PLIST_SOURCE" "$PLIST_DEST"
echo "✓ Copied $PLIST_NAME to ~/Library/LaunchAgents/"

# Unload if already loaded (ignore errors)
launchctl unload "$PLIST_DEST" 2>/dev/null

# Load the plist
echo "Loading scheduler..."
launchctl load "$PLIST_DEST"

if [ $? -eq 0 ]; then
    echo "✓ Successfully loaded scheduler"
    echo ""
    echo "================================================"
    echo "Setup Complete!"
    echo "================================================"
    echo ""
    echo "The news delivery will run automatically:"
    echo "  • Monday-Friday at 5:00 AM"
    echo "  • Logs: /Users/seo/kindle-news-delivery/logs/"
    echo ""
    echo "To check status:"
    echo "  launchctl list | grep kindle"
    echo ""
    echo "To uninstall:"
    echo "  ./uninstall_scheduler.sh"
    echo ""
else
    echo "✗ Failed to load scheduler"
    exit 1
fi
