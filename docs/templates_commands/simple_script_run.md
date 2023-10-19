---
description: Simple script template file
---

# Simple Script Run

## Description

This simple template runs a script called `my_script.py`

## Example call

```python title="my_script.py"
print("hello world!")
```

```bash
csm-orc run run.json
```

## Template

```json title="run.json" linenums="1"
--8<-- "templates/SimplePythonScript.json"
```