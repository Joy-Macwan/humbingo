#!/usr/bin/env python3
"""
Launcher script for the Library Management System.
This file is a convenient entry point to start the application.
"""

import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main module and run it
try:
    from main import main
    main()
except ImportError as e:
    print(f"Error importing main module: {e}")
    print("Make sure you're running this script from the project directory.")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
