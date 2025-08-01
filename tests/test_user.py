# test_user.py
# 用户数据库操作测试

import os
import sys
import asyncio
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from module.database.user import new_user, get_user_by_id, delete_user_by_id, User
from module.database.user_detail import get_user_detail


async def test_new_user():
    """测试创建新用户"""
    print("=" * 50)
    print("测试阶段：创建新用户")
    print("=" * 50)
    
    # 测试正常创建用户
    print("\n🔹 测试创建新用户")
    username = "testuser123"
    password_hash = "hashed_password_test_123"
    
    print(f"输入参数:")
    print(f"  - 用户名: {username}")
    print(f"  - 密码哈希: {password_hash}")
    
    result = await new_user(username, password_hash)
    
    if isinstance(result, str) and result:
        print(f"✓ 创建新用户成功")
        print(f"  - 用户ID: {result}")
        print(f"  - ID长度: {len(result)}")
        
        # 验证用户详情是否也被正确创建
        user = await get_user_by_id(result)
        if isinstance(user, User):
            print(f"  - 用户详情ID: {user.user_detail_id}")
            
            # 验证用户详情是否存在
            user_detail = await get_user_detail(user.user_detail_id)
            if hasattr(user_detail, 'id'):
                print(f"✓ 用户详情创建成功")
            else:
                print(f"✗ 用户详情创建失败: {user_detail}")
        
        return result, username, password_hash
    else:
        print(f"✗ 创建新用户失败: {result}")
        return None, None, None


async def test_get_user_by_id(user_id, expected_username, expected_password_hash):
    """测试根据ID获取用户"""
    print("\n" + "=" * 50)
    print("测试阶段：根据ID获取用户")
    print("=" * 50)
    
    # 测试获取存在的用户
    if user_id:
        print(f"\n🔹 测试获取存在的用户 (ID: {user_id})")
        result = await get_user_by_id(user_id)
        
        if isinstance(result, User):
            print(f"✓ 成功获取用户:")
            print(f"  - 用户ID: {result.id}")
            print(f"  - 用户名: {result.username}")
            print(f"  - 密码哈希: {result.password_hash}")
            print(f"  - 用户详情ID: {result.user_detail_id}")
            
            # 验证数据正确性
            if result.id == user_id:
                print(f"✓ 用户ID匹配")
            else:
                print(f"✗ 用户ID不匹配: 期望 {user_id}, 实际 {result.id}")
                
            if result.username == expected_username:
                print(f"✓ 用户名匹配")
            else:
                print(f"✗ 用户名不匹配: 期望 {expected_username}, 实际 {result.username}")
                
            if result.password_hash == expected_password_hash:
                print(f"✓ 密码哈希匹配")
            else:
                print(f"✗ 密码哈希不匹配: 期望 {expected_password_hash}, 实际 {result.password_hash}")
            
            # 验证用户详情是否存在
            if result.user_detail_id:
                user_detail = await get_user_detail(result.user_detail_id)
                if hasattr(user_detail, 'id'):
                    print(f"✓ 用户详情存在且有效")
                else:
                    print(f"✗ 用户详情无效: {user_detail}")
            else:
                print(f"✗ 用户详情ID为空")
                
        else:
            print(f"✗ 获取用户失败: {result}")
    else:
        print("⚠ 跳过获取存在的用户测试（没有有效的用户ID）")
    
    # 测试获取不存在的用户
    print("\n🔹 测试获取不存在的用户")
    fake_id = "nonexistent_user_id_12345"
    result = await get_user_by_id(fake_id)
    if isinstance(result, dict) and result.get("type") == "error":
        print(f"✓ 正确处理不存在的用户: {result['message']}")
    else:
        print(f"✗ 未正确处理不存在的用户: {result}")
    
    # 测试空字符串ID
    print("\n🔹 测试空字符串ID")
    result = await get_user_by_id("")
    if isinstance(result, dict) and result.get("type") == "error":
        print(f"✓ 正确处理空字符串ID: {result['message']}")
    else:
        print(f"✗ 未正确处理空字符串ID: {result}")


