def calculate():
    print("Advanced Calculator")
    print("Enter 'exit' to quit.")

    while True:
        try:
            expression = input("Enter calculation (e.g., 2 + 3, 5 ** 2): ")
            if expression.lower() == 'exit':
                break

            # Evaluate the expression
            result = eval(expression)
            print("Result:", result)

        except ZeroDivisionError:
            print("Error: Cannot divide by zero.")
        except SyntaxError:
            print("Error: Invalid expression. Please check your input.")
        except NameError:
            print("Error: Invalid input. Please use numbers and operators.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    calculate()