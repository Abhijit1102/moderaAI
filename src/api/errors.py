from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from pydantic import BaseModel
from typing import List, Optional


# -------- Pydantic Models --------

class ApiErrorResponse(BaseModel):
    success: bool = False
    message: str = "Something went wrong"
    errors: List[str] = []
    stack: Optional[str] = None


class ApiResponse(BaseModel):
    status_code : int
    success: bool = True
    message: str = "Success"
    data: Optional[object] = None  


# -------- Exception Classes --------

class ApiError(Exception):
    def __init__(
        self,
        status_code: int,
        message: str = "Something went wrong",
        errors: Optional[List[str]] = None,
        stack: str = "",
    ):
        self.status_code = status_code
        self.message = message
        self.errors = errors or []
        self.stack = stack


# -------- Exception Handlers --------

async def api_error_handler(request: Request, exc: ApiError):
    payload = ApiErrorResponse(
        message=exc.message,
        errors=exc.errors,
        stack=exc.stack or None
    )
    return JSONResponse(status_code=exc.status_code, content=payload.dict())


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    payload = ApiErrorResponse(
        message="Validation error",
        errors=[str(err) for err in exc.errors()]
    )
    return JSONResponse(status_code=422, content=payload.dict())


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    payload = ApiErrorResponse(
        message=exc.detail,
        errors=[]
    )
    return JSONResponse(status_code=exc.status_code, content=payload.dict())


async def generic_exception_handler(request: Request, exc: Exception):
    payload = ApiErrorResponse(
        message="Internal Server Error",
        errors=[str(exc)]
    )
    return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content=payload.dict())
