import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from LibrarySystem.models.users import User
from LibrarySystem.utils.db_connection import db_manager
from LibrarySystem.utils.logger import logger

class LoginScreen:
    def __init__(self, root: tk.Tk, on_login_success: Callable[[User], None]):
        self.root = root
        self.on_login_success = on_login_success
        self.user = None
        
        # Configure root window
        self.root.title("Library Management System - Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Center the window
        self._center_window()
        
        # Create and setup UI
        self._create_widgets()
        
        # Try to connect to database
        self._check_database_connection()
    
    def _center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self):
        """Create and arrange widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Library Management System", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Connection status
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Email field
        ttk.Label(main_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(main_frame, textvariable=self.email_var, width=25)
        self.email_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Password field
        ttk.Label(main_frame, text="Password:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, 
                                      show="*", width=25)
        self.password_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Login button
        self.login_button = ttk.Button(main_frame, text="Login", command=self._login)
        self.login_button.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Default credentials info
        info_frame = ttk.LabelFrame(main_frame, text="Default Credentials", padding="10")
        info_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(info_frame, text="Admin: admin@library.com / admin123").pack()
        
        # Register new user button
        self.register_button = ttk.Button(main_frame, text="Register New User", 
                                        command=self._show_register_dialog)
        self.register_button.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self._login())
        
        # Set focus to email entry
        self.email_entry.focus_set()
    
    def _check_database_connection(self):
        """Check database connection and update status."""
        if db_manager.connect():
            self.status_label.config(text="✓ Database connected", foreground="green")
            self.login_button.config(state="normal")
            self.register_button.config(state="normal")
        else:
            self.status_label.config(text="⚠ Database not connected - View only mode", 
                                   foreground="red")
            self.login_button.config(state="disabled")
            self.register_button.config(state="disabled")
    
    def _login(self):
        """Handle login attempt."""
        email = self.email_var.get().strip()
        password = self.password_var.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter both email and password")
            return
        
        if not db_manager.connected:
            messagebox.showerror("Error", "Database not connected")
            return
        
        # Authenticate user
        user = User.authenticate(email, password)
        
        if user:
            logger.info(f"User logged in: {user.email} ({user.role})")
            self.user = user
            self.root.withdraw()  # Hide login window
            self.on_login_success(user)
        else:
            messagebox.showerror("Error", "Invalid email or password")
            self.password_var.set("")  # Clear password field
    
    def _show_register_dialog(self):
        """Show user registration dialog."""
        if not db_manager.connected:
            messagebox.showerror("Error", "Database not connected")
            return
        
        # Create registration window
        register_window = tk.Toplevel(self.root)
        register_window.title("Register New User")
        register_window.geometry("400x350")
        register_window.resizable(False, False)
        register_window.transient(self.root)
        register_window.grab_set()
        
        # Center the window
        register_window.update_idletasks()
        x = (register_window.winfo_screenwidth() // 2) - (200)
        y = (register_window.winfo_screenheight() // 2) - (175)
        register_window.geometry(f"400x350+{x}+{y}")
        
        # Create registration form
        main_frame = ttk.Frame(register_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Register New User", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Form fields
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.X)
        
        # Name
        ttk.Label(fields_frame, text="Full Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=name_var, width=30).grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Email
        ttk.Label(fields_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        reg_email_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=reg_email_var, width=30).grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Password
        ttk.Label(fields_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        reg_password_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=reg_password_var, show="*", width=30).grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Confirm Password
        ttk.Label(fields_frame, text="Confirm Password:").grid(row=3, column=0, sticky=tk.W, pady=5)
        confirm_password_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=confirm_password_var, show="*", width=30).grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Role (only for admin registration)
        ttk.Label(fields_frame, text="Role:").grid(row=4, column=0, sticky=tk.W, pady=5)
        role_var = tk.StringVar(value="user")
        role_combo = ttk.Combobox(fields_frame, textvariable=role_var, 
                                 values=["user", "admin"], state="readonly", width=27)
        role_combo.grid(row=4, column=1, pady=5, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        def register_user():
            name = name_var.get().strip()
            email = reg_email_var.get().strip()
            password = reg_password_var.get()
            confirm_password = confirm_password_var.get()
            role = role_var.get()
            
            # Validate input
            if not all([name, email, password, confirm_password]):
                messagebox.showerror("Error", "All fields are required")
                return
            
            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match")
                return
            
            # Create user
            user = User(name=name, email=email, role=role)
            
            if user.save(password):
                messagebox.showinfo("Success", "User registered successfully!")
                register_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to register user. Email may already exist.")
        
        ttk.Button(button_frame, text="Register", command=register_user).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=register_window.destroy).pack(side=tk.LEFT)
    
    def show(self):
        """Show the login window."""
        self.root.deiconify()
        self.root.mainloop()
    
    def destroy(self):
        """Destroy the login window."""
        self.root.destroy()
