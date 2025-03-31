# Cosmotech Orchestrator API

This module provides functions that implement the core functionality of the `csm-orc` CLI commands, allowing them to be used directly without the CLI context.

## Usage Examples

### Running a Template

```python
from cosmotech.orchestrator.api.run import run_template

# Run a template
success, results = run_template(
    template_path="path/to/template.json",
    dry_run=False,
    exit_handlers=True
)

if success:
    print("Template executed successfully!")
    # Access results
    for step_id, step_data in results.items():
        print(f"Step {step_id}: {step_data['status']}")
else:
    print("Template execution failed")
```

### Validating a Template

```python
from cosmotech.orchestrator.api.run import validate_template

# Validate a template without running it
is_valid = validate_template("path/to/template.json")
if is_valid:
    print("Template is valid")
else:
    print("Template is invalid")
```

### Working with Environment Variables

```python
from cosmotech.orchestrator.api.run import display_environment, generate_env_file

# Display environment variables required by a template
display_environment("path/to/template.json")

# Generate a .env file with all required environment variables
generate_env_file("path/to/template.json", ".env")
```

### Working with Templates

```python
from cosmotech.orchestrator.api.templates import list_templates, get_template_details

# List all available templates
templates = list_templates(verbose=True)
for template in templates:
    print(f"Template: {template['id']}")

# Get details for a specific template
template_info = get_template_details("template-id", verbose=True)
if template_info:
    print(f"Template command: {template_info['command']}")
```

### Docker Entrypoint

```python
from cosmotech.orchestrator.api.entrypoint import run_entrypoint

# Run the Docker entrypoint logic
exit_code = run_entrypoint()
print(f"Entrypoint exited with code: {exit_code}")
```

## API Reference

### Run Module

- `run_template(template_path, dry_run=False, display_env=False, gen_env_target=None, skipped_steps=None, validate_only=False, exit_handlers=True)`: Run a template file
- `validate_template(template_path)`: Validate a template file without running it
- `display_environment(template_path)`: Display environment variables required by a template
- `generate_env_file(template_path, target_path)`: Generate a .env file with all environment variables required by a template

### Templates Module

- `list_templates(template_ids=None, orchestration_file=None, verbose=False)`: List available templates
- `get_template_details(template_id, verbose=True)`: Get details for a specific template
- `load_template_from_file(file_path)`: Load templates from an orchestration file
- `display_template(template, verbose=False)`: Display information about a template

### Entrypoint Module

- `run_entrypoint()`: Run the Docker entrypoint logic
- `get_entrypoint_env()`: Get environment variables from the project file
- `run_direct_simulator(args=None)`: Run the simulator directly
- `run_template_with_id(template_id, project_root=Path("/pkg/share"))`: Run a template with the given ID
