import os
from library import functions
from library.classes_8 import Budget

os.system('cls' if os.name == 'nt' else 'clear')

name = input("Enter your name: ")
os.system('cls' if os.name == 'nt' else 'clear')

print(f"Hey {name}, this is Budget Buddy! Your personal Budgeting Assistant.")

income = float(input("Please enter your monthly income (only numbers): "))

total_expenses = [] 

grocery = Budget("Grocery")
car = Budget("Car") 

grocery.add_expenses() 
car.add_expenses()  

grocery.get_expenses()  
car.get_expenses()  

total_expenses.append(grocery.get_expenses())
total_expenses.append(car.get_expenses())

bal = function.calc_balance(income, total_expenses)

function.financial_status(bal)