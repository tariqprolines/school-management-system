from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.config.database import Base, engine
from app.config.settings import settings
from app.controllers import (
    academic_controller,
    auth_controller,
    dashboard_controller,
    fee_controller,
    people_controller,
    timetable_controller,
)
from app.services.seed_service import SeedService
from app.config.database import async_session
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as db:
        await SeedService.seed_all(db)
    yield


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, list):
        message = "; ".join(str(item) for item in detail)
    else:
        message = str(detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "status": "error",
            "message": message,
            "data": None,
        },
    )


@app.exception_handler(IntegrityError)
async def integrity_exception_handler(_request: Request, exc: IntegrityError):
    from app.utils.db_errors import integrity_error_message

    return JSONResponse(
        status_code=400,
        content={
            "status_code": 400,
            "status": "error",
            "message": integrity_error_message(exc),
            "data": None,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception):
    if settings.DEBUG:
        message = str(exc)
    else:
        message = "An unexpected server error occurred"
    return JSONResponse(
        status_code=500,
        content={
            "status_code": 500,
            "status": "error",
            "message": message,
            "data": None,
        },
    )


app.include_router(auth_controller.router, prefix="/api/v1")
app.include_router(academic_controller.router, prefix="/api/v1")
app.include_router(people_controller.router, prefix="/api/v1")
app.include_router(timetable_controller.router, prefix="/api/v1")
app.include_router(fee_controller.router, prefix="/api/v1")
app.include_router(dashboard_controller.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}
