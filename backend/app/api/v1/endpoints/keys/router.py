# backend/app/api/v1/endpoints/keys/router.py

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
from app.schemas import api_key as schemas
from app.schemas.api_key import ApiProvider
from app.services.api_key_service import api_key_service, ApiKeyServiceError

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/providers", summary="获取支持的API供应商列表", response_model=schemas.ApiProviderListResponse)
async def get_api_providers(
    current_user: User = Depends(get_current_active_user)
) -> schemas.ApiProviderListResponse:
    """
    获取支持的API供应商列表
    
    返回所有支持的API供应商选项，前端可用于下拉选择器。
    """
    providers = [provider.value for provider in ApiProvider]
    return schemas.ApiProviderListResponse(providers=providers)


@router.get("/public-key", summary="获取 RSA 公钥", response_model=RSAPublicKeyResponse)
async def get_rsa_public_key(
    current_user: User = Depends(get_current_active_user)
) -> RSAPublicKeyResponse:
    """
    获取 RSA 公钥
    
    需要用户认证。前端在提交 API Key 之前需要调用此接口获取公钥进行加密。
    
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

# ==================== API Key CRUD 端点 ====================

@router.post("/", summary="创建 API Key", response_model=schemas.ApiKeyCreateResponse)
async def create_api_key(
    *,
    db: Session = Depends(get_db),
    api_key_in: schemas.ApiKeyCreate,
    current_user: User = Depends(get_current_active_user)
) -> schemas.ApiKeyCreateResponse:
    """
    创建新的 API Key
    
    Args:
        api_key_in: API Key 创建数据
        current_user: 当前用户
        
    Returns:
        创建的 API Key 信息
        
    Raises:
        HTTPException: 当名称重复或创建失败时
    """
    
    
    try:
        # 使用服务层创建 API Key
        api_key_data = api_key_service.create_api_key(
            user_id=current_user.id,
            api_key_data=api_key_in,
            db=db
        )
        
        return schemas.ApiKeyCreateResponse(
            id=api_key_data["id"],
            name=api_key_data["name"],
            provider=api_key_data["provider"],
            base_url=api_key_data["base_url"],
            key_preview=api_key_data["key_preview"],
            status=api_key_data["status"],
            usage_count=api_key_data["usage_count"],
            created_at=api_key_data["created_at"],
            updated_at=api_key_data["updated_at"]
        )
        
    except ApiKeyServiceError as e:
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
        logger.error(f"创建 API Key 失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API Key 创建失败"
        )


@router.get("/", summary="获取 API Key 列表", response_model=schemas.ApiKeyList)
async def get_api_keys(
    *,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    provider: Optional[str] = Query(None, description="按提供商过滤"),
    status: Optional[str] = Query(None, regex="^(active|inactive)$", description="按状态过滤"),
    current_user: User = Depends(get_current_active_user)
) -> schemas.ApiKeyList:
    """
    获取当前用户的 API Key 列表
    
    Args:
        page: 页码（从1开始）
        size: 每页数量
        provider: 按提供商过滤
        status: 按状态过滤
        current_user: 当前用户
        
    Returns:
        分页的 API Key 列表
    """
    
    try:
        # 将页码转换为 skip
        skip = (page - 1) * size
        
        # 使用服务层获取 API Key 列表
        result = api_key_service.get_user_api_keys(
            user_id=current_user.id,
            db=db,
            provider=provider,
            status=status,
            skip=skip,
            limit=size
        )
        
        pages = (result["total"] + size - 1) // size  # 向上取整
        
        return schemas.ApiKeyList(
            items=[schemas.ApiKeyResponse.model_validate(item) for item in result["items"]],
            total=result["total"],
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"获取 API Key 列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取 API Key 列表失败"
        )


@router.get("/{key_id}", summary="获取单个 API Key", response_model=schemas.ApiKeyResponse)
async def get_api_key(
    *,
    db: Session = Depends(get_db),
    key_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> schemas.ApiKeyResponse:
    """
    获取指定的 API Key
    
    Args:
        key_id: API Key ID
        current_user: 当前用户
        
    Returns:
        API Key 详细信息
        
    Raises:
        HTTPException: 当 API Key 不存在时
    """
    try:
        # 使用服务层获取 API Key
        api_key_data = api_key_service.get_api_key(
            api_key_id=key_id,
            user_id=current_user.id,
            db=db
        )
        
        return schemas.ApiKeyResponse.model_validate(api_key_data)
        
    except ApiKeyServiceError as e:
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
        logger.error(f"获取 API Key 失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取 API Key 失败"
        )


@router.put("/{key_id}", summary="更新 API Key", response_model=schemas.ApiKeyResponse)
async def update_api_key(
    *,
    db: Session = Depends(get_db),
    key_id: UUID,
    api_key_in: schemas.ApiKeyUpdate,
    current_user: User = Depends(get_current_active_user)
) -> schemas.ApiKeyResponse:
    """
    更新 API Key 信息
    
    Args:
        key_id: API Key ID
        api_key_in: 更新数据
        current_user: 当前用户
        
    Returns:
        更新后的 API Key 信息
        
    Raises:
        HTTPException: 当 API Key 不存在或名称冲突时
    """
    try:
        # 使用服务层更新 API Key
        updated_data = api_key_service.update_api_key(
            api_key_id=key_id,
            user_id=current_user.id,
            update_data=api_key_in,
            db=db
        )
        
        return schemas.ApiKeyResponse.model_validate(updated_data)
        
    except ApiKeyServiceError as e:
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
        logger.error(f"更新 API Key 失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新 API Key 失败"
        )


@router.delete("/{key_id}", summary="删除 API Key")
async def delete_api_key(
    *,
    db: Session = Depends(get_db),
    key_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    删除 API Key
    
    Args:
        key_id: API Key ID
        current_user: 当前用户
        
    Returns:
        删除确认信息
        
    Raises:
        HTTPException: 当 API Key 不存在时
    """
    try:
        # 使用服务层删除 API Key
        success = api_key_service.delete_api_key(
            api_key_id=key_id,
            user_id=current_user.id,
            db=db
        )
        
        return {"message": "API Key 删除成功", "id": str(key_id)}
        
    except ApiKeyServiceError as e:
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
        logger.error(f"删除 API Key 失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除 API Key 失败"
        )


