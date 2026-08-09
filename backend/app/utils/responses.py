from typing import Any, Generic, TypeVar

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    status_code: int = 200
    status: str = "success"
    message: str = ""
    data: T | None = None


def serialize_for_json(data: Any) -> Any:
    """Convert ORM models, UUIDs, dates, decimals, and enums to JSON-safe values."""
    return jsonable_encoder(data)


def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> JSONResponse:
    content = {
        "status_code": status_code,
        "status": "success",
        "message": message,
        "data": serialize_for_json(data),
    }
    return JSONResponse(status_code=status_code, content=content)


def error_response(message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "status_code": status_code,
            "status": "error",
            "message": message,
            "data": None,
        },
    )
