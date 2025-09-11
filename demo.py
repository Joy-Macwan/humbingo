#!/usr/bin/env python3
"""
Demo script for the Library Management System
This demonstrates the core functionality without requiring a GUI
"""

import os
import sys
from datetime import datetime

def main():
    print("=" * 60)
    print("Library Management System - Demo")
    print("=" * 60)
    
    # Add the project directory to the Python path
    project_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_dir)
    
    # Import modules
    from LibrarySystem.models.users import User
    from LibrarySystem.models.books import Book
    from LibrarySystem.utils.db_connection import db_manager
    from LibrarySystem.utils.logger import logger
    
    # Connect to database
    if not db_manager.connect():
        print("❌ Could not connect to database")
        return False
    
    print("\n📊 Database Status: Connected")
    print(f"📁 Database location: {db_manager.db_path}")
    
    # Demo 1: User Authentication
    print("\n" + "="*40)
    print("Demo 1: User Authentication")
    print("="*40)
    
    # Try to authenticate the default admin
    admin_user = User.authenticate("admin@library.com", "admin123")
    if admin_user:
        print(f"✅ Admin login successful: {admin_user.name} ({admin_user.role})")
    else:
        print("❌ Admin login failed")
    
    # Demo 2: Book Management
    print("\n" + "="*40)
    print("Demo 2: Book Management")
    print("="*40)
    
    # Get all books
    all_books = Book.get_all_books()
    print(f"📚 Total books in catalog: {len(all_books)}")
    
    if all_books:
        print("\n📖 Sample books:")
        for i, book in enumerate(all_books[:3]):  # Show first 3 books
            print(f"   {i+1}. {book.title} by {book.author}")
            print(f"      Category: {book.category}, Available: {book.available_copies}/{book.total_copies}")
    
    # Demo 3: Create a new book (if admin is logged in)
    if admin_user:
        print("\n" + "="*40)
        print("Demo 3: Adding a New Book")
        print("="*40)
        
        # Create a demo book
        demo_book = Book(
            title="Python Programming Guide",
            author="Demo Author",
            isbn="9781234567890",
            category="Programming",
            total_copies=3,
            available_copies=3,
            description="A comprehensive guide to Python programming."
        )
        
        # Try to save it
        if demo_book.save():
            print(f"✅ Book added successfully: {demo_book.title}")
            print(f"   Book ID: {demo_book.book_id}")
        else:
            print("❌ Failed to add book (may already exist)")
    
    # Demo 4: User Management
    print("\n" + "="*40)
    print("Demo 4: User Management")
    print("="*40)
    
    all_users = User.get_all_users()
    print(f"👥 Total users: {len(all_users)}")
    
    print("\n👤 Sample users:")
    for i, user in enumerate(all_users[:3]):  # Show first 3 users
        status = "Active" if user.is_active else "Inactive"
        print(f"   {i+1}. {user.name} ({user.email}) - {user.role.title()} - {status}")
    
    # Demo 5: Search functionality
    print("\n" + "="*40)
    print("Demo 5: Search Functionality")
    print("="*40)
    
    # Search for Python books
    python_books = Book.search_books("Python")
    print(f"🔍 Books containing 'Python': {len(python_books)}")
    
    for book in python_books:
        print(f"   📖 {book.title} by {book.author}")
    
    # Demo 6: Statistics
    print("\n" + "="*40)
    print("Demo 6: System Statistics")
    print("="*40)
    
    # Get categories
    categories = Book.get_categories()
    print(f"📂 Available categories: {', '.join(categories) if categories else 'None'}")
    
    # Get available books
    available_books = Book.get_available_books()
    print(f"📚 Available books: {len(available_books)}")
    
    print("\n" + "="*60)
    print("✅ Demo completed successfully!")
    print("="*60)
    print("\n💡 To run the full GUI application:")
    print("   1. On a system with GUI support, run: python run.py")
    print("   2. Login with: admin@library.com / admin123")
    print("   3. Explore the admin dashboard features")
    print("\n📝 Features demonstrated:")
    print("   ✓ Database connectivity")
    print("   ✓ User authentication")
    print("   ✓ Book management")
    print("   ✓ Search functionality")
    print("   ✓ User management")
    print("   ✓ System statistics")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
