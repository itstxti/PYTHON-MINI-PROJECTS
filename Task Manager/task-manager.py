import sqlite3
import tkinter as tk
from tkinter import ttk
from datetime import date, datetime

from tkcalendar import DateEntry


# Configuration

DATABASE = "tasks.db"

BG_COLOR = "#F5F5F7"
CARD_COLOR = "#FFFFFF"
TEXT_COLOR = "#1D1D1F"
SECONDARY_TEXT = "#6E6E73"
BORDER_COLOR = "#E5E5E7"

PRIMARY_COLOR = "#007AFF"
DANGER_COLOR = "#FF3B30"
SUCCESS_COLOR = "#34C759"

HIGH_COLOR = "#C8231B"
MEDIUM_COLOR = "#D78717"
LOW_COLOR = "#1DA43F"


# Database

def connect_database():
    return sqlite3.connect(DATABASE)


def create_database():
    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT NOT NULL,
            due_date TEXT,
            completed INTEGER NOT NULL DEFAULT 0
        )
    """)

    connection.commit()
    connection.close()


# Main Window

root = tk.Tk()

root.title("To-Do Manager")
root.geometry("1000x780")
root.minsize(900, 700)
root.configure(bg=BG_COLOR)


# Variables

selected_task_id = None

search_var = tk.StringVar()
status_filter_var = tk.StringVar(value="All")
priority_filter_var = tk.StringVar(value="All")
sort_var = tk.StringVar(value="Due Date")
selected_task_completed = False

status_message = tk.StringVar(
    value="Ready."
)


# Styles

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background=CARD_COLOR,
    foreground=TEXT_COLOR,
    fieldbackground=CARD_COLOR,
    rowheight=42,
    borderwidth=0,
    font=("Segoe UI", 10)
)

style.configure(
    "Treeview.Heading",
    background="#F2F2F4",
    foreground=SECONDARY_TEXT,
    font=("Segoe UI", 9, "bold"),
    relief="flat",
    padding=(10, 11)
)

style.map(
    "Treeview",
    background=[
        ("selected", "#E5F0FF")
    ],
    foreground=[
        ("selected", TEXT_COLOR)
    ]
)

style.configure(
    "TCombobox",
    padding=8,
    font=("Segoe UI", 10)
)


# Database Queries

def get_tasks():

    connection = connect_database()
    cursor = connection.cursor()

    query = """
        SELECT
            id,
            title,
            description,
            priority,
            due_date,
            completed
        FROM tasks
        WHERE 1=1
    """

    parameters = []

    # Search
    search = search_var.get().strip()

    if search:

        query += """
            AND (
                title LIKE ?
                OR description LIKE ?
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value
        ])

    # Status filter
    status = status_filter_var.get()

    if status == "Pending":

        query += """
            AND completed = 0
        """

    elif status == "Completed":

        query += """
            AND completed = 1
        """

    # Priority filter
    priority = priority_filter_var.get()

    if priority != "All":

        query += """
            AND priority = ?
        """

        parameters.append(priority)

    # Sorting
    sort = sort_var.get()

    if sort == "Priority":

        query += """
            ORDER BY
            CASE priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
            END
        """

    elif sort == "Title":

        query += """
            ORDER BY title COLLATE NOCASE
        """

    elif sort == "Created":

        query += """
            ORDER BY id DESC
        """

    else:

        query += """
            ORDER BY
            CASE
                WHEN due_date IS NULL THEN 1
                ELSE 0
            END,
            due_date
        """

    cursor.execute(
        query,
        parameters
    )

    tasks = cursor.fetchall()

    connection.close()

    return tasks


# Refresh Tasks

def refresh_tasks():

    for item in tree.get_children():
        tree.delete(item)

    tasks = get_tasks()

    today = date.today().isoformat()

    for task in tasks:

        task_id = task[0]
        title = task[1]
        description = task[2] or ""
        priority = task[3]
        due_date = task[4] or ""
        completed = task[5]

        if completed:

            status = "Completed"

        elif due_date and due_date < today:

            status = "Overdue"

        else:

            status = "Pending"

        tree.insert(
            "",
            tk.END,
            iid=str(task_id),
            values=(
                title,
                description,
                priority,
                due_date,
                status
            ),
            tags=(
                status.lower(),
                priority.lower()
            )
        )

    update_statistics(tasks)


