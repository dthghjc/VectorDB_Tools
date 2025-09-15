# backend/app/services/milvus_connection_service.py

from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
import logging
import threading
from sqlalchemy.orm import Session

from app.crud.milvus_connection import milvus_connection_crud
from app.models.milvus_connection import MilvusConnection
from app.schemas.milvus_connection import MilvusConnectionCreate, MilvusConnectionUpdate

logger = logging.getLogger(__name__)


class MilvusConnectionServiceError(Exception):
    """Milvus 连接服务专用异常"""
    def __init__(self, message: str, error_code: str = "MILVUS_CONNECTION_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class MilvusConnectionService:
    """
    Milvus 连接配置管理服务
    
    职责：
    1. Milvus 连接配置的 CRUD 业务逻辑
    2. 连接验证和状态管理
    3. 使用统计和报告
    
    遵循 Linus 哲学：
    - 简洁的接口：每个方法只做一件事
    - 统一的错误处理：消除特殊情况
    - 实用主义：解决实际问题
    """
    
    def create_connection(
        self,
        *,
        user_id: UUID,
        connection_data: MilvusConnectionCreate,
        db: Session
    ) -> Dict[str, Any]:
        """
        创建新的 Milvus 连接配置
        
        Args:
            user_id: 用户 ID
            connection_data: 连接配置创建数据
            db: 数据库会话
            
        Returns:
            创建的连接配置信息（不包含敏感数据）
            
        Raises:
            MilvusConnectionServiceError: 创建失败时
        """
        try:
            # 检查名称是否重复
            existing_connection = milvus_connection_crud.get_by_name(
                db=db, name=connection_data.name, user_id=user_id
            )
            if existing_connection:
                raise MilvusConnectionServiceError(
                    f"连接配置名称 '{connection_data.name}' 已存在",
                    "DUPLICATE_NAME"
                )
            
            # 创建连接配置
            connection_obj = milvus_connection_crud.create(
                db=db, obj_in=connection_data, user_id=user_id
            )
            
            # 异步测试新创建的连接配置（不阻塞响应）
            logger.info(f"启动异步测试 - Milvus 连接: {connection_obj.name}")
            self.async_test_connection(connection_obj.id, user_id)
            
            # 返回安全信息
            return self._format_connection_response(connection_obj)
            
        except MilvusConnectionServiceError:
            raise
        except Exception as e:
            logger.error(f"创建 Milvus 连接配置失败: {e}", exc_info=True)
            raise MilvusConnectionServiceError(
                f"创建连接配置失败: {str(e)}",
                "CREATE_ERROR"
            )
    
    def get_user_connections(
        self,
        *,
        user_id: UUID,
        db: Session,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        获取用户的 Milvus 连接配置列表
        
        Args:
            user_id: 用户 ID
            db: 数据库会话
            status: 过滤状态
            skip: 跳过数量
            limit: 限制数量
            
        Returns:
            包含连接配置列表和总数的字典
        """
        try:
            connections, total = milvus_connection_crud.get_multi(
                db=db,
                user_id=user_id,
                status=status,
                skip=skip,
                limit=limit
            )
            
            return {
                "items": [self._format_connection_response(conn) for conn in connections],
                "total": total,
                "skip": skip,
                "limit": limit
            }
            
        except Exception as e:
            logger.error(f"获取用户 Milvus 连接配置列表失败: {e}", exc_info=True)
            raise MilvusConnectionServiceError(
                f"获取连接配置列表失败: {str(e)}",
                "GET_LIST_ERROR"
            )
    
    def get_connection(
        self,
        *,
        connection_id: UUID,
        user_id: UUID,
        db: Session
    ) -> Dict[str, Any]:
        """
        获取单个 Milvus 连接配置信息
        
        Args:
            connection_id: 连接配置 ID
            user_id: 用户 ID
            db: 数据库会话
            
        Returns:
            连接配置信息
        """
        try:
            connection_obj = milvus_connection_crud.get(db=db, id=connection_id, user_id=user_id)
            if not connection_obj:
                raise MilvusConnectionServiceError(
                    f"连接配置不存在或您无权访问: {connection_id}",
                    "NOT_FOUND"
                )
            
            return self._format_connection_response(connection_obj)
            
        except MilvusConnectionServiceError:
            raise
        except Exception as e:
            logger.error(f"获取 Milvus 连接配置失败: {e}", exc_info=True)
            raise MilvusConnectionServiceError(
                f"获取连接配置失败: {str(e)}",
                "GET_ERROR"
            )
    
    def update_connection(
        self,
        *,
        connection_id: UUID,
        user_id: UUID,
        update_data: MilvusConnectionUpdate,
        db: Session
    ) -> Dict[str, Any]:
        """
        更新 Milvus 连接配置
        
        Args:
            connection_id: 连接配置 ID
            user_id: 用户 ID
            update_data: 更新数据
            db: 数据库会话
            
        Returns:
            更新后的连接配置信息
        """
        try:
            # 获取现有连接配置
            connection_obj = milvus_connection_crud.get(db=db, id=connection_id, user_id=user_id)
            if not connection_obj:
                raise MilvusConnectionServiceError(
                    f"连接配置不存在或您无权访问: {connection_id}",
                    "NOT_FOUND"
                )
            
            # 检查名称重复（如果要更新名称）
            if update_data.name and update_data.name != connection_obj.name:
                existing_connection = milvus_connection_crud.get_by_name(
                    db=db, name=update_data.name, user_id=user_id
                )
                if existing_connection:
                    raise MilvusConnectionServiceError(
                        f"连接配置名称 '{update_data.name}' 已存在",
                        "DUPLICATE_NAME"
                    )
            
            # 更新连接配置
            updated_connection = milvus_connection_crud.update(
                db=db, db_obj=connection_obj, obj_in=update_data
            )
            
            return self._format_connection_response(updated_connection)
            
        except MilvusConnectionServiceError:
            raise
        except Exception as e:
            logger.error(f"更新 Milvus 连接配置失败: {e}", exc_info=True)
            raise MilvusConnectionServiceError(
                f"更新连接配置失败: {str(e)}",
                "UPDATE_ERROR"
            )
    
    def delete_connection(
        self,
        *,
        connection_id: UUID,
        user_id: UUID,
        db: Session
    ) -> bool:
        """
        删除 Milvus 连接配置
        
        Args:
            connection_id: 连接配置 ID
            user_id: 用户 ID
            db: 数据库会话
            
        Returns:
            是否删除成功
        """
        try:
            success = milvus_connection_crud.delete(db=db, id=connection_id, user_id=user_id)
            if not success:
                raise MilvusConnectionServiceError(
                    f"连接配置不存在或您无权删除: {connection_id}",
                    "NOT_FOUND"
                )
            
            logger.info(f"成功删除 Milvus 连接配置: {connection_id}")
            return True
            
        except MilvusConnectionServiceError:
            raise
        except Exception as e:
            logger.error(f"删除 Milvus 连接配置失败: {e}", exc_info=True)
            raise MilvusConnectionServiceError(
                f"删除连接配置失败: {str(e)}",
                "DELETE_ERROR"
            )
    
    def validate_connection(
        self,
        *,
        connection_id: UUID,
        user_id: UUID,
        db: Session,
        timeout_seconds: int = 10,
        save_result: bool = True
    ) -> Tuple[bool, str, float | None, Optional[str], Optional[int]]:
        """
        验证 Milvus 连接配置是否有效
        
        Args:
            connection_id: 连接配置 ID
            user_id: 用户 ID
            db: 数据库会话
            timeout_seconds: 连接超时时间
            save_result: 是否保存测试结果到数据库
            
        Returns:
            (是否有效, 验证信息, 响应时间ms, 服务器版本, 集合数量)
        """
        import time
        start_time = time.time()
        
        try:
            # 获取连接配置
            connection_obj = milvus_connection_crud.get(db=db, id=connection_id, user_id=user_id)
            if not connection_obj:
                return False, "连接配置不存在或您无权访问", None, None, None
            
            if not connection_obj.is_active():
                response_time = (time.time() - start_time) * 1000
                if save_result:
                    milvus_connection_crud.update_test_result(
                        db=db, db_obj=connection_obj, 
                        success=False, message="连接配置已被禁用", response_time=response_time
                    )
                return False, "连接配置已被禁用", response_time, None, None
            
            # 获取明文认证 token
            token = milvus_connection_crud.get_plaintext_token(
                connection=connection_obj
            )
            
            # 尝试连接 Milvus
            is_valid, message, server_version, collections_count = self._test_milvus_connection(
                uri=connection_obj.uri,
                database_name=connection_obj.database_name,
                token=token,
                timeout_seconds=timeout_seconds
            )
            
            response_time = (time.time() - start_time) * 1000
            
            # 保存测试结果
            if save_result:
                milvus_connection_crud.update_test_result(
                    db=db, db_obj=connection_obj,
                    success=is_valid, message=message, response_time=response_time,
                    server_version=server_version, collections_count=collections_count
                )
            
            if is_valid:
                logger.info(f"Milvus 连接验证成功: {connection_obj.name}")
            else:
                logger.warning(f"Milvus 连接验证失败: {connection_obj.name}, 原因: {message}")
            
            return is_valid, message, response_time, server_version, collections_count
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            error_message = f"验证过程中发生错误: {str(e)}"
            
            # 保存错误结果
            if save_result:
                try:
                    connection_obj = milvus_connection_crud.get(db=db, id=connection_id, user_id=user_id)
                    if connection_obj:
                        milvus_connection_crud.update_test_result(
                            db=db, db_obj=connection_obj,
                            success=False, message=error_message, response_time=response_time
                        )
                except:
                    pass  # 避免在保存错误时再次出错
            
            logger.error(f"Milvus 连接验证过程中发生错误: {e}", exc_info=True)
            return False, error_message, response_time, None, None
    
    def async_test_connection(self, connection_id: UUID, user_id: UUID) -> None:
        """
        异步测试 Milvus 连接配置（后台任务）
        
        Args:
            connection_id: 连接配置 ID
            user_id: 用户 ID
        """
        def test_in_background():
            try:
                # 创建新的数据库会话用于后台任务
                from app.core.db import SessionLocal
                db = SessionLocal()
                
                try:
                    # 执行测试（保存结果到数据库）
                    is_valid, message, response_time, server_version, collections_count = self.validate_connection(
                        connection_id=connection_id,
                        user_id=user_id,
                        db=db,
                        save_result=True
                    )
                    
                    logger.info(f"异步测试完成 - Milvus 连接: {connection_id}, 结果: {'成功' if is_valid else '失败'}")
                    
                finally:
                    db.close()
                    
            except Exception as e:
                logger.error(f"异步测试 Milvus 连接失败: {e}", exc_info=True)
        
        # 在后台线程中执行测试
        thread = threading.Thread(target=test_in_background, daemon=True)
        thread.start()
    
    def get_user_stats(
        self,
        *,
        user_id: UUID,
        db: Session
    ) -> Dict[str, Any]:
        """
        获取用户 Milvus 连接配置统计信息
        
        Args:
            user_id: 用户 ID
            db: 数据库会话
            
        Returns:
            统计信息字典
        """
        try:
            stats = milvus_connection_crud.get_user_stats(db=db, user_id=user_id)
            return stats
            
        except Exception as e:
            logger.error(f"获取用户统计信息失败: {e}", exc_info=True)
            raise MilvusConnectionServiceError(
                f"获取统计信息失败: {str(e)}",
                "STATS_ERROR"
            )
    
    def _get_token_display_info(self, connection_obj: MilvusConnection) -> str:
        """
        获取 token 的脱敏显示信息
        
        Args:
            connection_obj: 连接对象
            
        Returns:
            脱敏后的 token 信息字符串
        """
        if not connection_obj.encrypted_token:
            return "未配置"
        
        try:
            from app.core.crypto import decrypt_sensitive_data
            token = decrypt_sensitive_data(connection_obj.encrypted_token)
            
            # 如果是 username:password 格式，脱敏显示
            if ':' in token:
                username, _ = token.split(':', 1)
                return f"{username}:****"
            else:
                # 单纯 token，显示前几位和后几位
                if len(token) <= 8:
                    return "****"
                else:
                    return f"{token[:4]}****{token[-4:]}"
        except:
            return "无法解析"
    
    def _format_connection_response(self, connection_obj: MilvusConnection) -> Dict[str, Any]:
        """
        格式化连接配置响应数据（安全格式，不包含敏感信息）
        
        Args:
            connection_obj: MilvusConnection 数据库对象
            
        Returns:
            格式化的响应数据
        """
        return {
            "id": connection_obj.id,
            "user_id": connection_obj.user_id,
            "name": connection_obj.name,
            "description": connection_obj.description,
            "uri": connection_obj.uri,
            "database_name": connection_obj.database_name,
            "token_info": self._get_token_display_info(connection_obj),
            "status": connection_obj.status,
            "last_used_at": connection_obj.last_used_at,
            "usage_count": connection_obj.usage_count,
            # 测试相关字段
            "last_tested_at": connection_obj.last_tested_at,
            "test_status": connection_obj.test_status,
            "test_message": connection_obj.test_message,
            "test_response_time": connection_obj.test_response_time,
            "created_at": connection_obj.created_at,
            "updated_at": connection_obj.updated_at,
            # 生成连接字符串用于显示
            "connection_string": connection_obj.get_connection_string()
        }
    
    def _test_milvus_connection(
        self,
        *,
        uri: str,
        database_name: Optional[str] = None,
        token: Optional[str] = None,
        timeout_seconds: int = 10
    ) -> Tuple[bool, str, Optional[str], Optional[int]]:
        """
        测试 Milvus 连接
        
        Args:
            uri: 连接 URI
            database_name: 数据库名称
            token: 认证 token（可以是 username:password 或纯 token）
            timeout_seconds: 超时时间
            
        Returns:
            (是否成功, 消息, 服务器版本, 集合数量)
        """
        try:
            from pymilvus import MilvusClient
            
            # 构建连接参数 - 直接使用 URI
            connect_params = {
                "uri": uri,
                "timeout": timeout_seconds
            }
            
            # 如果有认证 token，直接使用
            if token:
                connect_params["token"] = token
            
            if database_name:
                connect_params["db_name"] = database_name
            
            try:
                # 使用 MilvusClient 建立连接
                client = MilvusClient(**connect_params)
                
                # 测试连接 - 尝试获取集合列表
                server_version = None
                collections_count = None
                
                try:
                    # 获取集合列表（这会测试连接是否有效）
                    collections_list = client.list_collections()
                    collections_count = len(collections_list) if collections_list else 0
                    
                    success_msg = "连接成功"
                    if collections_count is not None:
                        success_msg += f", 集合数量: {collections_count}"
                    
                    return True, success_msg, server_version, collections_count
                    
                except Exception as list_error:
                    # 如果获取集合失败，但客户端创建成功，可能是权限问题
                    if "permission" in str(list_error).lower() or "unauthorized" in str(list_error).lower():
                        return True, "连接成功（但可能权限受限）", server_version, 0
                    else:
                        raise list_error
                
            except Exception as e:
                error_msg = str(e)
                if "connection refused" in error_msg.lower() or "failed to connect" in error_msg.lower():
                    return False, f"连接被拒绝: 请检查连接地址 {uri} 是否正确", None, None
                elif "authentication" in error_msg.lower() or "credential" in error_msg.lower() or "unauthorized" in error_msg.lower():
                    return False, "认证失败: 请检查认证 token 是否正确", None, None
                elif "timeout" in error_msg.lower():
                    return False, f"连接超时: 服务器响应时间超过 {timeout_seconds} 秒", None, None
                else:
                    return False, f"连接失败: {error_msg}", None, None
                
        except ImportError:
            return False, "PyMilvus 库未安装: 无法测试 Milvus 连接", None, None
        except Exception as e:
            return False, f"测试过程中发生未知错误: {str(e)}", None, None


# 全局服务实例
milvus_connection_service = MilvusConnectionService()
