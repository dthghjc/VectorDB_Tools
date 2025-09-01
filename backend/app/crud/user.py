from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from passlib.context import CryptContext

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    stmt = select(User).where(User.email == email)
    return db.scalar(stmt)


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """根据ID获取用户"""
    stmt = select(User).where(User.id == user_id)
    return db.scalar(stmt)


def create_user(db: Session, user: UserCreate) -> User:
    """创建新用户"""
    # 生成密码哈希
    hashed_password = get_password_hash(user.password)
    
    # 创建用户对象
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=False  # 新用户默认非激活状态，需要管理员审核
    )
    
    # 保存到数据库
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """验证用户身份"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user(db: Session, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
    """更新用户信息"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # 如果包含密码更新，需要哈希处理
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # 更新用户字段
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: UUID) -> bool:
    """删除用户"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    db.delete(user)
    db.commit()
    return True


def is_user_active(user: User) -> bool:
    """检查用户是否激活"""
    return user.is_active
