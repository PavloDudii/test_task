from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
import logging

from .exceptions import (
    BookManagementException,
    NotFoundError,
    ValidationError,
    DuplicateError,
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
)

logger = logging.getLogger(__name__)


async def book_management_exception_handler(
    request: Request, exc: BookManagementException
):
    """Handle custom book management exceptions"""
    logger.error(f"BookManagementException: {exc.message}")

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exc, NotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif isinstance(exc, DuplicateError):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, AuthorizationError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, DatabaseError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    logger.error(f"Validation error: {exc.errors()}")

    formatted_errors = []
    for error in exc.errors():
        field = ".".join([str(loc) for loc in error["loc"][1:]])  # Skip 'body'
        formatted_errors.append(
            {"field": field, "message": error["msg"], "type": error["type"]}
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Input validation failed",
            "details": formatted_errors,
        },
    )


async def pydantic_validation_exception_handler(
    request: Request, exc: PydanticValidationError
):
    """Handle direct Pydantic validation errors"""
    logger.error(f"Pydantic validation error: {exc.errors()}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Data validation failed",
            "details": exc.errors(),
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "details": {},
        },
    )
