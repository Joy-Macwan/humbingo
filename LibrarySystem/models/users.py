from typing import Optional, List, Dict, Any
from datetime import datetime
from LibrarySystem.utils.db_connection import db_manager
from LibrarySystem.utils.validators import validators
from LibrarySystem.utils.logger import logger

class User:
    def __init__(self, user_id: Optional[int] = None, name: str = "", 
                 email: str = "", role: str = "user", is_active: bool = True):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role
        self.is_active = is_active
        self.created_date = None
    
    @classmethod
    def authenticate(cls, email: str, password: str) -> Optional['User']:
        """Authenticate user with email and password."""
        if not db_manager.connected:
            return None
        
        password_hash = db_manager.hash_password(password)
        
        result = db_manager.execute_query(
            "SELECT * FROM users WHERE email = ? AND password_hash = ? AND is_active = 1",
            (email, password_hash)
        )
        
        if result and len(result) > 0:
            user_data = result[0]
            user = cls()
            user._load_from_dict(user_data)
            logger.info(f"User authenticated: {email}")
            return user
        
        logger.warning(f"Authentication failed for: {email}")
        return None
    
    @classmethod
    def get_by_id(cls, user_id: int) -> Optional['User']:
        """Get user by ID."""
        if not db_manager.connected:
            return None
        
        result = db_manager.execute_query(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        
        if result and len(result) > 0:
            user = cls()
            user._load_from_dict(result[0])
            return user
        
        return None
    
    @classmethod
    def get_all_users(cls, include_inactive: bool = False) -> List['User']:
        """Get all users."""
        if not db_manager.connected:
            return []
        
        query = "SELECT * FROM users"
        if not include_inactive:
            query += " WHERE is_active = 1"
        query += " ORDER BY name"
        
        result = db_manager.execute_query(query)
        users = []
        
        if result:
            for user_data in result:
                user = cls()
                user._load_from_dict(user_data)
                users.append(user)
        
        return users
    
    @classmethod
    def search_users(cls, search_term: str) -> List['User']:
        """Search users by name or email."""
        if not db_manager.connected:
            return []
        
        search_pattern = f"%{search_term}%"
        result = db_manager.execute_query(
            "SELECT * FROM users WHERE (name LIKE ? OR email LIKE ?) AND is_active = 1 ORDER BY name",
            (search_pattern, search_pattern)
        )
        
        users = []
        if result:
            for user_data in result:
                user = cls()
                user._load_from_dict(user_data)
                users.append(user)
        
        return users
    
    def save(self, password: Optional[str] = None) -> bool:
        """Save user to database."""
        if not db_manager.connected:
            return False
        
        # Validate data
        is_valid, error_msg = self._validate()
        if not is_valid:
            logger.error(f"User validation failed: {error_msg}")
            return False
        
        try:
            if self.user_id is None:  # New user
                if not password:
                    logger.error("Password required for new user")
                    return False
                
                password_hash = db_manager.hash_password(password)
                
                # Check if email already exists
                existing = db_manager.execute_query(
                    "SELECT user_id FROM users WHERE email = ?", (self.email,)
                )
                if existing:
                    logger.error(f"Email already exists: {self.email}")
                    return False
                
                success = db_manager.execute_update(
                    "INSERT INTO users (name, email, password_hash, role, is_active) VALUES (?, ?, ?, ?, ?)",
                    (self.name, self.email, password_hash, self.role, self.is_active)
                )
                
                if success:
                    self.user_id = db_manager.get_last_insert_id()
                    logger.info(f"New user created: {self.email}")
                    return True
            else:  # Update existing user
                success = db_manager.execute_update(
                    "UPDATE users SET name = ?, email = ?, role = ?, is_active = ? WHERE user_id = ?",
                    (self.name, self.email, self.role, self.is_active, self.user_id)
                )
                
                if success:
                    logger.info(f"User updated: {self.email}")
                    return True
        
        except Exception as e:
            logger.error(f"Error saving user: {e}")
        
        return False
    
    def change_password(self, new_password: str) -> bool:
        """Change user password."""
        if not db_manager.connected or not self.user_id:
            return False
        
        is_valid, error_msg = validators.validate_password(new_password)
        if not is_valid:
            logger.error(f"Password validation failed: {error_msg}")
            return False
        
        password_hash = db_manager.hash_password(new_password)
        success = db_manager.execute_update(
            "UPDATE users SET password_hash = ? WHERE user_id = ?",
            (password_hash, self.user_id)
        )
        
        if success:
            logger.info(f"Password changed for user: {self.email}")
        
        return success
    
    def delete(self) -> bool:
        """Soft delete user (set inactive)."""
        if not db_manager.connected or not self.user_id:
            return False
        
        # Check if user has active lendings
        active_lendings = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM lending WHERE user_id = ? AND status = 'active'",
            (self.user_id,)
        )
        
        if active_lendings and active_lendings[0]['count'] > 0:
            logger.error(f"Cannot delete user with active lendings: {self.email}")
            return False
        
        success = db_manager.execute_update(
            "UPDATE users SET is_active = 0 WHERE user_id = ?",
            (self.user_id,)
        )
        
        if success:
            self.is_active = False
            logger.info(f"User deactivated: {self.email}")
        
        return success
    
    def get_borrowed_books(self) -> List[Dict[str, Any]]:
        """Get list of currently borrowed books."""
        if not db_manager.connected or not self.user_id:
            return []
        
        result = db_manager.execute_query("""
            SELECT l.*, b.title, b.author, b.isbn 
            FROM lending l
            JOIN books b ON l.book_id = b.book_id
            WHERE l.user_id = ? AND l.status = 'active'
            ORDER BY l.due_date
        """, (self.user_id,))
        
        return result if result else []
    
    def get_reservations(self) -> List[Dict[str, Any]]:
        """Get list of current reservations."""
        if not db_manager.connected or not self.user_id:
            return []
        
        result = db_manager.execute_query("""
            SELECT r.*, b.title, b.author, b.isbn 
            FROM reservations r
            JOIN books b ON r.book_id = b.book_id
            WHERE r.user_id = ? AND r.status = 'pending'
            ORDER BY r.reservation_date
        """, (self.user_id,))
        
        return result if result else []
    
    def get_notifications(self, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get user notifications."""
        if not db_manager.connected or not self.user_id:
            return []
        
        query = "SELECT * FROM notifications WHERE user_id = ?"
        if unread_only:
            query += " AND is_read = 0"
        query += " ORDER BY created_date DESC"
        
        result = db_manager.execute_query(query, (self.user_id,))
        return result if result else []
    
    def _validate(self) -> tuple[bool, str]:
        """Validate user data."""
        is_valid, error_msg = validators.validate_required_field(self.name, "Name")
        if not is_valid:
            return False, error_msg
        
        is_valid, error_msg = validators.validate_email(self.email)
        if not is_valid:
            return False, error_msg
        
        is_valid, error_msg = validators.validate_role(self.role)
        if not is_valid:
            return False, error_msg
        
        return True, ""
    
    def _load_from_dict(self, data: Dict[str, Any]):
        """Load user data from dictionary."""
        self.user_id = data.get('user_id')
        self.name = data.get('name', '')
        self.email = data.get('email', '')
        self.role = data.get('role', 'user')
        self.is_active = bool(data.get('is_active', True))
        self.created_date = data.get('created_date')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_date': self.created_date
        }
    
    def __str__(self):
        return f"User(id={self.user_id}, name='{self.name}', email='{self.email}', role='{self.role}')"
