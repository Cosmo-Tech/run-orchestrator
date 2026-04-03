import os
import pathlib
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.routing import APIRoute
from cosmotech.orchestrator.utils.logger import LOGGER
from cosmotech.orchestrator import __version__ as orchestrator_version


@asynccontextmanager
async def lifespan(app: FastAPI):
    LOGGER.info("Starting Visual Orchestrator API...")

    yield

    LOGGER.info("Stopping Visual Orchestrator API...")


# Code found on FastAPI discussion : https://github.com/fastapi/fastapi/discussions/6695#discussioncomment-8247988
# Used to remove 422 error code from documentation
_openapi = FastAPI.openapi


def openapi(self: FastAPI):
    _openapi(self)

    for _, method_item in self.openapi_schema.get("paths").items():
        for _, param in method_item.items():
            responses = param.get("responses")
            # remove 422 response, also can remove other status code
            if "422" in responses:
                del responses["422"]

            # Keep only the most specific (last) tag so that sub-router endpoints
            # appear exclusively under their own category and not under every
            # ancestor router's category.
            if "tags" in param and len(param["tags"]) > 1:
                param["tags"] = [param["tags"][-1]]

    return self.openapi_schema


FastAPI.openapi = openapi

app = FastAPI(
    version=orchestrator_version,
    docs_url="/swagger",
    redoc_url="/swagger/redoc",
    swagger_ui_oauth2_redirect_url="/swagger/oauth2-redirect",
    openapi_url="/openapi.json",
    title="Visual Orchestrator API",
    description="API for Visual Orchestrator",
    root_path="/",
    lifespan=lifespan,
)

from .router.project import project_router
from .router.templates import template_router

app.include_router(project_router)
app.include_router(template_router)


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name  # in this case, 'read_items'


use_route_names_as_operation_ids(app)
