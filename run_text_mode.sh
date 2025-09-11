#!/bin/bash

# Library Management System Text Mode Launcher
echo "Starting Library Management System in text mode..."
echo "---------------------------------------------"

# Check if Python is available
if command -v python3 &>/dev/null; then
    python3 library_cli.py
elif command -v python &>/dev/null; then
    python library_cli.py
else
    echo "Error: Python not found. Please install Python 3.x to run this application."
    exit 1
fi