async def test_delete_user_by_id(user_id, username):
    """测试删除用户"""
    print("\n" + "=" * 50)
    print("测试阶段：删除用户")
    print("=" * 50)
    
    if not user_id:
        print("⚠ 跳过删除用户测试（没有有效的用户ID）")
        return
    
    print(f"\n🔹 测试删除存在的用户 (ID: {user_id}, 用户名: {username})")
    
    # 首先验证用户存在
    user = await get_user_by_id(user_id)
    if isinstance(user, User):
        print(f"✓ 确认用户存在，用户详情ID: {user.user_detail_id}")
        user_detail_id = user.user_detail_id
        
        # 删除用户
        result = await delete_user_by_id(user_id)
        
        if isinstance(result, dict) and result.get("type") == "success":
            print(f"✓ 删除用户成功")
            
            # 验证用户是否已被删除
            deleted_user = await get_user_by_id(user_id)
            if isinstance(deleted_user, dict) and deleted_user.get("type") == "error":
                print(f"✓ 确认用户已被删除")
            else:
                print(f"✗ 用户删除后仍然存在: {deleted_user}")
            
            # 验证用户详情是否也被删除
            user_detail = await get_user_detail(user_detail_id)
            if isinstance(user_detail, dict) and user_detail.get("type") == "error":
                print(f"✓ 确认用户详情也已被删除")
            else:
                print(f"✗ 用户详情删除失败: {user_detail}")
                
        else:
            print(f"✗ 删除用户失败: {result}")
    else:
        print(f"⚠ 用户不存在，无法测试删除: {user}")
    
    # 测试删除不存在的用户
    print("\n🔹 测试删除不存在的用户")
    fake_id = "nonexistent_user_id_12345"
    result = await delete_user_by_id(fake_id)
    if isinstance(result, dict) and result.get("type") == "error":
        print(f"✓ 正确处理删除不存在的用户: {result.get('message', 'Unknown error')}")
    else:
        print(f"✗ 未正确处理删除不存在的用户: {result}")
    
    # 测试删除空字符串ID
    print("\n🔹 测试删除空字符串ID")
    result = await delete_user_by_id("")
    if isinstance(result, dict) and result.get("type") == "error":
        print(f"✓ 正确处理删除空字符串ID: {result.get('message', 'Unknown error')}")
    else:
        print(f"✗ 未正确处理删除空字符串ID: {result}")


async def test_multiple_users():
    """测试创建多个用户"""
    print("\n" + "=" * 50)
    print("测试阶段：创建多个用户")
    print("=" * 50)
    
    users_data = []
    
    print("\n🔹 创建多个用户")
    for i in range(3):
        username = f"testuser_{i+1}"
        password_hash = f"hashed_password_{i+1}"
        
        print(f"\n创建用户 {i+1}:")
        print(f"  - 用户名: {username}")
        print(f"  - 密码哈希: {password_hash}")
        
        user_id = await new_user(username, password_hash)
        
        if isinstance(user_id, str) and user_id:
            print(f"✓ 创建成功，用户ID: {user_id}")
            users_data.append((user_id, username, password_hash))
        else:
            print(f"✗ 创建失败: {user_id}")
    
    print(f"\n总共创建了 {len(users_data)} 个用户")
    
    # 验证所有用户的ID都是唯一的
    print("\n🔹 验证用户ID唯一性")
    user_ids = [data[0] for data in users_data]
    unique_ids = set(user_ids)
    
    if len(user_ids) == len(unique_ids):
        print(f"✓ 所有用户ID都是唯一的 ({len(user_ids)} 个)")
    else:
        print(f"✗ 存在重复的用户ID: 创建 {len(user_ids)} 个，唯一 {len(unique_ids)} 个")
    
    return users_data


async def test_concurrent_user_creation():
    """测试并发创建用户"""
    print("\n" + "=" * 50)
    print("测试阶段：并发创建用户")
    print("=" * 50)
    
    print("\n🔹 并发创建5个用户")
    
    async def create_single_user(index):
        username = f"concurrent_user_{index}"
        password_hash = f"concurrent_hash_{index}"
        user_id = await new_user(username, password_hash)
        print(f"  并发任务 {index}: 创建用户ID {user_id}")
        return user_id, username, password_hash
    
    # 同时创建5个用户
    tasks = [create_single_user(i) for i in range(5)]
    results = await asyncio.gather(*tasks)
    
    # 验证结果
    successful_creations = [r for r in results if isinstance(r[0], str) and r[0]]
    print(f"\n✓ 成功创建了 {len(successful_creations)} 个用户")
    
    # 验证ID唯一性
    user_ids = [r[0] for r in successful_creations]
    unique_ids = set(user_ids)
    
    if len(user_ids) == len(unique_ids):
        print(f"✓ 并发创建的用户ID都是唯一的")
    else:
        print(f"✗ 并发创建存在重复ID")
    
    return successful_creations


