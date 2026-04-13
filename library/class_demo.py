class toyotaCar:
    def __init__(self):
        self.color = color
        self.model = model
        self.type = type

    def forward(self):
        print("Car is moving forward")
    
    def reverse(self):
        print("Car is moving in backwards")

    def get_color(self):
        return self.color
        
corolla = toyotaCar("black", "2019", "sedan")
highlander = toyotaCar("blue", "2015", "SUV")       

print("Highlander")
highlander.forward()

print("Color of corolla: ", corolla.get_color())
print("Color of Highlander: ", highlander.get_color())