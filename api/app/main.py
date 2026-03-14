from fastapi.staticfiles import StaticFiles
from api.config.settings import settings
import os
from fastapi import FastAPI
from sqlalchemy import text
from contextlib import asynccontextmanager
from asgi_correlation_id import CorrelationIdMiddleware

from api.config.db import Base, engine
from api.routes.auth import router as auth_router
from api.routes.protected import router as protected_router
from api.routes.health import router as health_router
from api.routes.clients import router as clients_router
from api.routes.documents import router as documents_router
from api.routes.locations import router as locations_router
from api.routes.products import router as products_router
from api.routes.product_categories import router as product_categories_router
from api.utils.logger import logger
from api.middlewares.logging import LoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connection OK")  # print to console
        logger.info("Database connection OK")  # print to log

    except Exception as e:
        print("Database connection FAILED:", e)  # print to console
        logger.error("Database connection FAILED:",
                     exc_info=True)  # print to log
        raise e
    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown complete")


app = FastAPI(title="Invoice API", lifespan=lifespan)

# ensure storage directory exists
os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)

# Add middleware for logging
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(LoggingMiddleware)

# Add routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(protected_router)
app.include_router(clients_router)
app.include_router(products_router)
app.include_router(product_categories_router)
app.include_router(documents_router)
app.include_router(locations_router)


# mount directory so files are retrievable by URL
app.mount("/files", StaticFiles(directory=settings.DOCUMENTS_DIR), name="files")
