#!/usr/bin/env python3
"""
Text-based Library Management System
This version works in environments without a display server, like dev containers
"""

import os
import sys
from datetime import datetime, timedelta

def main():
    # Setup project path
    project_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_dir)
    
    # Import modules
    from LibrarySystem.models.users import User
    from LibrarySystem.models.books import Book
    from LibrarySystem.utils.db_connection import db_manager
    from LibrarySystem.utils.logger import logger
    
    # Connect to database
    if not db_manager.connect():
        print("❌ Failed to connect to database.")
        return False
    
    print("\n" + "="*60)
    print("📚 LIBRARY MANAGEMENT SYSTEM - TEXT MODE")
    print("="*60)
    
    # Authenticate user
    current_user = None
    while not current_user:
        print("\n🔐 Login")
        email = input("Email (default: admin@library.com): ").strip() or "admin@library.com"
        password = input("Password (default: admin123): ").strip() or "admin123"
        
        current_user = User.authenticate(email, password)
        if not current_user:
            print("❌ Authentication failed. Please try again.")
    
    print(f"\n✅ Login successful! Welcome, {current_user.name} ({current_user.role})")
    
    # Main menu loop
    while True:
        print("\n" + "="*60)
        print(f"👤 Logged in as: {current_user.name} ({current_user.role})")
        print("="*60)
        
        # Display menu based on user role
        if current_user.role == "admin":
            print_admin_menu()
            choice = input("\nSelect an option (0-9): ").strip()
            
            if choice == '0':
                print("\n👋 Logging out. Goodbye!")
                break
            elif choice == '1':
                view_all_books()
            elif choice == '2':
                add_book()
            elif choice == '3':
                search_books()
            elif choice == '4':
                view_all_users()
            elif choice == '5':
                add_user()
            elif choice == '6':
                view_book_lendings()
            elif choice == '7':
                issue_book()
            elif choice == '8':
                return_book()
            elif choice == '9':
                view_system_statistics()
            else:
                print("❌ Invalid option. Please try again.")
        else:
            print_user_menu()
            choice = input("\nSelect an option (0-5): ").strip()
            
            if choice == '0':
                print("\n👋 Logging out. Goodbye!")
                break
            elif choice == '1':
                view_all_books()
            elif choice == '2':
                search_books()
            elif choice == '3':
                view_my_books(current_user)
            elif choice == '4':
                view_my_reservations(current_user)
            elif choice == '5':
                update_profile(current_user)
            else:
                print("❌ Invalid option. Please try again.")
    
    return True

def print_admin_menu():
    print("\n📋 ADMIN MENU:")
    print("1. View All Books")
    print("2. Add New Book")
    print("3. Search Books")
    print("4. View All Users")
    print("5. Add New User")
    print("6. View Book Lendings")
    print("7. Issue Book")
    print("8. Return Book")
    print("9. System Statistics")
    print("0. Logout")

def print_user_menu():
    print("\n📋 USER MENU:")
    print("1. View All Books")
    print("2. Search Books")
    print("3. My Borrowed Books")
    print("4. My Reservations")
    print("5. Update Profile")
    print("0. Logout")

def view_all_books():
    from LibrarySystem.models.books import Book
    
    print("\n" + "="*60)
    print("📚 ALL BOOKS")
    print("="*60)
    
    books = Book.get_all_books()
    if not books:
        print("No books found in the catalog.")
        return
    
    print(f"Found {len(books)} books:")
    for i, book in enumerate(books, 1):
        status = "Available" if book.available_copies > 0 else "Not Available"
        print(f"{i}. {book.title} by {book.author}")
        print(f"   ID: {book.book_id} | ISBN: {book.isbn} | Category: {book.category}")
        print(f"   Copies: {book.available_copies}/{book.total_copies} | Status: {status}")
        if book.description:
            print(f"   Description: {book.description[:100]}..." if len(book.description) > 100 else f"   Description: {book.description}")
        print()
    
    input("Press Enter to continue...")

