import os
import tkinter as tk
from tkinter import filedialog, ttk

from typer import style

from config import load_config, save_config
from organizer import (
    delete_files,
    find_duplicates,
    organize_files,
    scan_folder,
    undo_operations
)
from utils import format_size


# =========================
# Theme
# =========================

LIGHT_BG = "#F5F7FA"
LIGHT_CARD = "#FFFFFF"
LIGHT_TEXT = "#1F2937"
LIGHT_SECONDARY = "#6B7280"
LIGHT_BORDER = "#E5E7EB"

DARK_BG = "#111827"
DARK_CARD = "#1F2937"
DARK_TEXT = "#F9FAFB"
DARK_SECONDARY = "#9CA3AF"
DARK_BORDER = "#374151"

ACCENT_COLOR = "#2563EB"
SUCCESS_COLOR = "#16A34A"
DANGER_COLOR = "#DC2626"
WARNING_COLOR = "#D97706"


# =========================
# Application state
# =========================

root = tk.Tk()
root.title("File Organizer")
root.geometry("1100x800")
root.minsize(950, 700)

categories = load_config()

selected_folder = ""
current_files = []
last_operations = []
dark_mode = False


# =========================
# Variables
# =========================

search_var = tk.StringVar()
status_var = tk.StringVar(value="Select a folder to get started.")

total_files_var = tk.StringVar(value="0")
total_size_var = tk.StringVar(value="0 B")
category_count_var = tk.StringVar(value="0")


# =========================
# Styles
# =========================

def configure_styles():
    style = ttk.Style()

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    if dark_mode:
        bg = DARK_BG
        card = DARK_CARD
        text = DARK_TEXT
        secondary = DARK_SECONDARY
        border = DARK_BORDER
    else:
        bg = LIGHT_BG
        card = LIGHT_CARD
        text = LIGHT_TEXT
        secondary = LIGHT_SECONDARY
        border = LIGHT_BORDER

    root.configure(bg=bg)

    style.configure(
        "TFrame",
        background=bg
    )

    style.configure(
        "Search.TEntry",
        font=("Segoe UI", 11),
        padding=(10, 4)
    )

    style.configure(
        "Card.TFrame",
        background=card
    )

    style.configure(
        "TLabel",
        background=bg,
        foreground=text,
        font=("Segoe UI", 10)
    )

    style.configure(
        "Title.TLabel",
        background=bg,
        foreground=text,
        font=("Segoe UI", 22, "bold")
    )

    style.configure(
        "Subtitle.TLabel",
        background=bg,
        foreground=secondary,
        font=("Segoe UI", 10)
    )

    style.configure(
        "Stat.TLabel",
        background=card,
        foreground=text,
        font=("Segoe UI", 18, "bold")
    )

    style.configure(
        "StatTitle.TLabel",
        background=card,
        foreground=secondary,
        font=("Segoe UI", 9)
    )

    style.configure(
        "TButton",
        font=("Segoe UI", 10),
        padding=(12, 7)
    )

    style.configure(
        "Accent.TButton",
        font=("Segoe UI", 10, "bold"),
        padding=(14, 8)
    )

    style.configure(
        "Danger.TButton",
        font=("Segoe UI", 10, "bold"),
        padding=(12, 7)
    )

    style.configure(
        "TEntry",
        fieldbackground=card,
        foreground=text,
        bordercolor=border
    )

    style.configure(
        "TCombobox",
        fieldbackground=card,
        foreground=text,
        bordercolor=border
    )

    style.configure(
        "Treeview",
        background=card,
        foreground=text,
        fieldbackground=card,
        bordercolor=border,
        rowheight=30,
        font=("Segoe UI", 9)
    )

    style.configure(
        "Treeview.Heading",
        background=bg,
        foreground=text,
        font=("Segoe UI", 9, "bold")
    )

    style.map(
        "Treeview",
        background=[("selected", ACCENT_COLOR)],
        foreground=[("selected", "#FFFFFF")]
    )


# =========================
# Helpers
# =========================

def update_status(message):
    status_var.set(message)