@router.post("/{key_id}/test", summary="测试 API Key", response_model=schemas.ApiKeyTestResponse)
async def test_api_key(
    *,
    db: Session = Depends(get_db),
    key_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> schemas.ApiKeyTestResponse:
    """
    测试 API Key 连通性
    
    使用统一的 LLM 客户端验证机制，无需传入额外参数。
    每个提供商都有自己的最佳验证方式。
    
    Args:
        key_id: API Key ID
        current_user: 当前用户
        
    Returns:
        测试结果，包含响应时间和详细状态
        
    Raises:
        HTTPException: 当 API Key 不存在时
    """
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 使用服务层的统一验证方法
        is_valid, message, response_time = api_key_service.validate_api_key(
            api_key_id=key_id,
            user_id=current_user.id,
            db=db,
            save_result=True  # 保存测试结果
        )
        
        from datetime import datetime
        return schemas.ApiKeyTestResponse(
            success=is_valid,
            message=message,
            response_time_ms=round(response_time, 2) if response_time else None,
            tested_at=datetime.utcnow()
        )
            
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"API Key 测试过程中发生错误: {e}", exc_info=True)
        
        return schemas.ApiKeyTestResponse(
            success=False,
            message=f"测试过程中发生错误: {str(e)}",
            response_time_ms=round(response_time, 2)
        )


@router.get("/stats/summary", summary="获取 API Key 统计", response_model=dict)
async def get_api_key_stats(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    获取当前用户的 API Key 统计信息
    
    Args:
        current_user: 当前用户
        
    Returns:
        统计信息
    """
    try:
        # 使用服务层获取统计信息
        return api_key_service.get_user_stats(
            user_id=current_user.id,
            db=db
        )
        
    except ApiKeyServiceError as e:
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
