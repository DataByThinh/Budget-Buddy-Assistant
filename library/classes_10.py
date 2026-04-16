class Budget: 
    def __init__(self, expense_type):
        self.expenses_type = expense_type
        #self.expenses = []
        #self.category = []
        self.expenses_dict = {}

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
                    self.expenses_dict[type] = float(exp)
                    #self.expenses.append(float(exp))
                    #self.category.append(type)
                    break 
                except:
                    print(" **ERROR** ")
                    print(" You entered an invalid input. Please enter the expense in \"Type Cost\" format.")
                    print()
        self.write_to_file() 

    def get_expenses(self):
        print()
        print(f"\nTotal money you spend on {self.expenses_type} is {sum(self.expenses_dict.values())}")
        return sum(self.expenses_dict.values())       
    

    def get_expenses_list(self):
        print()
        print(f"\nMoney you spent on {self.expenses_type} are:")
        
        for type, exp in self.expenses_dict.items():
            print(f"{type}: ${exp}")

    def write_to_file(self):
        with open("data.txt", "a") as expense_data:
            expense_data.write(f"{self.expenses_type}")
            expense_data.write("\n")

            for type, exp in self.expenses_dict.items():
                expense_data.write(f"{type} : ${exp}")
                expense_data.write("\n")
            expense_data.write("\n")
