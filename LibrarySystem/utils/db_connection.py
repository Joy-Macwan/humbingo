import sqlite3
import os
import hashlib
from datetime import datetime
from typing import Optional, Union, List, Dict, Any

class DatabaseManager:
    def __init__(self, db_path: str = "db/library.db"):
        self.db_path = db_path
        self.connection = None
        self.connected = False
        
    def connect(self) -> bool:
        """Establish database connection and create tables if needed."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            self.connected = True
            
            # Enable foreign key constraints
            self.connection.execute("PRAGMA foreign_keys = ON")
            
            # Create tables
            self._create_tables()
            self._create_default_admin()
            
            return True
            
        except Exception as e:
            print(f"Database connection failed: {e}")
            self.connected = False
            return False
    
    def _create_tables(self):
        """Create all necessary tables."""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('admin', 'user')),
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE,
                category TEXT,
                total_copies INTEGER DEFAULT 1,
                available_copies INTEGER DEFAULT 1,
                description TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS lending (
                lending_id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                user_id INTEGER,
                issue_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                due_date DATETIME NOT NULL,
                return_date DATETIME,
                fine_amount DECIMAL(10,2) DEFAULT 0,
                status TEXT DEFAULT 'active' CHECK (status IN ('active', 'returned', 'overdue')),
                FOREIGN KEY (book_id) REFERENCES books (book_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS reservations (
                reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                user_id INTEGER,
                reservation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'fulfilled', 'cancelled')),
                notification_sent BOOLEAN DEFAULT 0,
                FOREIGN KEY (book_id) REFERENCES books (book_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message TEXT NOT NULL,
                type TEXT DEFAULT 'info' CHECK (type IN ('info', 'warning', 'overdue', 'reservation')),
                is_read BOOLEAN DEFAULT 0,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL,
                updated_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        for table_sql in tables:
            self.connection.execute(table_sql)
        
        self.connection.commit()
    
    def _create_default_admin(self):
        """Create default admin user if none exists."""
        cursor = self.connection.execute(
            "SELECT COUNT(*) as count FROM users WHERE role = 'admin'"
        )
        admin_count = cursor.fetchone()['count']
        
        if admin_count == 0:
            admin_password = self.hash_password("admin123")
            self.connection.execute("""
                INSERT INTO users (name, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            """, ("Administrator", "admin@library.com", admin_password, "admin"))
            self.connection.commit()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def execute_query(self, query: str, params: tuple = ()) -> Optional[List[Dict]]:
        """Execute a SELECT query and return results."""
        if not self.connected:
            return None
        
        try:
            cursor = self.connection.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Query execution failed: {e}")
            return None
    
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """Execute INSERT, UPDATE, or DELETE query."""
        if not self.connected:
            return False
        
        try:
            cursor = self.connection.execute(query, params)
            self.connection.commit()
            self.last_cursor = cursor  # Store for lastrowid access
            return True
        except Exception as e:
            print(f"Update execution failed: {e}")
            return False
    
    def get_last_insert_id(self) -> Optional[int]:
        """Get the ID of the last inserted row."""
        if not self.connected:
            return None
        if hasattr(self, 'last_cursor') and self.last_cursor:
            return self.last_cursor.lastrowid
        return self.connection.lastrowid
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connected = False

# Global database instance
db_manager = DatabaseManager()
