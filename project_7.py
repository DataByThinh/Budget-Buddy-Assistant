import os
from library import function
os.system('cls' if os.name == 'nt' else 'clear')

name = input("Enter your name: ")
os.system('cls' if os.name == 'nt' else 'clear')

print(f"Hey {name}, this is Budget Buddy! Your personal Budgeting Assistant.")

income = float(input("Please enter your monthly income (only numbers): "))

num_expenses = int(input("Enter number of expenses you want to store (integer only): "))

expenses = [] 

for i in range(num_expenses):
    expense = float(input(f"Enter expense #{i + 1} (only numbers): "))
    expenses.append(expense)

balance = function.calc_balance(income, expenses)
function.financial_status(balance)