async def test_edge_cases():
    """测试边界情况"""
    print("\n" + "=" * 50)
    print("测试阶段：边界情况测试")
    print("=" * 50)
    
    # 测试特殊字符用户名
    print("\n🔹 测试特殊字符用户名")
    special_username = "test@user.com"
    special_password = "password_with_special_chars!@#$%^&*()"
    
    result = await new_user(special_username, special_password)
    if isinstance(result, str) and result:
        print(f"✓ 成功创建包含特殊字符的用户: {result}")
        
        # 验证能否正确获取
        user = await get_user_by_id(result)
        if isinstance(user, User) and user.username == special_username:
            print(f"✓ 成功获取包含特殊字符的用户")
        else:
            print(f"✗ 获取包含特殊字符的用户失败")
    else:
        print(f"✗ 创建包含特殊字符的用户失败: {result}")
    
    # 测试很长的用户名和密码
    print("\n🔹 测试长用户名和密码")
    long_username = "a" * 100
    long_password = "b" * 200
    
    result = await new_user(long_username, long_password)
    if isinstance(result, str) and result:
        print(f"✓ 成功创建长用户名密码的用户: {result}")
        
        # 验证能否正确获取
        user = await get_user_by_id(result)
        if isinstance(user, User):
            print(f"✓ 成功获取长用户名密码的用户")
            print(f"  - 用户名长度: {len(user.username)}")
            print(f"  - 密码长度: {len(user.password_hash)}")
        else:
            print(f"✗ 获取长用户名密码的用户失败")
    else:
        print(f"✗ 创建长用户名密码的用户失败: {result}")
    
    # 测试空用户名和密码（虽然可能不被允许，但要测试系统的健壮性）
    print("\n🔹 测试空用户名")
    try:
        result = await new_user("", "some_password")
        if isinstance(result, str) and result:
            print(f"⚠ 系统允许空用户名: {result}")
        else:
            print(f"✓ 系统正确拒绝空用户名: {result}")
    except Exception as e:
        print(f"✓ 系统通过异常拒绝空用户名: {type(e).__name__}: {e}")
    
    print("\n🔹 测试空密码")
    try:
        result = await new_user("test_user", "")
        if isinstance(result, str) and result:
            print(f"⚠ 系统允许空密码: {result}")
        else:
            print(f"✓ 系统正确拒绝空密码: {result}")
    except Exception as e:
        print(f"✓ 系统通过异常拒绝空密码: {type(e).__name__}: {e}")


async def test_data_integrity():
    """测试数据完整性"""
    print("\n" + "=" * 50)
    print("测试阶段：数据完整性测试")
    print("=" * 50)
    
    print("\n🔹 创建用户并验证数据完整性")
    
    # 创建用户
    username = "integrity_test_user"
    password_hash = "integrity_test_password_hash"
    
    user_id = await new_user(username, password_hash)
    print(f"创建用户ID: {user_id}")
    
    if isinstance(user_id, str) and user_id:
        # 多次获取用户，验证数据一致性
        print("\n🔹 多次获取用户验证数据一致性")
        for i in range(3):
            user = await get_user_by_id(user_id)
            if isinstance(user, User):
                print(f"第 {i+1} 次获取:")
                print(f"  - ID: {user.id}")
                print(f"  - 用户名: {user.username}")
                print(f"  - 密码哈希: {user.password_hash}")
                
                # 验证数据一致性
                if user.id == user_id and user.username == username and user.password_hash == password_hash:
                    print(f"  ✓ 数据一致")
                else:
                    print(f"  ✗ 数据不一致")
            else:
                print(f"第 {i+1} 次获取失败: {user}")
    
    # 测试用户模型验证
    print("\n🔹 测试User模型验证")
    try:
        # 测试正常的User对象创建
        valid_user = User(
            id="test_id_123",
            username="test_username",
            password_hash="test_password_hash",
            user_detail_id="test_user_detail_id_123"
        )
        print(f"✓ 正常User对象创建成功: {valid_user.username}")
    except Exception as e:
        print(f"✗ 正常User对象创建失败: {type(e).__name__}: {e}")
    
    try:
        # 测试缺少必需字段的User对象创建
        # 这里故意传入不完整的参数来测试验证，应该会抛出异常
        try:
            invalid_user = User(id="test_id_456")  # 缺少username、password_hash和user_detail_id
            print(f"⚠ 不完整User对象创建成功（可能有问题）: {invalid_user}")
        except TypeError as te:
            print(f"✓ 正确拒绝不完整User对象（缺少参数）: {te}")
        except Exception as e:
            print(f"✓ 正确拒绝不完整User对象: {type(e).__name__}: {e}")
    except Exception as e:
        print(f"✗ 测试不完整User对象时发生意外错误: {type(e).__name__}: {e}")


