import tkinter as tk
from tkinter import messagebox
import secrets
import string


def generate_password():
    try:
        length = int(length_entry.get())

        if length < 4:
            messagebox.showerror(
                "Invalid length",
                "Password length must be at least 4."
            )
            return

    except ValueError:
        messagebox.showerror(
            "Invalid length",
            "Please enter a valid number."
        )
        return

    characters = ""

    if uppercase_var.get():
        characters += string.ascii_uppercase

    if lowercase_var.get():
        characters += string.ascii_lowercase

    if numbers_var.get():
        characters += string.digits

    if symbols_var.get():
        characters += string.punctuation

    if not characters:
        messagebox.showerror(
            "No character types selected",
            "Select at least one character type."
        )
        return

    password = "".join(
        secrets.choice(characters)
        for _ in range(length)
    )

    password_entry.delete(0, tk.END)
    password_entry.insert(0, password)

    update_strength(length)


def update_strength(length):
    selected_types = sum([
        uppercase_var.get(),
        lowercase_var.get(),
        numbers_var.get(),
        symbols_var.get()
    ])

    if length >= 16 and selected_types >= 3:
        strength_label.config(text="Strength: Strong")
    elif length >= 10 and selected_types >= 2:
        strength_label.config(text="Strength: Medium")
    else:
        strength_label.config(text="Strength: Weak")


def copy_password():
    password = password_entry.get()

    if not password:
        messagebox.showwarning(
            "No password",
            "Generate a password first."
        )
        return

    root.clipboard_clear()
    root.clipboard_append(password)
    root.update()

    messagebox.showinfo(
        "Copied",
        "Password copied to clipboard."
    )


# Window
root = tk.Tk()
root.title("Password Generator")
root.geometry("420x540")
root.resizable(False, False)

# Title
title_label = tk.Label(
    root,
    text="Password Generator",
    font=("Arial", 24, "bold")
)
title_label.pack(pady=(25, 20))

# Length
length_frame = tk.Frame(root)
length_frame.pack(pady=10)

tk.Label(
    length_frame,
    text="Password length:",
    font=("Arial", 12)
).pack(side="left", padx=5)

length_entry = tk.Entry(
    length_frame,
    width=6,
    font=("Arial", 12),
    justify="center"
)
length_entry.insert(0, "16")
length_entry.pack(side="left", padx=5)

# Character options
options_frame = tk.LabelFrame(
    root,
    text="Character types",
    font=("Arial", 11),
    padx=15,
    pady=10
)
options_frame.pack(fill="x", padx=40, pady=15)

uppercase_var = tk.BooleanVar(value=True)
lowercase_var = tk.BooleanVar(value=True)
numbers_var = tk.BooleanVar(value=True)
symbols_var = tk.BooleanVar(value=True)

tk.Checkbutton(
    options_frame,
    text="Uppercase letters (A-Z)",
    variable=uppercase_var,
    font=("Arial", 11)
).pack(anchor="w")

tk.Checkbutton(
    options_frame,
    text="Lowercase letters (a-z)",
    variable=lowercase_var,
    font=("Arial", 11)
).pack(anchor="w")

tk.Checkbutton(
    options_frame,
    text="Numbers (0-9)",
    variable=numbers_var,
    font=("Arial", 11)
).pack(anchor="w")

tk.Checkbutton(
    options_frame,
    text="Symbols (!@#$...)",
    variable=symbols_var,
    font=("Arial", 11)
).pack(anchor="w")

# Generate button
generate_button = tk.Button(
    root,
    text="Generate Password",
    font=("Arial", 13, "bold"),
    command=generate_password,
    padx=20,
    pady=8
)
generate_button.pack(pady=15)

# Password output
password_entry = tk.Entry(
    root,
    font=("Arial", 15),
    justify="center"
)
password_entry.pack(fill="x", padx=40, ipady=8)

# Strength
strength_label = tk.Label(
    root,
    text="Strength: -",
    font=("Arial", 12, "bold")
)
strength_label.pack(pady=12)

# Copy button
copy_button = tk.Button(
    root,
    text="Copy to Clipboard",
    font=("Arial", 11),
    command=copy_password,
    padx=15,
    pady=5
)
copy_button.pack()

root.mainloop()