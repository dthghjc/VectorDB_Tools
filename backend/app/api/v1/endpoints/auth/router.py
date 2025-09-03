from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.db import get_db
from app.core.config import settings
from app.core.security import create_access_token, get_current_active_user
from app.crud.user import authenticate_user, create_user, get_user_by_email
from app.schemas.user import Token, UserLogin, UserRegister, User, LoginResponse

router = APIRouter()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
) -> Any:
    """
    用户注册
    
    注册新用户账户。会检查邮箱是否已经存在，如果存在则返回错误。
    
    Args:
        user_data: 用户注册数据
        db: 数据库会话
        
    Returns:
        User: 创建的用户信息(不包含密码)
        
    Raises:
        HTTPException: 邮箱已存在时
    """
    # 检查邮箱是否已存在
    existing_user = get_user_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # 创建新用户
        user = create_user(db=db, user=user_data)
        return user
    except IntegrityError:
        # 处理数据库完整性错误(比如并发注册相同邮箱)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except Exception as e:
        # 处理其他未预期的错误
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.post("/login", response_model=LoginResponse)
async def login_user(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    用户登录
    
    验证用户凭据并返回访问令牌。
    
    Args:
        user_credentials: 用户登录凭据
        db: 数据库会话
        
    Returns:
        Token: 包含访问令牌的响应
        
    Raises:
        HTTPException: 认证失败时
    """
    # 验证用户凭据
    user = authenticate_user(
        db, 
        email=user_credentials.email, 
        password=user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": user.email,
        "full_name": user.full_name
    }


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取当前用户信息
    
    需要有效的访问令牌。返回当前认证用户的信息。
    
    Args:
        current_user: 当前认证用户
        
    Returns:
        User: 当前用户信息
    """
    return current_user


@router.post("/test-auth")
async def test_protected_route(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    测试认证保护的路由
    
    这是一个测试端点，用于验证认证功能是否正常工作。
    
    Args:
        current_user: 当前认证用户
        
    Returns:
        dict: 包含成功消息和用户信息的响应
    """
    return {
        "message": "Authentication successful",
        "user_email": current_user.email,
        "user_id": str(current_user.id)
    }
