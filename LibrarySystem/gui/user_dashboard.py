import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict, List
from LibrarySystem.models.users import User
from LibrarySystem.models.books import Book
from LibrarySystem.utils.logger import logger

class UserDashboard:
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
        self._show_catalog()
    
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
        
        ttk.Label(user_frame, text=f"Logged in as: {self.user.name}").pack(side=tk.LEFT, padx=10)
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
            ("Book Catalog", self._show_catalog),
            ("My Loans", self._show_my_loans),
            ("My Reservations", self._show_my_reservations),
            ("My Profile", self._show_profile),
            ("Notifications", self._show_notifications)
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
    
    def _show_catalog(self):
        """Show book catalog"""
        self._clear_content()
        
        # Catalog title
        ttk.Label(self.content_frame, text="Book Catalog", 
                 font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=10)
        
        # Search frame
        search_frame = ttk.Frame(self.content_frame)
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        search_entry = ttk.Entry(search_frame, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(search_frame, text="Search").pack(side=tk.LEFT)
        
        # Categories filter
        filter_frame = ttk.Frame(self.content_frame)
        filter_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(filter_frame, text="Filter by:").pack(side=tk.LEFT, padx=(0, 5))
        category_combobox = ttk.Combobox(filter_frame, values=["All Categories", "Fiction", "Non-Fiction", 
                                                           "Science", "History", "Biography"])
        category_combobox.current(0)
        category_combobox.pack(side=tk.LEFT, padx=(0, 10))
        
        # Book list
        list_frame = ttk.Frame(self.content_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create columns
        columns = ("id", "title", "author", "category", "available")
        
        tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Define headings
        tree.heading("id", text="ID")
        tree.heading("title", text="Title")
        tree.heading("author", text="Author")
        tree.heading("category", text="Category")
        tree.heading("available", text="Available")
        
        # Define column widths
        tree.column("id", width=50)
        tree.column("title", width=200)
        tree.column("author", width=150)
        tree.column("category", width=100)
        tree.column("available", width=80)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add placeholder data
        for i in range(1, 20):
            tree.insert("", tk.END, values=(
                i, f"Book Title {i}", f"Author {i}", 
                "Fiction" if i % 2 == 0 else "Non-Fiction",
                "Yes" if i % 3 != 0 else "No"
            ))
        
        # Action buttons
        action_frame = ttk.Frame(self.content_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="View Details").pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Borrow Book").pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Reserve Book").pack(side=tk.LEFT, padx=5)
    
    def _show_my_loans(self):
        """Show user's current loans"""
        self._clear_content()
        
        ttk.Label(self.content_frame, text="My Loans", 
                 font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=10)
        
        # Create tabs for current and history
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Current loans tab
        current_frame = ttk.Frame(notebook)
        notebook.add(current_frame, text="Current Loans")
        
        # History tab
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text="Loan History")
        
        # Current loans list
        columns = ("id", "title", "author", "issued_date", "due_date", "status")
        
        tree = ttk.Treeview(current_frame, columns=columns, show="headings")
        
        # Define headings
        tree.heading("id", text="ID")
        tree.heading("title", text="Title")
        tree.heading("author", text="Author")
        tree.heading("issued_date", text="Issued Date")
        tree.heading("due_date", text="Due Date")
        tree.heading("status", text="Status")
        
        # Define column widths
        tree.column("id", width=50)
        tree.column("title", width=200)
        tree.column("author", width=150)
        tree.column("issued_date", width=100)
        tree.column("due_date", width=100)
        tree.column("status", width=80)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(current_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add placeholder data
        import datetime
        today = datetime.date.today()
        for i in range(1, 5):
            due_date = today + datetime.timedelta(days=7*i)
            status = "Overdue" if i == 1 else "Active"
            tree.insert("", tk.END, values=(
                i, f"Book Title {i}", f"Author {i}", 
                today.strftime("%Y-%m-%d"),
                due_date.strftime("%Y-%m-%d"),
                status
            ))
        
        # Add return button
        ttk.Button(current_frame, text="Return Selected Book").pack(anchor=tk.W, pady=10)
        
        # Similar structure for history tab (placeholder)
        ttk.Label(history_frame, text="Your loan history will appear here").pack(pady=20)
    
    def _show_my_reservations(self):
        """Show user's reservations"""
        self._clear_content()
        
        ttk.Label(self.content_frame, text="My Reservations", 
                 font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=10)
        
        # Placeholder content
        ttk.Label(self.content_frame, text="You have no active reservations.").pack(pady=20)
    
    def _show_profile(self):
        """Show user profile"""
        self._clear_content()
        
        ttk.Label(self.content_frame, text="My Profile", 
                 font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=10)
        
        # Profile form
        form_frame = ttk.Frame(self.content_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Two column layout
        left_frame = ttk.Frame(form_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        right_frame = ttk.Frame(form_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Left column fields
        ttk.Label(left_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(left_frame, width=30)
        name_entry.insert(0, self.user.name)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(left_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        email_entry = ttk.Entry(left_frame, width=30)
        email_entry.insert(0, self.user.email)
        email_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Right column fields
        ttk.Label(right_frame, text="Member Since:").grid(row=0, column=0, sticky=tk.W, pady=5)
        member_since = ttk.Label(right_frame, text="2023-01-01")
        member_since.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(right_frame, text="Account Status:").grid(row=1, column=0, sticky=tk.W, pady=5)
        status = ttk.Label(right_frame, text="Active")
        status.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Password change section
        pw_frame = ttk.LabelFrame(self.content_frame, text="Change Password")
        pw_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(pw_frame, text="Current Password:").grid(row=0, column=0, sticky=tk.W, pady=5)
        current_pw = ttk.Entry(pw_frame, show="*", width=30)
        current_pw.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(pw_frame, text="New Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        new_pw = ttk.Entry(pw_frame, show="*", width=30)
        new_pw.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(pw_frame, text="Confirm Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        confirm_pw = ttk.Entry(pw_frame, show="*", width=30)
        confirm_pw.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Action buttons
        action_frame = ttk.Frame(self.content_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Update Profile").pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Change Password").pack(side=tk.LEFT, padx=5)
    
    def _show_notifications(self):
        """Show user notifications"""
        self._clear_content()
        
        ttk.Label(self.content_frame, text="Notifications", 
                 font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=10)
        
        # Placeholder for notifications
        notifications_frame = ttk.Frame(self.content_frame)
        notifications_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas with scrollbar for notifications
        canvas = tk.Canvas(notifications_frame)
        scrollbar = ttk.Scrollbar(notifications_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Sample notifications
        notifications = [
            {"title": "Book Due Soon", 
             "message": "Your book 'Python Programming' is due in 2 days.", 
             "date": "2023-09-09",
             "is_read": False},
            {"title": "Reserved Book Available", 
             "message": "The book 'Data Science Handbook' you reserved is now available.", 
             "date": "2023-09-08",
             "is_read": False},
            {"title": "Overdue Notice", 
             "message": "Your book 'JavaScript Essentials' is overdue. Please return it as soon as possible.", 
             "date": "2023-09-05",
             "is_read": True},
        ]
        
        if not notifications:
            ttk.Label(scrollable_frame, text="You have no notifications").pack(pady=20)
        else:
            for i, notif in enumerate(notifications):
                # Create notification card
                card = ttk.Frame(scrollable_frame)
                card.pack(fill=tk.X, pady=5, padx=5)
                
                # Background color based on read status
                if not notif["is_read"]:
                    card.configure(style="Unread.TFrame")
                
                # Title with date
                header_frame = ttk.Frame(card)
                header_frame.pack(fill=tk.X)
                
                ttk.Label(header_frame, text=notif["title"], 
                         font=("Arial", 10, "bold")).pack(side=tk.LEFT)
                ttk.Label(header_frame, text=notif["date"]).pack(side=tk.RIGHT)
                
                # Message
                ttk.Label(card, text=notif["message"], wraplength=500).pack(
                    anchor=tk.W, pady=(5, 10), padx=5)
                
                # Separator
                ttk.Separator(scrollable_frame, orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        # Mark all as read button
        ttk.Button(self.content_frame, text="Mark All as Read").pack(anchor=tk.W, pady=10)
