import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable, Dict, Any
from LibrarySystem.models.books import Book
from LibrarySystem.utils.logger import logger

class BookDetailsDialog:
    def __init__(self, parent, book: Optional[Book] = None, on_save: Optional[Callable[[Book], None]] = None):
        """
        Dialog for viewing, adding, or editing book details
        
        Parameters:
        - parent: The parent window
        - book: Optional book object to edit; if None, creates a new book
        - on_save: Callback to execute when book is saved
        """
        self.parent = parent
        self.book = book
        self.on_save = on_save
        self.is_new = book is None
        
        # Create the dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Book" if self.is_new else "Edit Book")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)  # Make dialog modal
        self.dialog.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        # Create and arrange widgets
        self._create_widgets()
        
        # Fill fields if editing
        if not self.is_new:
            self._populate_fields()
    
    def _center_dialog(self):
        """Center the dialog on the parent window"""
        self.dialog.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create and arrange dialog widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form entries in a grid layout
        # Title
        ttk.Label(main_frame, text="Title:*").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.title_var, width=40).grid(
            row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Author
        ttk.Label(main_frame, text="Author:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.author_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.author_var, width=40).grid(
            row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # ISBN
        ttk.Label(main_frame, text="ISBN:*").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.isbn_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.isbn_var, width=40).grid(
            row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Category
        ttk.Label(main_frame, text="Category:*").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        categories = ["Fiction", "Non-Fiction", "Science", "History", "Biography", 
                     "Fantasy", "Mystery", "Thriller", "Romance", "Self-Help", "Other"]
        self.category_combobox = ttk.Combobox(main_frame, textvariable=self.category_var, 
                                            values=categories, width=38)
        self.category_combobox.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Total copies
        ttk.Label(main_frame, text="Total Copies:*").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.total_copies_var = tk.StringVar(value="1")
        ttk.Spinbox(main_frame, from_=1, to=100, textvariable=self.total_copies_var, width=5).grid(
            row=4, column=1, sticky=tk.W, pady=5)
        
        # Available copies (only for editing)
        ttk.Label(main_frame, text="Available Copies:*").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.available_copies_var = tk.StringVar(value="1")
        self.available_copies_spinbox = ttk.Spinbox(
            main_frame, from_=0, to=100, textvariable=self.available_copies_var, width=5)
        self.available_copies_spinbox.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        if self.is_new:
            self.available_copies_spinbox.configure(state="disabled")
        
        # Description
        ttk.Label(main_frame, text="Description:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.description_text = tk.Text(main_frame, width=40, height=8)
        self.description_text.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Image upload (placeholder for future implementation)
        ttk.Label(main_frame, text="Cover Image:").grid(row=7, column=0, sticky=tk.W, pady=5)
        image_frame = ttk.Frame(main_frame)
        image_frame.grid(row=7, column=1, sticky=tk.W, pady=5)
        
        ttk.Button(image_frame, text="Upload Image", command=self._upload_image).pack(
            side=tk.LEFT, padx=(0, 10))
        self.image_label = ttk.Label(image_frame, text="No image selected")
        self.image_label.pack(side=tk.LEFT)
        
        # Required fields note
        ttk.Label(main_frame, text="* Required fields", font=("Arial", 8, "italic")).grid(
            row=8, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # Action buttons at the bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save", command=self._save_book).pack(
            side=tk.LEFT, padx=5)
    
    def _populate_fields(self):
        """Fill form fields with book data when editing"""
        if not self.book:
            return
        
        self.title_var.set(self.book.title)
        self.author_var.set(self.book.author)
        self.isbn_var.set(self.book.isbn)
        self.category_var.set(self.book.category)
        self.total_copies_var.set(str(self.book.total_copies))
        self.available_copies_var.set(str(self.book.available_copies))
        self.description_text.insert("1.0", self.book.description)
    
    def _upload_image(self):
        """Placeholder for image upload functionality"""
        # This would be expanded in a real implementation to handle actual image uploads
        file_path = filedialog.askopenfilename(
            title="Select Cover Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")]
        )
        
        if file_path:
            # Just show the filename for now
            file_name = file_path.split("/")[-1]
            self.image_label.config(text=file_name)
            # In a real implementation, you would:
            # 1. Validate the image
            # 2. Resize it if needed
            # 3. Store it or its path
            # 4. Display a thumbnail
    
    def _validate_inputs(self) -> bool:
        """Validate form inputs"""
        # Check required fields
        if not self.title_var.get().strip():
            messagebox.showerror("Validation Error", "Title is required")
            return False
        
        if not self.author_var.get().strip():
            messagebox.showerror("Validation Error", "Author is required")
            return False
        
        if not self.isbn_var.get().strip():
            messagebox.showerror("Validation Error", "ISBN is required")
            return False
        
        if not self.category_var.get():
            messagebox.showerror("Validation Error", "Category is required")
            return False
        
        # Validate ISBN format (simple check)
        isbn = self.isbn_var.get().strip().replace("-", "")
        if not isbn.isdigit() or not (len(isbn) == 10 or len(isbn) == 13):
            messagebox.showerror("Validation Error", "ISBN must be 10 or 13 digits")
            return False
        
        # Validate numeric fields
        try:
            total_copies = int(self.total_copies_var.get())
            available_copies = int(self.available_copies_var.get())
            
            if total_copies < 1:
                messagebox.showerror("Validation Error", "Total copies must be at least 1")
                return False
                
            if available_copies < 0:
                messagebox.showerror("Validation Error", "Available copies cannot be negative")
                return False
                
            if available_copies > total_copies:
                messagebox.showerror("Validation Error", 
                                    "Available copies cannot exceed total copies")
                return False
                
        except ValueError:
            messagebox.showerror("Validation Error", "Copies must be valid numbers")
            return False
        
        return True
    
    def _save_book(self):
        """Save the book data"""
        if not self._validate_inputs():
            return
        
        # Get values from form
        book_data = {
            "title": self.title_var.get().strip(),
            "author": self.author_var.get().strip(),
            "isbn": self.isbn_var.get().strip(),
            "category": self.category_var.get(),
            "total_copies": int(self.total_copies_var.get()),
            "available_copies": int(self.available_copies_var.get()),
            "description": self.description_text.get("1.0", tk.END).strip()
        }
        
        if self.is_new:
            # Create new book
            new_book = Book(
                title=book_data["title"],
                author=book_data["author"],
                isbn=book_data["isbn"],
                category=book_data["category"],
                total_copies=book_data["total_copies"],
                available_copies=book_data["available_copies"],
                description=book_data["description"]
            )
            
            # Call the save callback if provided
            if self.on_save:
                self.on_save(new_book)
        else:
            # Update existing book
            self.book.title = book_data["title"]
            self.book.author = book_data["author"]
            self.book.isbn = book_data["isbn"]
            self.book.category = book_data["category"]
            self.book.total_copies = book_data["total_copies"]
            self.book.available_copies = book_data["available_copies"]
            self.book.description = book_data["description"]
            
            # Call the save callback if provided
            if self.on_save:
                self.on_save(self.book)
        
        # Close the dialog
        self.dialog.destroy()
