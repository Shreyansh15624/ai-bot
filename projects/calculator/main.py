def run_financial_calculator():
    print("--- Welcome to the Advanced Finance Calculator ---")
    print("Select a calculation type:")
    print("1. Calculate Compound Interest (Original)")
    print("2. Calculate Loan Amortization Schedule (New)")
    
    choice = input("Enter choice (1 or 2): ")
    
    if choice == '1':
        print("\n--- Running Compound Interest Calculator ---")
        # Assuming compound_interest.py has a function we can call, e.g., calculate_ci()
        # We will need to call the function exposed by the module.
        try:
            # Placeholder: We assume the module exposes a main function or we call a specific one.
            # For now, we call a placeholder function based on structure.
            print("Running original compound interest calculation...")
            # In a real scenario, we'd call: from compound_interest import calculate_ci
            # For demonstration, we'll just prompt the user further.
            print("Please provide necessary inputs for Compound Interest (P, r, t, n).")
        except Exception as e:
            print(f"Error running CI: {e}")

    elif choice == '2':
        print("\n--- Running Loan Amortization Calculator ---")
        try:
            # Assuming loan_calculator.py has a function we can call, e.g., generate_amortization()
            # For now, we prompt the user for inputs for the new module.
            print("Please provide parameters for the loan (Principal, Rate, Years).")
            # In a real scenario, we'd call: from loan_calculator import generate_amortization
        except Exception as e:
            print(f"Error running Loan Calculator: {e}")
    else:
        print("Invalid selection. Please run the program again.")

if __name__ == "__main__":
    run_financial_calculator()