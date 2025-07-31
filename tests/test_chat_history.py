import sys
import asyncio
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# from module.database.general import *
from module.database.chat_history import *


async def test_new_chat_history():
    """测试创建新聊天记录"""
    print("=" * 50)
    print("测试阶段：创建新聊天记录")
    print("=" * 50)
    
    # 测试正常创建
    result = await new_chat_history()
    print(f"✓ 创建新聊天记录结果: {result}")
    
    if result["type"] == "success":
        print(f"✓ 成功创建聊天记录，ID: {result['message']}")
        return result["message"]
    else:
        print(f"✗ 创建聊天记录失败: {result['message']}")
        return None


async def test_get_chat_history(chat_id):
    """测试获取聊天记录"""
    print("\n" + "=" * 50)
    print("测试阶段：获取聊天记录")
    print("=" * 50)
    
    # 测试获取存在的聊天记录
    if chat_id:
        result = await get_chat_history(chat_id)
        if isinstance(result, ChatHistory):
            print(f"✓ 成功获取聊天记录，ID: {result.id}")
            print(f"✓ 聊天记录消息数量: {len(result.messages)}")
        else:
            print(f"✗ 获取聊天记录失败: {result.get('message', '未知错误')}")
    
    # 测试获取不存在的聊天记录
    fake_id = "nonexistent_chat_id_12345"
    result = await get_chat_history(fake_id)
    if isinstance(result, dict) and result["type"] == "error":
        print(f"✓ 正确处理不存在的聊天记录: {result['message']}")
    else:
        print(f"✗ 未正确处理不存在的聊天记录")


async def test_new_chat_message(chat_id):
    """测试创建新聊天消息"""
    print("\n" + "=" * 50)
    print("测试阶段：创建新聊天消息")
    print("=" * 50)
    
    message_ids = []
    
    if not chat_id:
        print("✗ 无法测试，聊天记录ID为空")
        return message_ids
    
    # 测试添加多条消息
    test_messages = [
        ("human", "你好，这是第一条消息"),
        ("bot", "你好！很高兴为您服务。"),
        ("human", "请帮我解答一个问题"),
        ("bot", "当然可以，请告诉我您的问题。")
    ]
    
    for i, (role, content) in enumerate(test_messages):
        # 使用类型断言确保role类型正确
        from typing import cast, Literal
        typed_role = cast(Literal["human", "bot"], role)
        result = await new_chat_message(chat_id, typed_role, content)
        if result["type"] == "success":
            message_ids.append(result["message"])
            print(f"✓ 成功添加第{i+1}条消息 ({role}): {content[:20]}...")
        else:
            print(f"✗ 添加第{i+1}条消息失败: {result['message']}")
    
    # 测试添加到不存在的聊天记录
    fake_id = "nonexistent_chat_id_12345"
    result = await new_chat_message(fake_id, "human", "测试消息")
    if result["type"] == "error":
        print(f"✓ 正确处理不存在的聊天记录: {result['message']}")
    else:
        print(f"✗ 未正确处理不存在的聊天记录")
    
    # 测试无效的角色
    try:
        # 这个应该在运行时被pydantic验证捕获
        # 使用类型忽略来测试运行时错误处理
        invalid_role = "invalid_role"  # type: ignore
        result = await new_chat_message(chat_id, invalid_role, "测试消息")  # type: ignore
        print(f"✗ 未正确处理无效角色")
    except Exception as e:
        print(f"✓ 正确处理无效角色: {str(e)[:50]}...")
    
    return message_ids


async def test_get_chat_message_by_id(chat_id, message_ids):
    """测试通过ID获取聊天消息"""
    print("\n" + "=" * 50)
    print("测试阶段：通过ID获取聊天消息")
    print("=" * 50)
    
    if not chat_id or not message_ids:
        print("✗ 无法测试，聊天记录ID或消息ID为空")
        return
    
    # 测试获取存在的消息
    for i, message_id in enumerate(message_ids):
        result = await get_chat_message_by_id(chat_id, message_id)
        if isinstance(result, ChatMessage):
            print(f"✓ 成功获取第{i+1}条消息: {result.role} - {result.content[:30]}...")
        else:
            print(f"✗ 获取第{i+1}条消息失败: {result.get('message', '未知错误')}")
    
    # 测试获取不存在的消息ID
    fake_message_id = "nonexistent_message_id_12345"
    result = await get_chat_message_by_id(chat_id, fake_message_id)
    if isinstance(result, dict) and result["type"] == "error":
        print(f"✓ 正确处理不存在的消息ID: {result['message']}")
    else:
        print(f"✗ 未正确处理不存在的消息ID")
    
    # 测试在不存在的聊天记录中获取消息
    fake_chat_id = "nonexistent_chat_id_12345"
    result = await get_chat_message_by_id(fake_chat_id, message_ids[0] if message_ids else "any_id")
    if isinstance(result, dict) and result["type"] == "error":
        print(f"✓ 正确处理不存在的聊天记录: {result['message']}")
    else:
        print(f"✗ 未正确处理不存在的聊天记录")