def update_dashboard(files):
    total_files_var.set(str(len(files)))

    total_size = sum(file_data["size"] for file_data in files)
    total_size_var.set(format_size(total_size))

    category_count_var.set(
        str(len(set(file_data["category"] for file_data in files)))
    )


def get_filtered_files():
    query = search_var.get().strip().lower()

    if not query:
        return current_files

    return [
        file_data
        for file_data in current_files
        if query in file_data["name"].lower()
        or query in file_data["category"].lower()
    ]


# =========================
# File list
# =========================

def refresh_file_list():
    for item in file_tree.get_children():
        file_tree.delete(item)

    files = get_filtered_files()

    for file_data in files:
        file_tree.insert(
            "",
            "end",
            values=(
                file_data["name"],
                file_data["category"],
                format_size(file_data["size"]),
                file_data["modified"].strftime("%d/%m/%Y %H:%M")
            )
        )

    update_dashboard(current_files)

    if selected_folder:
        update_status(
            f"{len(files)} file(s) shown."
        )


def scan_current_folder():
    global current_files

    if not selected_folder:
        update_status("Select a folder first.")
        return

    current_files = scan_folder(
        selected_folder,
        categories
    )

    refresh_file_list()


# =========================
# Folder selection
# =========================

def choose_folder():
    global selected_folder

    folder = filedialog.askdirectory(
        title="Select folder"
    )

    if not folder:
        return

    selected_folder = folder

    folder_label.config(
        text=selected_folder
    )

    scan_current_folder()

    update_status(
        f"Folder selected: {os.path.basename(selected_folder)}"
    )


# =========================
# Preview
# =========================

def show_preview():
    if not selected_folder:
        update_status("Select a folder first.")
        return

    files = get_filtered_files()

    preview_window = tk.Toplevel(root)
    preview_window.title("Preview")
    preview_window.geometry("800x500")
    preview_window.minsize(700, 400)

    preview_window.configure(
        bg=DARK_BG if dark_mode else LIGHT_BG
    )

    title = ttk.Label(
        preview_window,
        text="Preview",
        style="Title.TLabel"
    )
    title.pack(
        anchor="w",
        padx=20,
        pady=(20, 5)
    )

    subtitle = ttk.Label(
        preview_window,
        text="No files will be moved until you click Organize Files.",
        style="Subtitle.TLabel"
    )
    subtitle.pack(
        anchor="w",
        padx=20,
        pady=(0, 15)
    )

    frame = ttk.Frame(
        preview_window,
        style="Card.TFrame"
    )
    frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 20)
    )

    columns = (
        "file",
        "destination"
    )

    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings"
    )

    tree.heading(
        "file",
        text="File"
    )

    tree.heading(
        "destination",
        text="Destination"
    )

    tree.column(
        "file",
        width=320
    )

    tree.column(
        "destination",
        width=350
    )

    scrollbar = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(
        yscrollcommand=scrollbar.set
    )

    tree.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(10, 0),
        pady=10
    )

    scrollbar.pack(
        side="right",
        fill="y",
        padx=(0, 10),
        pady=10
    )

    for file_data in files:
        destination = os.path.join(
            selected_folder,
            file_data["category"],
            file_data["name"]
        )

        tree.insert(
            "",
            "end",
            values=(
                file_data["name"],
                destination
            )
        )


# =========================
# Organize
# =========================

