#!/usr/bin/env python3
"""
测试修复后的 API Key 列表接口
"""

import requests
import json

def test_api_key_list():
    """测试 API Key 列表接口"""
    
    # 首先需要登录获取 token
    login_url = "http://127.0.0.1:8000/api/v1/auth/login"
    login_data = {
        "email": "test@example.com",  # 需要替换为实际的用户账号
        "password": "test123"         # 需要替换为实际的密码
    }
    
    try:
        # 1. 登录获取 token
        print("🔐 正在登录...")
        login_response = requests.post(login_url, json=login_data)
        print(f"登录响应状态: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print("❌ 登录失败，请检查用户名密码")
            print(f"错误信息: {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        print("✅ 登录成功")
        
        # 2. 测试 API Key 列表接口
        print("\n📋 正在测试 API Key 列表接口...")
        list_url = "http://127.0.0.1:8000/api/v1/keys/?page=1&size=10"
        headers = {"Authorization": f"Bearer {token}"}
        
        list_response = requests.get(list_url, headers=headers)
        print(f"API Key 列表响应状态: {list_response.status_code}")
        
        if list_response.status_code == 200:
            data = list_response.json()
            print("✅ API Key 列表接口正常工作")
            print(f"📊 返回数据结构: {json.dumps(data, indent=2, default=str)}")
        else:
            print("❌ API Key 列表接口仍有问题")
            print(f"错误信息: {list_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    test_api_key_list()
