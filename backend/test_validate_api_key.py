#!/usr/bin/env python3
"""
测试 OpenAIClient 的 validate_api_key 函数
使用数据库中存储的 OpenAI API key
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.crud.api_key import ApiKeyCRUD
from app.llm_clients.openai_client import OpenAIClient
from app.core.config import settings
from app.core.crypto import initialize_crypto


def get_openai_key_from_db() -> tuple[str, str] | None:
    """
    从数据库获取 OpenAI 的 API key
    
    Returns:
        tuple[api_key, base_url] 或 None
    """
    db: Session = SessionLocal()
    api_key_crud = ApiKeyCRUD()
    
    try:
        from app.models.api_key import ApiKey
        
        # 查询 provider 为 'openai' 的 API key
        api_key_record = db.query(ApiKey).filter(
            ApiKey.provider == 'bce-qianfan',
            ApiKey.status == 'active'
        ).first()
        
        if api_key_record:
            # 解密 API key
            decrypted_key = api_key_crud.get_plaintext_key(
                encrypted_key=api_key_record.encrypted_api_key
            )
            return decrypted_key, api_key_record.base_url
        else:
            print("❌ 数据库中没有找到活跃的 OpenAI API key")
            
            # 显示所有可用的 API keys 供参考
            all_keys = db.query(ApiKey).all()
            if all_keys:
                print("📋 数据库中现有的 API keys:")
                for key in all_keys:
                    print(f"   - ID: {key.id}, Name: {key.name}, Provider: {key.provider}, Status: {key.status}")
            else:
                print("📋 数据库中没有任何 API keys")
            return None
            
    except Exception as e:
        print(f"❌ 从数据库获取 API key 时出错: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()


def test_validate_api_key():
    """
    测试 OpenAIClient 的 validate_api_key 函数
    """
    print("🚀 开始测试 OpenAIClient.validate_api_key() 函数...")
    print("🎯 目标：测试数据库中的 OpenAI API key")
    print("=" * 60)
    
    # 0. 初始化加密系统
    print("0️⃣ 初始化加密系统...")
    try:
        initialize_crypto()
        print("✅ 加密系统初始化成功")
    except Exception as e:
        print(f"❌ 加密系统初始化失败: {e}")
        print("请确保已经运行了 generate-keys.sh 并配置了 .env 文件")
        return
    
    # 1. 检查配置
    print("\n1️⃣ 检查数据库配置...")
    if not settings.DATABASE_URL:
        print("❌ 数据库未配置，请检查环境变量")
        return
    print("✅ 数据库配置正常")
    
    # 2. 从数据库获取 OpenAI API key
    print("\n2️⃣ 从数据库获取 OpenAI API key...")
    key_info = get_openai_key_from_db()
    
    if not key_info:
        print("❌ 无法获取 OpenAI API key，测试终止")
        return
        
    api_key, base_url = key_info
    print(f"✅ 成功获取 API key: {api_key[:10]}...{api_key[-4:]}")
    print(f"✅ Base URL: {base_url}")
    
    # 3. 创建 OpenAIClient 实例
    print("\n3️⃣ 创建 OpenAIClient 实例...")
    try:
        client = OpenAIClient(api_key=api_key, base_url=base_url)
        print("✅ OpenAIClient 实例创建成功")
    except Exception as e:
        print(f"❌ 创建 OpenAIClient 实例失败: {e}")
        return
    
    # 4. 测试 validate_api_key 函数
    print("\n4️⃣ 测试 validate_api_key 函数...")
    print("正在验证 OpenAI API key...")
    
    try:
        is_valid, message = client.validate_api_key()
        
        print(f"\n📊 测试结果:")
        print(f"   验证结果: {'✅ 有效' if is_valid else '❌ 无效'}")
        print(f"   返回消息: {message}")
        
        if is_valid:
            print("\n🎉 测试成功！OpenAI API key 验证通过")
        else:
            print(f"\n⚠️  测试发现问题：{message}")
            
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()


def test_with_fake_key():
    """
    使用假的 API key 测试验证函数（验证错误处理）
    """
    print("\n" + "=" * 60)
    print("🧪 测试错误处理：使用无效的 API key...")
    
    fake_client = OpenAIClient(
        api_key="sk-fake-invalid-key-12345", 
        base_url="https://api.openai.com/v1"
    )
    
    try:
        is_valid, message = fake_client.validate_api_key()
        print(f"验证结果: {'✅ 有效' if is_valid else '❌ 无效'}")
        print(f"错误消息: {message}")
        
        if not is_valid:
            print("✅ 错误处理正常：成功识别无效 API key")
        else:
            print("⚠️  错误处理异常：假 API key 被误认为有效")
            
    except Exception as e:
        print(f"❌ 测试假 API key 时发生异常: {e}")


def test_available_providers():
    """
    显示数据库中所有可用的 API 提供商
    """
    print("\n" + "=" * 60)
    print("📋 检查数据库中所有可用的 API 提供商...")
    
    db: Session = SessionLocal()
    try:
        from app.models.api_key import ApiKey
        
        # 获取所有提供商的统计
        providers = db.query(ApiKey.provider, ApiKey.status).all()
        
        if providers:
            provider_stats = {}
            for provider, status in providers:
                if provider not in provider_stats:
                    provider_stats[provider] = {"active": 0, "inactive": 0}
                provider_stats[provider][status] += 1
            
            print("📊 提供商统计:")
            for provider, stats in provider_stats.items():
                print(f"   🔑 {provider}: {stats['active']} 个活跃, {stats['inactive']} 个禁用")
        else:
            print("❌ 数据库中没有任何 API keys")
            
    except Exception as e:
        print(f"❌ 获取提供商信息时出错: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    # 检查所有可用的提供商
    test_available_providers()
    
    # 测试真实的 OpenAI API key
    test_validate_api_key()
    
    # 测试错误处理
    test_with_fake_key()
    
    print("\n" + "=" * 60)
    print("✨ 测试完成！")