def add_book():
    from LibrarySystem.models.books import Book
    from LibrarySystem.utils.logger import logger
    
    print("\n" + "="*60)
    print("📕 ADD NEW BOOK")
    print("="*60)
    
    title = input("Title: ").strip()
    if not title:
        print("❌ Title is required.")
        return
    
    author = input("Author: ").strip()
    if not author:
        print("❌ Author is required.")
        return
    
    isbn = input("ISBN: ").strip()
    if not isbn:
        print("❌ ISBN is required.")
        return
    
    category = input("Category: ").strip()
    if not category:
        print("❌ Category is required.")
        return
    
    try:
        total_copies = int(input("Total Copies: ").strip() or "1")
        if total_copies < 1:
            print("❌ Total copies must be at least 1.")
            return
        
        available_copies = total_copies
    except ValueError:
        print("❌ Invalid number for copies.")
        return
    
    description = input("Description (optional): ").strip()
    
    # Create and save book
    book = Book(
        title=title,
        author=author,
        isbn=isbn,
        category=category,
        total_copies=total_copies,
        available_copies=available_copies,
        description=description
    )
    
    if book.save():
        print(f"\n✅ Book '{title}' added successfully!")
    else:
        print("\n❌ Failed to add book. Check if the ISBN already exists.")

def search_books():
    from LibrarySystem.models.books import Book
    
    print("\n" + "="*60)
    print("🔍 SEARCH BOOKS")
    print("="*60)
    
    search_term = input("Enter search term (title, author, or category): ").strip()
    if not search_term:
        print("❌ Search term is required.")
        return
    
    books = Book.search_books(search_term)
    
    if not books:
        print(f"No books found matching '{search_term}'.")
        return
    
    print(f"Found {len(books)} books matching '{search_term}':")
    for i, book in enumerate(books, 1):
        status = "Available" if book.available_copies > 0 else "Not Available"
        print(f"{i}. {book.title} by {book.author}")
        print(f"   ID: {book.book_id} | ISBN: {book.isbn} | Category: {book.category}")
        print(f"   Copies: {book.available_copies}/{book.total_copies} | Status: {status}")
        print()
    
    input("Press Enter to continue...")

def view_all_users():
    from LibrarySystem.models.users import User
    
    print("\n" + "="*60)
    print("👥 ALL USERS")
    print("="*60)
    
    users = User.get_all_users(include_inactive=True)
    
    if not users:
        print("No users found.")
        return
    
    print(f"Found {len(users)} users:")
    for i, user in enumerate(users, 1):
        status = "Active" if user.is_active else "Inactive"
        print(f"{i}. {user.name} ({user.email})")
        print(f"   ID: {user.user_id} | Role: {user.role.title()} | Status: {status}")
        print()
    
    input("Press Enter to continue...")

def add_user():
    from LibrarySystem.models.users import User
    from LibrarySystem.utils.validators import validators
    
    print("\n" + "="*60)
    print("👤 ADD NEW USER")
    print("="*60)
    
    name = input("Name: ").strip()
    if not name:
        print("❌ Name is required.")
        return
    
    email = input("Email: ").strip()
    if not email:
        print("❌ Email is required.")
        return
    
    is_valid, error_msg = validators.validate_email(email)
    if not is_valid:
        print(f"❌ {error_msg}")
        return
    
    role = input("Role (admin/user, default: user): ").strip().lower() or "user"
    if role not in ["admin", "user"]:
        print("❌ Role must be 'admin' or 'user'.")
        return
    
    password = input("Password: ").strip()
    if not password:
        print("❌ Password is required.")
        return
    
    is_valid, error_msg = validators.validate_password(password)
    if not is_valid:
        print(f"❌ {error_msg}")
        return
    
    # Create and save user
    user = User(
        name=name,
        email=email,
        role=role
    )
    
    if user.save(password=password):
        print(f"\n✅ User '{name}' added successfully!")
    else:
        print("\n❌ Failed to add user. Check if the email already exists.")

