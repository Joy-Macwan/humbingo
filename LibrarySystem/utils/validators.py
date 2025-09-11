import re
from typing import Tuple, Optional
from datetime import datetime

class Validators:
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format."""
        if not email:
            return False, "Email is required"
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        return True, ""
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """Validate password strength."""
        if not password:
            return False, "Password is required"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        return True, ""
    
    @staticmethod
    def validate_isbn(isbn: str) -> Tuple[bool, str]:
        """Validate ISBN format."""
        if not isbn:
            return True, ""  # ISBN is optional
        
        # Remove hyphens and spaces
        isbn_clean = re.sub(r'[-\s]', '', isbn)
        
        # Check if it's 10 or 13 digits
        if not (len(isbn_clean) in [10, 13] and isbn_clean.replace('X', '').isdigit()):
            return False, "ISBN must be 10 or 13 digits (may contain hyphens and spaces)"
        
        return True, ""
    
    @staticmethod
    def validate_required_field(value: str, field_name: str) -> Tuple[bool, str]:
        """Validate that a required field is not empty."""
        if not value or not value.strip():
            return False, f"{field_name} is required"
        return True, ""
    
    @staticmethod
    def validate_positive_integer(value: str, field_name: str) -> Tuple[bool, str]:
        """Validate that a value is a positive integer."""
        try:
            int_value = int(value)
            if int_value <= 0:
                return False, f"{field_name} must be a positive number"
            return True, ""
        except ValueError:
            return False, f"{field_name} must be a valid number"
    
    @staticmethod
    def validate_date(date_str: str, field_name: str) -> Tuple[bool, str]:
        """Validate date format (YYYY-MM-DD)."""
        if not date_str:
            return False, f"{field_name} is required"
        
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True, ""
        except ValueError:
            return False, f"{field_name} must be in YYYY-MM-DD format"
    
    @staticmethod
    def validate_role(role: str) -> Tuple[bool, str]:
        """Validate user role."""
        valid_roles = ['admin', 'user']
        if role not in valid_roles:
            return False, f"Role must be one of: {', '.join(valid_roles)}"
        return True, ""

# Global validator instance
validators = Validators()
