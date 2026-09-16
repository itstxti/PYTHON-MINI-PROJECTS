import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import date, datetime


# Database

connection = sqlite3.connect("expenses.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        date TEXT NOT NULL
    )
""")

connection.commit()


# Date helpers

def convert_to_database_date(value):
    """
    Convert DD/MM/YYYY to YYYY-MM-DD.
    """
    try:
        parsed_date = datetime.strptime(
            value,
            "%d/%m/%Y"
        )

        return parsed_date.strftime(
            "%Y-%m-%d"
        )

    except ValueError:
        return None


def convert_to_display_date(value):
    """
    Convert YYYY-MM-DD to DD/MM/YYYY.
    """
    try:
        parsed_date = datetime.strptime(
            value,
            "%Y-%m-%d"
        )

        return parsed_date.strftime(
            "%d/%m/%Y"
        )

    except ValueError:
        return value


# Expense functions

def add_expense():
    description = description_entry.get().strip()
    amount = amount_entry.get().strip()
    category = category_var.get()
    expense_date = date_entry.get().strip()

    if not description or not amount or not category or not expense_date:
        messagebox.showerror(
            "Missing information",
            "Please fill in all fields."
        )
        return

    try:
        amount = float(amount)

        if amount <= 0:
            raise ValueError

    except ValueError:
        messagebox.showerror(
            "Invalid amount",
            "Please enter a valid positive amount."
        )
        return

    formatted_date = convert_to_database_date(
        expense_date
    )

    if not formatted_date:
        messagebox.showerror(
            "Invalid date",
            "Please use the format DD/MM/YYYY.\n\n"
            "Example: 16/09/2026"
        )
        return

    cursor.execute("""
        INSERT INTO expenses (
            description,
            amount,
            category,
            date
        )
        VALUES (?, ?, ?, ?)
    """, (
        description,
        amount,
        category,
        formatted_date
    ))

    connection.commit()

    clear_fields()

    load_expenses()

    messagebox.showinfo(
        "Expense added",
        "Expense added successfully."
    )


def load_expenses():
    expenses_list.delete(
        0,
        tk.END
    )

    # Important:
    # Clear the internal IDs before rebuilding the list.
    expense_ids.clear()

    category_filter = filter_category_var.get()
    date_filter = filter_date_entry.get().strip()

    query = """
        SELECT
            id,
            description,
            amount,
            category,
            date
        FROM expenses
        WHERE 1 = 1
    """

    parameters = []

    # Category filter

    if category_filter != "All":
        query += " AND category = ?"
        parameters.append(
            category_filter
        )

    # Date filter

    if date_filter:
        formatted_date = convert_to_database_date(
            date_filter
        )

        if not formatted_date:
            messagebox.showerror(
                "Invalid date",
                "Please use the format DD/MM/YYYY.\n\n"
                "Example: 16/09/2026"
            )
            return

        query += " AND date = ?"
        parameters.append(
            formatted_date
        )


    # Ordering

    query += """
        ORDER BY date DESC, id DESC
    """

    cursor.execute(
        query,
        parameters
    )

    expenses = cursor.fetchall()

    total = 0

    # Display expenses

    for expense in expenses:

        expense_id = expense[0]
        description = expense[1]
        amount = expense[2]
        category = expense[3]
        expense_date = expense[4]

        display_date = convert_to_display_date(
            expense_date
        )

        # Fixed-width columns
        row = (
            f"{display_date:<12}"
            f"{category:<15}"
            f"{description:<30}"
            f"€{amount:>10.2f}"
        )

        expenses_list.insert(
            tk.END,
            row
        )

        # Store the database ID internally.
        # It is not displayed to the user.
        expense_ids.append(
            expense_id
        )

        total += amount

    # -------------------------
    # Summary
    # -------------------------

    count_label.config(
        text=f"{len(expenses)} expense(s)"
    )

    total_label.config(
        text=f"Total: €{total:.2f}"
    )


def select_expense(event):
    selected = expenses_list.curselection()

    if not selected:
        return

    index = selected[0]

    if index >= len(expense_ids):
        return

    # Get the real database ID
    # from the selected row.
    expense_id = expense_ids[index]

    cursor.execute("""
        SELECT
            description,
            amount,
            category,
            date
        FROM expenses
        WHERE id = ?
    """, (
        expense_id,
    ))

    expense = cursor.fetchone()

    if not expense:
        return

    description = expense[0]
    amount = expense[1]
    category = expense[2]
    expense_date = expense[3]

    clear_fields()

    description_entry.insert(
        0,
        description
    )

    amount_entry.insert(
        0,
        amount
    )

    category_var.set(
        category
    )

    date_entry.delete(
        0,
        tk.END
    )

    date_entry.insert(
        0,
        convert_to_display_date(
            expense_date
        )
    )

    selected_id.set(
        expense_id
    )


def update_expense():
    expense_id = selected_id.get()

    if not expense_id:
        messagebox.showwarning(
            "No expense selected",
            "Select an expense to update."
        )
        return

    description = description_entry.get().strip()
    amount = amount_entry.get().strip()
    category = category_var.get()
    expense_date = date_entry.get().strip()

    if not description or not amount or not category or not expense_date:
        messagebox.showerror(
            "Missing information",
            "Please fill in all fields."
        )
        return

    try:
        amount = float(amount)

        if amount <= 0:
            raise ValueError

    except ValueError:
        messagebox.showerror(
            "Invalid amount",
            "Please enter a valid positive amount."
        )
        return

    formatted_date = convert_to_database_date(
        expense_date
    )

    if not formatted_date:
        messagebox.showerror(
            "Invalid date",
            "Please use the format DD/MM/YYYY.\n\n"
            "Example: 16/09/2026"
        )
        return

    cursor.execute("""
        UPDATE expenses
        SET
            description = ?,
            amount = ?,
            category = ?,
            date = ?
        WHERE id = ?
    """, (
        description,
        amount,
        category,
        formatted_date,
        expense_id
    ))

    connection.commit()

    selected_id.set("")

    clear_fields()

    load_expenses()

    messagebox.showinfo(
        "Expense updated",
        "Expense updated successfully."
    )


def delete_expense():
    expense_id = selected_id.get()

    if not expense_id:
        messagebox.showwarning(
            "No expense selected",
            "Select an expense to delete."
        )
        return

    confirmation = messagebox.askyesno(
        "Delete expense",
        "Are you sure you want to delete this expense?"
    )

    if not confirmation:
        return

    cursor.execute("""
        DELETE FROM expenses
        WHERE id = ?
    """, (
        expense_id,
    ))

    connection.commit()

    # Clear the selected ID first.
    selected_id.set("")

    clear_fields()

    load_expenses()

    messagebox.showinfo(
        "Expense deleted",
        "Expense deleted successfully."
    )


# Form functions

def clear_fields():
    description_entry.delete(
        0,
        tk.END
    )

    amount_entry.delete(
        0,
        tk.END
    )

    category_var.set(
        "Food"
    )

    date_entry.delete(
        0,
        tk.END
    )

    date_entry.insert(
        0,
        date.today().strftime(
            "%d/%m/%Y"
        )
    )


def clear_selection():
    selected_id.set("")

    expenses_list.selection_clear(
        0,
        tk.END
    )

    clear_fields()


# Filter functions

def apply_filters():
    selected_id.set("")

    expenses_list.selection_clear(
        0,
        tk.END
    )

    load_expenses()


def clear_filters():
    selected_id.set("")

    filter_category_var.set(
        "All"
    )

    filter_date_entry.delete(
        0,
        tk.END
    )

    expenses_list.selection_clear(
        0,
        tk.END
    )

    load_expenses()


# Main window

root = tk.Tk()

root.title(
    "Expense Tracker"
)

root.geometry(
    "820x720"
)

root.resizable(
    False,
    False
)


# Title

title_label = tk.Label(
    root,
    text="Expense Tracker",
    font=("Arial", 24, "bold")
)

title_label.pack(
    pady=(25, 20)
)


# Form

form_frame = tk.Frame(
    root
)

form_frame.pack(
    padx=40,
    fill="x"
)


# Description

tk.Label(
    form_frame,
    text="Description:",
    font=("Arial", 11)
).grid(
    row=0,
    column=0,
    sticky="w",
    pady=6
)

description_entry = tk.Entry(
    form_frame,
    font=("Arial", 11)
)

description_entry.grid(
    row=0,
    column=1,
    sticky="ew",
    padx=10
)


# Amount

tk.Label(
    form_frame,
    text="Amount:",
    font=("Arial", 11)
).grid(
    row=1,
    column=0,
    sticky="w",
    pady=6
)

amount_entry = tk.Entry(
    form_frame,
    font=("Arial", 11)
)

amount_entry.grid(
    row=1,
    column=1,
    sticky="ew",
    padx=10
)


# Category

tk.Label(
    form_frame,
    text="Category:",
    font=("Arial", 11)
).grid(
    row=2,
    column=0,
    sticky="w",
    pady=6
)

category_var = tk.StringVar(
    value="Food"
)

category_menu = tk.OptionMenu(
    form_frame,
    category_var,
    "Food",
    "Transport",
    "Leisure",
    "Shopping",
    "Bills",
    "Other"
)

category_menu.grid(
    row=2,
    column=1,
    sticky="w",
    padx=10
)


# Date

tk.Label(
    form_frame,
    text="Date:",
    font=("Arial", 11)
).grid(
    row=3,
    column=0,
    sticky="w",
    pady=6
)

date_entry = tk.Entry(
    form_frame,
    font=("Arial", 11)
)

date_entry.grid(
    row=3,
    column=1,
    sticky="ew",
    padx=10
)

date_entry.insert(
    0,
    date.today().strftime(
        "%d/%m/%Y"
    )
)

form_frame.columnconfigure(
    1,
    weight=1
)


# CRUD buttons

buttons_frame = tk.Frame(
    root
)

buttons_frame.pack(
    pady=20
)


tk.Button(
    buttons_frame,
    text="Add Expense",
    font=("Arial", 11, "bold"),
    command=add_expense,
    padx=15,
    pady=7
).grid(
    row=0,
    column=0,
    padx=5
)


tk.Button(
    buttons_frame,
    text="Update",
    font=("Arial", 11, "bold"),
    command=update_expense,
    padx=15,
    pady=7
).grid(
    row=0,
    column=1,
    padx=5
)


tk.Button(
    buttons_frame,
    text="Delete",
    font=("Arial", 11, "bold"),
    command=delete_expense,
    padx=15,
    pady=7
).grid(
    row=0,
    column=2,
    padx=5
)


tk.Button(
    buttons_frame,
    text="Clear",
    font=("Arial", 11),
    command=clear_selection,
    padx=15,
    pady=7
).grid(
    row=0,
    column=3,
    padx=5
)


# Filters

filter_frame = tk.LabelFrame(
    root,
    text="Filters",
    font=("Arial", 11),
    padx=15,
    pady=10
)

filter_frame.pack(
    padx=40,
    fill="x",
    pady=(5, 15)
)


# Category filter

tk.Label(
    filter_frame,
    text="Category:"
).grid(
    row=0,
    column=0,
    padx=5
)

filter_category_var = tk.StringVar(
    value="All"
)

tk.OptionMenu(
    filter_frame,
    filter_category_var,
    "All",
    "Food",
    "Transport",
    "Leisure",
    "Shopping",
    "Bills",
    "Other"
).grid(
    row=0,
    column=1,
    padx=5
)


# Date filter

tk.Label(
    filter_frame,
    text="Date:"
).grid(
    row=0,
    column=2,
    padx=(15, 5)
)

filter_date_entry = tk.Entry(
    filter_frame,
    width=12
)

filter_date_entry.grid(
    row=0,
    column=3,
    padx=5
)


# Apply filters

tk.Button(
    filter_frame,
    text="Apply",
    command=apply_filters,
    padx=10
).grid(
    row=0,
    column=4,
    padx=5
)


# Clear filters

tk.Button(
    filter_frame,
    text="Clear Filters",
    command=clear_filters,
    padx=10
).grid(
    row=0,
    column=5,
    padx=5
)


# Expenses section

tk.Label(
    root,
    text="Expenses",
    font=("Arial", 16, "bold")
).pack(
    pady=(5, 10)
)


# Table header

header = (
    f"{'Date':<12}"
    f"{'Category':<15}"
    f"{'Description':<30}"
    f"{'Amount':>10}"
)

header_label = tk.Label(
    root,
    text=header,
    font=("Courier", 11, "bold"),
    anchor="w"
)

header_label.pack(
    fill="x",
    padx=40
)


# Expenses list

expenses_list = tk.Listbox(
    root,
    font=("Courier", 11),
    height=12,
    activestyle="none"
)

expenses_list.pack(
    fill="both",
    expand=True,
    padx=40,
    pady=(3, 10)
)

expenses_list.bind(
    "<<ListboxSelect>>",
    select_expense
)


# Summary

summary_frame = tk.Frame(
    root
)

summary_frame.pack(
    fill="x",
    padx=40,
    pady=(5, 15)
)


count_label = tk.Label(
    summary_frame,
    text="0 expense(s)",
    font=("Arial", 11)
)

count_label.pack(
    side="left"
)


total_label = tk.Label(
    summary_frame,
    text="Total: €0.00",
    font=("Arial", 13, "bold")
)

total_label.pack(
    side="right"
)


# Internal state

selected_id = tk.StringVar()

# Database IDs corresponding to
# the rows currently displayed.
expense_ids = []


# Initial load

load_expenses()


# Start application

root.mainloop()


# Close database

connection.close()