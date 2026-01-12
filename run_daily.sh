#!/bin/bash

# Daily News Delivery Runner Script
# This script activates the virtual environment and runs the main script

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the project directory
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "env" ]; then
    source env/bin/activate
fi

# Run the main script
echo "================================================"
echo "Starting Daily News Delivery - $(date)"
echo "================================================"

python3 main.py

EXIT_CODE=$?

echo "================================================"
echo "Finished - $(date)"
echo "Exit Code: $EXIT_CODE"
echo "================================================"

exit $EXIT_CODE
