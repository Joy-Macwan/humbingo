
# 📚 Library Management System

A comprehensive library management system with book catalog, user management, lending, and reservation features.

## 📖 Project Description

The **Library Management System** is an application designed to manage library resources efficiently with multiple user roles (Admin and User). It handles book lending, returns, overdue alerts, reservations, and report generation. The multi-user capability ensures that administrators can manage the system, while users can borrow/reserve books and view their history.

## ✨ Features

- **User Authentication**: Role-based access (Admin/User)
- **Book Catalog Management**: Add, edit, search, and remove books
- **Lending System**: Issue books, track due dates, and process returns
- **Reservation System**: Queue reservations for unavailable books
- **Fine Calculation**: Automatic calculation for overdue books
- **User Notifications**: Alerts for overdue books and available reservations
- **Detailed Statistics**: Track popular books and user activity
- **Text-Based Interface**: Works in environments without display servers

## 💻 Running the Application

### Text Mode (No GUI required)

```bash
./run_text_mode.sh
```

or

```bash
python library_cli.py
```

### GUI Mode (Requires display server)

```bash
python main.py
```

## 🔐 Default Login

- **Admin**
  - Email: admin@library.com
  - Password: admin123

## 🧩 Project Structure

---

## 🧩 Project Structure

```
LibrarySystem/
├── assets/           # Images and static files
├── db/               # Database files
├── gui/              # GUI components
│   ├── login_screen.py
│   └── other GUI components
├── models/           # Data models
│   ├── books.py      # Book management
│   ├── lending.py    # Lending operations
│   ├── reservations.py # Reservation system
│   └── users.py      # User authentication
└── utils/            # Utility functions
    ├── db_connection.py # Database connectivity
    ├── logger.py     # Logging functionality
    └── validators.py # Input validation
```

## � Database Schema

- **users**: User accounts and authentication
- **books**: Book catalog information
- **lending**: Book lending records
- **reservations**: Book reservation queue
- **notifications**: User notifications

## 🔍 Running in Different Environments

### Dev Container / Docker / WSL

In environments without a display server, use the text-based interface:

```bash
./run_text_mode.sh
```

### Desktop Environment

In environments with a display server, use the GUI interface:

```bash
python main.py
```

## 🛠️ API Overview

### User Management

The `User` class provides methods for:
- User authentication and creation
- Profile management
- Book lending history

### Book Management

The `Book` class handles:
- Adding and updating books
- Searching and filtering
- Availability tracking

### Lending System

The `Lending` class manages:
- Book checkout and return
- Due date tracking
- Fine calculation

### Reservation System

The `Reservation` class handles:
- Book reservation queue
- Notifications for available books

## 📝 Development Notes

This application uses:
- Python 3.8+ for core functionality
- SQLite for database storage
- Clean architecture with separation of concerns
- Text-based interface for headless environments

## 📄 License

This project is licensed under the MIT License

### Directory Structure

```
LibrarySystem/
│
├── assets/            # Images, icons and other static assets
├── db/                # Database files
├── gui/               # Graphical user interface modules
├── models/            # Data models
└── utils/             # Utility functions
```

### Extending the Application

The application is designed to be modular and extensible. See the developer documentation in the LibrarySystem directory for more details.

---

## 📜 **License**

This project is licensed under the MIT License.




Here’s a **complete module breakdown** and **feature set** for your **Library System with Multi-User Support**, covering both **Admin** and **Client (User)** sides for a **fully functional desktop application** using **Python + Tkinter + SQLite**. I’ve also included behavior when the database isn’t connected and exception handling guidelines.

---

## 📑 **Modules and Features**

### 1️⃣ **Admin Modules (Librarian Role)**

| Module                         | Features                                                                                                                                                            |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Authentication & Dashboard** | • Secure login/logout<br>• View quick stats: total books, borrowed books, overdue, active users                                                                     |
| **User Management**            | • Add/Edit/Delete library members<br>• Assign/revoke roles<br>• Search/filter users<br>• Reset passwords                                                            |
| **Book Catalog Management**    | • Add/Edit/Delete books (title, author, ISBN, category, availability)<br>• Upload cover images (optional)<br>• Bulk import/export (CSV)<br>• Advanced search/filter |
| **Lending & Returns**          | • Issue books to users with due dates<br>• Process returns and calculate overdue fines (optional)<br>• Handle damaged/lost book records                             |
| **Reservation Queue**          | • View/manage reservation queues<br>• Approve or reject reservations<br>• Notify next user in queue                                                                 |
| **Overdue Alerts**             | • View overdue books and borrower details<br>• Send reminders (in-app notification or email placeholder)                                                            |
| **Reports & Analytics**        | • Generate and export reports (PDF/CSV)<br>• Popular books and active borrowers<br>• Monthly/weekly lending statistics                                              |
| **Settings & Backup**          | • Configure system settings (loan duration, fine rules)<br>• Backup/restore database<br>• Change admin password                                                     |
| **Error Logs & Audit**         | • View exception logs for debugging<br>• Audit trail for critical operations                                                                                        |