def organize_current_folder():
    global last_operations

    if not selected_folder:
        update_status("Select a folder first.")
        return

    files = get_filtered_files()

    if not files:
        update_status("There are no files to organize.")
        return

    confirmation = tk.Toplevel(root)
    confirmation.title("Confirm Organization")
    confirmation.geometry("460x220")
    confirmation.resizable(False, False)

    if dark_mode:
        confirmation.configure(bg=DARK_BG)
    else:
        confirmation.configure(bg=LIGHT_BG)

    ttk.Label(
        confirmation,
        text="Organize Files",
        style="Title.TLabel"
    ).pack(
        anchor="w",
        padx=25,
        pady=(25, 8)
    )

    ttk.Label(
        confirmation,
        text=(
            f"{len(files)} file(s) will be moved into "
            "their corresponding category folders."
        ),
        style="Subtitle.TLabel"
    ).pack(
        anchor="w",
        padx=25,
        pady=(0, 20)
    )

    button_frame = ttk.Frame(
        confirmation
    )
    button_frame.pack(
        fill="x",
        padx=25
    )

    def confirm():
        global last_operations

        last_operations = organize_files(
            selected_folder,
            files
        )

        confirmation.destroy()

        scan_current_folder()

        if last_operations:
            update_status(
                f"{len(last_operations)} file(s) organized successfully."
            )
        else:
            update_status(
                "No files were organized."
            )

    ttk.Button(
        button_frame,
        text="Cancel",
        command=confirmation.destroy
    ).pack(
        side="right",
        padx=(10, 0)
    )

    ttk.Button(
        button_frame,
        text="Organize",
        style="Accent.TButton",
        command=confirm
    ).pack(
        side="right"
    )


# =========================
# Undo
# =========================

def undo_last_organization():
    global last_operations

    if not last_operations:
        update_status("There is no organization to undo.")
        return

    restored = undo_operations(
        last_operations
    )

    last_operations = []

    scan_current_folder()

    update_status(
        f"{restored} file(s) restored."
    )


# =========================
# Duplicate Manager
# =========================

