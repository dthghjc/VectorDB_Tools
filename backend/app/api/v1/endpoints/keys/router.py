# backend/app/api/v1/endpoints/keys/router.py

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.crypto import get_public_key
from app.core.security import get_current_active_user
from app.core.db import get_db
from app.models.user import User
from app.schemas.crypto import RSAPublicKeyResponse
from app.schemas import api_key as schemas
from app.crud.api_key import api_key_crud
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

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
    # 检查名称是否重复
    existing = api_key_crud.get_by_name(db, name=api_key_in.name, user_id=current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API Key 名称 '{api_key_in.name}' 已存在"
        )
    
    try:
        # 创建 API Key
        api_key = api_key_crud.create(db, obj_in=api_key_in, user_id=current_user.id)
        
        return schemas.ApiKeyCreateResponse(
            id=api_key.id,
            name=api_key.name,
            provider=api_key.provider,
            base_url=api_key.base_url,
            key_preview=api_key.key_preview,
            status=api_key.status,
            usage_count=api_key.usage_count,
            created_at=api_key.created_at,
            updated_at=api_key.updated_at
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
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    provider: Optional[str] = Query(None, description="按提供商过滤"),
    status: Optional[str] = Query(None, regex="^(active|inactive)$", description="按状态过滤"),
    current_user: User = Depends(get_current_active_user)
) -> schemas.ApiKeyList:
    """
    获取当前用户的 API Key 列表
    
    Args:
        skip: 跳过数量
        limit: 每页数量
        provider: 按提供商过滤
        status: 按状态过滤
        current_user: 当前用户
        
    Returns:
        分页的 API Key 列表
    """
    items, total = api_key_crud.get_multi(
        db, 
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        provider=provider,
        status=status
    )
    
    pages = (total + limit - 1) // limit  # 向上取整
    
    return schemas.ApiKeyList(
        items=[schemas.ApiKeyResponse.model_validate(item) for item in items],
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=pages
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
    api_key = api_key_crud.get(db, id=key_id, user_id=current_user.id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key 不存在"
        )
    
    return schemas.ApiKeyResponse.model_validate(api_key)


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
    # 获取原 API Key
    api_key = api_key_crud.get(db, id=key_id, user_id=current_user.id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key 不存在"
        )
    
    # 检查名称冲突（如果更新了名称）
    if api_key_in.name and api_key_in.name != api_key.name:
        existing = api_key_crud.get_by_name(db, name=api_key_in.name, user_id=current_user.id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"API Key 名称 '{api_key_in.name}' 已存在"
            )
    
    # 更新 API Key
    updated_api_key = api_key_crud.update(db, db_obj=api_key, obj_in=api_key_in)
    
    return schemas.ApiKeyResponse.model_validate(updated_api_key)


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
    success = api_key_crud.delete(db, id=key_id, user_id=current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key 不存在"
        )
    
    return {"message": "API Key 删除成功", "id": str(key_id)}


@router.post("/{key_id}/test", summary="测试 API Key", response_model=schemas.ApiKeyTestResponse)
async def test_api_key(
    *,
    db: Session = Depends(get_db),
    key_id: UUID,
    test_in: Optional[schemas.ApiKeyTestRequest] = None,
    current_user: User = Depends(get_current_active_user)
) -> schemas.ApiKeyTestResponse:
    """
    测试 API Key 连通性
    
    Args:
        key_id: API Key ID
        test_in: 测试请求数据
        current_user: 当前用户
        
    Returns:
        测试结果
        
    Raises:
        HTTPException: 当 API Key 不存在或测试失败时
    """
    import time
    import httpx
    
    # 获取 API Key
    api_key = api_key_crud.get(db, id=key_id, user_id=current_user.id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key 不存在"
        )
    
    if not api_key.is_active():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API Key 已被禁用"
        )
    
    try:
        # 解密获取真实密钥
        real_api_key = api_key_crud.get_plaintext_key(encrypted_key=api_key.encrypted_api_key)
        
        # 构建测试URL
        test_endpoint = test_in.test_endpoint if test_in else "/models"
        test_url = f"{api_key.base_url.rstrip('/')}{test_endpoint}"
        
        # 执行测试请求
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                test_url,
                headers={"Authorization": f"Bearer {real_api_key}"}
            )
        
        response_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        # 更新使用统计
        api_key_crud.update_usage(db, db_obj=api_key)
        
        if response.status_code == 200:
            return schemas.ApiKeyTestResponse(
                success=True,
                message="API Key 测试成功",
                response_time_ms=response_time,
                status_code=response.status_code
            )
        else:
            return schemas.ApiKeyTestResponse(
                success=False,
                message=f"API 返回错误: {response.status_code}",
                response_time_ms=response_time,
                status_code=response.status_code
            )
            
    except httpx.TimeoutException:
        return schemas.ApiKeyTestResponse(
            success=False,
            message="请求超时，请检查网络连接或API服务状态"
        )
    except Exception as e:
        logger.error(f"API Key 测试失败: {e}")
        return schemas.ApiKeyTestResponse(
            success=False,
            message=f"测试失败: {str(e)}"
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
    return api_key_crud.get_user_stats(db, user_id=current_user.id)
