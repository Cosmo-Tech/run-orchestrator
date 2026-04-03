from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
import pathlib
import json
from typing import Annotated
import subprocess
import asyncio
import os


def find_projects():
    yield sorted(pathlib.Path(".").glob("**/run.json"))


projectListDependency = Annotated[list, Depends(find_projects)]

project_router = APIRouter(prefix="/project", tags=["Project"])


@project_router.get("/list")
async def list_projects(project_files: projectListDependency):
    project_names = [p.parent.name for p in project_files]
    return project_names


@project_router.post("/create")
async def create_project(project_data: dict = Body(...), project_files: projectListDependency = None):
    name = project_data.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Project name is required")
    # Validate name (alphanumeric, hyphens, underscores)
    import re

    if not re.match(r"^[a-zA-Z0-9_-]+$", name):
        raise HTTPException(
            status_code=400, detail="Project name must contain only letters, numbers, hyphens, and underscores"
        )
    # Check if project already exists
    existing = [p.parent.name for p in project_files]
    if name in existing:
        raise HTTPException(status_code=409, detail=f"Project '{name}' already exists")
    # Create project directory and run.json
    project_dir = pathlib.Path(".") / name
    project_dir.mkdir(parents=True, exist_ok=False)
    run_json = project_dir / "run.json"
    with open(run_json, "w") as f:
        json.dump({"steps": []}, f, indent=4)
    return {"name": name}


@project_router.get("/{project_name}/step/{step_id}")
async def get_step(project_name, step_id, project_files: projectListDependency):
    project_path = next((p for p in project_files if p.parent.name == project_name), None)
    if project_path is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    with open(project_path) as f:
        project_content = json.load(f)
    step = next((s for s in project_content["steps"] if s["id"] == step_id), None)
    if step is None:
        raise HTTPException(status_code=404, detail=f"Step '{step_id}' not found")
    return step


@project_router.put("/{project_name}/step/{step_id}")
async def update_step(project_name, step_id, step_data: dict = Body(...), project_files: projectListDependency = None):
    project_path = next((p for p in project_files if p.parent.name == project_name), None)
    if project_path is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    with open(project_path) as f:
        project_content = json.load(f)
    step_index = next((i for i, s in enumerate(project_content["steps"]) if s["id"] == step_id), None)
    if step_index is None:
        raise HTTPException(status_code=404, detail=f"Step '{step_id}' not found")
    if step_data["id"] != step_id:
        for i, step in enumerate(project_content["steps"]):
            if "precedents" in step:
                project_content["steps"][i]["precedents"] = [
                    precedent if precedent != step_id else step_data["id"] for precedent in step["precedents"]
                ]
    project_content["steps"][step_index] = step_data
    with open(project_path, "w") as f:
        json.dump(project_content, f, indent=4)
    return step_data


@project_router.post("/{project_name}/step")
async def create_step(project_name, step_data: dict = Body(...), project_files: projectListDependency = None):
    project_path = next((p for p in project_files if p.parent.name == project_name), None)
    if project_path is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    with open(project_path) as f:
        project_content = json.load(f)
    if not step_data.get("id"):
        raise HTTPException(status_code=400, detail="Step 'id' is required")
    existing = next((s for s in project_content["steps"] if s["id"] == step_data["id"]), None)
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Step '{step_data['id']}' already exists")
    project_content["steps"].append(step_data)
    with open(project_path, "w") as f:
        json.dump(project_content, f, indent=4)
    return step_data


@project_router.delete("/{project_name}/step/{step_id}")
async def remove_step(project_name, step_id, project_files: projectListDependency = None):
    project_path = next((p for p in project_files if p.parent.name == project_name), None)
    if project_path is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    with open(project_path) as f:
        project_content = json.load(f)
    step_index = next((i for i, s in enumerate(project_content["steps"]) if s["id"] == step_id), None)
    if step_index is None:
        raise HTTPException(status_code=404, detail=f"Step '{step_id}' not found")
    for i, step in enumerate(project_content["steps"]):
        if "precedents" in step:
            project_content["steps"][i]["precedents"] = [
                precedent for precedent in step["precedents"] if precedent != step_id
            ]
    project_content["steps"].pop(step_index)
    with open(project_path, "w") as f:
        json.dump(project_content, f, indent=4)
    return project_content


