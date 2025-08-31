from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from datetime import datetime


# --- 用户基础 Schema ---
class UserBase(BaseModel):
    """用户的基础字段"""
    email: EmailStr
    full_name: Optional[str] = None


# --- 用户创建 Schema ---
class UserCreate(UserBase):
    """创建用户时需要的字段"""
    password: str


# --- 用户更新 Schema ---
class UserUpdate(BaseModel):
    """更新用户时可选的字段"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


# --- 数据库中的用户 Schema ---
class UserInDB(UserBase):
    """数据库中用户的完整信息(包含敏感字段)"""
    id: UUID
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- 返回给前端的用户 Schema ---
class User(UserBase):
    """返回给前端的用户信息(不包含敏感字段)"""
    id: UUID
    is_active: bool  # 只在响应中显示，不允许用户修改
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- 认证相关 Schema ---
class Token(BaseModel):
    """JWT Token 响应"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token 中携带的数据"""
    email: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录请求"""
    email: EmailStr
    password: str


class UserRegister(UserCreate):
    """用户注册请求(继承自UserCreate)"""
    pass
