from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api import moderation, analytics
from src.database import Base, engine
import uvicorn

from src.api.errors import (
    ApiError,
    api_error_handler,
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.logger import logger

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Starting up Smart Content Moderator API...")
    yield
    logger.info("Shutting down Smart Content Moderator API...")

app = FastAPI(title="Smart Content Moderator API", lifespan=lifespan)

# Include routers
app.include_router(moderation.router, prefix="/api/v1/moderate", tags=["Moderation"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])


# Add exception handlers
app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

if __name__ == "__main__":
    logger.info("Launching app with Uvicorn")
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
