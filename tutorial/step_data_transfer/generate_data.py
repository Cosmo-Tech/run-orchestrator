import random
from cosmotech.orchestrator.utils.logger import log_data

# Generate a random temperature between 0 and 30
temperature = random.uniform(0, 30)

# Output the temperature using the data logger
log_data("temperature", f"{temperature:.2f}")

# Regular logging still works
print(f"Generated temperature: {temperature:.2f}°C")
