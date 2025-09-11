# Library Management System

A multi-user library management system built with Python and Tkinter.

## Project Structure

```
LibrarySystem/
│
├── assets/            # Images, icons and other static assets
├── db/                # Database files
├── gui/               # Graphical user interface modules
│   ├── login_screen.py
│   ├── admin_dashboard.py
│   ├── user_dashboard.py
│   └── book_details.py
├── models/            # Data models
│   ├── books.py
│   ├── users.py
│   ├── lending.py
│   └── reservations.py
└── utils/             # Utility functions
    ├── db_connection.py
    ├── logger.py
    └── validators.py
```

## Features

### Admin Features
- User management (add, edit, delete library members)
- Book catalog management (add, edit, delete books)
- Lending and returns processing
- Manage reservation queues
- Generate reports and analytics
- System settings configuration

### User Features
- Browse and search book catalog
- Borrow books and view current loans
- Reserve books that are currently unavailable
- View borrowing history
- Receive notifications for due dates and reservations
- Update personal profile

## Running the Application

### From the Command Line

```bash
# Run from the project root directory
python run.py
```

### Default Login Credentials

- **Admin**: admin@library.com / admin123

## Development

### Adding New Features

1. **GUI Components**: Add new screens and dialogs in the `gui/` directory.
2. **Data Models**: Expand the models in the `models/` directory.
3. **Database Changes**: Update the database schema in `utils/db_connection.py`.

### Code Style Guidelines

- Follow PEP 8 style guidelines
- Use type hints where possible
- Document public functions and classes with docstrings
- Log important events using the logger module

### Testing

The application has built-in error handling and logging. Check the logs in case of unexpected behavior.

## Dependencies

- Python 3.8+
- Tkinter (included in standard Python installation)
- SQLite3 (included in standard Python installation)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