async def test_comprehensive_workflow():
    """综合工作流测试"""
    print("\n" + "=" * 50)
    print("测试阶段：综合工作流测试")
    print("=" * 50)
    
    print("\n🔹 模拟真实用户注册和登录流程")
    
    # 模拟用户注册
    print("\n步骤1: 用户注册")
    username = "real_user_test"
    original_password = "my_secure_password_123"
    
    # 在真实应用中，这里会对密码进行哈希处理
    import hashlib
    password_hash = hashlib.sha256(original_password.encode()).hexdigest()
    print(f"  原始密码: {original_password}")
    print(f"  密码哈希: {password_hash}")
    
    user_id = await new_user(username, password_hash)
    if isinstance(user_id, str) and user_id:
        print(f"✓ 用户注册成功，用户ID: {user_id}")
    else:
        print(f"✗ 用户注册失败: {user_id}")
        return
    
    # 模拟用户登录验证
    print("\n步骤2: 用户登录验证")
    user = await get_user_by_id(user_id)
    if isinstance(user, User):
        print(f"✓ 成功获取用户信息")
        
        # 验证密码（在真实应用中会比较哈希值）
        input_password = "my_secure_password_123"
        input_password_hash = hashlib.sha256(input_password.encode()).hexdigest()
        
        if user.password_hash == input_password_hash:
            print(f"✓ 密码验证成功，用户登录成功")
        else:
            print(f"✗ 密码验证失败")
    else:
        print(f"✗ 获取用户信息失败: {user}")
    
    # 模拟错误密码登录
    print("\n步骤3: 错误密码登录测试")
    wrong_password = "wrong_password"
    wrong_password_hash = hashlib.sha256(wrong_password.encode()).hexdigest()
    
    if isinstance(user, User) and user.password_hash != wrong_password_hash:
        print(f"✓ 正确拒绝错误密码")
    else:
        print(f"✗ 错误接受了错误密码")


async def main():
    """主测试函数"""
    print("🚀 开始用户数据库操作测试")
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. 基本功能测试
        print("\n" + "🔥" * 20 + " 基本功能测试 " + "🔥" * 20)
        
        # 测试创建用户
        user_id, username, password_hash = await test_new_user()
        
        # 测试获取用户
        await test_get_user_by_id(user_id, username, password_hash)
        
        # 2. 删除功能测试
        print("\n" + "🗑️ " * 20 + " 删除功能测试 " + "🗑️ " * 20)
        
        # 创建一个用于删除测试的用户
        delete_test_user_id, delete_test_username, _ = await test_new_user()
        if delete_test_user_id:
            await test_delete_user_by_id(delete_test_user_id, delete_test_username)
        
        # 3. 多用户测试
        print("\n" + "👥" * 20 + " 多用户测试 " + "👥" * 20)
        await test_multiple_users()
        
        # 4. 并发测试
        print("\n" + "💪" * 20 + " 并发测试 " + "💪" * 20)
        await test_concurrent_user_creation()
        
        # 5. 边界情况测试
        print("\n" + "🎯" * 20 + " 边界情况测试 " + "🎯" * 20)
        await test_edge_cases()
        
        # 6. 数据完整性测试
        print("\n" + "🔐" * 20 + " 数据完整性测试 " + "🔐" * 20)
        await test_data_integrity()
        
        # 7. 综合工作流测试
        print("\n" + "🌟" * 20 + " 综合工作流测试 " + "🌟" * 20)
        await test_comprehensive_workflow()
        
        print("\n" + "🎊" * 60)
        print("🎊" + " " * 18 + "所有用户测试完成！" + " " * 18 + "🎊")
        print("🎊" * 60)
        
    except Exception as e:
        print(f"\n💥 测试过程中发生未捕获的异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