@project_router.get("/{project_name}/steps")
async def get_steps(project_name, project_files: projectListDependency):
    project_path = next((p for p in project_files if p.parent.name == project_name), None)
    if project_path is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    with open(project_path) as f:
        project_content = json.load(f)
    steps = [s["id"] for s in project_content["steps"]]
    return steps


@project_router.get("/{project_name}/precedents")
async def get_steps_with_precedents(project_name, project_files: projectListDependency):
    project_path = next((p for p in project_files if p.parent.name == project_name), None)
    if project_path is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    with open(project_path) as f:
        project_content = json.load(f)
    precedents = {s["id"]: s.get("precedents", []) for s in project_content["steps"]}
    return precedents


@project_router.get("/{project_name}/outputs")
async def get_step_outputs(project_name, project_files: projectListDependency):
    project_path = next((p for p in project_files if p.parent.name == project_name), None)
    if project_path is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    with open(project_path) as f:
        project_content = json.load(f)
    result = {}
    for step in project_content["steps"]:
        outputs = step.get("outputs", {})
        if outputs:
            result[step["id"]] = list(outputs.keys())
    return result


@project_router.post("/{project_name}/link")
async def add_link(project_name, link_data: dict = Body(...), project_files: projectListDependency = None):
    project_path = next((p for p in project_files if p.parent.name == project_name), None)
    if project_path is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    source = link_data.get("source")
    target = link_data.get("target")
    if not source or not target:
        raise HTTPException(status_code=400, detail="Both 'source' and 'target' are required")
    if source == target:
        raise HTTPException(status_code=400, detail="Cannot link a step to itself")
    with open(project_path) as f:
        project_content = json.load(f)
    step_ids = [s["id"] for s in project_content["steps"]]
    if source not in step_ids:
        raise HTTPException(status_code=404, detail=f"Source step '{source}' not found")
    if target not in step_ids:
        raise HTTPException(status_code=404, detail=f"Target step '{target}' not found")
    target_step = next(s for s in project_content["steps"] if s["id"] == target)
    precedents = target_step.get("precedents", [])
    if source in precedents:
        raise HTTPException(status_code=409, detail=f"Link already exists")
    # Cycle detection: check if target can reach source through existing edges
    adjacency = {}
    for s in project_content["steps"]:
        adjacency[s["id"]] = s.get("precedents", [])
    # Add the proposed link temporarily
    temp_precedents = adjacency.get(target, []) + [source]
    adjacency[target] = temp_precedents
    # BFS from source following reverse edges (precedents) to see if we reach target
    visited = set()
    queue = [source]
    while queue:
        current = queue.pop(0)
        if current == target:
            raise HTTPException(status_code=400, detail="This link would create a cycle in the graph")
        if current in visited:
            continue
        visited.add(current)
        for p in adjacency.get(current, []):
            queue.append(p)
    precedents.append(source)
    target_step["precedents"] = precedents
    with open(project_path, "w") as f:
        json.dump(project_content, f, indent=4)
    return {"source": source, "target": target}


@project_router.delete("/{project_name}/link")
async def remove_link(project_name, link_data: dict = Body(...), project_files: projectListDependency = None):
    project_path = next((p for p in project_files if p.parent.name == project_name), None)
    if project_path is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    source = link_data.get("source")
    target = link_data.get("target")
    if not source or not target:
        raise HTTPException(status_code=400, detail="Both 'source' and 'target' are required")
    with open(project_path) as f:
        project_content = json.load(f)
    target_step = next((s for s in project_content["steps"] if s["id"] == target), None)
    if target_step is None:
        raise HTTPException(status_code=404, detail=f"Target step '{target}' not found")
    precedents = target_step.get("precedents", [])
    if source not in precedents:
        raise HTTPException(status_code=404, detail=f"Link not found")
    precedents.remove(source)
    target_step["precedents"] = precedents
    with open(project_path, "w") as f:
        json.dump(project_content, f, indent=4)
    return {"source": source, "target": target}


