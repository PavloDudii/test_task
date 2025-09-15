from fastapi import APIRouter, Depends, status
import asyncpg

from src.core.deps import get_current_user
from src.core.database import get_db
from src.services.auth_service import AuthService
from src.schemas.user import UserCreate, UserLogin, User, Token

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate, connection: asyncpg.Connection = Depends(get_db)
):
    """Register a new user"""
    service = AuthService(connection)
    return await service.register_user(user_data)


@router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin, connection: asyncpg.Connection = Depends(get_db)
):
    """Authenticate user and return JWT token"""
    service = AuthService(connection)
    return await service.authenticate_user(login_data)


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.post("/logout")
async def logout_user(current_user: User = Depends(get_current_user)):
    """Logout user (client should discard the token)"""
    return {"message": "Successfully logged out"}
