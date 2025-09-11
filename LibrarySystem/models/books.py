from typing import Optional, List, Dict, Any
from datetime import datetime
from LibrarySystem.utils.db_connection import db_manager
from LibrarySystem.utils.validators import validators
from LibrarySystem.utils.logger import logger

class Book:
    def __init__(self, book_id: Optional[int] = None, title: str = "", 
                 author: str = "", isbn: str = "", category: str = "",
                 total_copies: int = 1, available_copies: int = 1, description: str = ""):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.category = category
        self.total_copies = total_copies
        self.available_copies = available_copies
        self.description = description
        self.created_date = None
    
    @classmethod
    def get_by_id(cls, book_id: int) -> Optional['Book']:
        """Get book by ID."""
        if not db_manager.connected:
            return None
        
        result = db_manager.execute_query(
            "SELECT * FROM books WHERE book_id = ?", (book_id,)
        )
        
        if result and len(result) > 0:
            book = cls()
            book._load_from_dict(result[0])
            return book
        
        return None
    
    @classmethod
    def get_all_books(cls) -> List['Book']:
        """Get all books."""
        if not db_manager.connected:
            return []
        
        result = db_manager.execute_query(
            "SELECT * FROM books ORDER BY title"
        )
        
        books = []
        if result:
            for book_data in result:
                book = cls()
                book._load_from_dict(book_data)
                books.append(book)
        
        return books
    
    @classmethod
    def search_books(cls, search_term: str, category: str = "") -> List['Book']:
        """Search books by title, author, or ISBN."""
        if not db_manager.connected:
            return []
        
        search_pattern = f"%{search_term}%"
        
        if category:
            result = db_manager.execute_query("""
                SELECT * FROM books 
                WHERE (title LIKE ? OR author LIKE ? OR isbn LIKE ?) AND category = ?
                ORDER BY title
            """, (search_pattern, search_pattern, search_pattern, category))
        else:
            result = db_manager.execute_query("""
                SELECT * FROM books 
                WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?
                ORDER BY title
            """, (search_pattern, search_pattern, search_pattern))
        
        books = []
        if result:
            for book_data in result:
                book = cls()
                book._load_from_dict(book_data)
                books.append(book)
        
        return books
    
    @classmethod
    def get_available_books(cls) -> List['Book']:
        """Get books that are available for borrowing."""
        if not db_manager.connected:
            return []
        
        result = db_manager.execute_query(
            "SELECT * FROM books WHERE available_copies > 0 ORDER BY title"
        )
        
        books = []
        if result:
            for book_data in result:
                book = cls()
                book._load_from_dict(book_data)
                books.append(book)
        
        return books
    
    @classmethod
    def get_categories(cls) -> List[str]:
        """Get all unique categories."""
        if not db_manager.connected:
            return []
        
        result = db_manager.execute_query(
            "SELECT DISTINCT category FROM books WHERE category IS NOT NULL AND category != '' ORDER BY category"
        )
        
        return [row['category'] for row in result] if result else []
    
    @classmethod
    def get_popular_books(cls, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most borrowed books."""
        if not db_manager.connected:
            return []
        
        result = db_manager.execute_query("""
            SELECT b.*, COUNT(l.lending_id) as borrow_count
            FROM books b
            LEFT JOIN lending l ON b.book_id = l.book_id
            GROUP BY b.book_id
            ORDER BY borrow_count DESC, b.title
            LIMIT ?
        """, (limit,))
        
        return result if result else []
    
    def save(self) -> bool:
        """Save book to database."""
        if not db_manager.connected:
            return False
        
        # Validate data
        is_valid, error_msg = self._validate()
        if not is_valid:
            logger.error(f"Book validation failed: {error_msg}")
            return False
        
        try:
            if self.book_id is None:  # New book
                # Check if ISBN already exists (if provided)
                if self.isbn:
                    existing = db_manager.execute_query(
                        "SELECT book_id FROM books WHERE isbn = ?", (self.isbn,)
                    )
                    if existing:
                        logger.error(f"ISBN already exists: {self.isbn}")
                        return False
                
                success = db_manager.execute_update("""
                    INSERT INTO books (title, author, isbn, category, total_copies, available_copies, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (self.title, self.author, self.isbn, self.category, 
                      self.total_copies, self.available_copies, self.description))
                
                if success:
                    self.book_id = db_manager.get_last_insert_id()
                    logger.info(f"New book created: {self.title}")
                    return True
            else:  # Update existing book
                success = db_manager.execute_update("""
                    UPDATE books SET title = ?, author = ?, isbn = ?, category = ?, 
                                   total_copies = ?, available_copies = ?, description = ?
                    WHERE book_id = ?
                """, (self.title, self.author, self.isbn, self.category,
                      self.total_copies, self.available_copies, self.description, self.book_id))
                
                if success:
                    logger.info(f"Book updated: {self.title}")
                    return True
        
        except Exception as e:
            logger.error(f"Error saving book: {e}")
        
        return False
    
    def delete(self) -> bool:
        """Delete book if no active lendings exist."""
        if not db_manager.connected or not self.book_id:
            return False
        
        # Check if book has active lendings
        active_lendings = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM lending WHERE book_id = ? AND status = 'active'",
            (self.book_id,)
        )
        
        if active_lendings and active_lendings[0]['count'] > 0:
            logger.error(f"Cannot delete book with active lendings: {self.title}")
            return False
        
        # Check if book has pending reservations
        pending_reservations = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM reservations WHERE book_id = ? AND status = 'pending'",
            (self.book_id,)
        )
        
        if pending_reservations and pending_reservations[0]['count'] > 0:
            logger.error(f"Cannot delete book with pending reservations: {self.title}")
            return False
        
        success = db_manager.execute_update(
            "DELETE FROM books WHERE book_id = ?", (self.book_id,)
        )
        
        if success:
            logger.info(f"Book deleted: {self.title}")
        
        return success
    
    def update_availability(self, change: int) -> bool:
        """Update available copies (positive to add, negative to subtract)."""
        if not db_manager.connected or not self.book_id:
            return False
        
        new_available = self.available_copies + change
        
        if new_available < 0:
            logger.error(f"Cannot reduce availability below 0 for book: {self.title}")
            return False
        
        if new_available > self.total_copies:
            logger.error(f"Available copies cannot exceed total copies for book: {self.title}")
            return False
        
        success = db_manager.execute_update(
            "UPDATE books SET available_copies = ? WHERE book_id = ?",
            (new_available, self.book_id)
        )
        
        if success:
            self.available_copies = new_available
            logger.info(f"Book availability updated: {self.title} (available: {new_available})")
        
        return success
    
    def is_available(self) -> bool:
        """Check if book is available for borrowing."""
        return self.available_copies > 0
    
    def get_current_borrowers(self) -> List[Dict[str, Any]]:
        """Get list of users currently borrowing this book."""
        if not db_manager.connected or not self.book_id:
            return []
        
        result = db_manager.execute_query("""
            SELECT l.*, u.name, u.email
            FROM lending l
            JOIN users u ON l.user_id = u.user_id
            WHERE l.book_id = ? AND l.status = 'active'
            ORDER BY l.issue_date
        """, (self.book_id,))
        
        return result if result else []
    
    def get_reservation_queue(self) -> List[Dict[str, Any]]:
        """Get reservation queue for this book."""
        if not db_manager.connected or not self.book_id:
            return []
        
        result = db_manager.execute_query("""
            SELECT r.*, u.name, u.email
            FROM reservations r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.book_id = ? AND r.status = 'pending'
            ORDER BY r.reservation_date
        """, (self.book_id,))
        
        return result if result else []
    
    def _validate(self) -> tuple[bool, str]:
        """Validate book data."""
        is_valid, error_msg = validators.validate_required_field(self.title, "Title")
        if not is_valid:
            return False, error_msg
        
        is_valid, error_msg = validators.validate_required_field(self.author, "Author")
        if not is_valid:
            return False, error_msg
        
        if self.isbn:
            is_valid, error_msg = validators.validate_isbn(self.isbn)
            if not is_valid:
                return False, error_msg
        
        if self.total_copies <= 0:
            return False, "Total copies must be greater than 0"
        
        if self.available_copies < 0:
            return False, "Available copies cannot be negative"
        
        if self.available_copies > self.total_copies:
            return False, "Available copies cannot exceed total copies"
        
        return True, ""
    
    def _load_from_dict(self, data: Dict[str, Any]):
        """Load book data from dictionary."""
        self.book_id = data.get('book_id')
        self.title = data.get('title', '')
        self.author = data.get('author', '')
        self.isbn = data.get('isbn', '')
        self.category = data.get('category', '')
        self.total_copies = data.get('total_copies', 1)
        self.available_copies = data.get('available_copies', 1)
        self.description = data.get('description', '')
        self.created_date = data.get('created_date')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert book to dictionary."""
        return {
            'book_id': self.book_id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'category': self.category,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'description': self.description,
            'created_date': self.created_date
        }
    
    def __str__(self):
        return f"Book(id={self.book_id}, title='{self.title}', author='{self.author}', available={self.available_copies}/{self.total_copies})"
