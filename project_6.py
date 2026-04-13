#Task 1

import os
from library import function
os.system('cls' if os.name == 'nt' else 'clear')

name = input("Enter your name: ")
os.system('cls' if os.name == 'nt' else 'clear')

print(f"Hey {name}, this is Budget Buddy! Your personal Budgeting Assistant.")

income = float(input("Please enter your monthly income (only numbers): "))
expense = [12.3, 45, 349, 123]

#Task 2
balance = function.calc_balance(income, expense)
function.financial_status(balance)