def show_duplicate_manager():
    if not selected_folder:
        update_status("Select a folder first.")
        return

    duplicates = find_duplicates(
        current_files
    )

    duplicate_window = tk.Toplevel(root)
    duplicate_window.title("Duplicate Manager")
    duplicate_window.geometry("850x600")
    duplicate_window.minsize(700, 450)

    if dark_mode:
        duplicate_window.configure(bg=DARK_BG)
    else:
        duplicate_window.configure(bg=LIGHT_BG)

    summary_var = tk.StringVar()

    manager_status_var = tk.StringVar()

    ttk.Label(
        duplicate_window,
        text="Duplicate Manager",
        style="Title.TLabel"
    ).pack(
        anchor="w",
        padx=20,
        pady=(20, 5)
    )

    frame = ttk.Frame(
        duplicate_window,
        style="Card.TFrame"
    )
    frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 10)
    )

    columns = (
        "group",
        "file",
        "size"
    )

    duplicate_tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings",
        selectmode="extended"
    )

    duplicate_tree.heading(
        "group",
        text="Group"
    )

    duplicate_tree.heading(
        "file",
        text="Duplicate File"
    )

    duplicate_tree.heading(
        "size",
        text="Size"
    )

    duplicate_tree.column(
        "group",
        width=100,
        anchor="center"
    )

    duplicate_tree.column(
        "file",
        width=480
    )

    duplicate_tree.column(
        "size",
        width=120,
        anchor="e"
    )

    scrollbar = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=duplicate_tree.yview
    )

    duplicate_tree.configure(
        yscrollcommand=scrollbar.set
    )

    duplicate_tree.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(10, 0),
        pady=10
    )

    scrollbar.pack(
        side="right",
        fill="y",
        padx=(0, 10),
        pady=10
    )

    duplicate_paths = {}

    def populate_duplicates():
        nonlocal duplicates

        duplicates = find_duplicates(
            current_files
        )

        duplicate_paths.clear()

        for item in duplicate_tree.get_children():
            duplicate_tree.delete(item)

        total_duplicate_files = 0

        for group_index, group in enumerate(
            duplicates,
            start=1
        ):
            # The first file is the oldest one and is kept.
            duplicate_files = group["files"][1:]

            for file_data in duplicate_files:
                item_id = duplicate_tree.insert(
                    "",
                    "end",
                    values=(
                        f"Group {group_index}",
                        file_data["name"],
                        format_size(file_data["size"])
                    )
                )

                duplicate_paths[item_id] = file_data["path"]

                total_duplicate_files += 1

        if duplicates:
            summary_var.set(
                f"{len(duplicates)} duplicate group(s) · "
                f"{total_duplicate_files} file(s) can be deleted"
            )
        else:
            summary_var.set(
                "No duplicate files found."
            )

    def delete_selected():
        selected_items = duplicate_tree.selection()

        if not selected_items:
            manager_status_var.set(
                "Select one or more duplicate files."
            )
            return

        paths = [
            duplicate_paths[item_id]
            for item_id in selected_items
            if item_id in duplicate_paths
        ]

        if not paths:
            return

        confirmation = tk.Toplevel(
            duplicate_window
        )
        confirmation.title("Confirm Deletion")
        confirmation.geometry("430x220")
        confirmation.resizable(False, False)

        ttk.Label(
            confirmation,
            text="Delete Selected Files",
            style="Title.TLabel"
        ).pack(
            anchor="w",
            padx=25,
            pady=(25, 8)
        )

        ttk.Label(
            confirmation,
            text=(
                f"{len(paths)} duplicate file(s) will be permanently "
                "deleted."
            ),
            style="Subtitle.TLabel"
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 20)
        )

        ttk.Label(
            confirmation,
            text="This action cannot be undone.",
            foreground=DANGER_COLOR
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 20)
        )

        button_frame = ttk.Frame(
            confirmation
        )
        button_frame.pack(
            fill="x",
            padx=25
        )

        def confirm_delete():
            deleted = delete_files(
                paths
            )

            confirmation.destroy()

            scan_current_folder()
            populate_duplicates()

            manager_status_var.set(
                f"{deleted} file(s) deleted."
            )

        ttk.Button(
            button_frame,
            text="Cancel",
            command=confirmation.destroy
        ).pack(
            side="right",
            padx=(10, 0)
        )

        ttk.Button(
            button_frame,
            text="Delete",
            style="Danger.TButton",
            command=confirm_delete
        ).pack(
            side="right"
        )

    def delete_all_duplicates():
        if not duplicates:
            manager_status_var.set(
                "No duplicate files found."
            )
            return

        paths = []

        for group in duplicates:
            # Keep the oldest file in every group.
            paths.extend(
                file_data["path"]
                for file_data in group["files"][1:]
            )

        if not paths:
            manager_status_var.set(
                "No duplicate files can be deleted."
            )
            return

        confirmation = tk.Toplevel(
            duplicate_window
        )
        confirmation.title("Delete All Duplicates")
        confirmation.geometry("460x230")
        confirmation.resizable(False, False)

        ttk.Label(
            confirmation,
            text="Delete All Duplicates",
            style="Title.TLabel"
        ).pack(
            anchor="w",
            padx=25,
            pady=(25, 8)
        )

        ttk.Label(
            confirmation,
            text=(
                f"{len(paths)} duplicate file(s) will be permanently "
                "deleted.\nOne copy from each group will be kept."
            ),
            style="Subtitle.TLabel"
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 15)
        )

        ttk.Label(
            confirmation,
            text="This action cannot be undone.",
            foreground=DANGER_COLOR
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 20)
        )

        button_frame = ttk.Frame(
            confirmation
        )
        button_frame.pack(
            fill="x",
            padx=25
        )

        def confirm_delete_all():
            deleted = delete_files(
                paths
            )

            confirmation.destroy()

            scan_current_folder()
            populate_duplicates()

            manager_status_var.set(
                f"{deleted} duplicate file(s) deleted."
            )

        ttk.Button(
            button_frame,
            text="Cancel",
            command=confirmation.destroy
        ).pack(
            side="right",
            padx=(10, 0)
        )

        ttk.Button(
            button_frame,
            text="Delete All",
            style="Danger.TButton",
            command=confirm_delete_all
        ).pack(
            side="right"
        )

    button_frame = ttk.Frame(
        duplicate_window
    )
    button_frame.pack(
        fill="x",
        padx=20,
        pady=(0, 5)
    )

    ttk.Button(
        button_frame,
        text="Delete Selected",
        style="Danger.TButton",
        command=delete_selected
    ).pack(
        side="left"
    )

    ttk.Button(
        button_frame,
        text="Delete All Duplicates",
        style="Danger.TButton",
        command=delete_all_duplicates
    ).pack(
        side="left",
        padx=10
    )

    ttk.Button(
        button_frame,
        text="Close",
        command=duplicate_window.destroy
    ).pack(
        side="right"
    )

    ttk.Label(
        duplicate_window,
        textvariable=manager_status_var,
        foreground=SUCCESS_COLOR
    ).pack(
        anchor="w",
        padx=20,
        pady=(0, 15)
    )

    populate_duplicates()


