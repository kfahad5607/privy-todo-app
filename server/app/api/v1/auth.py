import asyncio
from typing import Any
import uuid
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.exceptions import (BaseAppException, ValidationException, UnauthorizedException)

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token
)
from app.db.database import get_db
from app.models.users import RefreshToken, User
from app.schemas.auth import Token, UserCreate, UserResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate
) -> Any:
    try:
        # Check if username exists
        result = await db.execute(select(User).where(User.username == user_in.username))
        if result.first():
            raise ValidationException(
                message="Username already registered"
            )
        
        # Check if email exists
        result = await db.execute(select(User).where(User.email == user_in.email))
        if result.first():
            raise ValidationException(
                message="Email already registered"
            )
        
        # Create new user
        user = User(
            username=user_in.username,
            email=user_in.email,
            name=user_in.name,
            hashed_password=get_password_hash(user_in.password)
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        raise BaseAppException("Could not create user. Please try again later.") from e

@router.post("/login", response_model=Token)
async def login(
    response: Response,
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    try:
        # Get user by username
        result = await db.execute(select(User).where(User.username == form_data.username))
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise UnauthorizedException(
                message="Incorrect username or password"
            )
        
        if not user.is_active:
            raise ValidationException(
                message="Inactive user"
            )
        
        # Create tokens
        access_token = create_access_token(user=user)
        refresh_token_jti = uuid.uuid4()
        refresh_token, refresh_token_expires_at = create_refresh_token(data={"sub": str(user.id), "jti": str(refresh_token_jti)})

        # Store refresh token in database
        refresh_token_obj = RefreshToken(
            jti=refresh_token_jti,
            token_hash=get_password_hash(refresh_token),
            user_id=user.id,
            expires_at=refresh_token_expires_at
        )
        db.add(refresh_token_obj)
        await db.commit()

        # Send refresh token as HttpOnly cookie
        response.set_cookie("refresh_token", refresh_token, httponly=True, secure=False, samesite="Strict")
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except UnauthorizedException:
        raise
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"Error logging in: {e}", exc_info=True)
        raise BaseAppException("Could not log in. Please try again later.") from e

@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request, response: Response,
    db: AsyncSession = Depends(get_db),
) -> Any:
    try:
        token = request.cookies.get("refresh_token")
        payload = verify_token(token)
        if not payload:
            raise UnauthorizedException(
                message="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        jti = payload.get("jti")

        if not user_id or not jti:
            raise UnauthorizedException(
                message="Invalid refresh token"
            )
        
        # Get refresh token from database
        result = await db.execute(select(RefreshToken).where(RefreshToken.jti == jti, RefreshToken.is_revoked == False))
        refresh_token_obj = result.scalar_one_or_none()

        if not refresh_token_obj or not verify_password(token, refresh_token_obj.token_hash):
            raise UnauthorizedException(
                message="Invalid refresh token"
            )

        user = await db.execute(select(User).where(User.id == int(user_id)))
        user = user.scalar_one_or_none()
        if not user:
            raise UnauthorizedException(
                message="User not found"
            )
        
        if not user.is_active:
            raise ValidationException(
                message="Inactive user"
            )
        
        # Create new tokens
        access_token = create_access_token(user=user)
        refresh_token_jti = uuid.uuid4()
        new_refresh_token, new_refresh_token_expires_at = create_refresh_token(data={"sub": str(user.id), "jti": str(refresh_token_jti)})

        # Revoke old refresh token
        refresh_token_obj.is_revoked = True
        await db.commit()

        # Store refresh token in database
        refresh_token_obj = RefreshToken(
            jti=refresh_token_jti,
            token_hash=get_password_hash(new_refresh_token),
            user_id=user.id,
            expires_at=new_refresh_token_expires_at
        )
        db.add(refresh_token_obj)
        await db.commit()

        # Send new refresh token as HttpOnly cookie
        response.set_cookie("refresh_token", new_refresh_token, httponly=True, secure=True, samesite="Strict")
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except UnauthorizedException:
        raise
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}", exc_info=True)
        raise BaseAppException("Could not refresh token. Please try again later.") from e

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        token = request.cookies.get("refresh_token")

        payload = verify_token(token)
        if not payload:
            raise UnauthorizedException(
                message="Invalid refresh token"
            )
        
        jti = payload.get("jti")
        if not jti:
            raise UnauthorizedException(
                message="Invalid refresh token"
            )
        
        # Get refresh token from database
        result = await db.execute(select(RefreshToken).where(RefreshToken.jti == jti, RefreshToken.is_revoked == False))
        refresh_token_obj = result.scalar_one_or_none()
        
        if not refresh_token_obj or not verify_password(token, refresh_token_obj.token_hash):
            raise UnauthorizedException(
                message="Invalid refresh token"
            )
        
        refresh_token_obj.is_revoked = True
        await db.commit()
        
        response.delete_cookie("refresh_token")
    except Exception as e:
        logger.error(f"Error logging out: {e}", exc_info=True)
        raise BaseAppException("Could not log out. Please try again later.") from e