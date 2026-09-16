# Expense Tracker

A desktop expense management application built with **Python**, **Tkinter**, and **SQLite**.

## Features

* Add new expenses
* Edit existing expenses
* Delete expenses
* Persistent data storage with SQLite
* Expense categories
* Date validation
* Filter expenses by category
* Filter expenses by date
* Display the total of filtered expenses
* Display the number of filtered expenses
* Clean and aligned expense table
* Input validation and error handling

## Tech Stack

| Technology | Purpose                        |
| ---------- | ------------------------------ |
| Python     | Application logic              |
| Tkinter    | Graphical user interface       |
| SQLite     | Local database                 |

## Getting Started

### Requirements

* Python 3.x
* Tkinter

Tkinter is included with most standard Python installations.

### Run the application

Clone the repository:

```bash
git clone https://github.com/itstxti/python-mini-projects.git
```

Navigate to the project:

```bash
cd python-mini-projects/expense-tracker
```

Run the application:

```bash
python expense_tracker.py
```

A SQLite database will be created automatically when the application is first run.

## How It Works

Expenses are stored locally in a SQLite database with the following information:

* Description
* Amount
* Category
* Date

## Database

The application uses SQLite for persistent local storage.

The database contains an `expenses` table:

```sql
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    date TEXT NOT NULL
);
```

Database operations use parameterized SQL queries rather than building SQL statements directly from user input.

## Screenshot



