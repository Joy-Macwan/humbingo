#!/usr/bin/env python3
"""
Simple entry point for the Library Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

def main():
    print("Starting Library Management System...")
    
    # Add the current directory to the Python path
    project_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_dir)
    
    # Import necessary modules
    try:
        from LibrarySystem.utils.logger import logger
        print("Logger module loaded successfully")
        
        from LibrarySystem.models.users import User
        print("User model loaded successfully")
        
        from LibrarySystem.gui.login_screen import LoginScreen
        print("Login screen loaded successfully")
        
        # Create the main window
        root = tk.Tk()
        root.title("Library Management System")
        root.geometry("800x600")
        
        # Create a simple UI for now
        frame = ttk.Frame(root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Library Management System", 
                 font=("Arial", 18, "bold")).pack(pady=20)
        
        ttk.Label(frame, text="All modules loaded successfully!").pack(pady=10)
        
        ttk.Button(frame, text="Exit", command=root.destroy).pack(pady=20)
        
        root.mainloop()
        
    except ImportError as e:
        print(f"Error importing modules: {e}")
        messagebox.showerror("Import Error", f"Failed to import required modules: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
