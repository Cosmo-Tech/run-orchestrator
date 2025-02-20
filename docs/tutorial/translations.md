---
description: Tutorial on adding and using translations in the run-orchestrator
---
# Adding translations

!!! abstract "Objective"
    + Learn how the run-orchestrator translation system works  
    + Add new languages to the existing translation system  
    + Create custom translations for your own projects  
    + Use translations effectively in your code  

!!! warning "Requirements"
    - Basic understanding of YAML file format  
    - Familiarity with Python package structure  

## Translation system overview

The run-orchestrator uses a hierarchical translation system based on YAML files. Each supported language has its own directory containing translation files.

```text title="Translation system structure"
cosmotech/translation/csm-orc/
├── br/                # Breton
├── de-DE/             # German
├── en-US/             # English (US)
├── es-ES/             # Spanish
├── fr-FR/             # French
├── sjn/               # Sindarin
├── tlh/               # Klingon
└── zh-CN/             # Chinese (Simplified)
```

Each language directory contains two main components:
```text
language-code/
├── csm-orc.yml       # Main translation file
└── rich/             # Rich text specific translations
    └── csm-orc.yml
```

## Basic translation usage

### Translation file format

Translation files use a simple YAML structure with nested keys:

```yaml title="Example: en-US/csm-orc.yml"
csm-orc:
  error:
    missing_env: "Missing environment values"
    missing_env_var: "Missing environment variables, check the logs"
  info:
    run_start: "===      Run     ==="
    run_end: "===     Results    ==="
```

### Using translations in code

The translation function `T` is your main tool for accessing translations. Here are real examples from the run-orchestrator project:

```python title="Example: Logging with translations"
from cosmotech.orchestrator.utils.translate import T
from cosmotech.orchestrator.utils.logger import LOGGER

# Simple log message
LOGGER.info(T("csm-orc.logs.step.starting").format(
    step_type="step",
    step_id=step.id
))

# Error message with variable
LOGGER.error(T("csm-orc.logs.step.template_not_found").format(
    step_id=step.display_id,
    command_id=step.display_command_id
))

# Status messages
LOGGER.info(T("csm-orc.logs.orchestrator.valid_file").format(
    file_path=json_file_path
))
```

The translation keys follow a hierarchical structure:
```yaml title="Translation key structure"
csm-orc:
  logs:
    step:
      starting: "Starting {step_type} {step_id}"
      template_not_found: "Template {command_id} not found for step {step_id}"
    orchestrator:
      valid_file: "File {file_path} is valid"
```

!!! tip "Translation formatting"
    - Use descriptive key hierarchies (e.g., `logs.step.starting`)  
    - Include variables using Python's string formatting syntax  
    - Keep messages clear and consistent across languages  

!!! info "Translation fallback"
    The system will:  
    1. Try to find the key in the current language  
    2. Fall back to English (en-US) if not found  
    3. Return the key itself if no translation exists  

### Setting the language

Use the `CSM_LOCALE` environment variable to control the active language:

```bash title="Setting the language"
# Use French translations
export CSM_LOCALE=fr-FR
csm-orc run my_template.json
```

## Adding a new language

To add support for a new language:

1. Create a new language directory:
```bash
mkdir -p cosmotech/translation/csm-orc/goa-uld/rich
```

2. Create the main translation file:
```yaml title="goa-uld/csm-orc.yml"
csm-orc:
  error:
    missing_env: "Kree! Environment values not found"
    missing_env_var: "Jaffa! Environment variables missing, check the logs"
  info:
    run_start: "=== Tau'ri Run Initiated ==="
    run_end: "=== Shol'va Results ==="
```

3. Create the rich text translations:
```yaml title="goa-uld/rich/csm-orc.yml"
csm-orc:
  rich:
    # Rich text specific translations
```

!!! tip "Translation process"
    1. Copy the English (en-US) files as a starting point  
    2. Translate each message while preserving the key structure  
    3. Keep any variable placeholders (e.g., {filename}) intact  
    4. Test the translations in context  

## Project-specific translations

You can add translations to your own project by following a similar structure:

1. Create the translation directory structure:
```text title="Project structure"
your-project/
└── cosmotech/
    └── translation/
        └── my-project/           # Your project name
            ├── __init__.py       # Required!
            ├── en-US/
            │   ├── my-project.yml
            │   └── rich/
            │       └── my-project.yml
            └── fr-FR/
                ├── my-project.yml
                └── rich/
                    └── my-project.yml
```

!!! warning "Important"
    The `__init__.py` file is required for the translation system to discover your translations. Without it, your translations will not be loaded.

2. Add the dependency requirement:
```text title="requirements.txt"
cosmotech-run-orchestrator>=2.0.0
```

!!! tip "Dependency management"
    You can also use other dependency management systems like poetry or setup.py, just ensure you specify a minimum version of 2.0.0 for cosmotech-run-orchestrator.

3. Create your translation files:
```yaml title="my-project/en-US/my-project.yml"
my-project:  # Your namespace
  info:
    start_message: "Starting process..."
    complete_message: "Process complete"
  error:
    invalid_input: "Invalid input: {input}"
```

4. Use translations in your code:
```python title="Using project translations"
from cosmotech.orchestrator.utils.translate import T

def process_data(input_value):
    if not validate_input(input_value):
        print(T("my-project.error.invalid_input").format(input=input_value))
    
    print(T("my-project.info.start_message"))
    # Process the data...
    print(T("my-project.info.complete_message"))
```

!!! tip "Project translation tips"
    - Use a unique namespace to avoid conflicts  
    - Organize translations into logical categories  
    - Keep keys consistent across languages  
    - Document any variables used in messages  

## Validation

Before deploying translations, validate your files:

```python title="validate_translations.py"
import yaml
from pathlib import Path

def validate_translation_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            translations = yaml.safe_load(f)
            print(f"✓ {file_path} is valid YAML")
            return translations
    except yaml.YAMLError as e:
        print(f"✗ Error in {file_path}: {e}")
        return None

# Validate a translation file
validate_translation_file("path/to/translation.yml")
```

!!! tip "Validation checklist"
    - [ ] YAML syntax is valid  
    - [ ] All required keys are present  
    - [ ] Variable placeholders are preserved  
    - [ ] Special characters are properly encoded  
    - [ ] Translations make sense in context