# =========================
# Categories
# =========================

def show_categories():
    category_window = tk.Toplevel(root)
    category_window.title("Categories")
    category_window.geometry("650x550")
    category_window.minsize(550, 450)

    if dark_mode:
        category_window.configure(bg=DARK_BG)
    else:
        category_window.configure(bg=LIGHT_BG)

    ttk.Label(
        category_window,
        text="Categories",
        style="Title.TLabel"
    ).pack(
        anchor="w",
        padx=20,
        pady=(20, 5)
    )

    ttk.Label(
        category_window,
        text=(
            "Customize categories and file extensions. "
            "Separate extensions with commas."
        ),
        style="Subtitle.TLabel"
    ).pack(
        anchor="w",
        padx=20,
        pady=(0, 15)
    )

    container = ttk.Frame(
        category_window,
        style="Card.TFrame"
    )
    container.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 15)
    )

    entries = {}

    for category, extensions in categories.items():
        row = ttk.Frame(
            container,
            style="Card.TFrame"
        )
        row.pack(
            fill="x",
            padx=15,
            pady=8
        )

        ttk.Label(
            row,
            text=category,
            width=14
        ).pack(
            side="left"
        )

        entry = ttk.Entry(
            row
        )
        entry.insert(
            0,
            ", ".join(extensions)
        )
        entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        entries[category] = entry

    button_frame = ttk.Frame(
        category_window
    )
    button_frame.pack(
        fill="x",
        padx=20,
        pady=(0, 20)
    )

    def save_categories():
        global categories

        updated_categories = {}

        for category, entry in entries.items():
            values = [
                item.strip().lower()
                for item in entry.get().split(",")
                if item.strip()
            ]

            normalized_values = []

            for extension in values:
                if not extension.startswith("."):
                    extension = "." + extension

                normalized_values.append(
                    extension
                )

            updated_categories[category] = normalized_values

        categories = updated_categories

        save_config(categories)

        category_window.destroy()

        scan_current_folder()

        update_status(
            "Categories updated successfully."
        )

    ttk.Button(
        button_frame,
        text="Cancel",
        command=category_window.destroy
    ).pack(
        side="right",
        padx=(10, 0)
    )

    ttk.Button(
        button_frame,
        text="Save",
        style="Accent.TButton",
        command=save_categories
    ).pack(
        side="right"
    )


# =========================
# Theme
# =========================

def toggle_theme():
    global dark_mode

    dark_mode = not dark_mode

    configure_styles()

    theme_button.config(
        text="Light Mode" if dark_mode else "Dark Mode"
    )


# =========================
# Search
# =========================

def on_search(*args):
    refresh_file_list()


# =========================
# Main UI
# =========================

configure_styles()

main_frame = ttk.Frame(
    root
)
main_frame.pack(
    fill="both",
    expand=True,
    padx=25,
    pady=25
)


# Header

header_frame = ttk.Frame(
    main_frame
)
header_frame.pack(
    fill="x"
)

title_frame = ttk.Frame(
    header_frame
)
title_frame.pack(
    side="left"
)

ttk.Label(
    title_frame,
    text="File Organizer",
    style="Title.TLabel"
).pack(
    anchor="w"
)

theme_button = ttk.Button(
    header_frame,
    text="Dark Mode",
    command=toggle_theme
)
theme_button.pack(
    side="right"
)


# Folder section

folder_card = ttk.Frame(
    main_frame,
    style="Card.TFrame"
)
folder_card.pack(
    fill="x",
    pady=(20, 15)
)

