import tkinter as tk


def click(button):
    current = entry.get()

    if button == "C":
        entry.delete(0, tk.END)

    elif button == "⌫":
        entry.delete(len(current) - 1, tk.END)

    elif button == "=":
        try:
            result = eval(current)
            entry.delete(0, tk.END)
            entry.insert(0, str(result))
        except (SyntaxError, ZeroDivisionError, NameError):
            entry.delete(0, tk.END)
            entry.insert(0, "Error")

    else:
        entry.insert(tk.END, button)


# Window
root = tk.Tk()
root.title("Calculator")
root.geometry("320x450")
root.resizable(False, False)

# Display
entry = tk.Entry(
    root,
    font=("Arial", 24),
    justify="right",
    bd=10,
    relief=tk.FLAT
)
entry.pack(fill="both", padx=10, pady=20, ipady=10)

# Buttons
buttons = [
    ["C", "⌫", "(", ")"],
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"],
]

frame = tk.Frame(root)
frame.pack(expand=True, fill="both", padx=10, pady=10)

for row, button_row in enumerate(buttons):
    for col, button in enumerate(button_row):
        btn = tk.Button(
            frame,
            text=button,
            font=("Arial", 18),
            command=lambda b=button: click(b)
        )
        btn.grid(
            row=row,
            column=col,
            sticky="nsew",
            padx=3,
            pady=3
        )

# Make rows and columns expand
for i in range(5):
    frame.rowconfigure(i, weight=1)

for i in range(4):
    frame.columnconfigure(i, weight=1)


root.mainloop()