---

### 2️⃣ **Client (User) Modules**

| Module                          | Features                                                                                                          |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Authentication & Profile**    | • Login/logout<br>• View/edit personal profile<br>• Change password                                               |
| **Browse/Search Catalog**       | • Search books by title, author, category<br>• Filter by availability<br>• View book details (cover, description) |
| **Borrowing & Lending History** | • Borrow books (if available)<br>• View current loans with due dates<br>• View full borrowing history             |
| **Reservations**                | • Reserve unavailable books<br>• Cancel reservations<br>• Get notified when a reserved book is available          |
| **Notifications**               | • See overdue alerts, reservation status, and system announcements                                                |
| **Feedback & Support**          | • Submit feedback or support requests (stored locally or emailed later)                                           |

---

## 🏗 **System Behavior**

1. **Normal Mode (Database Connected)**

   * All modules fully functional.
   * CRUD operations persist to SQLite database.

2. **Offline Mode (Database Not Connected)**

   * Application starts in **GUI-only mode** with a banner: “⚠ Database not connected—view only mode.”
   * Show static placeholders for books/users (non-editable).
   * Disable all actions like Add/Edit/Delete/Issue/Reserve.

---

## 🧰 **Exception Handling Strategy**

| Area                | Exception Type                                      | Handling Strategy                                                                                  |
| ------------------- | --------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Database Connection | `sqlite3.OperationalError`, `sqlite3.DatabaseError` | Show warning dialog, switch to offline mode, log error to `error.log`.                             |
| CRUD Operations     | Integrity or foreign key errors                     | Show user-friendly message (“Cannot delete book: active loans exist.”)                             |
| User Input          | Invalid formats (e.g., ISBN not numeric)            | Validate before submission, highlight the field, show error label.                                 |
| File Operations     | Missing CSV/backup files                            | Use `try-except`, show “File not found” alert.                                                     |
| General App Errors  | Unexpected exceptions                               | Use a global error handler (`sys.excepthook`) to log stack traces and show a generic error dialog. |

---

## 📂 **Suggested Directory Structure**

```
LibrarySystem/
│
├── main.py                # Entry point
├── db/
│   └── library.db         # SQLite database
├── gui/
│   ├── admin_dashboard.py
│   ├── user_dashboard.py
│   ├── login_screen.py
│   ├── book_forms.py
│   └── error_dialogs.py
├── models/
│   ├── books.py
│   ├── users.py
│   ├── lending.py
│   └── reservations.py
├── utils/
│   ├── db_connection.py   # Handles DB connection & fallback
│   ├── validators.py
│   └── logger.py
└── assets/
    └── icons/             # Optional images/icons
```

---

## 🗄 **Database Schema (Core Tables)**

1. **Users**: `user_id`, `name`, `role (admin/user)`, `email`, `password_hash`.
2. **Books**: `book_id`, `title`, `author`, `category`, `isbn`, `availability`.
3. **Lending**: `lending_id`, `book_id`, `user_id`, `issue_date`, `due_date`, `return_date`.
4. **Reservations**: `reservation_id`, `book_id`, `user_id`, `reservation_date`, `status`.
5. **Notifications**: `notif_id`, `user_id`, `message`, `status`.

---

## 🚀 **Key Features for a Full Website-Like Experience (Tkinter Desktop)**

* **Tabbed UI or Multiple Windows**: Use `ttk.Notebook` or multi-window design for Admin/User dashboards.
* **Responsive Design**: Dynamically resize widgets for different screens.
* **Search Bars & Filters**: Use Tkinter `Entry` and `ttk.Treeview`.
* **Pagination for Large Data**: Handle large book catalogs gracefully.
* **Report Export**: Use `csv` or `reportlab` for report generation.
* **Modular Code**: Makes it easy to expand later (e.g., email integration or cloud sync).

---

Would you like me to **generate a starter Tkinter code template** (with login, database connection handling, and placeholder dashboards for Admin and User) so you can expand it into a full application?
