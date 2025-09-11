#!/usr/bin/env python3
"""
Simple test script to verify module imports
"""

import sys
import os

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

try:
    print(f"Project directory: {project_dir}")
    print(f"Python path: {sys.path}")
    
    # Try importing modules
    print("\nAttempting to import modules...")
    from LibrarySystem.models.users import User
    print("Successfully imported User model")
    
    from LibrarySystem.models.books import Book
    print("Successfully imported Book model")
    
    from LibrarySystem.utils.db_connection import db_manager
    print("Successfully imported db_manager")
    
    print("\nAll imports successful!")
except ImportError as e:
    print(f"Import error: {e}")
    print("Module import failed. Check your project structure.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
