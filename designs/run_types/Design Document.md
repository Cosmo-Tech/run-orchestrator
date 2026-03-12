# CSM-ORC Run Type Files Feature Design

## Business Context

### Problem Statement
When a runner is deleted in the CosmoTech platform, associated runs are removed however associated result data pushed by the runner execution are not removed. This causes:
- Accumulation of unused data in Superset
- Database bloat from deleted scenarios
- Confusion from stale visualizations
- Storage waste

### Global Solution
To solve this problem we have 3 sector of action to take care of. First, csm-orc must be capable to execute a deletion (this is the solution describe in this document). Second, the cosmotech API must be able to trigger said deletion. And third, Coal lib must provide the delete capability to it's writing capability; meaning that what's coal allows to write into, coal must also be allowed to remove from.

### Solution
Because each runner — and, by extension, each run_template — can produce its own output data, every run_template must provide a way to remove the data it creates. To enable this, a run_template must define a `delete.json` file alongside its `run.json`. The API sets the `CSM_RUN_TYPE=delete` environment variable when triggering a runner deletion, causing `entrypoint.py` to load `delete.json` instead of `run.json` and execute its steps through the same orchestrator mechanism.

## Overview
This document describes the design for adding support for different run types (regular run vs delete) in the run-orchestrator project. The solution introduces a `delete.json` file per run_template that uses the exact same execution mechanism as `run.json`.

**Supported Run Types:**
- `run` — Default execution (loads `run.json`)
- `delete` — Delete operations after runner deletion (loads `delete.json`)

**Set by:** API or administrator via the `CSM_RUN_TYPE` environment variable:
- Regular run: Not set, or explicitly `"run"`
- Delete run: Set to `"delete"` on runner deletion event

**Missing file behavior:**
- `run.json` missing → error (run is always required)
- `delete.json` missing → log a warning and exit successfully (delete is optional; not all templates need cleanup)

## Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────┐
│ API - Event Handlers                                    │
│                                                         │
│ @EventListener onRunnerDeleted(event)                   │
│   └─ Trigger: CSM_RUN_TYPE=delete                       │
│                                                         │
│ @EventListener onRegularRun(event)                      │
│   └─ Trigger: CSM_RUN_TYPE=run (or not set)             │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ Transmission - Environment Variable                     │
│                                                         │
│ CSM_RUN_TYPE=delete           (delete run)              │
│ CSM_RUN_TYPE=run              (regular run, default)    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ CSM-ORC - entrypoint.py                                 │
│                                                         │
│ run_template_with_id()                                  │
│   ├─ Read CSM_RUN_TYPE from environment                 │
│   ├─ Build file path:                                   │
│   │   /pkg/share/code/run_templates/{id}/{type}.json    │
│   │   ├─ "run"     → run.json                           │
│   │   └─ "delete"  → delete.json                        │
│   ├─ File exists?                                       │
│   │   ├─ Yes → Execute: csm-orc run <path-to-json>      │
│   │   └─ No  → run type = "run"  : raise error          │
│   │            run type = other  : log warning, skip    │
│                                                         │
│ Orchestrator                                            │
│   ├─ Load and validate JSON file                        │
│   ├─ Build DAG from steps                               │
│   └─ Execute steps in dependency order                  │
└─────────────────────────────────────────────────────────┘
```

## Current Architecture

### Execution Flow
1. **Entrypoint** (`entrypoint.py`):
   - Reads `CSM_RUN_TEMPLATE_ID` from environment
   - Constructs path: `/pkg/share/code/run_templates/{template_id}/run.json`
   - Executes: `csm-orc run <path-to-run.json>`

2. **Orchestrator** (`orchestrator.py`):
   - Loads the JSON file
   - Validates against schema
   - Creates Step objects from the JSON
   - Builds a DAG (Directed Acyclic Graph) using flowpipe
   - Executes steps in dependency order

3. **Template Structure**:
   ```json
   {
     "commandTemplates": [...],  // Reusable command definitions
     "steps": [...]              // Actual execution steps
   }
   ```

## Proposed Solution

### 1. Environment Variable
Add a new environment variable to indicate the run type:
- **Name**: `CSM_RUN_TYPE`
- **Values**: 
  - `"run"` (default) - executes `run.json`
  - `"delete"` - executes `delete.json`
- **Set by**: API when triggering a runner deletion

### 2. File Structure
Both files will coexist in the same template directory:
```
/pkg/share/code/run_templates/
  └── {template_id}/
      ├── run.json     # Regular execution steps
      └── delete.json  # Delete steps
