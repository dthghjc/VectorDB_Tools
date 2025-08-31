from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.crud.user import get_user_by_email, is_user_active
from app.schemas.user import TokenData
from app.models.user import User

# OAuth2 Bearer Token 方案
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT 访问令牌
    
    Args:
        data: 要编码到 token 中的数据
        expires_delta: token 过期时间，如果不指定则使用默认值
    
    Returns:
        JWT token 字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception: HTTPException) -> TokenData:
    """
    验证 JWT token
    
    Args:
        token: JWT token 字符串
        credentials_exception: 验证失败时抛出的异常
        
    Returns:
        TokenData: 解码后的 token 数据
        
    Raises:
        HTTPException: 当 token 无效时
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    return token_data


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前认证用户
    
    这个依赖函数会：
    1. 从请求头中提取 Bearer token
    2. 验证 token 的有效性
    3. 从数据库中获取用户信息
    4. 检查用户是否激活
    
    Args:
        credentials: HTTP Bearer 认证凭据
        db: 数据库会话
        
    Returns:
        User: 当前认证的用户对象
        
    Raises:
        HTTPException: 认证失败时
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 验证 token
    token_data = verify_token(credentials.credentials, credentials_exception)
    
    # 从数据库获取用户
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前激活的用户
    
    Args:
        current_user: 当前认证用户
        
    Returns:
        User: 激活的用户对象
        
    Raises:
        HTTPException: 用户未激活时
    """
    if not is_user_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user


def get_user_id_from_token(token: str) -> Optional[UUID]:
    """
    从 token 中提取用户 ID (可选的工具函数)
    
    Args:
        token: JWT token 字符串
        
    Returns:
        Optional[UUID]: 用户 ID，如果提取失败则返回 None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("user_id")
        if user_id_str:
            return UUID(user_id_str)
    except (JWTError, ValueError):
        pass
    return None
