import os

# Get the temperature from environment variable
temperature = float(os.environ["INPUT_TEMP"])

# Process the temperature
if temperature < 10:
    category = "Cold"
elif temperature < 20:
    category = "Mild"
else:
    category = "Hot"

print(f"Temperature {temperature:.2f}°C is categorized as: {category}")
