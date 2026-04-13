class Budget: 
    def __init__(self, expense_type):
        self.expenses_type = expense_type
        self.expenses = []
        self.category = []

    def add_expenses(self):
        while True:
            try:
                nump_expenses = int(input(f"\nEnter number of {self.expenses_type} expenses you want to add (integers only): "))
                break
            except:
                print(" **ERROR** ")
                print(" You entered an invalid input. Please enter an integer for the number of expenses.")
                print()
    
        print("\nEnter input expenses in \"Type Cost\" format. For e.g. Milk 10")
        for i in range(nump_expenses):
            while True:
                try:
                    type, exp = input(f"Enter expense #{i+1}: ").split()
                    self.expenses.append(float(exp))
                    self.category.append(type)
                    break 
                except:
                    print(" **ERROR** ")
                    print(" You entered an invalid input. Please enter the expense in \"Type Cost\" format.")
                    print()

    def get_expenses(self):
        print(f"\nTotal money you spend on {self.expenses_type} is {sum(self.expenses)}")
        return sum(self.expenses)       
    

    def get_expenses_list(self):
        print(f"\nMoney you spent on {self.expenses_type} are:")
        for i in range(len(self.expenses)):
            print(f"{self.category[i]}: {self.expenses[i]}")