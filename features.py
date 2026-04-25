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

        self.data = {"users": {}, "last_user_key": ""}

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
                self.data = {"users": {}, "last_user_key": ""}

        if "users" not in self.data:
            old_user = self.data.get("user", {})
            old_history = self.data.get("history", [])
            self.data = {"users": {}, "last_user_key": ""}
            if old_user.get("name") and old_user.get("dob"):
                key = self.make_user_key(old_user["name"], old_user["dob"])
                self.data["users"][key] = {
                    "name": old_user["name"],
                    "dob": old_user["dob"],
                    "history": old_history,
                }
                self.data["last_user_key"] = key

    def save_data_file(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def make_user_key(self, name, dob):
        return f"{name.strip().lower()}|{dob.strip()}"

    def get_current_user_record(self):
        key = self.make_user_key(self.user_name, self.user_dob)
        return self.data["users"].setdefault(
            key,
            {"name": self.user_name, "dob": self.user_dob, "history": []},
        )

    def get_current_history(self):
        return self.get_current_user_record().setdefault("history", [])

    # -------------------------
    # Helpers
    # -------------------------
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def safe_float(self, value):
        value = value.strip()
        if value == "":
            return 0.0
        return float(value)

    def format_dob(self, event=None):
        text = self.dob_var.get()
        if text == "mm/dd/yyyy":
            return

        digits = "".join(ch for ch in text if ch.isdigit())[:8]
        formatted = ""

        if len(digits) >= 1:
            formatted = digits[:2]
        if len(digits) >= 3:
            formatted = digits[:2] + "/" + digits[2:4]
        if len(digits) >= 5:
            formatted = digits[:2] + "/" + digits[2:4] + "/" + digits[4:8]

        self.dob_var.set(formatted)

    def clear_dob_placeholder(self, event=None):
        if self.dob_var.get() == "mm/dd/yyyy":
            self.dob_var.set("")
            self.dob_entry.config(fg="#111827")

    def restore_dob_placeholder(self, event=None):
        if self.dob_var.get().strip() == "":
            self.dob_var.set("mm/dd/yyyy")
            self.dob_entry.config(fg="#9ca3af")

    def check_budget_status(self, income, expense):
        if income <= 0 and expense <= 0:
            return "No data", "#6b7280"

        ratio = expense / income if income > 0 else 0

        if ratio < 0.7:
            return "Healthy spending", "#2e7d32"
        elif ratio <= 1.0:
            return "Moderate spending", "#f9a825"
        return "Over budget", "#c62828"

    def build_category_summary(self, expense_items, total_expense):
        categories = defaultdict(float)
        for item in expense_items:
            categories[item["category"]] += item["amount"]

        categorized_total = sum(categories.values())
        other = max(total_expense - categorized_total, 0)
        if other > 0:
            categories["Other"] += other

        return dict(categories)

    def get_latest_snapshot(self):
        history = self.get_current_history()
        if not history:
            return None
        return history[-1]

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
            return "Hi — I’m ready to review your budget. Add your income and expense items to begin."
        if not categories:
            return "You’ve entered totals, but categorized expenses will help me give more accurate feedback."

        top_category = max(categories, key=categories.get)
        ratio = expense / income if income > 0 else 0

        if ratio < 0.7:
            return f"You are currently in a healthy range. Your biggest expense category is {top_category}, but you still have a comfortable savings buffer."
        elif ratio <= 1.0:
            return f"Your budget is manageable, but your margin is getting tighter. Keep a closer eye on {top_category}."
        return f"Your spending is above your income right now. Start by reviewing {top_category} first."

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
            return f"Recommendation: your savings buffer is thin. Start by reviewing {top_category}, currently ${top_amount:.2f}."
        return "Recommendation: your budget looks stable. Consider moving part of your savings into an emergency or goal-based fund."

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
            highlightthickness=1,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        tk.Label(card, text="Connexa", font=("Helvetica", 26, "bold"), bg="white", fg="#111827").pack(pady=(35, 8))
        tk.Label(card, text="Track smarter. Spend better.", font=("Helvetica", 11), bg="white", fg="#6b7280").pack(pady=(0, 8))

        tk.Label(card, text="Full Name", font=("Helvetica", 11), bg="white", fg="#374151").pack(anchor="w", padx=45)
        self.name_entry = tk.Entry(card, font=("Helvetica", 12), bd=0, bg="#f3f4f6", fg="#111827")
        self.name_entry.pack(padx=45, fill="x", ipady=12, pady=(6, 14))

        tk.Label(card, text="Date of Birth", font=("Helvetica", 11), bg="white", fg="#374151").pack(anchor="w", padx=45)
        self.dob_var = tk.StringVar(value="mm/dd/yyyy")
        self.dob_entry = tk.Entry(card, textvariable=self.dob_var, font=("Helvetica", 12), bd=0, bg="#f3f4f6", fg="#9ca3af")
        self.dob_entry.pack(padx=45, fill="x", ipady=12, pady=(6, 22))
        self.dob_entry.bind("<FocusIn>", self.clear_dob_placeholder)
        self.dob_entry.bind("<FocusOut>", self.restore_dob_placeholder)
        self.dob_entry.bind("<KeyRelease>", self.format_dob)

        last_key = self.data.get("last_user_key", "")
        saved_user = self.data.get("users", {}).get(last_key, {})
        if saved_user:
            self.name_entry.insert(0, saved_user.get("name", ""))
            self.dob_var.set(saved_user.get("dob", ""))
            self.dob_entry.config(fg="#111827")

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
            command=self.login,
        ).pack(padx=45, fill="x")

    def login(self):
        name = self.name_entry.get().strip()
        dob = self.dob_entry.get().strip()

        if not name or not dob or dob == "mm/dd/yyyy":
            messagebox.showerror("Input Error", "Please enter both Name and DOB.")
            return

        try:
            datetime.strptime(dob, "%m/%d/%Y")
        except ValueError:
            messagebox.showerror("Format Error", "DOB must be in MM/DD/YYYY format.")
            return

        self.user_name = name
        self.user_dob = dob
        user_key = self.make_user_key(name, dob)
        self.data["users"].setdefault(user_key, {"name": name, "dob": dob, "history": []})
        self.data["users"][user_key]["name"] = name
        self.data["users"][user_key]["dob"] = dob
        self.data["last_user_key"] = user_key
        self.save_data_file()

        self.build_app_layout(active_page="Dashboard")
        self.show_dashboard_page()

    # -------------------------
    # Layout + Sidebar
    # -------------------------
    def build_app_layout(self, active_page="Dashboard"):
        self.clear_window()

        app_frame = tk.Frame(self.root, bg="#f5f7fb")
        app_frame.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(app_frame, bg="#0f172a", width=280)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main_area = tk.Frame(app_frame, bg="#f5f7fb")
        self.main_area.pack(side="left", fill="both", expand=True)

        tk.Label(
            self.sidebar,
            text="◉  Budget Buddy Assistant",
            font=("Helvetica", 12, "bold"),
            bg="#0f172a",
            fg="#f8fafc",
        ).pack(anchor="w", padx=18, pady=(14, 26))

        tk.Label(self.sidebar, text="👤", font=("Helvetica", 44), bg="#dbeafe", fg="#0f172a", width=2).pack(pady=(0, 8))
        tk.Label(self.sidebar, text=self.user_name, font=("Helvetica", 20, "bold"), bg="#0f172a", fg="#f8fafc").pack()
        tk.Label(self.sidebar, text="● Online", font=("Helvetica", 12), bg="#0f172a", fg="#22c55e").pack(pady=(6, 14))
        tk.Label(self.sidebar, text=f"DOB: {self.user_dob}", font=("Helvetica", 11), bg="#0f172a", fg="#f8fafc").pack(pady=(0, 26))

        tk.Frame(self.sidebar, bg="#334155", height=1).pack(fill="x", padx=18, pady=(0, 20))
        tk.Label(self.sidebar, text="FEATURES", font=("Helvetica", 10, "bold"), bg="#0f172a", fg="#94a3b8").pack(anchor="w", padx=24, pady=(0, 10))

        self.add_sidebar_item("Dashboard", "📊", active_page == "Dashboard", self.show_dashboard_page)
        self.add_sidebar_item("Income", "💰", active_page == "Income", self.show_income_page)
        self.add_sidebar_item("Expense", "💳", active_page == "Expense", self.show_expense_page)
        self.add_sidebar_item("Insights & Reports", "🔍", active_page == "Insights", self.show_insights_page)

        tk.Frame(self.sidebar, bg="#334155", height=1).pack(fill="x", padx=18, pady=(20, 20))
        self.sidebar_button("Reset All Data", "🔄", bg="#8b1e1e", command=self.reset_user_data).pack(fill="x", padx=18, pady=(0, 18))
        self.sidebar_button("Log Out", "🚪", bg="#334155", command=self.show_login_page).pack(fill="x", padx=18, pady=(0, 20))

    def sidebar_button(self, text, icon, bg="#0f172a", active=False, command=None):
        color = "#284a83" if active else bg
        return tk.Button(
            self.sidebar,
            text=f"{icon}   {text}",
            font=("Helvetica", 12),
            anchor="w",
            bg=color,
            fg="#f8fafc",
            activebackground="#334155",
            activeforeground="#f8fafc",
            bd=0,
            padx=18,
            pady=14,
            command=command,
        )

    def add_sidebar_item(self, text, icon, active, command):
        btn = self.sidebar_button(text, icon, active=active)
        btn.pack(fill="x", padx=18, pady=(0, 8))
        btn.bind("<Double-Button-1>", lambda event: command())
        return btn

    # -------------------------
    # Dashboard Page
    # -------------------------
    def show_dashboard_page(self):
        self.build_app_layout(active_page="Dashboard")
        self.clear_main_area()

        header = tk.Frame(self.main_area, bg="#f5f7fb")
        header.pack(fill="x", padx=32, pady=(28, 20))

        tk.Label(header, text="Hi, I’m Connexa!", font=("Helvetica", 30, "bold"), bg="#f5f7fb", fg="#111827").pack(anchor="w")
        tk.Label(
            header,
            text="Dashboard overview — income, expenses, savings, budget status, and quick insights.",
            font=("Helvetica", 14),
            bg="#f5f7fb",
            fg="#6b7280",
        ).pack(anchor="w", pady=(8, 0))

        cards_frame = tk.Frame(self.main_area, bg="#f5f7fb")
        cards_frame.pack(fill="x", padx=32, pady=(0, 22))
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="cards")

        self.income_card = self.create_card(cards_frame, "Total Income", "$0.00", "💵", "#16a34a")
        self.income_card.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        self.expense_card = self.create_card(cards_frame, "Total Expense", "$0.00", "↓", "#ef4444")
        self.expense_card.grid(row=0, column=1, sticky="ew", padx=12)

        self.savings_card = self.create_card(cards_frame, "Savings", "$0.00", "🐷", "#2563eb")
        self.savings_card.grid(row=0, column=2, sticky="ew", padx=12)

        self.status_card = self.create_card(cards_frame, "Status", "No data", "◔", "#f59e0b")
        self.status_card.grid(row=0, column=3, sticky="ew", padx=(12, 0))

        top_content = tk.Frame(self.main_area, bg="#f5f7fb")
        top_content.pack(fill="x", padx=32, pady=(0, 22))
        top_content.grid_columnconfigure(0, weight=1, uniform="top")
        top_content.grid_columnconfigure(1, weight=1, uniform="top")

        input_card = tk.Frame(top_content, bg="white", highlightbackground="#dfe3eb", highlightthickness=1)
        input_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.build_input_card(input_card)

        feedback_card = tk.Frame(top_content, bg="white", highlightbackground="#dfe3eb", highlightthickness=1)
        feedback_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.build_feedback_card(feedback_card)

        bottom_content = tk.Frame(self.main_area, bg="#f5f7fb")
        bottom_content.pack(fill="both", expand=True, padx=32, pady=(0, 28))
        bottom_content.grid_columnconfigure(0, weight=1, uniform="charts")
        bottom_content.grid_columnconfigure(1, weight=1, uniform="charts")
        bottom_content.grid_rowconfigure(0, weight=1)

        pie_card = tk.Frame(bottom_content, bg="white", highlightbackground="#dfe3eb", highlightthickness=1)
        pie_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(pie_card, text="Expense Breakdown", font=("Helvetica", 14, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=18, pady=(18, 0))
        self.pie_frame = tk.Frame(pie_card, bg="white")
        self.pie_frame.pack(fill="both", expand=True, padx=12, pady=8)

        line_card = tk.Frame(bottom_content, bg="white", highlightbackground="#dfe3eb", highlightthickness=1)
        line_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        tk.Label(line_card, text="Income vs Expense Trend", font=("Helvetica", 14, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=18, pady=(18, 0))
        self.line_frame = tk.Frame(line_card, bg="white")
        self.line_frame.pack(fill="both", expand=True, padx=12, pady=8)

        self.history_listbox = tk.Listbox(self.main_area)
        self.refresh_history_list()
        self.draw_default_pie()
        self.draw_trend_chart()

        latest = self.get_latest_snapshot()
        if latest:
            self.fill_entries(latest)
            self.apply_snapshot(latest)

    def build_input_card(self, input_card):
        tk.Label(input_card, text="Add New Expense", font=("Helvetica", 16, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=18, pady=(18, 12))

        self.create_entry_field(input_card, "Monthly Income", "income_entry")

        tk.Label(input_card, text="Category", font=("Helvetica", 10, "bold"), bg="white", fg="#374151").pack(anchor="w", padx=18)
        self.category_combobox = ttk.Combobox(
            input_card,
            values=["Food", "Transportation", "Entertainment", "Rent", "Bills", "Shopping", "Other"],
            state="readonly",
            font=("Helvetica", 10),
        )
        self.category_combobox.pack(padx=18, fill="x", pady=(4, 10), ipady=5)
        self.category_combobox.set("Food")
        self.category_combobox.bind("<<ComboboxSelected>>", self.toggle_other_category_entry)

        self.other_category_frame = tk.Frame(input_card, bg="white")
        self.other_category_frame.pack(padx=18, fill="x", pady=(0, 0))
        self.other_category_label = tk.Label(self.other_category_frame, text="Custom Expense Category", font=("Helvetica", 10, "bold"), bg="white", fg="#374151")
        self.other_category_entry = tk.Entry(self.other_category_frame, font=("Helvetica", 11), bd=0, bg="#f3f4f6", fg="#111827")

        tk.Label(input_card, text="Amount ($)", font=("Helvetica", 10, "bold"), bg="white", fg="#374151").pack(anchor="w", padx=18)
        self.expense_amount_entry = tk.Entry(input_card, font=("Helvetica", 11), bd=0, bg="#f3f4f6", fg="#111827")
        self.expense_amount_entry.pack(padx=18, fill="x", ipady=8, pady=(4, 10))

        tk.Label(input_card, text="Description (optional)", font=("Helvetica", 10, "bold"), bg="white", fg="#374151").pack(anchor="w", padx=18)
        self.description_entry = tk.Entry(input_card, font=("Helvetica", 11), bd=0, bg="#f3f4f6", fg="#111827")
        self.description_entry.pack(padx=18, fill="x", ipady=8, pady=(4, 12))

        btn_row = tk.Frame(input_card, bg="white")
        btn_row.pack(fill="x", padx=18, pady=(0, 14))
        tk.Button(btn_row, text="Add Expense", font=("Helvetica", 11, "bold"), bg="#2563eb", fg="white", bd=0, pady=12, command=self.add_expense_item).pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Button(btn_row, text="Clear Items", font=("Helvetica", 11, "bold"), bg="#e5e7eb", fg="#111827", bd=0, pady=12, command=self.clear_expense_items).pack(side="left", fill="x", expand=True, padx=(8, 0))

        self.expense_listbox = tk.Listbox(input_card, font=("Helvetica", 10), bd=0, bg="#f3f4f6", fg="#111827", height=2)
        self.expense_listbox.pack(padx=18, fill="x", pady=(0, 14))

        tk.Frame(input_card, bg="#e5e7eb", height=1).pack(fill="x", padx=18, pady=(0, 14))
        tk.Label(input_card, text="Snapshot Actions", font=("Helvetica", 13, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=18, pady=(0, 10))

        save_frame = tk.Frame(input_card, bg="white")
        save_frame.pack(fill="x", padx=18, pady=(0, 18))
        tk.Button(save_frame, text="Save Snapshot", font=("Helvetica", 11, "bold"), bg="#15803d", fg="white", bd=0, pady=5, command=self.save_snapshot).pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Button(save_frame, text="Load Latest", font=("Helvetica", 11, "bold"), bg="#2563eb", fg="white", bd=0, pady=5, command=self.load_latest_snapshot).pack(side="left", fill="x", expand=True, padx=(8, 0))

    def build_feedback_card(self, feedback_card):
        tk.Label(feedback_card, text="Smart Insights", font=("Helvetica", 16, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=22, pady=(18, 18))

        tk.Label(feedback_card, text="Spending Pattern:", font=("Helvetica", 11, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=22, pady=(0, 6))
        self.pattern_label = tk.Label(feedback_card, text="No data yet.", font=("Helvetica", 10), bg="white", fg="#374151", wraplength=560, justify="left")
        self.pattern_label.pack(anchor="w", padx=22, pady=(0, 18))

        tk.Label(feedback_card, text="AI Feedback:", font=("Helvetica", 11, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=22, pady=(0, 6))
        self.ai_feedback_label = tk.Label(feedback_card, text="No data yet.", font=("Helvetica", 10), bg="white", fg="#374151", wraplength=560, justify="left")
        self.ai_feedback_label.pack(anchor="w", padx=22, pady=(0, 18))

        tk.Label(feedback_card, text="Recommendation:", font=("Helvetica", 11, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=22, pady=(0, 6))
        self.recommendation_label = tk.Label(feedback_card, text="No data yet.", font=("Helvetica", 10), bg="white", fg="#374151", wraplength=560, justify="left")
        self.recommendation_label.pack(anchor="w", padx=22, pady=(0, 18))

        tk.Label(feedback_card, text="Category Summary:", font=("Helvetica", 11, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=22, pady=(0, 6))
        self.category_summary_label = tk.Label(feedback_card, text="No data yet.", font=("Helvetica", 10), bg="white", fg="#374151", wraplength=560, justify="left")
        self.category_summary_label.pack(anchor="w", padx=22, pady=(0, 18))

        progress_row = tk.Frame(feedback_card, bg="white")
        progress_row.pack(fill="x", padx=22, pady=(4, 8))
        tk.Label(progress_row, text="Spending Progress:", font=("Helvetica", 11, "bold"), bg="white", fg="#111827").pack(side="left")
        self.progress_text = tk.Label(progress_row, text="0% of income spent", font=("Helvetica", 12, "bold"), bg="white", fg="#2563eb")
        self.progress_text.pack(side="right")

        self.progress_canvas = tk.Canvas(feedback_card, width=560, height=28, bg="white", highlightthickness=0)
        self.progress_canvas.pack(fill="x", padx=22, pady=(0, 18))
        self.progress_canvas.create_rectangle(0, 9, 560, 21, fill="#e5e7eb", outline="")
        self.progress_fill = self.progress_canvas.create_rectangle(0, 9, 0, 21, fill="#2563eb", outline="")

    # -------------------------
    # Income Page
    # -------------------------
    def show_income_page(self):
        self.build_app_layout(active_page="Income")
        self.clear_main_area()

        self.page_header("Income Tracking", "Track how your income changes across saved snapshots.")

        card = tk.Frame(self.main_area, bg="white", highlightbackground="#dfe3eb", highlightthickness=1)
        card.pack(fill="both", expand=True, padx=32, pady=(0, 28))

        tk.Label(card, text="Income Bar Chart", font=("Helvetica", 18, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=22, pady=(22, 6))
        tk.Label(card, text="Double-click Income in the sidebar to open this focused page.", font=("Helvetica", 11), bg="white", fg="#6b7280").pack(anchor="w", padx=22, pady=(0, 12))

        frame = tk.Frame(card, bg="white")
        frame.pack(fill="both", expand=True, padx=18, pady=18)
        self.draw_income_bar_chart(frame)

    def draw_income_bar_chart(self, parent):
        history = self.get_current_history()
        fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=100)
        fig.patch.set_facecolor("white")

        if history:
            labels = [item["date"][5:10] for item in history[-10:]]
            incomes = [item["income"] for item in history[-10:]]
            ax.bar(labels, incomes)
            ax.set_title("Income by Snapshot", fontsize=13, pad=12)
            ax.set_ylabel("Income ($)")
            ax.tick_params(axis="x", rotation=25)
            ax.grid(True, axis="y", alpha=0.3)
        else:
            ax.text(0.5, 0.5, "No income snapshots yet", ha="center", va="center", transform=ax.transAxes, fontsize=12)
            ax.set_xticks([])
            ax.set_yticks([])

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    # -------------------------
    # Expense Page
    # -------------------------
    def show_expense_page(self):
        self.build_app_layout(active_page="Expense")
        self.clear_main_area()

        self.page_header("Expense Tracking", "Track what you spend on and compare spending categories.")

        card = tk.Frame(self.main_area, bg="white", highlightbackground="#dfe3eb", highlightthickness=1)
        card.pack(fill="both", expand=True, padx=32, pady=(0, 28))

        tk.Label(card, text="Expense Category Bar Chart", font=("Helvetica", 18, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=22, pady=(22, 6))
        tk.Label(card, text="This page focuses only on expense breakdown from your latest snapshot.", font=("Helvetica", 11), bg="white", fg="#6b7280").pack(anchor="w", padx=22, pady=(0, 12))

        frame = tk.Frame(card, bg="white")
        frame.pack(fill="both", expand=True, padx=18, pady=18)
        self.draw_expense_bar_chart(frame)

    def draw_expense_bar_chart(self, parent):
        latest = self.get_latest_snapshot()
        fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=100)
        fig.patch.set_facecolor("white")

        if latest:
            categories = self.build_category_summary(latest.get("expense_items", []), latest.get("expense", 0))
            filtered = {k: v for k, v in categories.items() if v > 0}
            if filtered:
                labels = list(filtered.keys())
                values = list(filtered.values())
                ax.bar(labels, values)
                ax.set_title("Expense by Category", fontsize=13, pad=12)
                ax.set_ylabel("Amount ($)")
                ax.tick_params(axis="x", rotation=25)
                ax.grid(True, axis="y", alpha=0.3)
            else:
                ax.text(0.5, 0.5, "No categorized expenses yet", ha="center", va="center", transform=ax.transAxes, fontsize=12)
                ax.set_xticks([])
                ax.set_yticks([])
        else:
            ax.text(0.5, 0.5, "No expense snapshots yet", ha="center", va="center", transform=ax.transAxes, fontsize=12)
            ax.set_xticks([])
            ax.set_yticks([])

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    # -------------------------
    # Insights Page
    # -------------------------
    def show_insights_page(self):
        self.build_app_layout(active_page="Insights")
        self.clear_main_area()

        self.page_header("Insights & Reports", "A deeper report based on your latest saved snapshot.")

        card = tk.Frame(self.main_area, bg="white", highlightbackground="#dfe3eb", highlightthickness=1)
        card.pack(fill="both", expand=True, padx=32, pady=(0, 28))

        latest = self.get_latest_snapshot()
        if not latest:
            tk.Label(card, text="No saved snapshots yet.", font=("Helvetica", 16, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=24, pady=24)
            tk.Label(card, text="Go back to Dashboard, add income and expenses, then save a snapshot.", font=("Helvetica", 12), bg="white", fg="#6b7280").pack(anchor="w", padx=24)
            return

        income = latest["income"]
        expense = latest["expense"]
        savings = income - expense
        categories = self.build_category_summary(latest.get("expense_items", []), expense)

        pattern = self.get_pattern_detection(categories, income, expense)
        feedback = self.get_ai_feedback(income, expense, savings, categories)
        recommendation = self.get_personalized_recommendation(income, expense, categories)

        report = [
            ("Latest Snapshot", latest["date"]),
            ("Income", f"${income:,.2f}"),
            ("Expense", f"${expense:,.2f}"),
            ("Savings", f"${savings:,.2f}"),
            ("Spending Pattern", pattern),
            ("AI Feedback", feedback),
            ("Recommendation", recommendation),
        ]

        for title, value in report:
            block = tk.Frame(card, bg="white")
            block.pack(fill="x", padx=24, pady=(18, 0))
            tk.Label(block, text=title, font=("Helvetica", 12, "bold"), bg="white", fg="#111827").pack(anchor="w")
            tk.Label(block, text=value, font=("Helvetica", 11), bg="white", fg="#374151", wraplength=900, justify="left").pack(anchor="w", pady=(4, 0))

    def page_header(self, title, subtitle):
        header = tk.Frame(self.main_area, bg="#f5f7fb")
        header.pack(fill="x", padx=32, pady=(28, 20))
        tk.Label(header, text=title, font=("Helvetica", 30, "bold"), bg="#f5f7fb", fg="#111827").pack(anchor="w")
        tk.Label(header, text=subtitle, font=("Helvetica", 14), bg="#f5f7fb", fg="#6b7280").pack(anchor="w", pady=(8, 0))

    # -------------------------
    # UI Components
    # -------------------------
    def create_entry_field(self, parent, label_text, attr_name):
        tk.Label(parent, text=label_text, font=("Helvetica", 10), bg="white", fg="#374151").pack(anchor="w", padx=18)
        entry = tk.Entry(parent, font=("Helvetica", 11), bd=0, bg="#f3f4f6", fg="#111827")
        entry.pack(padx=18, fill="x", ipady=8, pady=(4, 8))
        setattr(self, attr_name, entry)

    def create_card(self, parent, title, value, icon, accent_color):
        card = tk.Frame(parent, bg="white", height=100, highlightbackground="#dfe3eb", highlightthickness=1)
        card.pack_propagate(False)

        row = tk.Frame(card, bg="white")
        row.pack(fill="both", expand=True, padx=18, pady=18)

        tk.Label(row, text=icon, font=("Helvetica", 24, "bold"), bg="white", fg=accent_color, width=3).pack(side="left", anchor="n", pady=(4, 0))

        text_box = tk.Frame(row, bg="white")
        text_box.pack(side="left", fill="both", expand=True, padx=(12, 0))

        tk.Label(text_box, text=title, font=("Helvetica", 11), bg="white", fg="#374151").pack(anchor="w", pady=(8, 12))
        value_label = tk.Label(text_box, text=value, font=("Helvetica", 14, "bold"), bg="white", fg=accent_color)
        value_label.pack(anchor="w")

        card.value_label = value_label
        return card

    # -------------------------
    # Expense Items
    # -------------------------
    def toggle_other_category_entry(self, event=None):
        if self.category_combobox.get() == "Other":
            self.other_category_label.pack(anchor="w", pady=(0, 2))
            self.other_category_entry.pack(fill="x", ipady=6, pady=(0, 8))
        else:
            self.other_category_entry.delete(0, tk.END)
            self.other_category_label.pack_forget()
            self.other_category_entry.pack_forget()

    def add_expense_item(self):
        try:
            category = self.category_combobox.get().strip()
            if category == "Other":
                custom_category = self.other_category_entry.get().strip()
                if not custom_category:
                    messagebox.showerror("Input Error", "Please enter the custom expense category.")
                    return
                category = custom_category

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

            if self.category_combobox.get() == "Other":
                self.other_category_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid expense amount.")

    def clear_expense_items(self):
        self.current_expense_items = []
        self.refresh_expense_items_list()

    def refresh_expense_items_list(self):
        if not hasattr(self, "expense_listbox"):
            return
        self.expense_listbox.delete(0, tk.END)
        for idx, item in enumerate(self.current_expense_items, start=1):
            self.expense_listbox.insert(tk.END, f"{idx}. {item['category']} — ${item['amount']:.2f}")

    # -------------------------
    # Snapshot Save / Load / Reset
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
                "expense_items": self.current_expense_items.copy(),
            }

            self.get_current_history().append(snapshot)
            self.save_data_file()
            self.refresh_history_list()
            self.apply_snapshot(snapshot)

            messagebox.showinfo("Saved", "Budget snapshot saved successfully.")

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers.")

    def refresh_history_list(self):
        if hasattr(self, "history_listbox"):
            self.history_listbox.delete(0, tk.END)
            for item in reversed(self.get_current_history()):
                display = f"{item['date']} | Income ${item['income']:.2f} | Expense ${item['expense']:.2f}"
                self.history_listbox.insert(tk.END, display)

    def load_latest_snapshot(self):
        latest = self.get_latest_snapshot()
        if not latest:
            messagebox.showwarning("No Data", "No saved snapshots yet.")
            return
        self.fill_entries(latest)
        self.apply_snapshot(latest)

    def fill_entries(self, snapshot):
        if hasattr(self, "income_entry"):
            self.income_entry.delete(0, tk.END)
            self.income_entry.insert(0, str(snapshot.get("income", 0)))
        self.current_expense_items = snapshot.get("expense_items", []).copy()
        self.refresh_expense_items_list()

    def reset_user_data(self):
        confirm = messagebox.askyesno("Confirm Reset", "Are you sure you want to delete all saved snapshots for this user?")
        if not confirm:
            return

        user = self.get_current_user_record()
        user["history"] = []
        self.current_expense_items = []
        self.save_data_file()

        messagebox.showinfo("Reset Complete", "All snapshots for this user have been deleted.")
        self.show_dashboard_page()

    # -------------------------
    # Apply Snapshot
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

        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        summary_parts = [f"{name}: ${value:.2f}" for name, value in sorted_categories if value > 0]
        category_summary = ", ".join(summary_parts[:5]) if summary_parts else "No category data yet."

        self.pattern_label.config(text=pattern)
        self.ai_feedback_label.config(text=ai_feedback)
        self.recommendation_label.config(text=recommendation)
        self.category_summary_label.config(text=category_summary)

        percentage = (expense / income * 100) if income > 0 else 0
        capped_percentage = min(percentage, 100)
        fill_width = (capped_percentage / 100) * 560
        self.progress_canvas.coords(self.progress_fill, 0, 9, fill_width, 21)
        self.progress_text.config(text=f"{percentage:.1f}% of income spent")

        self.update_pie_chart(categories)
        self.draw_trend_chart()

    # -------------------------
    # Dashboard Charts
    # -------------------------
    def draw_default_pie(self):
        for widget in self.pie_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(3.2, 2.0), dpi=100)
        fig.patch.set_facecolor("white")
        ax.pie([1], labels=["No data"], autopct="%1.0f%%", startangle=90, textprops={"fontsize": 8})
        ax.set_title("Expense Breakdown", fontsize=10, pad=6)
        fig.tight_layout(pad=1.0)

        canvas = FigureCanvasTkAgg(fig, master=self.pie_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def update_pie_chart(self, categories):
        for widget in self.pie_frame.winfo_children():
            widget.destroy()

        filtered = {k: v for k, v in categories.items() if v > 0}
        if not filtered:
            self.draw_default_pie()
            return

        fig, ax = plt.subplots(figsize=(3.2, 2.0), dpi=100)
        fig.patch.set_facecolor("white")
        ax.pie(list(filtered.values()), labels=list(filtered.keys()), autopct="%1.0f%%", startangle=90, textprops={"fontsize": 8})
        ax.set_title("Expense Breakdown", fontsize=10, pad=6)
        fig.tight_layout(pad=1.0)

        canvas = FigureCanvasTkAgg(fig, master=self.pie_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def draw_trend_chart(self):
        for widget in self.line_frame.winfo_children():
            widget.destroy()

        history = self.get_current_history()
        fig, ax = plt.subplots(figsize=(3.4, 2.4), dpi=100)
        fig.patch.set_facecolor("white")

        if history:
            daily_data = {}
            for item in history:
                day_key = item["date"][:10]
                daily_data[day_key] = item

            sorted_days = sorted(daily_data.keys())
            labels = [day[5:] for day in sorted_days]
            incomes = [daily_data[day]["income"] for day in sorted_days]
            expenses = [daily_data[day]["expense"] for day in sorted_days]

            ax.plot(labels, incomes, marker="o", linewidth=2, label="Income")
            ax.plot(labels, expenses, marker="o", linewidth=2, label="Expense")
            ax.set_title("Income vs Expense Trend", fontsize=10, pad=8)
            ax.set_ylabel("Amount ($)", fontsize=8)
            ax.tick_params(axis="x", rotation=25, labelsize=8)
            ax.tick_params(axis="y", labelsize=8)
            ax.legend(fontsize=8, loc="upper left")
            ax.grid(True, axis="y", alpha=0.3)
        else:
            ax.text(0.5, 0.5, "Save snapshots over time\nto see your trend", ha="center", va="center", transform=ax.transAxes, fontsize=9)
            ax.set_title("Income vs Expense Trend", fontsize=10, pad=8)
            ax.set_xticks([])
            ax.set_yticks([])

        fig.tight_layout(pad=1.0)
        canvas = FigureCanvasTkAgg(fig, master=self.line_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)


if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetBuddyApp(root)
    root.mainloop()
