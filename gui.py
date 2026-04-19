import tkinter as tk
from tkinter import messagebox

# ----- Budget Logic -----
def check_budget(income, spending):
    if spending < income * 0.7:
        return "Good job! You are saving well."
    elif spending <= income:
        return "You are okay, but try to save more."
    else:
        return "Warning: You are spending too much."

# ----- Button Function -----
def handle_check():
    try:
        income = float(entry_income.get())
        spending = float(entry_spending.get())

        result = check_budget(income, spending)
        result_label.config(text=result)

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers.")

# ----- Main Window -----
root = tk.Tk()
root.title("Budget Buddy Assistant")
root.geometry("400x300")
root.resizable(False, False)

# Title
title_label = tk.Label(root, text="Budget Buddy Assistant", font=("Arial", 16, "bold"))
title_label.pack(pady=15)

# Income input
income_label = tk.Label(root, text="Enter your monthly income:")
income_label.pack()
entry_income = tk.Entry(root, width=30)
entry_income.pack(pady=5)

# Spending input
spending_label = tk.Label(root, text="Enter your monthly spending:")
spending_label.pack()
entry_spending = tk.Entry(root, width=30)
entry_spending.pack(pady=5)

# Button
check_button = tk.Button(root, text="Check Budget", command=handle_check, width=20, bg="lightblue")
check_button.pack(pady=15)

# Result
result_label = tk.Label(root, text="", font=("Arial", 12), wraplength=300, justify="center")
result_label.pack(pady=10)

# Run app
root.mainloop()