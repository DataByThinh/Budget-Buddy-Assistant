user_input = input("Enter your name: ")
print(f"Hello, {user_input} this is BudgetBuddy! Your personal budgeting assistant.")

def calc_balance(income, expenses):
    balance = income - expenses
    return balance
def financial_status(balance):
    if balance > 0:
        print("Great! You are saving money!")
    elif balance == 0:
        print("You are breaking even.")  
    else:
        print("Warning!!!: You are overspending!")

income = float(input("Enter your income (Numbers only): "))
expenses = float(input("Enter your expenses (Numbers only): "))

balance = calc_balance(income, expenses)

financial_status(balance)