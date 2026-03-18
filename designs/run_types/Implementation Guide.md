# Implementation Guide: Run Type Support

## Quick Start

### 1. Apply the Code Changes

The main change is in the entrypoint.py file. Here's the exact modification needed:

**File**: `/home/lalepee/git/run-orchestrator/cosmotech/orchestrator/api/entrypoint.py`

**Find this code** (around line 145-151):
```python
def run_template_with_id(template_id: str, project_root: Path = Path("/pkg/share")) -> int:
    """
    Run a template with the given ID.

    Args:
        template_id: ID of the template to run
        project_root: Root directory of the project

    Returns:
        Exit code from the template run
    """
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.info(T("csm-orc.cli.entrypoint.start"))

    if importlib.util.find_spec("cosmotech") is None or importlib.util.find_spec("cosmotech.orchestrator") is None:
        raise EntrypointException(T("csm-orc.orchestrator.errors.missing_library"))

    orchestrator_json = project_root / "code/run_templates" / template_id / "run.json"
    if not orchestrator_json.is_file():
        raise EntrypointException(T("csm-orc.orchestrator.errors.no_run_json").format(template_id=template_id))
```

**Replace with**:
```python
def run_template_with_id(template_id: str, project_root: Path = Path("/pkg/share")) -> int:
    """
    Run a template with the given ID.

    Args:
        template_id: ID of the template to run
        project_root: Root directory of the project

    Returns:
        Exit code from the template run
    """
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.info(T("csm-orc.cli.entrypoint.start"))

    if importlib.util.find_spec("cosmotech") is None or importlib.util.find_spec("cosmotech.orchestrator") is None:
        raise EntrypointException(T("csm-orc.orchestrator.errors.missing_library"))

    # Determine which template file to use based on CSM_RUN_TYPE
    run_type = os.environ.get("CSM_RUN_TYPE", "run").lower()
    template_filename = f"{run_type}.json"
    
    LOGGER.debug(f"Run type: {run_type}, loading template: {template_filename}")
    
    orchestrator_json = project_root / "code/run_templates" / template_id / template_filename
    if not orchestrator_json.is_file():
        error_msg = f"Template file '{template_filename}' not found for template '{template_id}' (run type: {run_type})"
        LOGGER.error(error_msg)
        raise EntrypointException(error_msg)
```

### 2. Test Locally

Create a test delete.json file:

```bash
cd /home/lalepee/git/run-orchestrator/examples/minimal_docker/code/run_templates/RUN/

# Create a simple delete.json for testing
cat > delete.json << 'EOF'
{
  "steps": [
    {
      "id": "delete_test",
      "command": "echo",
      "description": "Test delete step",
      "arguments": [
        "Running delete for run: $CSM_RUN_ID"
      ],
      "environment": {
        "CSM_RUN_ID": {
          "defaultValue": "test-run-123",
          "description": "The run ID to delete"
        }
      }
    }
  ]
}
EOF
```

Test the normal run:
```bash
cd /home/lalepee/git/run-orchestrator
CSM_RUN_TYPE=run csm-orc run examples/minimal_docker/code/run_templates/RUN/run.json
```

Test the delete run:
```bash
cd /home/lalepee/git/run-orchestrator
CSM_RUN_TYPE=delete csm-orc run examples/minimal_docker/code/run_templates/RUN/delete.json
```

## Rollout Plan

### Phase 1: Infrastructure (Week 1)
- [ ] Apply entrypoint.py changes
- [ ] Create unit tests for run type selection
- [ ] Test locally with example templates
- [ ] Update documentation

### Phase 2: Template Creation (Week 2)
- [ ] Create delete.json template structure
- [ ] Implement Superset delete script
- [ ] Implement database delete script
- [ ] Test delete scripts with real data