def view_book_lendings():
    from LibrarySystem.models.lending import Lending
    
    print("\n" + "="*60)
    print("📖 BOOK LENDINGS")
    print("="*60)
    
    status = input("Filter by status (active/returned/all, default: active): ").strip().lower() or "active"
    
    if status == "all":
        lendings = Lending.get_all_lendings()
    else:
        lendings = Lending.get_lendings_by_status(status)
    
    if not lendings:
        print(f"No {status} lendings found.")
        return
    
    print(f"Found {len(lendings)} {status} lendings:")
    for i, lending in enumerate(lendings, 1):
        due_date_str = lending.due_date.strftime("%Y-%m-%d") if lending.due_date else "N/A"
        return_date_str = lending.return_date.strftime("%Y-%m-%d") if lending.return_date else "Not returned"
        
        print(f"{i}. Lending ID: {lending.lending_id}")
        print(f"   Book ID: {lending.book_id} | User ID: {lending.user_id}")
        print(f"   Issue Date: {lending.issue_date.strftime('%Y-%m-%d')}")
        print(f"   Due Date: {due_date_str} | Return Date: {return_date_str}")
        print(f"   Status: {lending.status}")
        
        if lending.status == "active" and lending.is_overdue():
            days = lending.days_overdue()
            print(f"   ⚠ Overdue by {days} days")
        
        print()
    
    input("Press Enter to continue...")

def issue_book():
    from LibrarySystem.models.lending import Lending
    from LibrarySystem.models.books import Book
    from LibrarySystem.models.users import User
    
    print("\n" + "="*60)
    print("📚 ISSUE BOOK")
    print("="*60)
    
    # Get book
    book_id = input("Book ID: ").strip()
    if not book_id:
        print("❌ Book ID is required.")
        return
    
    try:
        book_id = int(book_id)
    except ValueError:
        print("❌ Book ID must be a number.")
        return
    
    book = Book.get_by_id(book_id)
    if not book:
        print(f"❌ Book with ID {book_id} not found.")
        return
    
    if not book.is_available():
        print(f"❌ Book '{book.title}' is not available for lending.")
        return
    
    # Get user
    user_id = input("User ID: ").strip()
    if not user_id:
        print("❌ User ID is required.")
        return
    
    try:
        user_id = int(user_id)
    except ValueError:
        print("❌ User ID must be a number.")
        return
    
    user = User.get_by_id(user_id)
    if not user:
        print(f"❌ User with ID {user_id} not found.")
        return
    
    if not user.is_active:
        print(f"❌ User '{user.name}' is inactive.")
        return
    
    # Create lending
    days = input("Loan period in days (default: 14): ").strip() or "14"
    try:
        days = int(days)
        if days < 1:
            print("❌ Loan period must be at least 1 day.")
            return
    except ValueError:
        print("❌ Invalid number of days.")
        return
    
    issue_date = datetime.now()
    due_date = issue_date + timedelta(days=days)
    
    lending = Lending(
        book_id=book_id,
        user_id=user_id,
        issue_date=issue_date,
        due_date=due_date,
        status="active"
    )
    
    if lending.save():
        # Update book availability
        book.update_availability(-1)
        print(f"\n✅ Book '{book.title}' issued to {user.name}.")
        print(f"   Due date: {due_date.strftime('%Y-%m-%d')}")
    else:
        print("\n❌ Failed to issue book.")

def return_book():
    from LibrarySystem.models.lending import Lending
    from LibrarySystem.models.books import Book
    
    print("\n" + "="*60)
    print("📚 RETURN BOOK")
    print("="*60)
    
    lending_id = input("Lending ID: ").strip()
    if not lending_id:
        print("❌ Lending ID is required.")
        return
    
    try:
        lending_id = int(lending_id)
    except ValueError:
        print("❌ Lending ID must be a number.")
        return
    
    lending = Lending.get_by_id(lending_id)
    if not lending:
        print(f"❌ Lending with ID {lending_id} not found.")
        return
    
    if lending.status != "active":
        print(f"❌ Lending is not active (status: {lending.status}).")
        return
    
    # Process return
    lending.return_date = datetime.now()
    lending.status = "returned"
    
    if lending.save():
        # Update book availability
        book = Book.get_by_id(lending.book_id)
        if book:
            book.update_availability(1)
        
        print(f"\n✅ Book returned successfully.")
        
        # Check if overdue
        if lending.is_overdue():
            days = lending.days_overdue()
            fine = lending.calculate_fine()
            print(f"⚠ Book was overdue by {days} days.")
            print(f"⚠ Fine amount: ${fine:.2f}")
    else:
        print("\n❌ Failed to process return.")