# Statistics

def update_statistics(tasks):

    total = len(tasks)

    completed = sum(
        task[5] == 1
        for task in tasks
    )

    pending = total - completed

    today = date.today().isoformat()

    overdue = sum(
        bool(task[4])
        and task[5] == 0
        and task[4] < today
        for task in tasks
    )

    total_value.config(
        text=str(total)
    )

    pending_value.config(
        text=str(pending)
    )

    completed_value.config(
        text=str(completed)
    )

    overdue_value.config(
        text=str(overdue)
    )


# Clear Form

def clear_form():

    global selected_task_id, selected_task_completed

    selected_task_id = None
    selected_task_completed = False

    title_entry.delete(
        0,
        tk.END
    )

    description_entry.delete(
        0,
        tk.END
    )

    priority_combo.set(
        "Medium"
    )

    due_date_entry.set_date(
        date.today()
    )

    form_title.config(
        text="New Task"
    )

    save_button.config(
        text="Add Task"
    )

    delete_form_button.config(
        state="disabled"
    )

    complete_form_button.config(
        state="disabled",
        text="Mark Complete"
    )

    status_message.set(
        "Ready to add a new task."
    )

    title_entry.focus()

# Save Task

def save_task():

    global selected_task_id

    title = title_entry.get().strip()

    description = description_entry.get().strip()

    priority = priority_combo.get()

    due_date = (
        due_date_entry
        .get_date()
        .isoformat()
    )

    if not title:

        status_message.set(
            "Please enter a task title."
        )

        title_entry.focus()

        return

    connection = connect_database()
    cursor = connection.cursor()

    if selected_task_id is None:

        cursor.execute(
            """
            INSERT INTO tasks
            (
                title,
                description,
                priority,
                due_date
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                title,
                description,
                priority,
                due_date
            )
        )

        message = "Task added successfully."

    else:

        cursor.execute(
            """
            UPDATE tasks
            SET
                title = ?,
                description = ?,
                priority = ?,
                due_date = ?
            WHERE id = ?
            """,
            (
                title,
                description,
                priority,
                due_date,
                selected_task_id
            )
        )

        message = "Task updated successfully."

    connection.commit()
    connection.close()

    clear_form()
    refresh_tasks()

    status_message.set(
        message
    )


# Select Task

def select_task(event=None):

    global selected_task_id, selected_task_completed

    selection = tree.selection()

    if not selection:
        return

    selected_task_id = int(
        selection[0]
    )

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            title,
            description,
            priority,
            due_date
        FROM tasks
        WHERE id = ?
        """,
        (selected_task_id,)
    )

    task = cursor.fetchone()

    connection.close()

    if not task:
        return

    title_entry.delete(
        0,
        tk.END
    )

    title_entry.insert(
        0,
        task[0]
    )

    delete_form_button.config(
    state="normal"
    )

    description_entry.delete(
        0,
        tk.END
    )

    description_entry.insert(
        0,
        task[1] or ""
    )

    priority_combo.set(
        task[2]
    )
    

    if task[3]:

        try:

            selected_date = datetime.strptime(
                task[3],
                "%Y-%m-%d"
            ).date()

            due_date_entry.set_date(
                selected_date
            )

        except ValueError:
            pass

    form_title.config(
        text="Edit Task"
    )

    save_button.config(
        text="Save Changes"
    )

    selected_task_completed = bool(
    tree.item(selected_task_id)["values"][4] == "Completed"
    )

    delete_form_button.config(
    state="normal"
)

    complete_form_button.config(
        state="normal",
        text=(
            "Mark Pending"
            if selected_task_completed
            else "Mark Complete"
        )
    )

    status_message.set(
        "Editing selected task."
    )


# Toggle Completed