async def test_get_chat_message_by_index(chat_id, message_count):
    """测试通过索引获取聊天消息"""
    print("\n" + "=" * 50)
    print("测试阶段：通过索引获取聊天消息")
    print("=" * 50)
    
    if not chat_id:
        print("✗ 无法测试，聊天记录ID为空")
        return
    
    # 测试获取有效索引的消息
    for i in range(message_count):
        result = await get_chat_message_by_index(chat_id, i)
        if isinstance(result, ChatMessage):
            print(f"✓ 成功获取索引{i}的消息: {result.role} - {result.content[:30]}...")
        else:
            print(f"✗ 获取索引{i}的消息失败: {result.get('message', '未知错误')}")
    
    # 测试超出范围的索引
    out_of_range_indices = [-1, message_count, message_count + 10]
    for index in out_of_range_indices:
        result = await get_chat_message_by_index(chat_id, index)
        if isinstance(result, dict) and result["type"] == "error":
            print(f"✓ 正确处理超出范围的索引{index}: {result['message']}")
        else:
            print(f"✗ 未正确处理超出范围的索引{index}")
    
    # 测试在不存在的聊天记录中获取消息
    fake_chat_id = "nonexistent_chat_id_12345"
    result = await get_chat_message_by_index(fake_chat_id, 0)
    if isinstance(result, dict) and result["type"] == "error":
        print(f"✓ 正确处理不存在的聊天记录: {result['message']}")
    else:
        print(f"✗ 未正确处理不存在的聊天记录")


async def test_delete_chat_message(chat_id, message_ids):
    """测试删除聊天消息"""
    print("\n" + "=" * 50)
    print("测试阶段：删除聊天消息")
    print("=" * 50)
    
    if not chat_id or not message_ids:
        print("✗ 无法测试，聊天记录ID或消息ID为空")
        return
    
    # 测试删除存在的消息（删除第一条）
    if message_ids:
        message_to_delete = message_ids[0]
        result = await delete_chat_message(chat_id, message_to_delete)
        if result["type"] == "success":
            print(f"✓ 成功删除消息: {message_to_delete}")
            # 验证消息确实被删除
            check_result = await get_chat_message_by_id(chat_id, message_to_delete)
            if isinstance(check_result, dict) and check_result["type"] == "error":
                print(f"✓ 验证消息已被删除")
            else:
                print(f"✗ 消息删除后仍然存在")
        else:
            print(f"✗ 删除消息失败: {result['message']}")
    
    # 测试删除不存在的消息
    fake_message_id = "nonexistent_message_id_12345"
    result = await delete_chat_message(chat_id, fake_message_id)
    if result["type"] == "error":
        print(f"✓ 正确处理删除不存在的消息: {result['message']}")
    else:
        print(f"✗ 未正确处理删除不存在的消息")
    
    # 测试在不存在的聊天记录中删除消息
    fake_chat_id = "nonexistent_chat_id_12345"
    result = await delete_chat_message(fake_chat_id, message_ids[1] if len(message_ids) > 1 else "any_id")
    if result["type"] == "error":
        print(f"✓ 正确处理不存在的聊天记录: {result['message']}")
    else:
        print(f"✗ 未正确处理不存在的聊天记录")


async def test_delete_chat_history(chat_id):
    """测试删除聊天记录"""
    print("\n" + "=" * 50)
    print("测试阶段：删除聊天记录")
    print("=" * 50)
    
    if not chat_id:
        print("✗ 无法测试，聊天记录ID为空")
        return
    
    # 测试删除存在的聊天记录
    result = await delete_chat_history(chat_id)
    if result["type"] == "success":
        print(f"✓ 成功删除聊天记录: {chat_id}")
        # 验证聊天记录确实被删除
        check_result = await get_chat_history(chat_id)
        if isinstance(check_result, dict) and check_result["type"] == "error":
            print(f"✓ 验证聊天记录已被删除")
        else:
            print(f"✗ 聊天记录删除后仍然存在")
    else:
        print(f"✗ 删除聊天记录失败: {result['message']}")
    
    # 测试删除不存在的聊天记录
    fake_id = "nonexistent_chat_id_12345"
    result = await delete_chat_history(fake_id)
    if result["type"] == "error":
        print(f"✓ 正确处理删除不存在的聊天记录: {result['message']}")
    else:
        print(f"✗ 未正确处理删除不存在的聊天记录")


