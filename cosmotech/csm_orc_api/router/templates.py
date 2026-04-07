from fastapi import APIRouter, HTTPException, Path
from typing import Annotated
from fastapi import Depends
from cosmotech.orchestrator.templates.library import Library

from cosmotech.orchestrator.core.command_template import CommandTemplate


def get_library():
    yield Library()


libraryDependency = Annotated[Library, Depends(get_library)]


def get_template_by_id(template_id: Annotated[str, Path(description="Id of the template")], library: libraryDependency):
    template = library.find_template_by_name(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


templateDependency = Annotated[CommandTemplate, Depends(get_template_by_id)]

template_router = APIRouter(prefix="/template", tags=["Template"])


@template_router.get("/list")
async def list_templates(library: libraryDependency):
    return [t.id for t in library.templates]


@template_router.get("/{template_id}")
async def get_template(template: templateDependency):
    return template.serialize()
