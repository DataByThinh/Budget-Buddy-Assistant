import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def clear_window():
    for widget in root.winfo_children():
        widget.destroy()


def validate_login():
    name = name_entry.get().strip()
    dob = dob_entry.get().strip()

    if name == "":
        messagebox.showerror("Input Error", "Please enter your full name.")
        return

    try:
        datetime.strptime(dob, "%m/%d/%Y")
    except ValueError:
        messagebox.showerror("DOB Error", "DOB must be in MM/DD/YYYY format.")
        return

    global current_user_key, expenses, current_income, current_name, current_dob, current_history

    current_user_key = name.lower().strip() + "|" + dob.strip()
    current_name = name
    current_dob = dob
    current_history = []

    all_data = load_all_data()

    if current_user_key in all_data:
        current_income = all_data[current_user_key]["income"]
        expenses = all_data[current_user_key]["expenses"]
        current_history = all_data[current_user_key].get("history", [])
    else:
        current_income = 0.0
        expenses = []
        current_history = []
        

    show_dashboard(name, dob)

def format_dob(event):
        text = dob_entry.get()
        digits = "".join(ch for ch in text if ch.isdigit())[:8]

        if len(digits) >= 5:
            formatted = digits[:2] + "/" + digits[2:4] + "/" + digits[4:]
        elif len(digits) >= 3:
            formatted = digits[:2] + "/" + digits[2:]
        else:
            formatted = digits

        dob_entry.delete(0, tk.END)
        dob_entry.insert(0, formatted)

def create_card(parent, title, value, icon):
    card = tk.Frame(parent, bg="white", height=95,
                    highlightbackground="#dfe3eb", highlightthickness=1)
    card.pack_propagate(False)

    tk.Label(card, text=icon, font=("Helvetica", 22), bg="white").pack(side="left", padx=20)

    text_box = tk.Frame(card, bg="white")
    text_box.pack(side="left")

    tk.Label(text_box, text=title, font=("Helvetica", 11),
             bg="white", fg="#374151").pack(anchor="w")

    value_label = tk.Label(text_box, text=value, font=("Helvetica", 14, "bold"),
                           bg="white", fg="#2563eb")
    value_label.pack(anchor="w", pady=(8, 0))

    return card, value_label

expenses = []
def load_all_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}


def save_all_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)
current_income = 0.0
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "budget_buddy_data.json")
current_user_key = ""
current_history = []

def add_expense():
    category = category_box.get()
    description = description_entry.get().strip()

    try:
        amount = float(amount_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid expense amount.")
        return

    if amount <= 0:
        messagebox.showerror("Input Error", "Expense must be greater than 0.")
        return

    expenses.append({
        "category": category,
        "amount": amount,
        "description": description
    })

    expense_listbox.insert(tk.END, f"{category} - ${amount:.2f} - {description}")

    amount_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)


