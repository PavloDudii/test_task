from fastapi import Depends, HTTPException, status
import asyncpg
from src.core.database import get_db
from src.core.security import get_current_user_token
from src.schemas.user import TokenData, User
from src.services.auth_service import AuthService


async def get_current_user(
    token_data: TokenData = Depends(get_current_user_token),
    connection: asyncpg.Connection = Depends(get_db),
) -> User:
    """Get current authenticated user"""
    auth_service = AuthService(connection)
    try:
        user = await auth_service.get_user_by_id(token_data.user_id)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated",
            )
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user"
        )