```

### 3. Implementation Changes

#### A. Modify `entrypoint.py` - `run_template_with_id()` function

**Location**: `/home/lalepee/git/run-orchestrator/cosmotech/orchestrator/api/entrypoint.py` (around line 145)

**Current Code**:
```python
def run_template_with_id(template_id: str, project_root: Path = Path("/pkg/share")) -> int:
    # ... setup code ...
    
    orchestrator_json = project_root / "code/run_templates" / template_id / "run.json"
    if not orchestrator_json.is_file():
        raise EntrypointException(T("csm-orc.orchestrator.errors.no_run_json").format(template_id=template_id))
    
    # ... execution code ...
```

**New Code**:
```python
def run_template_with_id(template_id: str, project_root: Path = Path("/pkg/share")) -> int:
    # ... setup code ...
    
    # Determine which JSON file to use based on CSM_RUN_TYPE
    run_type = os.environ.get("CSM_RUN_TYPE", "run").lower()
    template_filename = f"{run_type}.json"
    
    orchestrator_json = project_root / "code/run_templates" / template_id / template_filename
    if not orchestrator_json.is_file():
        if run_type == "run":
            raise EntrypointException(
                T("csm-orc.orchestrator.errors.no_template_json").format(
                    template_id=template_id,
                    run_type=run_type,
                    filename=template_filename
                )
            )
        else:
            LOGGER.warning(
                f"No {template_filename} found for template '{template_id}' "
                f"(run type: {run_type}) — skipping."
            )
            return 0
    
    # ... execution code ...
```

#### B. Update Translation Messages (Optional but Recommended)

**Location**: Translation files (likely in `cosmotech/orchestrator/utils/` or similar)

Add/update error messages:
- `csm-orc.orchestrator.errors.no_template_json`: "Template file '{filename}' not found for template '{template_id}' (run type: {run_type})"

#### C. CLI Enhancement (Optional)

Add a `--run-type` option to the `csm-orc run` command for testing:

**Location**: `/home/lalepee/git/run-orchestrator/cosmotech/csm_orc/run.py`

```python
@click.option(
    "--run-type",
    envvar="CSM_RUN_TYPE",
    show_envvar=True,
    default="run",
    show_default=True,
    type=click.Choice(["run", "delete"], case_sensitive=False),
    help="Type of template to execute (run.json or delete.json)",
)
def run_command(
    template: str,
    # ... other parameters ...
    run_type: str,
):
    # Note: This option mainly serves for CLI testing
    # The actual logic is in entrypoint.py which reads CSM_RUN_TYPE directly
```

## Implementation Details

### Phase 1: Core Functionality
1. ✅ Modify `run_template_with_id()` to support dynamic template names
2. ✅ Update error messages for missing template files
3. ✅ Test with environment variable `CSM_RUN_TYPE`

## Benefits of This Approach

1. **Minimal Code Changes**: Only modifying the entrypoint logic
2. **Reuses Existing Infrastructure**: All orchestrator features work (precedents, environment variables, DAG execution)
3. **Clear Separation**: `run.json` and `delete.json` are separate files, clear responsibility
4. **Flexible**: Each template can define its own delete steps
5. **Testable**: Can test delete locally using `CSM_RUN_TYPE=delete csm-orc run <template>`
6. **Graceful Degradation**: Templates without a `delete.json` are silently skipped, ensuring backward compatibility and safe rollout

## Testing Strategy

### Unit Tests
```python
def test_run_template_with_delete_type():
    os.environ["CSM_RUN_TYPE"] = "delete"
    # Verify delete.json is loaded
    
def test_run_template_with_default_type():
    # Verify run.json is loaded by default
    
def test_run_template_missing_delete_file():
    os.environ["CSM_RUN_TYPE"] = "delete"
    # Verify exit code 0 (skip) when delete.json doesn't exist
    
def test_run_template_missing_run_file():
    # Verify error is raised when run.json doesn't exist
```

### Integration Tests
1. Create a test template with both `run.json` and `delete.json`
2. Execute with `CSM_RUN_TYPE=run` - verify run.json steps execute
3. Execute with `CSM_RUN_TYPE=delete` - verify delete.json steps execute

### Manual Testing
```bash
# Test regular run
cd /home/lalepee/git/run-orchestrator
CSM_RUN_TYPE=run csm-orc run examples/minimal_docker/code/run_templates/RUN/run.json

# Test delete run (after creating delete.json)
CSM_RUN_TYPE=delete csm-orc run examples/minimal_docker/code/run_templates/RUN/delete.json
```