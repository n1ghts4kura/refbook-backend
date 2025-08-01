#!/usr/bin/env python3
"""
临时脚本：生成正确的密码哈希并修复数据库
"""

from passlib.context import CryptContext
import json

# 创建密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 生成 admin 密码的哈希
admin_password = "admin"
admin_hash = pwd_context.hash(admin_password)

print(f"原密码: {admin_password}")
print(f"哈希值: {admin_hash}")

# 读取并修复数据库文件
db_file_path = "database_file/db_user_v1.json"

try:
    with open(db_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 修复用户数据
    if "_default" in data and "1" in data["_default"]:
        user_data = data["_default"]["1"]
        if user_data["password_hash"] == "admin":  # 如果是明文密码
            user_data["password_hash"] = admin_hash
            print("✓ 已修复用户密码哈希")
        else:
            print("用户密码哈希已经是正确格式")
    
    # 写回文件
    with open(db_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"✓ 数据库文件已更新: {db_file_path}")
    
except Exception as e:
    print(f"❌ 修复失败: {e}")
