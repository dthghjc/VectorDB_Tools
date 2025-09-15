# backend/app/api/v1/endpoints/connections/router.py

import time
from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.crypto import get_public_key
from app.core.security import get_current_active_user
from app.core.db import get_db
from app.models.user import User
from app.schemas.crypto import RSAPublicKeyResponse
from app.schemas import milvus_connection as schemas
from app.services.milvus_connection_service import milvus_connection_service, MilvusConnectionServiceError

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/public-key", summary="获取 RSA 公钥", response_model=RSAPublicKeyResponse)
async def get_rsa_public_key(
    current_user: User = Depends(get_current_active_user)
) -> RSAPublicKeyResponse:
    """
    获取 RSA 公钥
    
    需要用户认证。前端在提交 Milvus 连接认证信息之前需要调用此接口获取公钥进行加密。
    
    Args:
        current_user: 当前认证的用户
        
    Returns:
        包含 PEM 格式公钥的响应
        
    Raises:
        HTTPException: 当公钥获取失败时
    """
    try:
        public_key_pem = get_public_key()
        
        return RSAPublicKeyResponse(public_key=public_key_pem)
        
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"加密系统未就绪: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取公钥失败: {e}"
        )

# ==================== Milvus 连接配置 CRUD 端点 ====================

@router.post("/", summary="创建 Milvus 连接配置", response_model=schemas.MilvusConnectionCreateResponse)
async def create_milvus_connection(
    *,
    db: Session = Depends(get_db),
    connection_in: schemas.MilvusConnectionCreate,
    current_user: User = Depends(get_current_active_user)
) -> schemas.MilvusConnectionCreateResponse:
    """
    创建新的 Milvus 连接配置
    
    Args:
        connection_in: 连接配置创建数据
        current_user: 当前用户
        
    Returns:
        创建的连接配置信息
        
    Raises:
        HTTPException: 当名称重复或创建失败时
    """
    try:
        # 使用服务层创建连接配置
        connection_data = milvus_connection_service.create_connection(
            user_id=current_user.id,
            connection_data=connection_in,
            db=db
        )
        
        return schemas.MilvusConnectionCreateResponse(
            id=connection_data["id"],
            name=connection_data["name"],
            description=connection_data["description"],
            uri=connection_data["uri"],
            database_name=connection_data["database_name"],
            token_info=connection_data["token_info"],
            status=connection_data["status"],
            usage_count=connection_data["usage_count"],
            connection_string=connection_data["connection_string"],
            created_at=connection_data["created_at"],
            updated_at=connection_data["updated_at"]
        )
        
    except MilvusConnectionServiceError as e:
        if e.error_code == "DUPLICATE_NAME":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.message
            )
    except Exception as e:
        logger.error(f"创建 Milvus 连接配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="连接配置创建失败"
        )


@router.get("/", summary="获取 Milvus 连接配置列表", response_model=schemas.MilvusConnectionList)
async def get_milvus_connections(
    *,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, regex="^(active|inactive)$", description="按状态过滤"),
    current_user: User = Depends(get_current_active_user)
) -> schemas.MilvusConnectionList:
    """
    获取当前用户的 Milvus 连接配置列表
    
    Args:
        page: 页码（从1开始）
        size: 每页数量
        status: 按状态过滤
        current_user: 当前用户
        
    Returns:
        分页的连接配置列表
    """
    try:
        # 将页码转换为 skip
        skip = (page - 1) * size
        
        # 使用服务层获取连接配置列表
        result = milvus_connection_service.get_user_connections(
            user_id=current_user.id,
            db=db,
            status=status,
            skip=skip,
            limit=size
        )
        
        pages = (result["total"] + size - 1) // size  # 向上取整
        
        return schemas.MilvusConnectionList(
            items=[schemas.MilvusConnectionResponse.model_validate(item) for item in result["items"]],
            total=result["total"],
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"获取 Milvus 连接配置列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取连接配置列表失败"
        )


@router.get("/{connection_id}", summary="获取单个 Milvus 连接配置", response_model=schemas.MilvusConnectionResponse)
async def get_milvus_connection(
    *,
    db: Session = Depends(get_db),
    connection_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> schemas.MilvusConnectionResponse:
    """
    获取指定的 Milvus 连接配置
    
    Args:
        connection_id: 连接配置 ID
        current_user: 当前用户
        
    Returns:
        连接配置详细信息
        
    Raises:
        HTTPException: 当连接配置不存在时
    """
    try:
        # 使用服务层获取连接配置
        connection_data = milvus_connection_service.get_connection(
            connection_id=connection_id,
            user_id=current_user.id,
            db=db
        )
        
        return schemas.MilvusConnectionResponse.model_validate(connection_data)
        
    except MilvusConnectionServiceError as e:
        if e.error_code == "NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.message
            )
    except Exception as e:
        logger.error(f"获取 Milvus 连接配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取连接配置失败"
        )