def view_system_statistics():
    from LibrarySystem.models.books import Book
    from LibrarySystem.models.users import User
    from LibrarySystem.models.lending import Lending
    from LibrarySystem.models.reservations import Reservation
    
    print("\n" + "="*60)
    print("📊 SYSTEM STATISTICS")
    print("="*60)
    
    # Book statistics
    books = Book.get_all_books()
    available_books = Book.get_available_books()
    categories = Book.get_categories()
    
    print(f"📚 Books: {len(books)} total, {len(available_books)} available")
    print(f"📂 Categories: {', '.join(categories)}")
    
    # User statistics
    users = User.get_all_users()
    admin_users = [u for u in users if u.role == "admin"]
    
    print(f"👥 Users: {len(users)} total, {len(admin_users)} admins")
    
    # Lending statistics
    active_lendings = Lending.get_lendings_by_status("active")
    overdue_lendings = [l for l in active_lendings if l.is_overdue()]
    
    print(f"📖 Active Lendings: {len(active_lendings)}, {len(overdue_lendings)} overdue")
    
    # Reservation statistics
    pending_reservations = Reservation.get_all_reservations("pending")
    
    print(f"🔖 Pending Reservations: {len(pending_reservations)}")
    
    # Most popular books
    popular_books = Book.get_popular_books(5)
    if popular_books:
        print("\n📈 Most Popular Books:")
        for i, book_data in enumerate(popular_books, 1):
            print(f"{i}. {book_data['title']} - Borrowed {book_data['borrow_count']} times")
    
    input("\nPress Enter to continue...")

def view_my_books(user):
    from LibrarySystem.models.books import Book
    
    print("\n" + "="*60)
    print("📚 MY BORROWED BOOKS")
    print("="*60)
    
    borrowed_books = user.get_borrowed_books()
    
    if not borrowed_books:
        print("You have no borrowed books.")
        return
    
    print(f"You have {len(borrowed_books)} borrowed books:")
    for i, book_data in enumerate(borrowed_books, 1):
        due_date = book_data.get('due_date', 'N/A')
        is_overdue = book_data.get('is_overdue', False)
        
        print(f"{i}. {book_data['title']} by {book_data['author']}")
        print(f"   Due Date: {due_date}")
        
        if is_overdue:
            print(f"   ⚠ OVERDUE")
        
        print()
    
    input("Press Enter to continue...")

def view_my_reservations(user):
    from LibrarySystem.models.books import Book
    
    print("\n" + "="*60)
    print("🔖 MY RESERVATIONS")
    print("="*60)
    
    reservations = user.get_reservations()
    
    if not reservations:
        print("You have no reservations.")
        return
    
    print(f"You have {len(reservations)} reservations:")
    for i, res_data in enumerate(reservations, 1):
        status = res_data.get('status', 'Unknown')
        reservation_date = res_data.get('reservation_date', 'Unknown')
        
        print(f"{i}. {res_data['title']} by {res_data['author']}")
        print(f"   Status: {status.title()}")
        print(f"   Reserved on: {reservation_date}")
        
        if status == 'ready':
            print(f"   ✅ Book is available for pickup!")
        
        print()
    
    input("Press Enter to continue...")

def update_profile(user):
    from LibrarySystem.utils.validators import validators
    
    print("\n" + "="*60)
    print("👤 UPDATE PROFILE")
    print("="*60)
    
    print(f"Current Name: {user.name}")
    print(f"Current Email: {user.email}")
    print(f"Current Role: {user.role.title()}")
    print()
    
    name = input("New Name (leave empty to keep current): ").strip()
    if name:
        user.name = name
    
    change_password = input("Change password? (y/n): ").strip().lower() == 'y'
    if change_password:
        password = input("New Password: ").strip()
        if not password:
            print("❌ Password cannot be empty.")
        else:
            is_valid, error_msg = validators.validate_password(password)
            if not is_valid:
                print(f"❌ {error_msg}")
            else:
                if user.change_password(password):
                    print("✅ Password changed successfully!")
                else:
                    print("❌ Failed to change password.")
    
    if name:
        if user.save():
            print("✅ Profile updated successfully!")
        else:
            print("❌ Failed to update profile.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program terminated by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
