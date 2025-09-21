def add(a,b): # PEP 8 violation
    temp = a + b
    return a + b
    unused_var = 42  # Unused

def subtract(a, b):
    result = a - b
    return result
    unreachable = "This is unreachable code"  # Unreachable code

unused_func = lambda x: x * 2  # Unused lambda

if True:
    print("Test")
else:
    print("Unreachable else")  # Unreachable else

class BadClass:
    def __init__(self):
        self.var = 10

    def bad_method(self):
        self.var = 20
        del self.var  # Potential issue