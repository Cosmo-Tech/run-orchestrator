---
description: Simple simulation template file
---

# Simple Simulation Run

## Description

This simple template make use of the `main` executable created when a Cosmo Tech simulator is built.

To use it locally you can add `Generated/Build/Bin` to your current `PATH` or just use `csm exec` if you have set
up `csmcli` on your system

## Example call

```bash
export CSM_SIMULATION=MySimulation
csm exec csm-orc run run.json
```

## Template

```json title="run.json" linenums="1"
--8<-- "templates/SimpleSimulationRun.json"
```