#!/bin/bash

# Uninstall the Daily News Delivery Scheduler

PLIST_NAME="com.kindle.news.delivery.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "================================================"
echo "Uninstalling Daily News Delivery Scheduler"
echo "================================================"

if [ -f "$PLIST_DEST" ]; then
    # Unload the plist
    echo "Unloading scheduler..."
    launchctl unload "$PLIST_DEST"

    # Remove the plist
    echo "Removing configuration file..."
    rm "$PLIST_DEST"

    echo "✓ Successfully uninstalled scheduler"
    echo ""
    echo "The automatic news delivery has been disabled."
    echo "You can still run manually with: python3 main.py"
else
    echo "Scheduler not found. Nothing to uninstall."
fi
