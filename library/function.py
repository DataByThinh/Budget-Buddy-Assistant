def calc_balance(income, expenses):
    print(f"Your expenses are: {expenses}")
    balance = income - sum(expenses)
    return balance

def financial_status(balance):
    if balance > 0:
        print("Great! You are saving money!")
    elif balance == 0:
        print("You are breaking even.")  
    else:
        print("Warning!!!: You are overspending!")