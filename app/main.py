import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.routers import chat, conversation, documents, health, jobs
from app.bootstrap import build_services
from app.core.config import Settings
from app.core.exceptions import ApplicationError
from app.core.logging import configure_logging
from app.services.container import Services

logger = logging.getLogger(__name__)


def create_app(services: Services | None = None, settings: Settings | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        configured = settings or Settings()
        configure_logging(configured.log_level)
        if services is not None:
            app.state.services = services
            yield
        else:
            async with build_services(configured) as dependencies:
                app.state.services = dependencies
                yield

    app = FastAPI(title="Mistral RAG", version="0.2.0", lifespan=lifespan)
    static = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static), name="static")

    @app.get("/", include_in_schema=False)
    async def chat_page():
        return FileResponse(static / "index.html")

    app.include_router(conversation.router, prefix="/api/v1")
    app.include_router(jobs.router, prefix="/api/v1")

    @app.exception_handler(ApplicationError)
    async def application_error(request: Request, error: ApplicationError):
        logger.warning(
            "%s %s -> %s (%s)", request.method, request.url.path, error.status_code, type(error).__name__
        )
        return JSONResponse(status_code=error.status_code, content={"detail": error.detail})

    for router in (health.router, documents.router, chat.router):
        app.include_router(router, prefix="/api/v1")
        # Compatibilité des premiers exemples ; seule l'API versionnée figure dans Swagger.
        app.include_router(router, include_in_schema=False)
    return app


app = create_app()
