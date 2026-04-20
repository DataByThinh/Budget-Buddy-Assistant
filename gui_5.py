import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from collections import defaultdict
import json
import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


DATA_FILE = "budget_buddy_data.json"


class BudgetBuddyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Buddy Assistant")
        self.root.state("zoomed")
        self.root.minsize(1400, 850)
        self.root.configure(bg="#f5f7fb")
        self.root.resizable(True, True)

        self.user_name = ""
        self.user_dob = ""

        self.current_expense_items = []

        self.data = {
            "user": {},
            "history": []
        }

        self.load_data()
        self.show_login_page()

    # -------------------------
    # Data
    # -------------------------
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {"user": {}, "history": []}

    def save_data_file(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    # -------------------------
    # Helpers
    # -------------------------
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def safe_float(self, value):
        value = value.strip()
        if value == "":
            return 0.0
        return float(value)

    def format_dob(self, event=None):
        text = self.dob_var.get()
        digits = "".join(ch for ch in text if ch.isdigit())[:8]

        formatted = ""
        if len(digits) >= 1:
            formatted += digits[:2]
        if len(digits) >= 3:
            formatted = digits[:2] + "/" + digits[2:4]
        if len(digits) >= 5:
            formatted = digits[:2] + "/" + digits[2:4] + "/" + digits[4:8]

        self.dob_var.set(formatted)

    def check_budget_status(self, income, expense):
        if income <= 0 and expense <= 0:
            return "No data", "#6b7280"

        ratio = expense / income if income > 0 else 0

        if ratio < 0.7:
            return "Healthy spending", "#2e7d32"
        elif ratio <= 1.0:
            return "Moderate spending", "#f9a825"
        else:
            return "Over budget", "#c62828"

    def build_category_summary(self, expense_items, total_expense):
        categories = defaultdict(float)

        for item in expense_items:
            category = item["category"]
            amount = item["amount"]
            categories[category] += amount

        categorized_total = sum(categories.values())
        other = max(total_expense - categorized_total, 0)

        if other > 0:
            categories["Other"] += other

        return dict(categories)

    def get_pattern_detection(self, categories, income, expense):
        if expense == 0:
            return "No spending data yet. Add some expense items to detect patterns."

        if not categories:
            return "No categorized expense items yet."

        top_category = max(categories, key=categories.get)
        top_value = categories[top_category]
        share = (top_value / expense) * 100 if expense > 0 else 0

        if expense > income and income > 0:
            return f"You are currently over budget. {top_category} is the largest spending category."

        if share >= 40:
            return f"Your spending is highly concentrated in {top_category} ({share:.1f}% of total expense)."

        if len(categories) >= 4:
            return "Your spending is spread across multiple categories, which suggests a diversified pattern."

        return f"{top_category} is currently your biggest expense driver."

    def get_ai_feedback(self, income, expense, savings, categories):
        if income == 0 and expense == 0:
            return "Hi — I’m ready to review your budget. Add your income, total expense, and expense items to begin."

        if not categories:
            return "You’ve entered totals, but categorized expenses will help me give more accurate feedback."

        top_category = max(categories, key=categories.get)
        ratio = expense / income if income > 0 else 0

        if ratio < 0.7:
            return (
                f"You are currently in a healthy range. Your biggest expense category is {top_category}, "
                f"but you still have a comfortable savings buffer."
            )
        elif ratio <= 1.0:
            return (
                f"Your budget is still manageable, but your margin is getting tighter. "
                f"I would keep a closer eye on {top_category} next."
            )
        else:
            return (
                f"Your spending is above your income right now, which may create short-term pressure. "
                f"Start by reviewing {top_category} first."
            )

    def get_personalized_recommendation(self, income, expense, categories):
        if income <= 0:
            return "Enter your income first so I can generate a realistic recommendation."

        if not categories:
            return "Add categorized expense items so I can provide a more personalized recommendation."

        top_category = max(categories, key=categories.get)
        top_amount = categories[top_category]
        savings = income - expense

        if expense > income:
            return f"Recommendation: reduce {top_category} by at least ${max(top_amount * 0.15, 20):.2f} to move closer to balance."

        if savings < income * 0.2:
            return f"Recommendation: your savings buffer is thin. Start by reviewing {top_category}, which is currently ${top_amount:.2f}."

        return "Recommendation: your budget looks stable. Consider moving part of your savings into an emergency or goal-based fund."

    def get_daily_checkin(self, income, expense):
        today = datetime.now().strftime("%B %d, %Y")

        if income == 0 and expense == 0:
            return f"Daily Check-in — {today}: No entries yet. Add your monthly snapshot to begin."

        if expense > income and income > 0:
            return f"Daily Check-in — {today}: You are over budget. Let’s make one small adjustment today."

        if income > 0 and expense > income * 0.8:
            return f"Daily Check-in — {today}: You are close to your spending limit. Stay mindful with the rest of your budget."

        return f"Daily Check-in — {today}: You are doing well. Your spending is in a manageable range."

    # -------------------------
    # Login Page
    # -------------------------
    def show_login_page(self):
        self.clear_window()

        main_frame = tk.Frame(self.root, bg="#f5f7fb")
        main_frame.pack(fill="both", expand=True)

        card = tk.Frame(
            main_frame,
            bg="white",
            width=460,
            height=430,
            highlightbackground="#dfe3eb",
            highlightthickness=1
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        tk.Label(
            card,
            text="Budget Buddy",
            font=("Helvetica", 26, "bold"),
            bg="white",
            fg="#111827"
        ).pack(pady=(35, 8))

        tk.Label(
            card,
            text="A calm digital wallet for smarter spending",
            font=("Helvetica", 11),
            bg="white",
            fg="#6b7280"
        ).pack(pady=(0, 8))

        tk.Label(
            card,
            text="Powered by Thinh Nguyen",
            font=("Helvetica", 10, "italic"),
            bg="white",
            fg="#9ca3af"
        ).pack(pady=(0, 22))

        tk.Label(card, text="Full Name", font=("Helvetica", 11), bg="white", fg="#374151").pack(anchor="w", padx=45)
        self.name_entry = tk.Entry(card, font=("Helvetica", 12), bd=0, bg="#f3f4f6", fg="#111827")
        self.name_entry.pack(padx=45, fill="x", ipady=12, pady=(6, 14))

        tk.Label(card, text="Date of Birth (MM/DD/YYYY)", font=("Helvetica", 11), bg="white", fg="#374151").pack(anchor="w", padx=45)
        self.dob_var = tk.StringVar()
        self.dob_entry = tk.Entry(card, textvariable=self.dob_var, font=("Helvetica", 12), bd=0, bg="#f3f4f6", fg="#111827")
        self.dob_entry.pack(padx=45, fill="x", ipady=12, pady=(6, 22))
        self.dob_entry.bind("<KeyRelease>", self.format_dob)

        saved_user = self.data.get("user", {})
        if saved_user:
            self.name_entry.insert(0, saved_user.get("name", ""))
            self.dob_var.set(saved_user.get("dob", ""))

        tk.Button(
            card,
            text="Enter Dashboard",
            font=("Helvetica", 12, "bold"),
            bg="#111827",
            fg="white",
            activebackground="#1f2937",
            activeforeground="white",
            bd=0,
            padx=10,
            pady=12,
            command=self.login
        ).pack(padx=45, fill="x")

    def login(self):
        name = self.name_entry.get().strip()
        dob = self.dob_entry.get().strip()

        if not name or not dob:
            messagebox.showerror("Input Error", "Please enter both Name and DOB.")
            return

        try:
            datetime.strptime(dob, "%m/%d/%Y")
        except ValueError:
            messagebox.showerror("Format Error", "DOB must be in MM/DD/YYYY format.")
            return

        self.user_name = name
        self.user_dob = dob
        self.data["user"] = {"name": name, "dob": dob}
        self.save_data_file()
        self.show_dashboard()

    # -------------------------
    # Dashboard
    # -------------------------
    def show_dashboard(self):
        self.clear_window()

        app_frame = tk.Frame(self.root, bg="#f5f7fb")
        app_frame.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(app_frame, bg="#0f172a", width=170)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main_area = tk.Frame(app_frame, bg="#f5f7fb")
        self.main_area.pack(side="left", fill="both", expand=True)

        # Sidebar
        tk.Label(
            self.sidebar,
            text="Budget Buddy",
            font=("Helvetica", 18, "bold"),
            bg="#0f172a",
            fg="white"
        ).pack(anchor="w", padx=20, pady=(30, 10))

        tk.Label(
            self.sidebar,
            text=self.user_name,
            font=("Helvetica", 12, "bold"),
            bg="#0f172a",
            fg="#e5e7eb"
        ).pack(anchor="w", padx=20, pady=(18, 4))

        tk.Label(
            self.sidebar,
            text=f"DOB: {self.user_dob}",
            font=("Helvetica", 10),
            bg="#0f172a",
            fg="#94a3b8"
        ).pack(anchor="w", padx=20, pady=(0, 20))

        tk.Button(
            self.sidebar,
            text="Log Out",
            font=("Helvetica", 11, "bold"),
            bg="#334155",
            fg="white",
            activebackground="#475569",
            activeforeground="white",
            bd=0,
            padx=10,
            pady=10,
            command=self.show_login_page
        ).pack(anchor="w", padx=20, pady=10)

        # Header
        header = tk.Frame(self.main_area, bg="#f5f7fb")
        header.pack(fill="x", padx=24, pady=(20, 10))

        tk.Label(
            header,
            text="Hi, I’m Penny.",
            font=("Helvetica", 26, "bold"),
            bg="#f5f7fb",
            fg="#111827"
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Your budgeting assistant — tracking spending, spotting patterns, and helping you make calmer money decisions.",
            font=("Helvetica", 12),
            bg="#f5f7fb",
            fg="#6b7280"
        ).pack(anchor="w", pady=(4, 0))

        # Cards row
        cards_frame = tk.Frame(self.main_area, bg="#f5f7fb")
        cards_frame.pack(fill="x", padx=24, pady=(6, 12))

        self.income_card = self.create_card(cards_frame, "Income", "$0.00", "#d1fae5")
        self.income_card.grid(row=0, column=0, padx=(0, 10))

        self.expense_card = self.create_card(cards_frame, "Expense", "$0.00", "#fee2e2")
        self.expense_card.grid(row=0, column=1, padx=10)

        self.savings_card = self.create_card(cards_frame, "Savings", "$0.00", "#dbeafe")
        self.savings_card.grid(row=0, column=2, padx=10)

        self.status_card = self.create_card(cards_frame, "Status", "No data", "#ede9fe")
        self.status_card.grid(row=0, column=3, padx=(10, 0))

        # Main content
        content = tk.Frame(self.main_area, bg="#f5f7fb")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        content.grid_columnconfigure(0, weight=2, uniform="col")
        content.grid_columnconfigure(1, weight=2, uniform="col")
        content.grid_columnconfigure(2, weight=3, uniform="col")
        content.grid_rowconfigure(0, weight=1)

        # ---------------- Left panel ----------------
        input_card = tk.Frame(content, bg="white", highlightbackground="#dfe3eb", highlightthickness=1)
        input_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(input_card, text="Budget Input", font=("Helvetica", 18, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=18, pady=(18, 6))


        self.create_entry_field(input_card, "Monthly Income", "income_entry")

        tk.Label(input_card, text="Expense Category", font=("Helvetica", 10), bg="white", fg="#374151").pack(anchor="w", padx=18)
        self.category_combobox = ttk.Combobox(
            input_card,
            values=["Food", "Transport", "Entertainment", "Rent", "Bills", "Shopping", "Other"],
            state="readonly",
            font=("Helvetica", 10)
        )
        self.category_combobox.pack(padx=18, fill="x", pady=(4, 8), ipady=4)
        self.category_combobox.set("Food")

        tk.Label(input_card, text="Expense Amount", font=("Helvetica", 10), bg="white", fg="#374151").pack(anchor="w", padx=18)
        self.expense_amount_entry = tk.Entry(input_card, font=("Helvetica", 11), bd=0, bg="#f3f4f6", fg="#111827")
        self.expense_amount_entry.pack(padx=18, fill="x", ipady=8, pady=(4, 10))

        btn_row = tk.Frame(input_card, bg="white")
        btn_row.pack(fill="x", padx=18, pady=(0, 10))

        tk.Button(
            btn_row,
            text="Add Expense",
            font=("Helvetica", 10, "bold"),
            bg="#111827",
            fg="white",
            bd=0,
            pady=10,
            command=self.add_expense_item
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        tk.Button(
            btn_row,
            text="Clear Items",
            font=("Helvetica", 10, "bold"),
            bg="#e5e7eb",
            fg="#111827",
            bd=0,
            pady=10,
            command=self.clear_expense_items
        ).pack(side="left", fill="x", expand=True, padx=(6, 0))

        tk.Label(input_card, text="Expense Items", font=("Helvetica", 13, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=18, pady=(4, 6))

        self.expense_listbox = tk.Listbox(
            input_card,
            font=("Helvetica", 10),
            bd=0,
            bg="#f3f4f6",
            fg="#111827",
            height=10
        )
        self.expense_listbox.pack(padx=18, fill="x", pady=(0, 12))

        save_frame = tk.Frame(input_card, bg="white")
        save_frame.pack(fill="x", padx=18, pady=(0, 8))

        tk.Button(
            save_frame,
            text="Save Snapshot",
            font=("Helvetica", 11, "bold"),
            bg="#111827",
            fg="white",
            bd=0,
            pady=10,
            command=self.save_snapshot
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        tk.Button(
            save_frame,
            text="Load Latest",
            font=("Helvetica", 11, "bold"),
            bg="#e5e7eb",
            fg="#111827",
            bd=0,
            pady=10,
            command=self.load_latest_snapshot
        ).pack(side="left", fill="x", expand=True, padx=(6, 0))

        self.checkin_label = tk.Label(
            input_card,
            text="Daily Check-in: No data yet.",
            font=("Helvetica", 10),
            bg="white",
            fg="#6b7280",
            wraplength=320,
            justify="left"
        )
        self.checkin_label.pack(anchor="w", padx=18, pady=(10, 8))

        tk.Label(input_card, text="Saved Snapshots", font=("Helvetica", 13, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=18, pady=(12, 6))

        self.history_listbox = tk.Listbox(
            input_card,
            font=("Helvetica", 10),
            bd=0,
            bg="#f3f4f6",
            fg="#111827",
            height=8
        )
        self.history_listbox.pack(padx=18, fill="both", expand=True, pady=(0, 18))
        self.history_listbox.bind("<<ListboxSelect>>", self.load_selected_snapshot)

        # ---------------- Middle panel ----------------
        feedback_card = tk.Frame(content, bg="white", highlightbackground="#dfe3eb", highlightthickness=1)
        feedback_card.grid(row=0, column=1, sticky="nsew", padx=10)

        tk.Label(feedback_card, text="Smart Insights", font=("Helvetica", 18, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=18, pady=(18, 12))

        tk.Label(feedback_card, text="Spending Pattern Detection", font=("Helvetica", 12, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=18, pady=(0, 6))
        self.pattern_label = tk.Label(feedback_card, text="No data yet.", font=("Helvetica", 10), bg="white", fg="#6b7280", wraplength=300, justify="left")
        self.pattern_label.pack(anchor="w", padx=18, pady=(0, 14))

        tk.Label(feedback_card, text="Auto Financial Feedback", font=("Helvetica", 12, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=18, pady=(0, 6))
        self.ai_feedback_label = tk.Label(feedback_card, text="No data yet.", font=("Helvetica", 10), bg="white", fg="#6b7280", wraplength=300, justify="left")
        self.ai_feedback_label.pack(anchor="w", padx=18, pady=(0, 14))

        tk.Label(feedback_card, text="Personalized Recommendation", font=("Helvetica", 12, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=18, pady=(0, 6))
        self.recommendation_label = tk.Label(feedback_card, text="No data yet.", font=("Helvetica", 10), bg="white", fg="#6b7280", wraplength=300, justify="left")
        self.recommendation_label.pack(anchor="w", padx=18, pady=(0, 14))

        tk.Label(feedback_card, text="Category Summary", font=("Helvetica", 12, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=18, pady=(0, 6))
        self.category_summary_label = tk.Label(feedback_card, text="No data yet.", font=("Helvetica", 10), bg="white", fg="#6b7280", wraplength=300, justify="left")
        self.category_summary_label.pack(anchor="w", padx=18, pady=(0, 14))

        self.progress_text = tk.Label(feedback_card, text="0% of income spent", font=("Helvetica", 10), bg="white", fg="#6b7280")
        self.progress_text.pack(anchor="w", padx=18, pady=(6, 8))

        self.progress_canvas = tk.Canvas(feedback_card, width=300, height=24, bg="white", highlightthickness=0)
        self.progress_canvas.pack(anchor="w", padx=18, pady=(0, 10))
        self.progress_canvas.create_rectangle(0, 7, 300, 18, fill="#e5e7eb", outline="")
        self.progress_fill = self.progress_canvas.create_rectangle(0, 7, 0, 18, fill="#111827", outline="")

        # ---------------- Right panel ----------------
        charts_card = tk.Frame(content, bg="white", highlightbackground="#dfe3eb", highlightthickness=1)
        charts_card.grid(row=0, column=2, sticky="nsew", padx=(10, 0))

        tk.Label(
            charts_card,
            text="Visual Dashboard",
            font=("Helvetica", 18, "bold"),
            bg="white",
            fg="#111827"
        ).pack(anchor="w", padx=18, pady=(18, 10))

        pie_container = tk.Frame(charts_card, bg="white", height=170)
        pie_container.pack(fill="x", padx=12, pady=(0, 6))
        pie_container.pack_propagate(False)
        self.pie_frame = pie_container

        line_container = tk.Frame(charts_card, bg="white", height=260)
        line_container.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        line_container.pack_propagate(False)
        self.line_frame = line_container

        self.refresh_history_list()
        self.draw_default_pie()
        self.draw_trend_chart()

        if self.data["history"]:
            self.load_latest_snapshot()

    def create_entry_field(self, parent, label_text, attr_name):
        tk.Label(parent, text=label_text, font=("Helvetica", 10), bg="white", fg="#374151").pack(anchor="w", padx=18)
        entry = tk.Entry(parent, font=("Helvetica", 11), bd=0, bg="#f3f4f6", fg="#111827")
        entry.pack(padx=18, fill="x", ipady=8, pady=(4, 8))
        setattr(self, attr_name, entry)

    def create_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg="white", width=230, height=95, highlightbackground="#dfe3eb", highlightthickness=1)
        card.pack_propagate(False)

        top = tk.Frame(card, bg=color, height=10)
        top.pack(fill="x")

        tk.Label(card, text=title, font=("Helvetica", 10), bg="white", fg="#6b7280").pack(anchor="w", padx=14, pady=(12, 2))
        value_label = tk.Label(card, text=value, font=("Helvetica", 18, "bold"), bg="white", fg="#111827")
        value_label.pack(anchor="w", padx=14)

        card.value_label = value_label
        return card

    # -------------------------
    # Expense items
    # -------------------------
    def add_expense_item(self):
        try:
            category = self.category_combobox.get().strip()
            amount = self.safe_float(self.expense_amount_entry.get())

            if not category:
                messagebox.showerror("Input Error", "Please choose an expense category.")
                return

            if amount <= 0:
                messagebox.showerror("Input Error", "Expense amount must be greater than 0.")
                return

            item = {"category": category, "amount": amount}
            self.current_expense_items.append(item)

            self.refresh_expense_items_list()
            self.expense_amount_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid expense amount.")

    def clear_expense_items(self):
        self.current_expense_items = []
        self.refresh_expense_items_list()

    def refresh_expense_items_list(self):
        self.expense_listbox.delete(0, tk.END)
        for idx, item in enumerate(self.current_expense_items, start=1):
            self.expense_listbox.insert(
                tk.END,
                f"{idx}. {item['category']} — ${item['amount']:.2f}"
            )

    # -------------------------
    # Snapshot save/load
    # -------------------------
    def save_snapshot(self):
        try:
            income = self.safe_float(self.income_entry.get())
            expense = sum(item["amount"] for item in self.current_expense_items)

            if income < 0 or expense < 0:
                messagebox.showerror("Input Error", "Income and expense must be positive.")
                return

            snapshot = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "income": income,
                "expense": expense,
                "expense_items": self.current_expense_items.copy()
            }

            self.data["history"].append(snapshot)
            self.save_data_file()
            self.refresh_history_list()
            self.apply_snapshot(snapshot)

            messagebox.showinfo("Saved", "Budget snapshot saved successfully.")

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers.")

    def refresh_history_list(self):
        if hasattr(self, "history_listbox"):
            self.history_listbox.delete(0, tk.END)
            for item in reversed(self.data["history"]):
                display = f"{item['date']} | Income ${item['income']:.2f} | Expense ${item['expense']:.2f}"
                self.history_listbox.insert(tk.END, display)

    def load_latest_snapshot(self):
        if not self.data["history"]:
            messagebox.showwarning("No Data", "No saved snapshots yet.")
            return

        snapshot = self.data["history"][-1]
        self.fill_entries(snapshot)
        self.apply_snapshot(snapshot)

    def load_selected_snapshot(self, event=None):
        if not self.history_listbox.curselection():
            return

        selected_index = self.history_listbox.curselection()[0]
        real_index = len(self.data["history"]) - 1 - selected_index
        snapshot = self.data["history"][real_index]

        self.fill_entries(snapshot)
        self.apply_snapshot(snapshot)

    def fill_entries(self, snapshot):
        self.income_entry.delete(0, tk.END)
        self.income_entry.insert(0, str(snapshot.get("income", 0)))

        self.expense_entry.delete(0, tk.END)
        self.expense_entry.insert(0, str(snapshot.get("expense", 0)))

        self.current_expense_items = snapshot.get("expense_items", []).copy()
        self.refresh_expense_items_list()

    # -------------------------
    # Apply snapshot
    # -------------------------
    def apply_snapshot(self, snapshot):
        income = snapshot["income"]
        expense = snapshot["expense"]
        expense_items = snapshot.get("expense_items", [])
        savings = income - expense

        categories = self.build_category_summary(expense_items, expense)
        status_text, status_color = self.check_budget_status(income, expense)

        self.income_card.value_label.config(text=f"${income:,.2f}")
        self.expense_card.value_label.config(text=f"${expense:,.2f}")
        self.savings_card.value_label.config(text=f"${savings:,.2f}")
        self.status_card.value_label.config(text=status_text, fg=status_color)

        pattern = self.get_pattern_detection(categories, income, expense)
        ai_feedback = self.get_ai_feedback(income, expense, savings, categories)
        recommendation = self.get_personalized_recommendation(income, expense, categories)
        checkin = self.get_daily_checkin(income, expense)

        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        summary_parts = [f"{name}: ${value:.2f}" for name, value in sorted_categories if value > 0]
        category_summary = ", ".join(summary_parts[:5]) if summary_parts else "No category data yet."

        self.pattern_label.config(text=pattern)
        self.ai_feedback_label.config(text=ai_feedback)
        self.recommendation_label.config(text=recommendation)
        self.checkin_label.config(text=checkin)
        self.category_summary_label.config(text=category_summary)

        percentage = (expense / income * 100) if income > 0 else 0
        capped_percentage = min(percentage, 100)
        fill_width = (capped_percentage / 100) * 300
        self.progress_canvas.coords(self.progress_fill, 0, 7, fill_width, 18)
        self.progress_text.config(text=f"{percentage:.1f}% of income spent")

        self.update_pie_chart(categories)
        self.draw_trend_chart()

    # -------------------------
    # Charts
    # -------------------------
        # -------------------------
    # Charts
    # -------------------------
    def draw_default_pie(self):
        for widget in self.pie_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(3.2, 2.0), dpi=100)
        fig.patch.set_facecolor("white")

        ax.pie(
            [1],
            labels=["No data"],
            autopct="%1.0f%%",
            startangle=90,
            textprops={"fontsize": 8}
        )
        ax.set_title("Expense Breakdown", fontsize=10, pad=6)

        fig.tight_layout(pad=1.0)

        canvas = FigureCanvasTkAgg(fig, master=self.pie_frame)
        canvas.draw()
        chart_widget = canvas.get_tk_widget()
        chart_widget.pack(fill="both", expand=True)

        plt.close(fig)

    def draw_default_bar(self):
        for widget in self.bar_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(3.2, 1.8), dpi=100)
        fig.patch.set_facecolor("white")

        ax.bar(["No data"], [0])
        ax.set_title("Expense by Category", fontsize=10, pad=6)
        ax.set_ylabel("Amount ($)", fontsize=8)
        ax.tick_params(axis="x", labelsize=8)
        ax.tick_params(axis="y", labelsize=8)

        fig.tight_layout(pad=1.0)

        canvas = FigureCanvasTkAgg(fig, master=self.bar_frame)
        canvas.draw()
        chart_widget = canvas.get_tk_widget()
        chart_widget.pack(fill="both", expand=True)

        plt.close(fig)

    def update_pie_chart(self, categories):
        for widget in self.pie_frame.winfo_children():
            widget.destroy()

        filtered = {k: v for k, v in categories.items() if v > 0}

        if not filtered:
            self.draw_default_pie()
            return

        labels = list(filtered.keys())
        values = list(filtered.values())

        fig, ax = plt.subplots(figsize=(3.2, 2.0), dpi=100)
        fig.patch.set_facecolor("white")

        ax.pie(
            values,
            labels=labels,
            autopct="%1.0f%%",
            startangle=90,
            textprops={"fontsize": 8}
        )
        ax.set_title("Expense Breakdown", fontsize=10, pad=6)

        fig.tight_layout(pad=1.0)

        canvas = FigureCanvasTkAgg(fig, master=self.pie_frame)
        canvas.draw()
        chart_widget = canvas.get_tk_widget()
        chart_widget.pack(fill="both", expand=True)

        plt.close(fig)

    def update_bar_chart(self, categories):
        for widget in self.bar_frame.winfo_children():
            widget.destroy()

        filtered = {k: v for k, v in categories.items() if v > 0}

        if not filtered:
            self.draw_default_bar()
            return

        labels = list(filtered.keys())
        values = list(filtered.values())

        fig, ax = plt.subplots(figsize=(3.2, 1.8), dpi=100)
        fig.patch.set_facecolor("white")

        ax.bar(labels, values)
        ax.set_title("Expense by Category", fontsize=10, pad=6)
        ax.set_ylabel("Amount ($)", fontsize=8)
        ax.tick_params(axis="x", rotation=20, labelsize=8)
        ax.tick_params(axis="y", labelsize=8)

        fig.tight_layout(pad=1.0)

        canvas = FigureCanvasTkAgg(fig, master=self.bar_frame)
        canvas.draw()
        chart_widget = canvas.get_tk_widget()
        chart_widget.pack(fill="both", expand=True)

        plt.close(fig)

    def draw_trend_chart(self):
        for widget in self.line_frame.winfo_children():
            widget.destroy()

        history = self.data["history"]

        fig, ax = plt.subplots(figsize=(3.0, 2.2), dpi=100)
        fig.patch.set_facecolor("white")

        if history:
            latest = history[-7:]
            labels = [item["date"][5:10] for item in latest]
            incomes = [item["income"] for item in latest]
            expenses = [item["expense"] for item in latest]

            ax.plot(labels, incomes, marker="o", label="Income")
            ax.plot(labels, expenses, marker="o", label="Expense")
            ax.set_title("Trend Over Time", fontsize=10, pad=6)
            ax.set_ylabel("Amount ($)", fontsize=8)
            ax.tick_params(axis="x", rotation=20, labelsize=8)
            ax.tick_params(axis="y", labelsize=8)
            ax.legend(fontsize=7, loc="upper right")
        else:
            ax.plot([0], [0])
            ax.set_title("Trend Over Time", fontsize=10, pad=6)
            ax.set_xticks([])
            ax.set_yticks([])

        fig.tight_layout(pad=1.0)

        canvas = FigureCanvasTkAgg(fig, master=self.line_frame)
        canvas.draw()
        chart_widget = canvas.get_tk_widget()
        chart_widget.pack(fill="both", expand=True)

        plt.close(fig)


if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetBuddyApp(root)
    root.mainloop()