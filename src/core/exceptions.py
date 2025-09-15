# app/core/exceptions.py
from fastapi import HTTPException, status
from typing import Optional, Dict, Any


class BookManagementException(Exception):
    """Base exception for book management system"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BookManagementException):
    pass


class NotFoundError(BookManagementException):
    pass


class DuplicateError(BookManagementException):
    pass


class AuthenticationError(BookManagementException):
    pass


class AuthorizationError(BookManagementException):
    pass


class DatabaseError(BookManagementException):
    pass


def http_404_not_found(resource: str, identifier: str = None):
    detail = f"{resource} not found"
    if identifier:
        detail += f" with identifier: {identifier}"
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def http_400_bad_request(message: str, details: Dict[str, Any] = None):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error": "Bad Request", "message": message, "details": details or {}},
    )


def http_422_validation_error(message: str, field: str = None):
    detail = {"error": "Validation Error", "message": message}
    if field:
        detail["field"] = field
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


def http_409_conflict(message: str):
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"error": "Conflict", "message": message},
    )


def http_401_unauthorized(message: str = "Authentication required"):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": "Unauthorized", "message": message},
        headers={"WWW-Authenticate": "Bearer"},
    )


def http_403_forbidden(message: str = "Insufficient permissions"):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"error": "Forbidden", "message": message},
    )


def http_429_too_many_requests(message: str = "Too many requests"):
    raise HTTPException(
        status_code=429,
        detail={"error": "Too Many Requests", "message": message},
    )