def save_snapshot():
    global current_income, current_history

    income_text = income_entry.get().strip()
    amount_text = amount_entry.get().strip()

    # Nếu không nhập gì hết
    if income_text == "" and amount_text == "":
        messagebox.showerror("Input Error", "Please enter income or expense before saving.")
        return

    # Nếu có nhập income thì update income
    if income_text != "":
        try:
            current_income += float(income_text)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid monthly income.")
            return

        if current_income <= 0:
            messagebox.showerror("Input Error", "Income must be greater than 0.")
            return

    # Nếu chưa từng nhập income
    if current_income <= 0:
        messagebox.showerror("Input Error", "Please enter monthly income at least once.")
        return

    # Nếu có nhập expense thì add expense
    if amount_text != "":
        try:
            amount = float(amount_text)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid expense amount.")
            return

        if amount <= 0:
            messagebox.showerror("Input Error", "Expense must be greater than 0.")
            return

        category = category_box.get()
        description = description_entry.get().strip()

        expenses.append({
            "category": category,
            "amount": amount,
            "description": description
        })

        expense_listbox.insert(tk.END, f"{category} - ${amount:.2f} - {description}")

    total_expense = sum(item["amount"] for item in expenses)
    savings = current_income - total_expense

    if savings > 0:
        status = "Saving money"
    elif savings == 0:
        status = "Break even"
    else:
        status = "Overspending"

    income_value_label.config(text=f"${current_income:.2f}")
    expense_value_label.config(text=f"${total_expense:.2f}")
    savings_value_label.config(text=f"${savings:.2f}")
    status_value_label.config(text=status)

    category_totals = {}
    for item in expenses:
        category = item["category"]
        amount = item["amount"]
        category_totals[category] = category_totals.get(category, 0) + amount

    if category_totals:
        highest_category = max(category_totals, key=category_totals.get)
        pattern_label.config(text=f"You spent the most on {highest_category}.")
    else:
        pattern_label.config(text="No expense data yet.")

    feedback_label.config(
        text=f"You spent ${total_expense:.2f} out of ${current_income:.2f} income."
    )

    if savings > 0:
        recommendation = "Good job. You are still saving money."
    elif savings == 0:
        recommendation = "You are breaking even. Try to reduce one category."
    else:
        recommendation = "Warning: You are overspending. Review your largest expense category."

    recommendation_label.config(text=recommendation)

    summary_text = ""
    for category, amount in category_totals.items():
        summary_text += f"{category}: ${amount:.2f}\n"

    if summary_text == "":
        summary_text = "No category data yet."

    category_summary_label.config(text=summary_text)

    snapshot = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "income": current_income,
        "total_expense": total_expense,
        "expenses": expenses.copy()
    }

    current_history.append(snapshot)

    all_data = load_all_data()
    all_data[current_user_key] = {
        "name": current_name,
        "dob": current_dob,
        "income": current_income,
        "expenses": expenses,
        "history": current_history
    }

    save_all_data(all_data)

    income_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)

    messagebox.showinfo("Saved", "Snapshot saved and KPI updated.")

def reset_all_data():
    global expenses, current_income, current_history

    confirm = messagebox.askyesno("Confirm Reset", "Are you sure you want to delete all data?")

    if not confirm:
        return

    # Reset data trong RAM
    expenses = []
    current_income = 0.0
    current_history = []

    # Xóa trong file JSON
    all_data = load_all_data()

    if current_user_key in all_data:
        del all_data[current_user_key]

    save_all_data(all_data)

    messagebox.showinfo("Reset", "All data has been deleted.")

    # Refresh lại dashboard
    show_dashboard(current_name, current_dob)   

# ===== CHART FUNCTIONS (PUT HERE) =====

def show_income_page():
    show_dashboard(current_name, current_dob)

    main_area = root.winfo_children()[1]

    for widget in main_area.winfo_children():
        widget.destroy()
    tk.Label(main_area, text="Income History",
             font=("Helvetica", 28, "bold"),
             bg="#f5f7fb").pack(anchor="w", padx=35, pady=30)

    if len(current_history) == 0:
        tk.Label(main_area, text="No income history yet.",
                 font=("Helvetica", 14),
                 bg="#f5f7fb").pack(anchor="w", padx=35)
        return

    fig, ax = plt.subplots(figsize=(8, 6))

    dates = [item["date"][:10] for item in current_history]
    incomes = [item["income"] for item in current_history]

    ax.plot(dates, incomes, marker="o")
    ax.set_title("Income Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Income ($)")
    ax.tick_params(axis="x", rotation=30)

    canvas = FigureCanvasTkAgg(fig, master=main_area)
    canvas.draw()
    canvas.get_tk_widget().pack(padx=35, pady=20)


