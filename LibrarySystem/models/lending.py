from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from LibrarySystem.utils.db_connection import db_manager
from LibrarySystem.utils.logger import logger
from LibrarySystem.models.books import Book
from LibrarySystem.models.users import User

class Lending:
    def __init__(self, lending_id: Optional[int] = None, book_id: int = 0, 
                 user_id: int = 0, issue_date: Optional[datetime] = None,
                 due_date: Optional[datetime] = None, return_date: Optional[datetime] = None,
                 fine_amount: float = 0.0, status: str = "active"):
        self.lending_id = lending_id
        self.book_id = book_id
        self.user_id = user_id
        self.issue_date = issue_date or datetime.now()
        self.due_date = due_date
        self.return_date = return_date
        self.fine_amount = fine_amount
        self.status = status
    
    @classmethod
    def issue_book(cls, book_id: int, user_id: int, loan_days: int = 14) -> Optional['Lending']:
        """Issue a book to a user."""
        if not db_manager.connected:
            return None
        
        # Check if book is available
        book = Book.get_by_id(book_id)
        if not book or not book.is_available():
            logger.error(f"Book not available for lending: {book_id}")
            return None
        
        # Check if user exists and is active
        user = User.get_by_id(user_id)
        if not user or not user.is_active:
            logger.error(f"User not found or inactive: {user_id}")
            return None
        
        # Check if user already has this book
        existing = db_manager.execute_query(
            "SELECT * FROM lending WHERE book_id = ? AND user_id = ? AND status = 'active'",
            (book_id, user_id)
        )
        if existing:
            logger.error(f"User already has this book: book_id={book_id}, user_id={user_id}")
            return None
        
        # Create lending record
        issue_date = datetime.now()
        due_date = issue_date + timedelta(days=loan_days)
        
        lending = cls(
            book_id=book_id,
            user_id=user_id,
            issue_date=issue_date,
            due_date=due_date,
            status="active"
        )
        
        if lending.save():
            # Update book availability
            if book.update_availability(-1):
                logger.info(f"Book issued: book_id={book_id}, user_id={user_id}")
                return lending
            else:
                # Rollback lending if book update fails
                lending.delete()
                return None
        
        return None
    
    @classmethod
    def return_book(cls, lending_id: int, fine_amount: float = 0.0) -> bool:
        """Return a book."""
        if not db_manager.connected:
            return False
        
        lending = cls.get_by_id(lending_id)
        if not lending or lending.status != 'active':
            logger.error(f"Lending not found or not active: {lending_id}")
            return False
        
        # Update lending record
        lending.return_date = datetime.now()
        lending.fine_amount = fine_amount
        lending.status = 'returned'
        
        if lending.save():
            # Update book availability
            book = Book.get_by_id(lending.book_id)
            if book and book.update_availability(1):
                logger.info(f"Book returned: lending_id={lending_id}")
                
                # Check if there are pending reservations
                cls._process_next_reservation(lending.book_id)
                return True
        
        return False
    
    @classmethod
    def get_by_id(cls, lending_id: int) -> Optional['Lending']:
        """Get lending by ID."""
        if not db_manager.connected:
            return None
        
        result = db_manager.execute_query(
            "SELECT * FROM lending WHERE lending_id = ?", (lending_id,)
        )
        
        if result and len(result) > 0:
            lending = cls()
            lending._load_from_dict(result[0])
            return lending
        
        return None
    
    @classmethod
    def get_active_lendings(cls) -> List[Dict[str, Any]]:
        """Get all active lendings with book and user details."""
        if not db_manager.connected:
            return []
        
        result = db_manager.execute_query("""
            SELECT l.*, b.title, b.author, b.isbn, u.name, u.email
            FROM lending l
            JOIN books b ON l.book_id = b.book_id
            JOIN users u ON l.user_id = u.user_id
            WHERE l.status = 'active'
            ORDER BY l.due_date
        """)
        
        return result if result else []
    
    @classmethod
    def get_lendings_by_status(cls, status: str = "active") -> List[Dict[str, Any]]:
        """Get lendings by status."""
        if not db_manager.connected:
            return []
        
        if status not in ["active", "returned", "all"]:
            status = "active"
            
        query = """
            SELECT l.*, b.title, b.author, b.isbn, u.name, u.email
            FROM lending l
            JOIN books b ON l.book_id = b.book_id
            JOIN users u ON l.user_id = u.user_id
        """
        
        params = []
        if status != "all":
            query += " WHERE l.status = ?"
            params.append(status)
            
        query += " ORDER BY l.due_date"
        
        result = db_manager.execute_query(query, tuple(params))
        return result if result else []
    
    @classmethod
    def get_overdue_lendings(cls) -> List[Dict[str, Any]]:
        """Get overdue lendings."""
        if not db_manager.connected:
            return []
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        result = db_manager.execute_query("""
            SELECT l.*, b.title, b.author, b.isbn, u.name, u.email
            FROM lending l
            JOIN books b ON l.book_id = b.book_id
            JOIN users u ON l.user_id = u.user_id
            WHERE l.status = 'active' AND DATE(l.due_date) < ?
            ORDER BY l.due_date
        """, (current_date,))
        
        return result if result else []
    
    @classmethod
    def get_user_lendings(cls, user_id: int, active_only: bool = False) -> List[Dict[str, Any]]:
        """Get lendings for a specific user."""
        if not db_manager.connected:
            return []
        
        query = """
            SELECT l.*, b.title, b.author, b.isbn
            FROM lending l
            JOIN books b ON l.book_id = b.book_id
            WHERE l.user_id = ?
        """
        
        if active_only:
            query += " AND l.status = 'active'"
        
        query += " ORDER BY l.issue_date DESC"
        
        result = db_manager.execute_query(query, (user_id,))
        return result if result else []
    
    @classmethod
    def get_book_lendings(cls, book_id: int) -> List[Dict[str, Any]]:
        """Get lending history for a specific book."""
        if not db_manager.connected:
            return []
        
        result = db_manager.execute_query("""
            SELECT l.*, u.name, u.email
            FROM lending l
            JOIN users u ON l.user_id = u.user_id
            WHERE l.book_id = ?
            ORDER BY l.issue_date DESC
        """, (book_id,))
        
        return result if result else []
    
    @classmethod
    def get_lending_statistics(cls, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get lending statistics for a date range."""
        if not db_manager.connected:
            return {}
        
        # Default to last 30 days if no dates provided
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        stats = {}
        
        # Total lendings in period
        result = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM lending WHERE DATE(issue_date) BETWEEN ? AND ?",
            (start_date, end_date)
        )
        stats['total_lendings'] = result[0]['count'] if result else 0
        
        # Currently active lendings
        result = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM lending WHERE status = 'active'"
        )
        stats['active_lendings'] = result[0]['count'] if result else 0
        
        # Overdue lendings
        current_date = datetime.now().strftime('%Y-%m-%d')
        result = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM lending WHERE status = 'active' AND DATE(due_date) < ?",
            (current_date,)
        )
        stats['overdue_lendings'] = result[0]['count'] if result else 0
        
        # Most active borrowers
        result = db_manager.execute_query("""
            SELECT u.name, u.email, COUNT(l.lending_id) as borrow_count
            FROM lending l
            JOIN users u ON l.user_id = u.user_id
            WHERE DATE(l.issue_date) BETWEEN ? AND ?
            GROUP BY l.user_id
            ORDER BY borrow_count DESC
            LIMIT 5
        """, (start_date, end_date))
        stats['top_borrowers'] = result if result else []
        
        return stats
    
    @classmethod
    def _process_next_reservation(cls, book_id: int):
        """Process next reservation in queue when book becomes available."""
        from models.reservations import Reservation
        
        # Get next reservation in queue
        reservations = db_manager.execute_query("""
            SELECT * FROM reservations 
            WHERE book_id = ? AND status = 'pending'
            ORDER BY reservation_date
            LIMIT 1
        """, (book_id,))
        
        if reservations:
            reservation_data = reservations[0]
            # Create notification for user
            db_manager.execute_update("""
                INSERT INTO notifications (user_id, message, type)
                VALUES (?, ?, ?)
            """, (reservation_data['user_id'], 
                  f"Your reserved book is now available: {book_id}", 
                  "reservation"))
            
            logger.info(f"Notification sent for reservation: {reservation_data['reservation_id']}")
    
    def save(self) -> bool:
        """Save lending to database."""
        if not db_manager.connected:
            return False
        
        try:
            if self.lending_id is None:  # New lending
                success = db_manager.execute_update("""
                    INSERT INTO lending (book_id, user_id, issue_date, due_date, return_date, fine_amount, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (self.book_id, self.user_id, self.issue_date, self.due_date,
                      self.return_date, self.fine_amount, self.status))
                
                if success:
                    self.lending_id = db_manager.get_last_insert_id()
                    return True
            else:  # Update existing lending
                success = db_manager.execute_update("""
                    UPDATE lending SET book_id = ?, user_id = ?, issue_date = ?, due_date = ?,
                                     return_date = ?, fine_amount = ?, status = ?
                    WHERE lending_id = ?
                """, (self.book_id, self.user_id, self.issue_date, self.due_date,
                      self.return_date, self.fine_amount, self.status, self.lending_id))
                
                return success
        
        except Exception as e:
            logger.error(f"Error saving lending: {e}")
        
        return False
    
    def delete(self) -> bool:
        """Delete lending record."""
        if not db_manager.connected or not self.lending_id:
            return False
        
        success = db_manager.execute_update(
            "DELETE FROM lending WHERE lending_id = ?", (self.lending_id,)
        )
        
        return success
    
    def is_overdue(self) -> bool:
        """Check if lending is overdue."""
        if self.status != 'active' or self.due_date is None:
            return False
        return datetime.now() > self.due_date
    
    def days_overdue(self) -> int:
        """Get number of days overdue."""
        if not self.is_overdue() or self.due_date is None:
            return 0
        return (datetime.now() - self.due_date).days
    
    def calculate_fine(self, fine_per_day: float = 1.0) -> float:
        """Calculate fine amount based on days overdue."""
        days = self.days_overdue()
        return days * fine_per_day if days > 0 else 0.0
    
    def _load_from_dict(self, data: Dict[str, Any]):
        """Load lending data from dictionary."""
        self.lending_id = data.get('lending_id')
        self.book_id = data.get('book_id')
        self.user_id = data.get('user_id')
        
        # Handle datetime fields
        issue_date_str = data.get('issue_date')
        if issue_date_str:
            self.issue_date = datetime.fromisoformat(issue_date_str)
        
        due_date_str = data.get('due_date')
        if due_date_str:
            self.due_date = datetime.fromisoformat(due_date_str)
        
        return_date_str = data.get('return_date')
        if return_date_str:
            self.return_date = datetime.fromisoformat(return_date_str)
        
        self.fine_amount = float(data.get('fine_amount', 0.0))
        self.status = data.get('status', 'active')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert lending to dictionary."""
        return {
            'lending_id': self.lending_id,
            'book_id': self.book_id,
            'user_id': self.user_id,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'fine_amount': self.fine_amount,
            'status': self.status
        }
    
    def __str__(self):
        return f"Lending(id={self.lending_id}, book_id={self.book_id}, user_id={self.user_id}, status='{self.status}')"
