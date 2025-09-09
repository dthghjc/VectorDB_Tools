#!/usr/bin/env python3
"""
测试 LLMClientFactory 和各种客户端的 validate_api_key 函数
使用数据库中存储的多个提供商的 API keys
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
from app.llm_clients.factory import LLMClientFactory
from app.core.config import settings
from app.core.crypto import initialize_crypto


def get_api_key_from_db(provider: str) -> tuple[str, str, str] | None:
    """
    从数据库获取指定提供商的 API key
    
    Args:
        provider: 提供商名称，如 'openai', 'nvidia-nim', 'bce-qianfan'
    
    Returns:
        tuple[api_key, base_url, provider] 或 None
    """
    db: Session = SessionLocal()
    api_key_crud = ApiKeyCRUD()
    
    try:
        from app.models.api_key import ApiKey
        
        # 查询指定 provider 的 API key
        api_key_record = db.query(ApiKey).filter(
            ApiKey.provider == provider,
            ApiKey.status == 'active'
        ).first()
        
        if api_key_record:
            # 解密 API key
            decrypted_key = api_key_crud.get_plaintext_key(
                encrypted_key=api_key_record.encrypted_api_key
            )
            return decrypted_key, api_key_record.base_url, api_key_record.provider
        else:
            print(f"❌ 数据库中没有找到活跃的 {provider} API key")
            return None
            
    except Exception as e:
        print(f"❌ 从数据库获取 {provider} API key 时出错: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()


def test_single_provider(provider: str) -> bool:
    """
    测试单个提供商的 API key 验证
    
    Args:
        provider: 提供商名称
        
    Returns:
        bool: 测试是否成功
    """
    print(f"\n🎯 测试 {provider.upper()} API key...")
    print("-" * 50)
    
    # 1. 从数据库获取 API key
    key_info = get_api_key_from_db(provider)
    
    if not key_info:
        print(f"❌ 跳过 {provider}：无法获取 API key")
        return False
        
    api_key, base_url, actual_provider = key_info
    print(f"✅ 成功获取 API key: {api_key[:10]}...{api_key[-4:]}")
    print(f"✅ Base URL: {base_url}")
    print(f"✅ Provider: {actual_provider}")
    
    # 2. 使用工厂创建客户端
    try:
        client = LLMClientFactory.get_client(
            provider=actual_provider,
            api_key=api_key,
            base_url=base_url
        )
        print(f"✅ 使用工厂模式创建 {actual_provider} 客户端成功")
    except Exception as e:
        print(f"❌ 创建 {actual_provider} 客户端失败: {e}")
        return False
    
    # 3. 测试 validate_api_key 函数
    print(f"🔍 正在验证 {actual_provider} API key...")
    
    try:
        is_valid, message = client.validate_api_key()
        
        print(f"📊 验证结果: {'✅ 有效' if is_valid else '❌ 无效'}")
        print(f"📝 返回消息: {message}")
        
        if is_valid:
            print(f"🎉 {actual_provider} API key 验证通过！")
            return True
        else:
            print(f"⚠️  {actual_provider} API key 验证失败: {message}")
            return False
            
    except Exception as e:
        print(f"❌ 验证 {actual_provider} API key 时发生异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_providers():
    """
    测试多个提供商的 API key 验证
    """
    print("🚀 开始测试多个提供商的 validate_api_key() 函数...")
    print("🎯 目标：openai、nvidia-nim、bce-qianfan")
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
    
    # 2. 测试目标提供商
    target_providers = ["openai", "nvidia-nim", "bce-qianfan"]
    results = {}
    
    print(f"\n2️⃣ 开始测试 {len(target_providers)} 个提供商...")
    
    for provider in target_providers:
        results[provider] = test_single_provider(provider)
    
    # 3. 输出汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    
    success_count = 0
    for provider, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   🔑 {provider.ljust(12)}: {status}")
        if success:
            success_count += 1
    
    print(f"\n🎯 总体结果: {success_count}/{len(target_providers)} 个提供商验证成功")
    
    if success_count == len(target_providers):
        print("🎉 所有目标提供商的 API keys 都验证通过！")
    elif success_count > 0:
        print("⚠️  部分提供商验证成功，请检查失败的 API keys")
    else:
        print("❌ 所有提供商验证都失败，请检查配置")


def test_error_handling():
    """
    使用假的 API key 测试各种客户端的错误处理
    """
    print("\n" + "=" * 60)
    print("🧪 测试错误处理：使用无效的 API keys...")
    
    test_cases = [
        {
            "provider": "openai",
            "fake_key": "sk-fake-invalid-key-12345",
            "base_url": "https://api.openai.com/v1"
        },
        {
            "provider": "nvidia-nim",
            "fake_key": "nvapi-fake-invalid-key-12345",
            "base_url": "https://integrate.api.nvidia.com/v1"
        },
        {
            "provider": "bce-qianfan",
            "fake_key": "fake_ak:fake_sk",
            "base_url": "https://aip.baidubce.com"
        }
    ]
    
    for test_case in test_cases:
        provider = test_case["provider"]
        print(f"\n🔍 测试 {provider} 错误处理...")
        
        try:
            client = LLMClientFactory.get_client(
                provider=provider,
                api_key=test_case["fake_key"],
                base_url=test_case["base_url"]
            )
            
            is_valid, message = client.validate_api_key()
            print(f"   验证结果: {'✅ 有效' if is_valid else '❌ 无效'}")
            print(f"   错误消息: {message}")
            
            if not is_valid:
                print(f"   ✅ {provider} 错误处理正常：成功识别无效 API key")
            else:
                print(f"   ⚠️  {provider} 错误处理异常：假 API key 被误认为有效")
                
        except Exception as e:
            print(f"   ❌ 测试 {provider} 假 API key 时发生异常: {e}")


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
    
    # 测试多个提供商的 API keys
    test_multiple_providers()
    
    # 测试错误处理
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("✨ 测试完成！")
