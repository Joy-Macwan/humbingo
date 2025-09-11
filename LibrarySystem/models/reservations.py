from typing import Optional, List, Dict, Any
from datetime import datetime
from LibrarySystem.utils.db_connection import db_manager
from LibrarySystem.utils.logger import logger
from LibrarySystem.models.books import Book
from LibrarySystem.models.users import User

class Reservation:
    def __init__(self, reservation_id: Optional[int] = None, book_id: int = 0, 
                 user_id: int = 0, reservation_date: Optional[datetime] = None,
                 status: str = "pending", notification_sent: bool = False):
        self.reservation_id = reservation_id
        self.book_id = book_id
        self.user_id = user_id
        self.reservation_date = reservation_date or datetime.now()
        self.status = status
        self.notification_sent = notification_sent
    
    @classmethod
    def create_reservation(cls, book_id: int, user_id: int) -> Optional['Reservation']:
        """Create a new reservation."""
        if not db_manager.connected:
            return None
        
        # Check if book exists
        book = Book.get_by_id(book_id)
        if not book:
            logger.error(f"Book not found: {book_id}")
            return None
        
        # Check if user exists and is active
        user = User.get_by_id(user_id)
        if not user or not user.is_active:
            logger.error(f"User not found or inactive: {user_id}")
            return None
        
        # Check if book is available (no need to reserve if available)
        if book.is_available():
            logger.error(f"Book is available, no need to reserve: {book_id}")
            return None
        
        # Check if user already has an active reservation for this book
        existing = db_manager.execute_query(
            "SELECT * FROM reservations WHERE book_id = ? AND user_id = ? AND status = 'pending'",
            (book_id, user_id)
        )
        if existing:
            logger.error(f"User already has reservation for this book: book_id={book_id}, user_id={user_id}")
            return None
        
        # Check if user currently has this book borrowed
        current_lending = db_manager.execute_query(
            "SELECT * FROM lending WHERE book_id = ? AND user_id = ? AND status = 'active'",
            (book_id, user_id)
        )
        if current_lending:
            logger.error(f"User already has this book borrowed: book_id={book_id}, user_id={user_id}")
            return None
        
        # Create reservation
        reservation = cls(
            book_id=book_id,
            user_id=user_id,
            reservation_date=datetime.now(),
            status="pending"
        )
        
        if reservation.save():
            logger.info(f"Reservation created: book_id={book_id}, user_id={user_id}")
            return reservation
        
        return None
    
    @classmethod
    def get_by_id(cls, reservation_id: int) -> Optional['Reservation']:
        """Get reservation by ID."""
        if not db_manager.connected:
            return None
        
        result = db_manager.execute_query(
            "SELECT * FROM reservations WHERE reservation_id = ?", (reservation_id,)
        )
        
        if result and len(result) > 0:
            reservation = cls()
            reservation._load_from_dict(result[0])
            return reservation
        
        return None
    
    @classmethod
    def get_all_reservations(cls, status: str = None) -> List[Dict[str, Any]]:
        """Get all reservations with book and user details."""
        if not db_manager.connected:
            return []
        
        query = """
            SELECT r.*, b.title, b.author, b.isbn, u.name, u.email
            FROM reservations r
            JOIN books b ON r.book_id = b.book_id
            JOIN users u ON r.user_id = u.user_id
        """
        
        params = []
        if status:
            query += " WHERE r.status = ?"
            params.append(status)
        
        query += " ORDER BY r.reservation_date"
        
        result = db_manager.execute_query(query, tuple(params))
        return result if result else []
    
    @classmethod
    def get_user_reservations(cls, user_id: int, active_only: bool = False) -> List[Dict[str, Any]]:
        """Get reservations for a specific user."""
        if not db_manager.connected:
            return []
        
        query = """
            SELECT r.*, b.title, b.author, b.isbn
            FROM reservations r
            JOIN books b ON r.book_id = b.book_id
            WHERE r.user_id = ?
        """
        
        if active_only:
            query += " AND r.status = 'pending'"
        
        query += " ORDER BY r.reservation_date DESC"
        
        result = db_manager.execute_query(query, (user_id,))
        return result if result else []
    
    @classmethod
    def get_book_reservations(cls, book_id: int, pending_only: bool = False) -> List[Dict[str, Any]]:
        """Get reservations for a specific book."""
        if not db_manager.connected:
            return []
        
        query = """
            SELECT r.*, u.name, u.email
            FROM reservations r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.book_id = ?
        """
        
        if pending_only:
            query += " AND r.status = 'pending'"
        
        query += " ORDER BY r.reservation_date"
        
        result = db_manager.execute_query(query, (book_id,))
        return result if result else []
    
    @classmethod
    def get_queue_position(cls, book_id: int, user_id: int) -> Optional[int]:
        """Get user's position in reservation queue for a book."""
        if not db_manager.connected:
            return None
        
        result = db_manager.execute_query("""
            SELECT COUNT(*) as position
            FROM reservations r1
            WHERE r1.book_id = ? 
            AND r1.status = 'pending'
            AND r1.reservation_date < (
                SELECT r2.reservation_date 
                FROM reservations r2 
                WHERE r2.book_id = ? AND r2.user_id = ? AND r2.status = 'pending'
            )
        """, (book_id, book_id, user_id))
        
        if result:
            return result[0]['position'] + 1  # +1 because counting starts from 0
        
        return None
    
    @classmethod
    def get_next_in_queue(cls, book_id: int) -> Optional['Reservation']:
        """Get next reservation in queue for a book."""
        if not db_manager.connected:
            return None
        
        result = db_manager.execute_query("""
            SELECT * FROM reservations 
            WHERE book_id = ? AND status = 'pending'
            ORDER BY reservation_date
            LIMIT 1
        """, (book_id,))
        
        if result:
            reservation = cls()
            reservation._load_from_dict(result[0])
            return reservation
        
        return None
    
    def fulfill(self) -> bool:
        """Mark reservation as fulfilled."""
        if not db_manager.connected or not self.reservation_id:
            return False
        
        if self.status != 'pending':
            logger.error(f"Cannot fulfill reservation with status: {self.status}")
            return False
        
        self.status = 'fulfilled'
        
        if self.save():
            logger.info(f"Reservation fulfilled: {self.reservation_id}")
            return True
        
        return False
    
    def cancel(self) -> bool:
        """Cancel reservation."""
        if not db_manager.connected or not self.reservation_id:
            return False
        
        if self.status != 'pending':
            logger.error(f"Cannot cancel reservation with status: {self.status}")
            return False
        
        self.status = 'cancelled'
        
        if self.save():
            logger.info(f"Reservation cancelled: {self.reservation_id}")
            return True
        
        return False
    
    def notify_user(self, message: str = None) -> bool:
        """Send notification to user about reservation."""
        if not db_manager.connected or not self.reservation_id:
            return False
        
        if not message:
            book = Book.get_by_id(self.book_id)
            book_title = book.title if book else "Unknown Book"
            message = f"Your reserved book '{book_title}' is now available for pickup."
        
        success = db_manager.execute_update("""
            INSERT INTO notifications (user_id, message, type)
            VALUES (?, ?, ?)
        """, (self.user_id, message, "reservation"))
        
        if success:
            # Mark notification as sent
            self.notification_sent = True
            self.save()
            logger.info(f"Notification sent for reservation: {self.reservation_id}")
            return True
        
        return False
    
    def save(self) -> bool:
        """Save reservation to database."""
        if not db_manager.connected:
            return False
        
        try:
            if self.reservation_id is None:  # New reservation
                success = db_manager.execute_update("""
                    INSERT INTO reservations (book_id, user_id, reservation_date, status, notification_sent)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.book_id, self.user_id, self.reservation_date, 
                      self.status, self.notification_sent))
                
                if success:
                    self.reservation_id = db_manager.get_last_insert_id()
                    return True
            else:  # Update existing reservation
                success = db_manager.execute_update("""
                    UPDATE reservations SET book_id = ?, user_id = ?, reservation_date = ?,
                                          status = ?, notification_sent = ?
                    WHERE reservation_id = ?
                """, (self.book_id, self.user_id, self.reservation_date,
                      self.status, self.notification_sent, self.reservation_id))
                
                return success
        
        except Exception as e:
            logger.error(f"Error saving reservation: {e}")
        
        return False
    
    def delete(self) -> bool:
        """Delete reservation."""
        if not db_manager.connected or not self.reservation_id:
            return False
        
        success = db_manager.execute_update(
            "DELETE FROM reservations WHERE reservation_id = ?", (self.reservation_id,)
        )
        
        if success:
            logger.info(f"Reservation deleted: {self.reservation_id}")
        
        return success
    
    def _load_from_dict(self, data: Dict[str, Any]):
        """Load reservation data from dictionary."""
        self.reservation_id = data.get('reservation_id')
        self.book_id = data.get('book_id')
        self.user_id = data.get('user_id')
        
        # Handle datetime field
        reservation_date_str = data.get('reservation_date')
        if reservation_date_str:
            self.reservation_date = datetime.fromisoformat(reservation_date_str)
        
        self.status = data.get('status', 'pending')
        self.notification_sent = bool(data.get('notification_sent', False))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert reservation to dictionary."""
        return {
            'reservation_id': self.reservation_id,
            'book_id': self.book_id,
            'user_id': self.user_id,
            'reservation_date': self.reservation_date.isoformat() if self.reservation_date else None,
            'status': self.status,
            'notification_sent': self.notification_sent
        }
    
    def __str__(self):
        return f"Reservation(id={self.reservation_id}, book_id={self.book_id}, user_id={self.user_id}, status='{self.status}')"
