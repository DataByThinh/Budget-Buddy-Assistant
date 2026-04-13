import os
from library import functions
from library.classes_9 import Budget

os.system('cls' if os.name == 'nt' else 'clear')

name = input("Enter your name: ")
os.system('cls' if os.name == 'nt' else 'clear')

print(f"Hey {name}, this is Budget Buddy! Your personal Budgeting Assistant.\n")

while True:
    try:
        income = float(input("Please enter your monthly income (only numbers): "))
        break
    except ValueError:
        print("Invalid input. Please enter a number.")

total_expenses = [] 

grocery = Budget("Grocery")
car = Budget("Car") 

grocery.add_expenses() 
car.add_expenses()  

exp_grocery = grocery.get_expenses() 
total_expenses.append(exp_grocery)

total_expenses.append(car.get_expenses())

bal= functions.calc_balance(income, sum(total_expenses))

functions.financial_status(bal)

grocery.get_expenses_list()
