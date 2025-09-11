import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict, List
from LibrarySystem.models.users import User
from LibrarySystem.models.books import Book
from LibrarySystem.utils.logger import logger

class AdminDashboard:
    def __init__(self, root: tk.Tk, user: User, on_logout: Callable[[], None]):
        self.root = root
        self.user = user
        self.on_logout = on_logout
        
        # Configure the main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create dashboard components
        self._create_header()
        self._create_sidebar()
        self._create_content_area()
        
        # Set default view
        self._show_dashboard_summary()
    
    def _create_header(self):
        """Create the header with user info and logout button"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # App title
        ttk.Label(header_frame, text="Library Management System", 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # User info and logout
        user_frame = ttk.Frame(header_frame)
        user_frame.pack(side=tk.RIGHT)
        
        ttk.Label(user_frame, text=f"Logged in as: {self.user.name} (Admin)").pack(side=tk.LEFT, padx=10)
        ttk.Button(user_frame, text="Logout", command=self.on_logout).pack(side=tk.LEFT)
    
    def _create_sidebar(self):
        """Create sidebar with navigation buttons"""
        # Create frames for sidebar and content
        self.content_container = ttk.Frame(self.main_frame)
        self.content_container.pack(fill=tk.BOTH, expand=True)
        
        sidebar_frame = ttk.Frame(self.content_container, width=200)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar_frame.pack_propagate(False)  # Prevent shrinking
        
        # Navigation buttons
        buttons = [
            ("Dashboard", self._show_dashboard_summary),
            ("Book Management", self._show_book_management),
            ("User Management", self._show_user_management),
            ("Lending", self._show_lending_management),
            ("Reservations", self._show_reservations),
            ("Reports", self._show_reports),
            ("Settings", self._show_settings)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(sidebar_frame, text=text, command=command, width=20)
            btn.pack(pady=5, padx=10, anchor=tk.W)
    
    def _create_content_area(self):
        """Create the main content area"""
        self.content_frame = ttk.Frame(self.content_container)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def _clear_content(self):
        """Clear the content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _show_dashboard_summary(self):
        """Show dashboard summary with key metrics"""
        self._clear_content()
        
        # Dashboard title
        ttk.Label(self.content_frame, text="Dashboard", 
                 font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=10)
        
        # Stats cards
        stats_frame = ttk.Frame(self.content_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Create placeholder stat cards
        stats = [
            {"title": "Total Books", "value": "Loading...", "color": "#4CAF50"},
            {"title": "Books on Loan", "value": "Loading...", "color": "#2196F3"},
            {"title": "Overdue Books", "value": "Loading...", "color": "#F44336"},
            {"title": "Active Users", "value": "Loading...", "color": "#FF9800"}
        ]
        
        for stat in stats:
            self._create_stat_card(stats_frame, stat["title"], stat["value"], stat["color"])
        
        # Recent activity section
        activity_frame = ttk.LabelFrame(self.content_frame, text="Recent Activity")
        activity_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(activity_frame, text="Recent activity will be displayed here.").pack(
            anchor=tk.W, padx=10, pady=10)
    
    def _create_stat_card(self, parent, title, value, color):
        """Create a statistic card widget"""
        card = tk.Frame(parent, bg=color, padx=10, pady=10, bd=1, relief=tk.RAISED)
        card.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        
        ttk.Label(card, text=title, background=color, foreground="white").pack(anchor=tk.W)
        ttk.Label(card, text=value, background=color, foreground="white", 
                 font=("Arial", 18, "bold")).pack(anchor=tk.W, pady=5)
    
    def _show_book_management(self):
        """Show book management screen"""
        self._clear_content()
        
        ttk.Label(self.content_frame, text="Book Management", 
                 font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=10)
        
        # Add book button
        ttk.Button(self.content_frame, text="Add New Book").pack(anchor=tk.W, pady=10)
        
        # Book list
        list_frame = ttk.Frame(self.content_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create columns
        columns = ("id", "title", "author", "category", "isbn", "available")
        
        tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Define headings
        tree.heading("id", text="ID")
        tree.heading("title", text="Title")
        tree.heading("author", text="Author")
        tree.heading("category", text="Category")
        tree.heading("isbn", text="ISBN")
        tree.heading("available", text="Available")
        
        # Define column widths
        tree.column("id", width=50)
        tree.column("title", width=200)
        tree.column("author", width=150)
        tree.column("category", width=100)
        tree.column("isbn", width=100)
        tree.column("available", width=80)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add placeholder data
        for i in range(1, 10):
            tree.insert("", tk.END, values=(
                i, f"Book Title {i}", f"Author {i}", 
                "Fiction" if i % 2 == 0 else "Non-Fiction",
                f"978-123456{i}", "Yes" if i % 3 != 0 else "No"
            ))
    
    def _show_user_management(self):
        """Show user management screen"""
        self._clear_content()
        
        ttk.Label(self.content_frame, text="User Management", 
                 font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=10)
        
        # Placeholder content
        ttk.Label(self.content_frame, text="User management functionality coming soon").pack(pady=20)
    
    def _show_lending_management(self):
        """Show lending management screen"""
        self._clear_content()
        
        ttk.Label(self.content_frame, text="Lending Management", 
                 font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=10)
        
        # Placeholder content
        ttk.Label(self.content_frame, text="Lending management functionality coming soon").pack(pady=20)
    
    def _show_reservations(self):
        """Show reservations management screen"""
        self._clear_content()
        
        ttk.Label(self.content_frame, text="Reservations", 
                 font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=10)
        
        # Placeholder content
        ttk.Label(self.content_frame, text="Reservations functionality coming soon").pack(pady=20)
    
    def _show_reports(self):
        """Show reports screen"""
        self._clear_content()
        
        ttk.Label(self.content_frame, text="Reports", 
                 font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=10)
        
        # Placeholder content
        ttk.Label(self.content_frame, text="Reports functionality coming soon").pack(pady=20)
    
    def _show_settings(self):
        """Show settings screen"""
        self._clear_content()
        
        ttk.Label(self.content_frame, text="Settings", 
                 font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=10)
        
        # Placeholder content
        ttk.Label(self.content_frame, text="Settings functionality coming soon").pack(pady=20)