folder_inner = ttk.Frame(
    folder_card,
    style="Card.TFrame"
)
folder_inner.pack(
    fill="x",
    padx=15,
    pady=15
)

ttk.Button(
    folder_inner,
    text="Select Folder",
    style="Accent.TButton",
    command=choose_folder
).pack(
    side="left"
)

folder_label = ttk.Label(
    folder_inner,
    text="No folder selected",
    style="Subtitle.TLabel"
)
folder_label.pack(
    side="left",
    padx=15
)


# Dashboard

dashboard = ttk.Frame(
    main_frame
)
dashboard.pack(
    fill="x",
    pady=(0, 15)
)

stat_cards = []

for title, variable in [
    ("FILES", total_files_var),
    ("TOTAL SIZE", total_size_var),
    ("CATEGORIES", category_count_var)
]:
    card = ttk.Frame(
        dashboard,
        style="Card.TFrame"
    )
    card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 10)
    )

    ttk.Label(
        card,
        text=title,
        style="StatTitle.TLabel"
    ).pack(
        anchor="w",
        padx=15,
        pady=(12, 2)
    )

    ttk.Label(
        card,
        textvariable=variable,
        style="Stat.TLabel"
    ).pack(
        anchor="w",
        padx=15,
        pady=(0, 12)
    )

    stat_cards.append(card)


# Search and actions

toolbar = ttk.Frame(
    main_frame
)
toolbar.pack(
    fill="x",
    pady=(0, 10)
)

search_frame = ttk.Frame(
    toolbar
)
search_frame.pack(
    side="left",
    fill="x",
    expand=True,
)

ttk.Label(
    search_frame,
    text="Search:"
).pack(
    side="left",
    padx=(0, 8)
)



search_entry = ttk.Entry(
    search_frame,
    textvariable=search_var,
    style="Search.TEntry"
)
search_entry.pack(
    side="left",
    fill="x",
    expand=True,
    ipady=6
)

ttk.Button(
    toolbar,
    text="Preview",
    command=show_preview
).pack(
    side="left",
    padx=(10, 0)
)

ttk.Button(
    toolbar,
    text="Organize Files",
    style="Accent.TButton",
    command=organize_current_folder
).pack(
    side="left",
    padx=(10, 0)
)

ttk.Button(
    toolbar,
    text="Undo",
    command=undo_last_organization
).pack(
    side="left",
    padx=(10, 0)
)

ttk.Button(
    toolbar,
    text="Manage Duplicates",
    command=show_duplicate_manager
).pack(
    side="left",
    padx=(10, 0)
)

ttk.Button(
    toolbar,
    text="Categories",
    command=show_categories
).pack(
    side="left",
    padx=(10, 0)
)


# File table

table_frame = ttk.Frame(
    main_frame,
    style="Card.TFrame"
)
table_frame.pack(
    fill="both",
    expand=True
)

columns = (
    "name",
    "category",
    "size",
    "modified"
)

file_tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)

file_tree.heading(
    "name",
    text="File"
)

file_tree.heading(
    "category",
    text="Category"
)

file_tree.heading(
    "size",
    text="Size"
)

file_tree.heading(
    "modified",
    text="Modified"
)

file_tree.column(
    "name",
    width=430
)

file_tree.column(
    "category",
    width=160
)

file_tree.column(
    "size",
    width=120,
    anchor="e"
)

file_tree.column(
    "modified",
    width=180
)

table_scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=file_tree.yview
)

file_tree.configure(
    yscrollcommand=table_scrollbar.set
)

file_tree.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(10, 0),
    pady=10
)

table_scrollbar.pack(
    side="right",
    fill="y",
    padx=(0, 10),
    pady=10
)


# Status

status_label = ttk.Label(
    main_frame,
    textvariable=status_var,
    style="Subtitle.TLabel"
)
status_label.pack(
    anchor="w",
    pady=(10, 0)
)


# Search binding

search_var.trace_add(
    "write",
    on_search
)


# Start application

root.mainloop()

