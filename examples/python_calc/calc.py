def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python3 calc.py <add|subtract> <num1> <num2>")
        sys.exit(1)
    op, x, y = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    if op == "add":
        print(add(x, y))
    elif op == "subtract":
        print(subtract(x, y))
    else:
        print("Unknown operation")
