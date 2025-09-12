# backend/app/crud/milvus_connection.py

from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.milvus_connection import MilvusConnection
from app.schemas.milvus_connection import MilvusConnectionCreate, MilvusConnectionUpdate
from app.core.crypto import encrypt_api_key, decrypt_api_key


class MilvusConnectionCRUD:
    """Milvus 连接配置 CRUD 操作类"""

    def create(
        self, 
        db: Session, 
        *, 
        obj_in: MilvusConnectionCreate, 
        user_id: UUID
    ) -> MilvusConnection:
        """
        创建新的 Milvus 连接配置
        
        Args:
            db: 数据库会话
            obj_in: 创建请求数据
            user_id: 用户ID
            
        Returns:
            创建的 MilvusConnection 对象
        """
        # 处理认证信息加密
        encrypted_username = None
        encrypted_password = None
        username_preview = None
        
        if obj_in.encrypted_username and obj_in.encrypted_password:
            # 双重加密：RSA解密 + AES加密存储
            encrypted_username = encrypt_api_key(obj_in.encrypted_username)
            encrypted_password = encrypt_api_key(obj_in.encrypted_password)
            
            # 解密生成预览（仅用于预览生成，不存储明文）
            original_username = decrypt_api_key(encrypted_username)
            username_preview = MilvusConnection().generate_username_preview(original_username)
        
        # 创建数据库对象
        db_obj = MilvusConnection(
            user_id=user_id,
            name=obj_in.name,
            description=obj_in.description,
            host=obj_in.host,
            port=obj_in.port,
            database_name=obj_in.database_name,
            encrypted_username=encrypted_username,
            encrypted_password=encrypted_password,
            username_preview=username_preview,
            secure=obj_in.secure,
            status="active"
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, id: UUID, user_id: UUID) -> Optional[MilvusConnection]:
        """
        根据ID获取用户的 Milvus 连接配置
        
        Args:
            db: 数据库会话
            id: 连接配置 ID
            user_id: 用户ID（权限控制）
            
        Returns:
            MilvusConnection 对象或 None
        """
        return db.query(MilvusConnection).filter(
            and_(MilvusConnection.id == id, MilvusConnection.user_id == user_id)
        ).first()

    def get_multi(
        self, 
        db: Session, 
        *, 
        user_id: UUID,
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        secure: Optional[bool] = None
    ) -> tuple[List[MilvusConnection], int]:
        """
        获取用户的 Milvus 连接配置列表（分页）
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            skip: 跳过数量
            limit: 限制数量
            status: 过滤状态
            secure: 过滤安全连接
            
        Returns:
            (连接配置列表, 总数量)
        """
        query = db.query(MilvusConnection).filter(MilvusConnection.user_id == user_id)
        
        # 添加过滤条件
        if status:
            query = query.filter(MilvusConnection.status == status)
        if secure is not None:
            query = query.filter(MilvusConnection.secure == secure)
            
        # 获取总数
        total = query.count()
        
        # 分页查询
        items = query.order_by(MilvusConnection.created_at.desc()).offset(skip).limit(limit).all()
        
        return items, total

    def update(
        self, 
        db: Session, 
        *, 
        db_obj: MilvusConnection, 
        obj_in: MilvusConnectionUpdate
    ) -> MilvusConnection:
        """
        更新 Milvus 连接配置
        
        Args:
            db: 数据库会话
            db_obj: 数据库中的 MilvusConnection 对象
            obj_in: 更新数据
            
        Returns:
            更新后的 MilvusConnection 对象
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
        删除用户的 Milvus 连接配置
        
        Args:
            db: 数据库会话
            id: 连接配置 ID
            user_id: 用户ID（权限控制）
            
        Returns:
            是否删除成功
        """
        obj = db.query(MilvusConnection).filter(
            and_(MilvusConnection.id == id, MilvusConnection.user_id == user_id)
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
    ) -> Optional[MilvusConnection]:
        """
        根据名称获取用户的 Milvus 连接配置
        
        Args:
            db: 数据库会话
            name: 连接配置名称
            user_id: 用户ID
            
        Returns:
            MilvusConnection 对象或 None
        """
        return db.query(MilvusConnection).filter(
            and_(MilvusConnection.name == name, MilvusConnection.user_id == user_id)
        ).first()

    def get_active_connections(
        self, 
        db: Session, 
        *, 
        user_id: UUID
    ) -> List[MilvusConnection]:
        """
        获取用户所有活跃的 Milvus 连接配置
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            活跃的连接配置列表
        """
        return db.query(MilvusConnection).filter(
            and_(
                MilvusConnection.user_id == user_id,
                MilvusConnection.status == "active"
            )
        ).all()

    def update_usage(
        self, 
        db: Session, 
        *, 
        db_obj: MilvusConnection
    ) -> MilvusConnection:
        """
        更新连接配置使用统计
        
        Args:
            db: 数据库会话
            db_obj: MilvusConnection 对象
            
        Returns:
            更新后的 MilvusConnection 对象
        """
        db_obj.update_last_used()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_plaintext_credentials(self, *, connection: MilvusConnection) -> tuple[Optional[str], Optional[str]]:
        """
        解密获取明文认证信息（仅用于实际连接）
        
        Args:
            connection: MilvusConnection 对象
            
        Returns:
            (用户名, 密码) 的元组，如果未配置认证则返回 (None, None)
        """
        if not connection.encrypted_username or not connection.encrypted_password:
            return None, None
            
        try:
            username = decrypt_api_key(connection.encrypted_username)
            password = decrypt_api_key(connection.encrypted_password)
            return username, password
        except Exception:
            return None, None
    
    def get_plaintext_credentials_by_id(
        self, 
        db: Session, 
        *, 
        connection_id: UUID, 
        user_id: UUID
    ) -> tuple[Optional[str], Optional[str]]:
        """
        通过连接配置 ID 安全获取明文认证信息（包含权限验证）
        
        Args:
            db: 数据库会话
            connection_id: 连接配置 ID
            user_id: 用户 ID（用于权限验证）
            
        Returns:
            (用户名, 密码) 的元组，如果不存在或无权限则返回 (None, None)
        """
        # 先验证权限：确保连接配置属于该用户
        db_obj = db.query(MilvusConnection).filter(
            MilvusConnection.id == connection_id,
            MilvusConnection.user_id == user_id
        ).first()
        
        if not db_obj:
            return None, None
            
        # 解密并返回明文认证信息
        return self.get_plaintext_credentials(connection=db_obj)

    def get_user_stats(self, db: Session, *, user_id: UUID) -> dict:
        """
        获取用户 Milvus 连接配置统计信息
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            统计信息字典
        """
        total = db.query(func.count(MilvusConnection.id)).filter(
            MilvusConnection.user_id == user_id
        ).scalar()
        
        active = db.query(func.count(MilvusConnection.id)).filter(
            and_(MilvusConnection.user_id == user_id, MilvusConnection.status == "active")
        ).scalar()
        
        # 最近7天使用过的连接数
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recently_used = db.query(func.count(MilvusConnection.id)).filter(
            and_(
                MilvusConnection.user_id == user_id,
                MilvusConnection.last_used_at >= seven_days_ago
            )
        ).scalar()
        
        # 按状态统计
        status_stats = db.query(
            MilvusConnection.status, 
            func.count(MilvusConnection.id).label('count')
        ).filter(MilvusConnection.user_id == user_id).group_by(MilvusConnection.status).all()
        
        # 按安全连接统计
        secure_stats = db.query(
            MilvusConnection.secure, 
            func.count(MilvusConnection.id).label('count')
        ).filter(MilvusConnection.user_id == user_id).group_by(MilvusConnection.secure).all()
        
        return {
            "total": total,
            "active": active,
            "inactive": total - active,
            "recently_used": recently_used,
            "by_status": {stat.status: stat.count for stat in status_stats},
            "by_secure": {"secure" if stat.secure else "insecure": stat.count for stat in secure_stats}
        }

    def update_test_result(
        self,
        db: Session,
        *,
        db_obj: MilvusConnection,
        success: bool,
        message: str,
        response_time: Optional[float] = None,
        server_version: Optional[str] = None,
        collections_count: Optional[int] = None
    ) -> MilvusConnection:
        """
        更新连接测试结果
        
        Args:
            db: 数据库会话
            db_obj: MilvusConnection 对象
            success: 测试是否成功
            message: 测试消息
            response_time: 响应时间（毫秒）
            server_version: 服务器版本（可选）
            collections_count: 集合数量（可选）
            
        Returns:
            更新后的 MilvusConnection 对象
        """
        db_obj.update_test_result(success, message, response_time)
        
        # 如果测试成功，可以保存额外的服务器信息到 test_message 中
        if success and (server_version or collections_count is not None):
            extra_info = []
            if server_version:
                extra_info.append(f"版本: {server_version}")
            if collections_count is not None:
                extra_info.append(f"集合数: {collections_count}")
            
            if extra_info:
                db_obj.test_message += f" ({', '.join(extra_info)})"
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# 创建全局实例
milvus_connection_crud = MilvusConnectionCRUD()
