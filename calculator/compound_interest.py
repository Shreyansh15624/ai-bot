
principal = 5000
rate = 0.045
time = 5

amount = principal * (1 + rate)**time
compound_interest = amount - principal

print(f"Compound interest: {compound_interest:.2f}")