@router.put("/{connection_id}", summary="更新 Milvus 连接配置", response_model=schemas.MilvusConnectionResponse)
async def update_milvus_connection(
    *,
    db: Session = Depends(get_db),
    connection_id: UUID,
    connection_in: schemas.MilvusConnectionUpdate,
    current_user: User = Depends(get_current_active_user)
) -> schemas.MilvusConnectionResponse:
    """
    更新 Milvus 连接配置信息
    
    Args:
        connection_id: 连接配置 ID
        connection_in: 更新数据
        current_user: 当前用户
        
    Returns:
        更新后的连接配置信息
        
    Raises:
        HTTPException: 当连接配置不存在或名称冲突时
    """
    try:
        # 使用服务层更新连接配置
        updated_data = milvus_connection_service.update_connection(
            connection_id=connection_id,
            user_id=current_user.id,
            update_data=connection_in,
            db=db
        )
        
        return schemas.MilvusConnectionResponse.model_validate(updated_data)
        
    except MilvusConnectionServiceError as e:
        if e.error_code == "NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.message
            )
        elif e.error_code == "DUPLICATE_NAME":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.message
            )
    except Exception as e:
        logger.error(f"更新 Milvus 连接配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新连接配置失败"
        )


@router.delete("/{connection_id}", summary="删除 Milvus 连接配置")
async def delete_milvus_connection(
    *,
    db: Session = Depends(get_db),
    connection_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    删除 Milvus 连接配置
    
    Args:
        connection_id: 连接配置 ID
        current_user: 当前用户
        
    Returns:
        删除确认信息
        
    Raises:
        HTTPException: 当连接配置不存在时
    """
    try:
        # 使用服务层删除连接配置
        success = milvus_connection_service.delete_connection(
            connection_id=connection_id,
            user_id=current_user.id,
            db=db
        )
        
        return {"message": "Milvus 连接配置删除成功", "id": str(connection_id)}
        
    except MilvusConnectionServiceError as e:
        if e.error_code == "NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.message
            )
    except Exception as e:
        logger.error(f"删除 Milvus 连接配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除连接配置失败"
        )


@router.post("/{connection_id}/test", summary="测试 Milvus 连接", response_model=schemas.MilvusConnectionTestResponse)
async def test_milvus_connection(
    *,
    db: Session = Depends(get_db),
    connection_id: UUID,
    test_request: schemas.MilvusConnectionTestRequest,
    current_user: User = Depends(get_current_active_user)
) -> schemas.MilvusConnectionTestResponse:
    """
    测试 Milvus 连接配置的连通性
    
    尝试连接到 Milvus 服务器并获取基本信息，如服务器版本和集合数量。
    
    Args:
        connection_id: 连接配置 ID
        test_request: 测试请求参数
        current_user: 当前用户
        
    Returns:
        测试结果，包含响应时间和详细状态
        
    Raises:
        HTTPException: 当连接配置不存在时
    """
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 使用服务层的统一验证方法
        is_valid, message, response_time, server_version, collections_count = milvus_connection_service.validate_connection(
            connection_id=connection_id,
            user_id=current_user.id,
            db=db,
            timeout_seconds=test_request.timeout_seconds,
            save_result=True  # 保存测试结果
        )
        
        return schemas.MilvusConnectionTestResponse(
            success=is_valid,
            message=message,
            response_time_ms=round(response_time, 2) if response_time else None,
            tested_at=datetime.utcnow(),
            server_version=server_version,
            collections_count=collections_count
        )
            
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"Milvus 连接测试过程中发生错误: {e}", exc_info=True)
        
        return schemas.MilvusConnectionTestResponse(
            success=False,
            message=f"测试过程中发生错误: {str(e)}",
            response_time_ms=round(response_time, 2)
        )


@router.get("/stats/summary", summary="获取 Milvus 连接配置统计", response_model=schemas.MilvusConnectionStatsResponse)
async def get_milvus_connection_stats(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.MilvusConnectionStatsResponse:
    """
    获取当前用户的 Milvus 连接配置统计信息
    
    Args:
        current_user: 当前用户
        
    Returns:
        统计信息
    """
    try:
        # 使用服务层获取统计信息
        stats = milvus_connection_service.get_user_stats(
            user_id=current_user.id,
            db=db
        )
        
        return schemas.MilvusConnectionStatsResponse.model_validate(stats)
        
    except MilvusConnectionServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计信息失败"
        )
