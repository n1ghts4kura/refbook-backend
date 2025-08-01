#!/usr/bin/env python3
"""
测试清理数据库API的脚本
"""

import requests
import json

# 测试配置
BASE_URL = "http://127.0.0.1:8000"
CLEAN_DB_URL = f"{BASE_URL}/api/clean_db"

def test_clean_db_endpoint():
    """测试清理数据库端点"""
    print("🧪 测试清理数据库API端点...")
    
    try:
        # 发送POST请求到清理数据库端点
        response = requests.post(CLEAN_DB_URL)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ 清理数据库成功！")
        elif response.status_code == 403:
            print("⚠️  权限不足 - 可能DEBUG模式未启用")
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_clean_db_endpoint()