def show_expense_page():

    show_dashboard(current_name, current_dob)

    main_area = root.winfo_children()[1]

    for widget in main_area.winfo_children():
        widget.destroy()

    if len(expenses) == 0:
        tk.Label(main_area, text="No expenses yet.",
                 font=("Helvetica", 14),
                 bg="#f5f7fb").pack(anchor="w", padx=35)
        return

    category_totals = {}

    for item in expenses:
        category = item["category"]
        amount = item["amount"]
        category_totals[category] = category_totals.get(category, 0) + amount

    fig, ax = plt.subplots(figsize=(8, 7))

    ax.bar(category_totals.keys(), category_totals.values())
    ax.set_title("Expense by Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Amount ($)")
    ax.tick_params(axis="x", rotation=30)

    canvas = FigureCanvasTkAgg(fig, master=main_area)
    canvas.draw()
    canvas.get_tk_widget().pack(padx=35, pady=20)

def show_insights_report_page():
    show_dashboard(current_name, current_dob)

    main_area = root.winfo_children()[1]

    for widget in main_area.winfo_children():
        widget.destroy()

    tk.Label(main_area, text="Insights & Reports",
             font=("Helvetica", 28, "bold"),
             bg="#f5f7fb").pack(anchor="w", padx=35, pady=(30, 10))

    if current_income <= 0 and len(expenses) == 0:
        tk.Label(main_area, text="No report data yet.",
                 font=("Helvetica", 14),
                 bg="#f5f7fb").pack(anchor="w", padx=35)
        return

    total_expense = sum(item["amount"] for item in expenses)
    savings = current_income - total_expense

    category_totals = {}
    for item in expenses:
        category = item["category"]
        amount = item["amount"]
        category_totals[category] = category_totals.get(category, 0) + amount

    if category_totals:
        highest_category = max(category_totals, key=category_totals.get)
        highest_amount = category_totals[highest_category]
    else:
        highest_category = "None"
        highest_amount = 0

    if savings > 0:
        status = "Saving money"
        advice = "You are doing well. Keep tracking expenses regularly."
    elif savings == 0:
        status = "Break even"
        advice = "You are spending exactly your income. Try reducing one flexible category."
    else:
        status = "Overspending"
        advice = "You are overspending. Start by reducing your highest expense category."

    report_box = tk.Frame(main_area, bg="white",
                          highlightbackground="#dfe3eb",
                          highlightthickness=1)
    report_box.pack(fill="both", expand=True, padx=35, pady=20)

    report_items = [
        ("Total Income", f"${current_income:.2f}"),
        ("Total Expense", f"${total_expense:.2f}"),
        ("Savings", f"${savings:.2f}"),
        ("Status", status),
        ("Highest Spending Category", f"{highest_category} (${highest_amount:.2f})"),
        ("Recommendation", advice)
    ]

    for title, value in report_items:
        tk.Label(report_box, text=title + ":",
                 font=("Helvetica", 12, "bold"),
                 bg="white").pack(anchor="w", padx=25, pady=(18, 3))

        tk.Label(report_box, text=value,
                 font=("Helvetica", 11),
                 bg="white",
                 fg="#374151",
                 wraplength=800,
                 justify="left").pack(anchor="w", padx=25)

def show_login():
    clear_window()

    card = tk.Frame(root, bg="white", width=420, height=390,
                    highlightbackground="#dfe3eb", highlightthickness=1)
    card.place(relx=0.5, rely=0.5, anchor="center")
    card.pack_propagate(False)

    tk.Label(card, text="Welcome to FinHusk", font=("Helvetica", 26, "bold"),
             bg="white").pack(pady=(40, 10))

    tk.Label(card, text="Track smarter. Spend better",
             font=("Helvetica", 11), bg="white", fg="#6b7280").pack(pady=(0, 20))

    tk.Label(card, text="Full Name", font=("Helvetica", 11),
             bg="white").pack(anchor="w", padx=45)

    global name_entry
    name_entry = tk.Entry(card, font=("Helvetica", 12), bd=0, bg="#f3f4f6")
    name_entry.pack(fill="x", padx=45, ipady=10, pady=(6, 15))

    tk.Label(card, text="Date of Birth (MM/DD/YYYY)", font=("Helvetica", 11),
             bg="white").pack(anchor="w", padx=45)

    global dob_entry
    dob_entry = tk.Entry(card, font=("Helvetica", 12), bd=0, bg="#f3f4f6")
    dob_entry.pack(fill="x", padx=45, ipady=10, pady=(6, 25))
    dob_entry.bind("<KeyRelease>", format_dob)

    tk.Button(card, text="Enter Dashboard", font=("Helvetica", 12, "bold"),
              bg="#111827", fg="white", bd=0, pady=12,
              command=validate_login).pack(fill="x", padx=45)
    


