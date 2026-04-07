import pathlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.routing import APIRoute
from cosmotech.orchestrator.utils.logger import LOGGER
from cosmotech.orchestrator import __version__ as orchestrator_version

STATIC_DIR = pathlib.Path(__file__).parent / "static"
VISUAL_ORC_SRC_DIR = pathlib.Path(__file__).parent.parent / "visual_orchestrator"


def is_dev_mode() -> bool:
    """Detect dev mode: no built static files but visual_orchestrator source exists."""
    return not (STATIC_DIR / "index.html").exists() and (VISUAL_ORC_SRC_DIR / "package.json").exists()


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
    root_path="",
    lifespan=lifespan,
)

from .router.project import project_router
from .router.templates import template_router

app.include_router(project_router)
app.include_router(template_router)

# Serve built static files in release mode
if (STATIC_DIR / "index.html").exists():
    from starlette.staticfiles import StaticFiles
    from starlette.responses import FileResponse, Response
    from starlette.types import Scope, Receive, Send
    import anyio

    class SPAStaticFiles(StaticFiles):
        """StaticFiles that falls back to index.html for SPA routing."""

        async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
            try:
                await super().__call__(scope, receive, send)
            except Exception:
                # If file not found, serve index.html for SPA client-side routing
                response = FileResponse(self.directory / "index.html")
                await response(scope, receive, send)

    app.mount("/", SPAStaticFiles(directory=STATIC_DIR, html=False), name="static")


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
