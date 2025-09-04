# backend/app/crud/api_key.py

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.api_key import ApiKey
from app.schemas.api_key import ApiKeyCreate, ApiKeyUpdate
from app.core.crypto import encrypt_api_key, decrypt_api_key


class ApiKeyCRUD:
    """API Key CRUD 操作类"""

    def create(
        self, 
        db: Session, 
        *, 
        obj_in: ApiKeyCreate, 
        user_id: UUID
    ) -> ApiKey:
        """
        创建新的 API Key
        
        Args:
            db: 数据库会话
            obj_in: 创建请求数据
            user_id: 用户ID
            
        Returns:
            创建的 API Key 对象
        """
        # 1. 双重加密：RSA解密 + AES加密存储
        encrypted_for_db = encrypt_api_key(obj_in.encrypted_api_key)
        
        # 2. 解密生成预览（仅用于预览生成，不存储明文）
        original_key = decrypt_api_key(encrypted_for_db)
        
        # 3. 创建数据库对象
        db_obj = ApiKey(
            user_id=user_id,
            name=obj_in.name,
            provider=obj_in.provider,
            base_url=obj_in.base_url,
            encrypted_api_key=encrypted_for_db,
            key_preview=ApiKey().generate_key_preview(original_key),
            status="active"
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, id: UUID, user_id: UUID) -> Optional[ApiKey]:
        """
        根据ID获取用户的 API Key
        
        Args:
            db: 数据库会话
            id: API Key ID
            user_id: 用户ID（权限控制）
            
        Returns:
            API Key 对象或 None
        """
        return db.query(ApiKey).filter(
            and_(ApiKey.id == id, ApiKey.user_id == user_id)
        ).first()

    def get_multi(
        self, 
        db: Session, 
        *, 
        user_id: UUID,
        skip: int = 0, 
        limit: int = 100,
        provider: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[ApiKey], int]:
        """
        获取用户的 API Key 列表（分页）
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            skip: 跳过数量
            limit: 限制数量
            provider: 过滤服务提供商
            status: 过滤状态
            
        Returns:
            (API Key 列表, 总数量)
        """
        query = db.query(ApiKey).filter(ApiKey.user_id == user_id)
        
        # 添加过滤条件
        if provider:
            query = query.filter(ApiKey.provider == provider)
        if status:
            query = query.filter(ApiKey.status == status)
            
        # 获取总数
        total = query.count()
        
        # 分页查询
        items = query.order_by(ApiKey.created_at.desc()).offset(skip).limit(limit).all()
        
        return items, total

    def update(
        self, 
        db: Session, 
        *, 
        db_obj: ApiKey, 
        obj_in: ApiKeyUpdate
    ) -> ApiKey:
        """
        更新 API Key
        
        Args:
            db: 数据库会话
            db_obj: 数据库中的 API Key 对象
            obj_in: 更新数据
            
        Returns:
            更新后的 API Key 对象
        """
        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: UUID, user_id: UUID) -> bool:
        """
        删除用户的 API Key
        
        Args:
            db: 数据库会话
            id: API Key ID
            user_id: 用户ID（权限控制）
            
        Returns:
            是否删除成功
        """
        obj = db.query(ApiKey).filter(
            and_(ApiKey.id == id, ApiKey.user_id == user_id)
        ).first()
        
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False

    def get_by_name(
        self, 
        db: Session, 
        *, 
        name: str, 
        user_id: UUID
    ) -> Optional[ApiKey]:
        """
        根据名称获取用户的 API Key
        
        Args:
            db: 数据库会话
            name: API Key 名称
            user_id: 用户ID
            
        Returns:
            API Key 对象或 None
        """
        return db.query(ApiKey).filter(
            and_(ApiKey.name == name, ApiKey.user_id == user_id)
        ).first()

    def get_active_by_provider(
        self, 
        db: Session, 
        *, 
        provider: str, 
        user_id: UUID
    ) -> List[ApiKey]:
        """
        获取用户指定提供商的所有活跃 API Key
        
        Args:
            db: 数据库会话
            provider: 服务提供商
            user_id: 用户ID
            
        Returns:
            活跃的 API Key 列表
        """
        return db.query(ApiKey).filter(
            and_(
                ApiKey.provider == provider,
                ApiKey.user_id == user_id,
                ApiKey.status == "active"
            )
        ).all()

    def update_usage(
        self, 
        db: Session, 
        *, 
        db_obj: ApiKey
    ) -> ApiKey:
        """
        更新 API Key 使用统计
        
        Args:
            db: 数据库会话
            db_obj: API Key 对象
            
        Returns:
            更新后的 API Key 对象
        """
        db_obj.update_last_used()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_plaintext_key(self, *, encrypted_key: str) -> str:
        """
        解密获取明文 API Key（仅用于实际API调用）
        
        Args:
            encrypted_key: 数据库中的加密密钥
            
        Returns:
            解密后的明文 API Key
        """
        return decrypt_api_key(encrypted_key)
    
    def get_plaintext_key_by_id(self, db: Session, *, api_key_id: UUID, user_id: UUID) -> Optional[str]:
        """
        通过 API Key ID 安全获取明文密钥（包含权限验证）
        
        Args:
            db: 数据库会话
            api_key_id: API Key ID
            user_id: 用户 ID（用于权限验证）
            
        Returns:
            解密后的明文 API Key，如果不存在或无权限则返回 None
        """
        # 先验证权限：确保密钥属于该用户
        db_obj = db.query(ApiKey).filter(
            ApiKey.id == api_key_id,
            ApiKey.user_id == user_id
        ).first()
        
        if not db_obj:
            return None
            
        # 解密并返回明文密钥
        try:
            return decrypt_api_key(db_obj.encrypted_api_key)
        except Exception:
            return None

    def get_user_stats(self, db: Session, *, user_id: UUID) -> dict:
        """
        获取用户 API Key 统计信息
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            统计信息字典
        """
        total = db.query(func.count(ApiKey.id)).filter(ApiKey.user_id == user_id).scalar()
        active = db.query(func.count(ApiKey.id)).filter(
            and_(ApiKey.user_id == user_id, ApiKey.status == "active")
        ).scalar()
        
        # 按提供商统计
        provider_stats = db.query(
            ApiKey.provider, 
            func.count(ApiKey.id).label('count')
        ).filter(ApiKey.user_id == user_id).group_by(ApiKey.provider).all()
        
        return {
            "total": total,
            "active": active,
            "inactive": total - active,
            "by_provider": {stat.provider: stat.count for stat in provider_stats}
        }


# 创建全局实例
api_key_crud = ApiKeyCRUD()
