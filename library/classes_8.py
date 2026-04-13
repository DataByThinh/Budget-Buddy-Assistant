class Budget: 
    def __init__(self, expense_type):
        self.expenses_type = expense_type
        self.expenses = []

    def add_expenses(self):
        nump_expenses = int(input(f"Enter number of {self.expenses_type} expenses you want to add (integers only): "))
    
        expenses = []

        for i in range(nump_expenses):
            exp = float(input(f"Enter expense #{i+1} (only numbers): "))
            self.expenses.append(exp)
        
    def get_expenses(self):
        print(f"Total money you spend on {self.expenses_type} is {sum(self.expenses)}")
        return sum(self.expenses)  