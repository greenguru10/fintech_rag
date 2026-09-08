"""FastAPI application factory and main entrypoint."""

from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.no_llm_policy import validate_no_llm_policy
from app.database.init_db import init_db
from app.database.session import SessionLocal
from app.api.router import api_router
from app.retrieval.index_manager import IndexManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Setup structured logging
    setup_logging()
    logger.info("startup.started", app=settings.APP_NAME, env=settings.APP_ENV)

    # 2. Strict No-LLM static verification
    app_dir = str(Path(__file__).resolve().parent)
    try:
        validate_no_llm_policy(app_dir)
        logger.info("startup.no_llm_policy_verified")
    except Exception as e:
        logger.error("startup.no_llm_violation", error=str(e))
        raise

    # 3. Load retrieval indexes immediately into memory
    idx_mgr = IndexManager.get_instance()
    loaded = idx_mgr.load_from_disk()
    if not loaded:
        db = SessionLocal()
        try:
            res = idx_mgr.rebuild_indexes(db)
            logger.info("startup.indexes_rebuilt", **res)
        finally:
            db.close()
    else:
        logger.info("startup.indexes_loaded_from_disk", chunks=len(idx_mgr.chunk_metadata))

    # 4. Optional background DB initialization check
    try:
        import anyio
        await anyio.to_thread.run_sync(init_db)
        logger.info("startup.database_initialized")
    except Exception as e:
        logger.warning(f"startup.init_db_notice: {e}")

    logger.info("startup.complete", ready=True)
    yield
    logger.info("shutdown.complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Deterministic, offline-first FinTech No-LLM Knowledge and Retrieval Chatbot",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes under prefix (e.g. /api/v1)
    app.include_router(api_router, prefix=settings.API_PREFIX)

    # Mount static assets for frontend
    static_dir = settings.BASE_DIR / "app" / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app


app = create_app()