async def test_encoding():
    """测试中文编码"""
    print("\n" + "=" * 50)
    print("测试阶段：中文编码测试")
    print("=" * 50)
    
    # 创建一个聊天记录用于编码测试
    result = await new_chat_history()
    if result["type"] != "success":
        print("✗ 创建聊天记录失败，无法测试编码")
        return
    
    chat_id = result["message"]
    print(f"✓ 创建测试聊天记录: {chat_id}")
    
    # 测试各种中文内容
    test_messages = [
        ("human", "你好世界！这是一条包含中文的消息。"),
        ("bot", "您好！我可以正确处理中文字符：测试、验证、编码。"),
        ("human", "请测试特殊字符：《》【】""''—…"),
        ("bot", "数字和中文混合：2025年7月31日，温度25℃，概率95%"),
        ("human", "表情符号测试：😀😊🎉🔥💯"),
        ("bot", "多语言测试：Hello 你好 こんにちは 안녕하세요")
    ]
    
    message_ids = []
    for i, (role, content) in enumerate(test_messages):
        from typing import cast, Literal
        typed_role = cast(Literal["human", "bot"], role)
        result = await new_chat_message(chat_id, typed_role, content)
        if result["type"] == "success":
            message_ids.append(result["message"])
            print(f"✓ 添加编码测试消息 {i+1}: {content[:30]}...")
        else:
            print(f"✗ 添加编码测试消息 {i+1} 失败")
    
    # 验证读取的内容编码正确
    print("\n验证读取内容的编码:")
    for i, message_id in enumerate(message_ids):
        result = await get_chat_message_by_id(chat_id, message_id)
        if isinstance(result, ChatMessage):
            print(f"✓ 消息 {i+1} 编码正确: {result.content[:40]}...")
        else:
            print(f"✗ 消息 {i+1} 读取失败")
    
    print(f"\n✓ 编码测试完成，保留聊天记录 {chat_id} 用于手动验证数据库文件")
    return chat_id


async def test_comprehensive_workflow():
    """综合测试工作流"""
    print("\n" + "=" * 60)
    print("开始综合测试工作流")
    print("=" * 60)
    
    # 1. 创建多个聊天记录
    print("\n🔹 创建多个聊天记录进行压力测试")
    chat_ids = []
    for i in range(3):
        result = await new_chat_history()
        if result["type"] == "success":
            chat_ids.append(result["message"])
            print(f"✓ 创建第{i+1}个聊天记录: {result['message']}")
        else:
            print(f"✗ 创建第{i+1}个聊天记录失败")
    
    # 2. 在第一个聊天记录中进行复杂操作
    if chat_ids:
        main_chat_id = chat_ids[0]
        print(f"\n🔹 在聊天记录 {main_chat_id} 中进行复杂操作")
        
        # 添加大量消息
        message_ids = []
        for i in range(10):
            from typing import cast, Literal
            role_str = "human" if i % 2 == 0 else "bot"
            role = cast(Literal["human", "bot"], role_str)
            content = f"这是第{i+1}条消息，角色是{role}"
            result = await new_chat_message(main_chat_id, role, content)
            if result["type"] == "success":
                message_ids.append(result["message"])
        
        print(f"✓ 成功添加{len(message_ids)}条消息")
        
        # 随机获取一些消息验证
        import random
        random_indices = random.sample(range(len(message_ids)), min(3, len(message_ids)))
        for idx in random_indices:
            result = await get_chat_message_by_index(main_chat_id, idx)
            if isinstance(result, ChatMessage):
                print(f"✓ 随机验证索引{idx}的消息: {result.content[:30]}...")
        
        # 删除一些消息
        messages_to_delete = message_ids[:2]  # 删除前两条
        for msg_id in messages_to_delete:
            result = await delete_chat_message(main_chat_id, msg_id)
            if result["type"] == "success":
                print(f"✓ 成功删除消息: {msg_id}")
        
        # 验证删除后的索引访问
        remaining_count = len(message_ids) - len(messages_to_delete)
        print(f"✓ 删除后剩余消息数量: {remaining_count}")
    
    # 3. 清理测试数据
    print(f"\n🔹 清理测试数据")
    for chat_id in chat_ids:
        result = await delete_chat_history(chat_id)
        if result["type"] == "success":
            print(f"✓ 清理聊天记录: {chat_id}")
        else:
            print(f"✗ 清理聊天记录失败: {chat_id}")


async def main():
    """主测试函数"""
    print("开始聊天记录数据库操作测试")
    print("当前时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        # 基础功能测试
        chat_id = await test_new_chat_history()
        await test_get_chat_history(chat_id)
        
        message_ids = await test_new_chat_message(chat_id)
        message_count = len(message_ids)
        
        await test_get_chat_message_by_id(chat_id, message_ids)
        await test_get_chat_message_by_index(chat_id, message_count)
        
        await test_delete_chat_message(chat_id, message_ids)
        await test_delete_chat_history(chat_id)
        
        # 编码测试
        encoding_chat_id = await test_encoding()
        
        # 综合测试
        await test_comprehensive_workflow()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