def toggle_completed():

    global selected_task_completed

    if selected_task_id is None:

        status_message.set(
            "Select a task first."
        )

        return

    new_status = (
        0
        if selected_task_completed
        else 1
    )

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET completed = ?
        WHERE id = ?
        """,
        (
            new_status,
            selected_task_id
        )
    )

    connection.commit()
    connection.close()

    selected_task_completed = bool(new_status)

    complete_form_button.config(
        text=(
            "Mark Pending"
            if selected_task_completed
            else "Mark Complete"
        )
    )

    refresh_tasks()

    status_message.set(
        "Task marked as completed."
        if selected_task_completed
        else "Task marked as pending."
    )

# Delete Task

def delete_task():

    selection = tree.selection()

    if not selection:

        status_message.set(
            "Select a task first."
        )

        return

    task_id = int(
        selection[0]
    )

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE id = ?
        """,
        (task_id,)
    )

    connection.commit()
    connection.close()

    clear_form()
    refresh_tasks()

    status_message.set(
        "Task deleted."
    )


# Clear Completed

def clear_completed():

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE completed = 1
        """
    )

    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    refresh_tasks()

    status_message.set(
        f"{deleted} completed task(s) removed."
    )


# Filters

def apply_filters(*args):

    refresh_tasks()


# Header

header_frame = tk.Frame(
    root,
    bg=BG_COLOR
)

header_frame.pack(
    fill="x",
    padx=30,
    pady=(25, 12)
)


tk.Label(
    header_frame,
    text="To-Do Manager",
    font=("Segoe UI", 26, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
).pack(
    anchor="w"
)


# Statistics

stats_frame = tk.Frame(
    root,
    bg=BG_COLOR
)

stats_frame.pack(
    fill="x",
    padx=25,
    pady=5
)


def create_stat_card(parent, column, title):

    card = tk.Frame(
        parent,
        bg=CARD_COLOR,
        highlightthickness=1,
        highlightbackground=BORDER_COLOR
    )

    card.grid(
        row=0,
        column=column,
        sticky="nsew",
        padx=5
    )

    parent.grid_columnconfigure(
        column,
        weight=1
    )

    tk.Label(
        card,
        text=title,
        font=("Segoe UI", 9, "bold"),
        bg=CARD_COLOR,
        fg=SECONDARY_TEXT
    ).pack(
        anchor="w",
        padx=16,
        pady=(11, 0)
    )

    value = tk.Label(
        card,
        text="0",
        font=("Segoe UI", 21, "bold"),
        bg=CARD_COLOR,
        fg=TEXT_COLOR
    )

    value.pack(
        anchor="w",
        padx=16,
        pady=(1, 11)
    )

    return value


total_value = create_stat_card(
    stats_frame,
    0,
    "TOTAL TASKS"
)

pending_value = create_stat_card(
    stats_frame,
    1,
    "PENDING"
)

completed_value = create_stat_card(
    stats_frame,
    2,
    "COMPLETED"
)

overdue_value = create_stat_card(
    stats_frame,
    3,
    "OVERDUE"
)


# New / Edit Task Card

style.configure(
    "Custom.TEntry",
    padding=(10, 8)
)

form_card = tk.Frame(
    root,
    bg=CARD_COLOR,
    highlightthickness=1,
    highlightbackground=BORDER_COLOR
)

form_card.pack(
    fill="x",
    padx=30,
    pady=14
)


form_title = tk.Label(
    form_card,
    text="New Task",
    font=("Segoe UI", 14, "bold"),
    bg=CARD_COLOR,
    fg=TEXT_COLOR
)

form_title.grid(
    row=0,
    column=0,
    columnspan=3,
    sticky="w",
    padx=22,
    pady=(16, 14)
)


# Task gets the most space

form_card.grid_columnconfigure(
    0,
    weight=5
)

form_card.grid_columnconfigure(
    1,
    weight=2
)

form_card.grid_columnconfigure(
    2,
    weight=2
)


# --------------------------------------------------
# Task
# --------------------------------------------------

tk.Label(
    form_card,
    text="Task",
    font=("Segoe UI", 9, "bold"),
    bg=CARD_COLOR,
    fg=SECONDARY_TEXT
).grid(
    row=1,
    column=0,
    sticky="w",
    padx=(22, 10)
)

title_entry = ttk.Entry(
    form_card,
    style="Custom.TEntry",
    font=("Segoe UI", 10)
)

title_entry.grid(
    row=2,
    column=0,
    sticky="ew",
    padx=(22, 10),
    pady=(5, 15)
)


# --------------------------------------------------
# Priority
# --------------------------------------------------

tk.Label(
    form_card,
    text="Priority",
    font=("Segoe UI", 9, "bold"),
    bg=CARD_COLOR,
    fg=SECONDARY_TEXT
).grid(
    row=1,
    column=1,
    sticky="w",
    padx=10
)


priority_combo = ttk.Combobox(
    form_card,
    values=[
        "Low",
        "Medium",
        "High"
    ],
    state="readonly",
    font=("Segoe UI", 10)
)

priority_combo.set(
    "Medium"
)

priority_combo.grid(
    row=2,
    column=1,
    sticky="ew",
    padx=10,
    pady=(5, 15),
)


# --------------------------------------------------
# Due Date
# --------------------------------------------------

tk.Label(
    form_card,
    text="Due Date",
    font=("Segoe UI", 9, "bold"),
    bg=CARD_COLOR,
    fg=SECONDARY_TEXT
).grid(
    row=1,
    column=2,
    sticky="w",
    padx=(10, 22)
)


due_date_entry = DateEntry(
    form_card,
    date_pattern="yyyy-mm-dd",
    font=("Segoe UI", 10),
    width=18
)

due_date_entry.grid(
    row=2,
    column=2,
    sticky="ew",
    padx=(10, 22),
    pady=(5, 15)
)


# --------------------------------------------------
# Description
# --------------------------------------------------

tk.Label(
    form_card,
    text="Description",
    font=("Segoe UI", 9, "bold"),
    bg=CARD_COLOR,
    fg=SECONDARY_TEXT
).grid(
    row=3,
    column=0,
    columnspan=3,
    sticky="w",
    padx=22
)


description_entry = ttk.Entry(
    form_card,
    style="Custom.TEntry",
    font=("Segoe UI", 10)
)

title_entry.grid(
    row=2,
    column=0,
    sticky="ew",
    padx=(22, 10),
    pady=(5, 15)
)

description_entry.grid(
    row=4,
    column=0,
    columnspan=3,
    sticky="ew",
    padx=22,
    pady=(5, 17),
    ipady=8
)


# --------------------------------------------------
# Buttons
# --------------------------------------------------



button_frame = tk.Frame(
    form_card,
    bg=CARD_COLOR
)

button_frame.grid(
    row=5,
    column=0,
    columnspan=3,
    sticky="e",
    padx=22,
    pady=(0, 17)
)

complete_form_button = tk.Button(
    button_frame,
    text="Mark Complete",
    command=toggle_completed,
    bg=SUCCESS_COLOR,
    fg="white",
    activebackground=SUCCESS_COLOR,
    activeforeground="white",
    relief="flat",
    font=("Segoe UI", 10, "bold"),
    padx=18,
    pady=9,
    cursor="hand2",
    state="disabled"
)

complete_form_button.pack(
    side="left",
    padx=(0, 8)
) 

delete_form_button = tk.Button(
    button_frame,
    text="Delete Task",
    command=delete_task,
    bg="#FF3B30",
    fg="white",
    activebackground="#D70015",
    activeforeground="white",
    relief="flat",
    font=("Segoe UI", 10, "bold"),
    padx=21,
    pady=9,
    cursor="hand2"
)

delete_form_button.pack(
    side="left",
    padx=(0, 8)
)



save_button = tk.Button(
    button_frame,
    text="Add Task",
    command=save_task,
    bg=PRIMARY_COLOR,
    fg="white",
    activebackground=PRIMARY_COLOR,
    activeforeground="white",
    relief="flat",
    font=("Segoe UI", 10, "bold"),
    padx=22,
    pady=9,
    cursor="hand2"
)

save_button.pack(
    side="left",
    padx=(0, 8)
)


clear_button = tk.Button(
    button_frame,
    text="Clear",
    command=clear_form,
    bg="#E5E5EA",
    fg=TEXT_COLOR,
    activebackground="#D1D1D6",
    relief="flat",
    font=("Segoe UI", 10),
    padx=22,
    pady=9,
    cursor="hand2"
)

clear_button.pack(
    side="left"
)



# Filters

filter_frame = tk.Frame(
    root,
    bg=BG_COLOR
)

filter_frame.pack(
    fill="x",
    padx=30,
    pady=(0, 8)
)


tk.Label(
    filter_frame,
    text="Search",
    font=("Segoe UI", 9, "bold"),
    bg=BG_COLOR,
    fg=SECONDARY_TEXT
).pack(
    side="left"
)


search_entry = ttk.Entry(
    filter_frame,
    textvariable=search_var,
    style="Custom.TEntry",
    width=28,
    font=("Segoe UI", 10)
)

search_entry.pack(
    side="left",
    padx=(8, 15)
)


status_filter = ttk.Combobox(
    filter_frame,
    textvariable=status_filter_var,
    values=[
        "All",
        "Pending",
        "Completed"
    ],
    state="readonly",
    width=13
)

status_filter.pack(
    side="left",
    padx=4
)


priority_filter = ttk.Combobox(
    filter_frame,
    textvariable=priority_filter_var,
    values=[
        "All",
        "Low",
        "Medium",
        "High"
    ],
    state="readonly",
    width=13
)

priority_filter.pack(
    side="left",
    padx=4
)


sort_combo = ttk.Combobox(
    filter_frame,
    textvariable=sort_var,
    values=[
        "Due Date",
        "Priority",
        "Title",
        "Created"
    ],
    state="readonly",
    width=13
)

sort_combo.pack(
    side="left",
    padx=4
)


search_var.trace_add(
    "write",
    apply_filters
)

status_filter_var.trace_add(
    "write",
    apply_filters
)

priority_filter_var.trace_add(
    "write",
    apply_filters
)

sort_var.trace_add(
    "write",
    apply_filters
)


# Task Table

table_card = tk.Frame(
    root,
    bg=CARD_COLOR,
    highlightthickness=1,
    highlightbackground=BORDER_COLOR
)

table_card.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=5
)


table_container = tk.Frame(
    table_card,
    bg=CARD_COLOR
)

table_container.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)


columns = (
    "task",
    "description",
    "priority",
    "due_date",
    "status"
)


tree = ttk.Treeview(
    table_container,
    columns=columns,
    show="headings",
    selectmode="browse"
)


tree.heading(
    "task",
    text="TASK"
)

tree.heading(
    "description",
    text="DESCRIPTION"
)

tree.heading(
    "priority",
    text="PRIORITY"
)

tree.heading(
    "due_date",
    text="DUE DATE"
)

tree.heading(
    "status",
    text="STATUS"
)


tree.column(
    "task",
    width=220,
    minwidth=160,
    anchor="center"
)

tree.column(
    "description",
    width=330,
    minwidth=180,
    anchor="center"
)

tree.column(
    "priority",
    width=100,
    minwidth=90,
    anchor="center"
)

tree.column(
    "due_date",
    width=125,
    minwidth=110,
    anchor="center"
)

tree.column(
    "status",
    width=120,
    minwidth=100,
    anchor="center"
)


# Table Colors

tree.tag_configure(
    "high",
    foreground=HIGH_COLOR
)

tree.tag_configure(
    "medium",
    foreground=MEDIUM_COLOR
)

tree.tag_configure(
    "low",
    foreground=LOW_COLOR
)

tree.tag_configure(
    "completed",
    foreground=SECONDARY_TEXT
)

tree.tag_configure(
    "overdue",
    foreground=DANGER_COLOR
)

tree.tag_configure(
    "pending",
    foreground=TEXT_COLOR
)


scrollbar = ttk.Scrollbar(
    table_container,
    orient="vertical",
    command=tree.yview
)

tree.configure(
    yscrollcommand=scrollbar.set
)


tree.pack(
    side="left",
    fill="both",
    expand=True
)

scrollbar.pack(
    side="right",
    fill="y"
)


tree.bind(
    "<<TreeviewSelect>>",
    select_task
)





# Status

status_label = tk.Label(
    root,
    textvariable=status_message,
    font=("Segoe UI", 9),
    bg=BG_COLOR,
    fg=SECONDARY_TEXT
)

status_label.pack(
    pady=(0, 9)
)


# Start Application

create_database()

refresh_tasks()

title_entry.focus()

root.mainloop()