def show_dashboard(name, dob):
    clear_window()

    sidebar = tk.Frame(root, bg="#0f172a", width=240)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    main_area = tk.Frame(root, bg="#f5f7fb")
    main_area.pack(side="left", fill="both", expand=True)

    tk.Label(sidebar, text="◉ Budget Buddy Assistant",
             font=("Helvetica", 12, "bold"), bg="#0f172a",
             fg="white").pack(anchor="w", padx=18, pady=(20, 30))

    tk.Label(sidebar, text="👤", font=("Helvetica", 40),
             bg="#dbeafe").pack(pady=(0, 8))

    tk.Label(sidebar, text=name, font=("Helvetica", 18, "bold"),
             bg="#0f172a", fg="white").pack()

    tk.Label(sidebar, text="● Online", font=("Helvetica", 11),
             bg="#0f172a", fg="#22c55e").pack(pady=(6, 10))

    tk.Label(sidebar, text=f"DOB: {dob}", font=("Helvetica", 10),
             bg="#0f172a", fg="white").pack(pady=(0, 25))

    tk.Button(sidebar, text="📊 Dashboard", font=("Helvetica", 12),
          anchor="w", bg="#0f172a", fg="white",
          bd=0, padx=18, pady=14,
          command=lambda: show_dashboard(current_name, current_dob)
          ).pack(fill="x", padx=15, pady=4)

    tk.Button(sidebar, text="💰 Income", font=("Helvetica", 12),
            anchor="w", bg="#0f172a", fg="white",
            bd=0, padx=18, pady=14,
            command=show_income_page
            ).pack(fill="x", padx=15, pady=4)

    tk.Button(sidebar, text="💳 Expense", font=("Helvetica", 12),
            anchor="w", bg="#0f172a", fg="white",
            bd=0, padx=18, pady=14,
            command=show_expense_page
            ).pack(fill="x", padx=15, pady=4)

    tk.Button(sidebar, text="🔍 Insights & Reports", font=("Helvetica", 12),
        anchor="w", bg="#0f172a", fg="white",
        bd=0, padx=18, pady=14,
        command=show_insights_report_page
        ).pack(fill="x", padx=15, pady=4)

    tk.Button(sidebar, text="🔄 Reset All Data", font=("Helvetica", 12),
          anchor="w", bg="#991b1b", fg="white",
          bd=0, padx=18, pady=14,
          command=reset_all_data
          ).pack(fill="x", padx=15, pady=(40, 8))

    tk.Button(sidebar, text="🚪 Log Out", font=("Helvetica", 12),
              anchor="w", bg="#334155", fg="white",
              bd=0, padx=18, pady=14,
              command=show_login).pack(fill="x", padx=15)

    tk.Label(main_area, text="Hi, I’m FinHusk!",
             font=("Helvetica", 30, "bold"), bg="#f5f7fb",
             fg="#111827").pack(anchor="w", padx=35, pady=(30, 8))

    tk.Label(main_area,
             text="Dashboard overview — income, expenses, savings, budget status, and quick insights.",
             font=("Helvetica", 13), bg="#f5f7fb",
             fg="#6b7280").pack(anchor="w", padx=35)

    cards_frame = tk.Frame(main_area, bg="#f5f7fb")
    cards_frame.pack(fill="x", padx=35, pady=25)

    for i in range(4):
        cards_frame.grid_columnconfigure(i, weight=1, uniform="cards")

    cards = [
        ("Total Income", "$0.00", "💵"),
        ("Total Expense", "$0.00", "↓"),
        ("Savings", "$0.00", "🐷"),
        ("Status", "No data", "◔")
    ]

    global income_value_label, expense_value_label, savings_value_label, status_value_label

    income_card, income_value_label = create_card(cards_frame, "Total Income", "$0.00", "💵")
    expense_card, expense_value_label = create_card(cards_frame, "Total Expense", "$0.00", "↓")
    savings_card, savings_value_label = create_card(cards_frame, "Savings", "$0.00", "🐷")
    status_card, status_value_label = create_card(cards_frame, "Status", "No data", "◔")

    income_card.grid(row=0, column=0, sticky="ew", padx=10)
    expense_card.grid(row=0, column=1, sticky="ew", padx=10)
    savings_card.grid(row=0, column=2, sticky="ew", padx=10)
    status_card.grid(row=0, column=3, sticky="ew", padx=10)

    content = tk.Frame(main_area, bg="#f5f7fb")
    content.pack(fill="both", expand=True, padx=35, pady=10)
    content.grid_columnconfigure(0, weight=1)
    content.grid_columnconfigure(1, weight=1)

    expense_box = tk.Frame(content, bg="white",
                           highlightbackground="#dfe3eb", highlightthickness=1)
    expense_box.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

    tk.Label(expense_box, text="Add New Expense",
             font=("Helvetica", 16, "bold"), bg="white").pack(anchor="w", padx=20, pady=(20, 15))

    global income_entry, category_box, amount_entry, description_entry, expense_listbox

    tk.Label(expense_box, text="Monthly Income", font=("Helvetica", 10, "bold"),
            bg="white").pack(anchor="w", padx=20)
    income_entry = tk.Entry(expense_box, font=("Helvetica", 11), bd=0, bg="#f3f4f6")
    income_entry.pack(fill="x", padx=20, ipady=8, pady=(5, 12))

    tk.Label(expense_box, text="Category", font=("Helvetica", 10, "bold"),
            bg="white").pack(anchor="w", padx=20)

    category_box = ttk.Combobox(
        expense_box,
        values=["Grocery", "Gas", "Food", "Rent", "Transportation", "Entertainment", "Other"],
        state="readonly",
        font=("Helvetica", 11)
    )
    category_box.set("Grocery")
    category_box.pack(fill="x", padx=20, ipady=5, pady=(5, 12))

    tk.Label(expense_box, text="Amount ($)", font=("Helvetica", 10, "bold"),
            bg="white").pack(anchor="w", padx=20)
    amount_entry = tk.Entry(expense_box, font=("Helvetica", 11), bd=0, bg="#f3f4f6")
    amount_entry.pack(fill="x", padx=20, ipady=8, pady=(5, 12))

    tk.Label(expense_box, text="Description (optional)", font=("Helvetica", 10, "bold"),
            bg="white").pack(anchor="w", padx=20)
    description_entry = tk.Entry(expense_box, font=("Helvetica", 11), bd=0, bg="#f3f4f6")
    description_entry.pack(fill="x", padx=20, ipady=8, pady=(5, 12))

    expense_listbox = tk.Listbox(expense_box, height=4, bd=0, bg="#f3f4f6")
    expense_listbox.pack(fill="x", padx=20, pady=(5, 12))
    for item in expenses:
        expense_listbox.insert(
            tk.END,
            f"{item['category']} - ${item['amount']:.2f} - {item['description']}"
    )

    button_row = tk.Frame(expense_box, bg="white")
    button_row.pack(fill="x", padx=20, pady=10)

    tk.Button(button_row, text="Save Snapshot", bg="#2563eb",
          fg="white", font=("Helvetica", 11, "bold"),
          bd=0, pady=12,
          command=save_snapshot).pack(side="left", fill="x", expand=True, padx=(0, 8))

    tk.Button(button_row, text="Clear Items", bg="#e5e7eb",
              fg="#111827", font=("Helvetica", 11, "bold"),
              bd=0, pady=12).pack(side="left", fill="x", expand=True, padx=(8, 0))

    insight_box = tk.Frame(content, bg="white",
                           highlightbackground="#dfe3eb", highlightthickness=1)
    insight_box.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

    tk.Label(insight_box, text="Smart Insights",
             font=("Helvetica", 16, "bold"), bg="white").pack(anchor="w", padx=20, pady=(20, 20))

    global pattern_label, feedback_label, recommendation_label, category_summary_label

    tk.Label(insight_box, text="Spending Pattern:", font=("Helvetica", 11, "bold"),
            bg="white").pack(anchor="w", padx=20, pady=(0, 5))
    pattern_label = tk.Label(insight_box, text="No data yet.", font=("Helvetica", 10),
                            bg="white", fg="#374151", wraplength=450, justify="left")
    pattern_label.pack(anchor="w", padx=20, pady=(0, 18))

    tk.Label(insight_box, text="AI Feedback:", font=("Helvetica", 11, "bold"),
            bg="white").pack(anchor="w", padx=20, pady=(0, 5))
    feedback_label = tk.Label(insight_box, text="No data yet.", font=("Helvetica", 10),
                            bg="white", fg="#374151", wraplength=450, justify="left")
    feedback_label.pack(anchor="w", padx=20, pady=(0, 18))

    tk.Label(insight_box, text="Recommendation:", font=("Helvetica", 11, "bold"),
            bg="white").pack(anchor="w", padx=20, pady=(0, 5))
    recommendation_label = tk.Label(insight_box, text="No data yet.", font=("Helvetica", 10),
                                    bg="white", fg="#374151", wraplength=450, justify="left")
    recommendation_label.pack(anchor="w", padx=20, pady=(0, 18))

    tk.Label(insight_box, text="Category Summary:", font=("Helvetica", 11, "bold"),
            bg="white").pack(anchor="w", padx=20, pady=(0, 5))
    category_summary_label = tk.Label(insight_box, text="No data yet.", font=("Helvetica", 10),
                                    bg="white", fg="#374151", wraplength=450, justify="left")
    category_summary_label.pack(anchor="w", padx=20, pady=(0, 18))
    if current_income > 0 or len(expenses) > 0:
        total_expense = sum(item["amount"] for item in expenses)
        savings = current_income - total_expense

        if savings > 0:
            status = "Saving money"
        elif savings == 0:
            status = "Break even"
        else:
            status = "Overspending"

        income_value_label.config(text=f"${current_income:.2f}")
        expense_value_label.config(text=f"${total_expense:.2f}")
        savings_value_label.config(text=f"${savings:.2f}")
        status_value_label.config(text=status)
        category_totals = {}

        for item in expenses:
            category = item["category"]
            amount = item["amount"]

            if category not in category_totals:
                category_totals[category] = 0

            category_totals[category] += amount

        highest_category = max(category_totals, key=category_totals.get)

        pattern_label.config(text=f"You spent the most on {highest_category}.")

        feedback_label.config(
            text=f"You spent ${total_expense:.2f} out of ${current_income:.2f} income."
        )

        if savings > 0:
            recommendation = "Good job. You are still saving money."
        elif savings == 0:
            recommendation = "You are breaking even. Try to reduce one category."
        else:
            recommendation = "Warning: You are overspending. Review your largest expense category."

        recommendation_label.config(text=recommendation)

        summary_text = ""
        for category, amount in category_totals.items():
            summary_text += f"{category}: ${amount:.2f}\n"

        category_summary_label.config(text=summary_text)

root = tk.Tk()
root.title("Budget Buddy Assistant")
root.geometry("1200x750")
root.configure(bg="#f5f7fb")

show_login()
root.mainloop()