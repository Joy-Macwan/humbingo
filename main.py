#!/usr/bin/env python3
"""
Main entry point for the Library Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from LibrarySystem.gui.login_screen import LoginScreen
from LibrarySystem.models.users import User
from LibrarySystem.utils.logger import logger

# These will be imported after user logs in
# from LibrarySystem.gui.admin_dashboard import AdminDashboard
# from LibrarySystem.gui.user_dashboard import UserDashboard

# Set up the main application
class LibraryApplication:
    def __init__(self, root):
        self.root = root
        self.current_user = None
        
        # Configure the root window
        self.root.title("Library Management System")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Initialize the login screen
        self._show_login_screen()
    
    def _show_login_screen(self):
        """Display the login screen"""
        # Clear current window content
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Show login screen
        self.login_screen = LoginScreen(self.root, self._on_login_success)
    
    def _on_login_success(self, user: User):
        """Called when login is successful"""
        self.current_user = user
        logger.info(f"User logged in: {user.email} ({user.role})")
        
        # Clear current window content
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Show appropriate dashboard based on user role
        if user.role == 'admin':
            self._show_admin_dashboard()
        else:
            self._show_user_dashboard()
    
    def _show_admin_dashboard(self):
        """Display the admin dashboard"""
        # We'll import the dashboard here to avoid circular imports
        from LibrarySystem.gui.admin_dashboard import AdminDashboard
        AdminDashboard(self.root, self.current_user, self._show_login_screen)
    
    def _show_user_dashboard(self):
        """Display the user dashboard"""
        # We'll import the dashboard here to avoid circular imports
        from LibrarySystem.gui.user_dashboard import UserDashboard
        UserDashboard(self.root, self.current_user, self._show_login_screen)

def main():
    # Set up exception handling
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Global exception handler"""
        # Log the error
        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        
        # Show error message to user
        error_msg = f"An unexpected error occurred:\n{exc_value}"
        messagebox.showerror("Application Error", error_msg)
    
    # Set the exception hook
    sys.excepthook = handle_exception
    
    # Create and run the application
    root = tk.Tk()
    app = LibraryApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()
