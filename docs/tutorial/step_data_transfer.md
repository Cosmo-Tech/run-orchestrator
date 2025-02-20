---
description: Tutorial on transferring data between steps
---
# Step Data Transfer

!!! abstract "Objective"

    * Learn how to pass data between steps  
    * Use the built-in data transfer system  
    * Create Python scripts that output data  
    * Connect steps using input/output configurations  

## Understanding Step Data Transfer

The orchestrator provides a built-in system for transferring data between steps. This allows one step to produce data that can be used by subsequent steps. Data transfer is achieved through a special output format and can be used in both shell commands and Python scripts.

## Creating Data-Producing Scripts

Let's create two Python scripts: one that generates some data and another that processes it.

=== "Generate Data"
    ```python title="generate_data.py" linenums="1"
    --8<-- "tutorial/step_data_transfer/generate_data.py"
    ```

=== "Process Data"
    ```python title="process_data.py" linenums="1"
    --8<-- "tutorial/step_data_transfer/process_data.py"
    ```

## Writing the Orchestration File

Now let's create an orchestration file that connects these scripts using the data transfer system:

```json title="temperature_analysis.json" linenums="1"
--8<-- "tutorial/step_data_transfer/temperature_analysis.json"
```

Let's break down the key elements:

The `generate-temp` step:

  * Defines an output named "temperature"  
  * Uses the `log_data` function to output the value  
  * Provides a default value as fallback  

The `analyze-temp` step:

  * Defines an input that connects to the previous step's output  
  * Maps the input to an environment variable named "INPUT_TEMP"  
  * Lists "generate-temp" as a precedent to ensure correct ordering  

## Running the Example

You can run this example with:

```bash
csm-orc run temperature_analysis.json
```

The output will show:

  * The generated temperature  
  * The analysis result  
  * Debug logs showing the data transfer  

## Alternative Output Methods

There are two ways to output data from a step:  

The Python logger (recommended for Python scripts):  
```python
from cosmotech.orchestrator.utils.logger import log_data
log_data("name", "value")
```

The direct output format (good for shell commands):  
```bash
echo "CSM-OUTPUT-DATA:name:value"
```

Both methods achieve the same result, but the logger provides a cleaner interface for Python code.

## Advanced Features

The data transfer system supports several advanced features:

Optional outputs and inputs:  
```json
{
  "outputs": {
    "debug_data": {
      "description": "Optional debug information",
      "optional": true
    }
  }
}
```

Default values as fallbacks:  
```json
{
  "inputs": {
    "data": {
      "stepId": "previous-step",
      "output": "result",
      "as": "INPUT_DATA",
      "defaultValue": "fallback-value"
    }
  }
}
```

Debug logging of transfers:  
You can enable detailed logging of data transfers by setting the LOG_LEVEL environment variable:  
```bash
# Using environment variable
LOG_LEVEL=debug csm-orc run temperature_analysis.json

# Or using command line flag
csm-orc --log-level debug run temperature_analysis.json
```
This will show:

  * When data is captured from a step's output  
  * When data is transferred between steps  
  * Default value usage  
  * Missing value warnings  

## Best Practices

  * Always provide default values for critical inputs  
  * Use descriptive names for outputs and inputs  
  * Document the expected format of data  
  * Use the Python logger in Python scripts  
  * Test with debug logging enabled during development  