@project_router.get("/{project_name}/links")
async def get_step_links(project_name, project_files: projectListDependency):
    project_path = next((p for p in project_files if p.parent.name == project_name), None)
    if project_path is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    with open(project_path) as f:
        project_content = json.load(f)
    links = [(precedent, step["id"]) for step in project_content["steps"] for precedent in step.get("precedents", [])]
    return links


@project_router.get("/{project_name}/environment")
async def get_project_environment(project_name, project_files: projectListDependency = None):
    """Collect all environment variables from steps and their templates."""
    project_path = next((p for p in project_files if p.parent.name == project_name), None)
    if project_path is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    with open(project_path) as f:
        project_content = json.load(f)

    # Try to load templates
    from cosmotech.orchestrator.templates.library import Library

    library = Library()

    env_vars = {}  # name -> { value, defaultValue, optional, description, systemValue, sources: [] }

    for step in project_content["steps"]:
        step_id = step["id"]
        # Collect from template if step has commandId
        command_id = step.get("commandId")
        if command_id:
            tpl = library.find_template_by_name(command_id)
            if tpl:
                tpl_data = tpl.serialize()
                for var_name, var_def in (tpl_data.get("environment") or {}).items():
                    if var_name not in env_vars:
                        env_vars[var_name] = {
                            "value": var_def.get("value", ""),
                            "defaultValue": var_def.get("defaultValue", ""),
                            "optional": var_def.get("optional", False),
                            "description": var_def.get("description", ""),
                            "sources": [],
                        }
                    env_vars[var_name]["sources"].append(
                        {
                            "type": "template",
                            "templateId": command_id,
                            "stepId": step_id,
                        }
                    )

        # Collect from step's own environment
        for var_name, var_def in (step.get("environment") or {}).items():
            if var_name not in env_vars:
                env_vars[var_name] = {
                    "value": var_def.get("value", ""),
                    "defaultValue": var_def.get("defaultValue", ""),
                    "optional": var_def.get("optional", False),
                    "description": var_def.get("description", ""),
                    "sources": [],
                }
            else:
                # Step overrides template values
                if var_def.get("value"):
                    env_vars[var_name]["value"] = var_def["value"]
                if var_def.get("defaultValue"):
                    env_vars[var_name]["defaultValue"] = var_def["defaultValue"]
                if "optional" in var_def:
                    env_vars[var_name]["optional"] = var_def["optional"]
                if var_def.get("description"):
                    env_vars[var_name]["description"] = var_def["description"]
            env_vars[var_name]["sources"].append(
                {
                    "type": "step",
                    "stepId": step_id,
                }
            )

    # Add system environment values for each defined variable
    for var_name in env_vars:
        system_val = os.environ.get(var_name)
        env_vars[var_name]["systemValue"] = system_val if system_val is not None else ""

    return env_vars


@project_router.post("/{project_name}/run")
async def run_project(project_name, run_data: dict = Body(default={}), project_files: projectListDependency = None):
    project_path = next((p for p in project_files if p.parent.name == project_name), None)
    if project_path is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")

    # Build environment for the subprocess
    env = os.environ.copy()
    user_env = run_data.get("environment", {})
    for k, v in user_env.items():
        if v is not None and v != "":
            env[k] = str(v)

    # Build skip-step arguments
    skipped_steps = run_data.get("skippedSteps", [])
    skip_args = []
    for step_id in skipped_steps:
        skip_args.extend(["--skip-step", step_id])

    async def event_stream():
        proc = await asyncio.create_subprocess_exec(
            "csm-orc",
            "run",
            *skip_args,
            str(project_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=env,
        )
        try:
            async for line in proc.stdout:
                text = line.decode("utf-8", errors="replace").rstrip("\n")
                yield f"data: {json.dumps({'type': 'log', 'text': text})}\n\n"
            await proc.wait()
            yield f"data: {json.dumps({'type': 'exit', 'code': proc.returncode})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'text': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@project_router.get("/{project_name}")
async def get_content(project_name, project_files: projectListDependency):
    project_path = next((p for p in project_files if p.parent.name == project_name), None)
    if project_path is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    with open(project_path) as f:
        project_content = json.load(f)
    return project_content
