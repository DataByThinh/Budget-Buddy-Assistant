# logic from project 1 
user_input = input("Enter your name: ")
print(f"Hello, {user_input} this is BudgetBuddy! Your personal budgeting assistant.")

# User income 

income = float(input("Enter your income (Numbers only): "))
expenses = float(input("Enter your expenses (Numbers only): "))

# Balance calculation
balance = income - expenses
print(f"Your balance is: {balance}")
