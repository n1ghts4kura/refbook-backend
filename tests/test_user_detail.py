# test_user_detail.py
# 用户详情数据库操作测试

import os
import sys
import asyncio
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from module.database.user_detail import *
from module.database.book import new_book, Book, Chapter, Section, Concept


async def test_new_user_detail():
    """测试创建新用户详情"""
    print("=" * 50)
    print("测试阶段：创建新用户详情")
    print("=" * 50)
    
    # 测试正常创建用户详情
    print("\n🔹 测试创建新用户详情")
    result = await new_user_detail()
    
    if isinstance(result, str) and result:
        print(f"✓ 创建新用户详情成功: {result}")
        return result
    else:
        print(f"✗ 创建新用户详情失败: {result}")
        return None


async def test_get_user_detail(user_detail_id):
    """测试获取用户详情"""
    print("\n" + "=" * 50)
    print("测试阶段：获取用户详情")
    print("=" * 50)
    
    # 测试获取存在的用户详情
    if user_detail_id:
        print(f"\n🔹 测试获取存在的用户详情 (ID: {user_detail_id[:16]}...)")
        result = await get_user_detail(user_detail_id)
        
        if isinstance(result, UserDetail):
            print(f"✓ 成功获取用户详情:")
            print(f"  - 用户详情ID: {result.id[:16]}...")
            print(f"  - 对话聊天记录ID: {result.conversation_chat_history_id[:16]}...")
            print(f"  - 图书聊天记录ID: {result.book_chat_history_id[:16]}...")
            print(f"  - 图书ID列表: {result.book_ids}")
        else:
            print(f"✗ 获取用户详情失败: {result}")
    else:
        print("⚠ 跳过获取存在的用户详情测试（没有有效的用户详情ID）")
    
    # 测试获取不存在的用户详情
    print("\n🔹 测试获取不存在的用户详情")
    fake_id = "nonexistent_user_detail_id_12345"
    result = await get_user_detail(fake_id)
    if isinstance(result, dict) and result["type"] == "error":
        print(f"✓ 正确处理不存在的用户详情: {result['message']}")
    else:
        print(f"✗ 未正确处理不存在的用户详情: {result}")
    
    # 测试空字符串ID
    print("\n🔹 测试空字符串ID")
    result = await get_user_detail("")
    if isinstance(result, dict) and result["type"] == "error":
        print(f"✓ 正确处理空字符串ID: {result['message']}")
    else:
        print(f"✗ 未正确处理空字符串ID: {result}")


async def test_add_book_to_user_detail(user_detail_id):
    """测试向用户详情添加图书ID"""
    print("\n" + "=" * 50)
    print("测试阶段：向用户详情添加图书ID")
    print("=" * 50)
    
    if not user_detail_id:
        print("⚠ 跳过添加图书测试（没有有效的用户详情ID）")
        return []
    
    # 首先创建一些测试图书
    print("\n🔹 创建测试图书")
    test_books = []
    
    for i in range(3):
        concept = Concept(
            introduction=f"测试概念{i+1}介绍",
            explanation=f"测试概念{i+1}解释",
            conclusion=f"测试概念{i+1}结论"
        )
        
        section = Section(
            title=f"测试小节{i+1}",
            introduction=f"测试小节{i+1}介绍",
            concepts=[concept]
        )
        
        chapter = Chapter(
            title=f"测试章节{i+1}",
            introduction=f"测试章节{i+1}介绍",
            sections=[section]
        )
        
        book = Book(
            id="",
            title=f"测试图书{i+1}",
            chapters=[chapter]
        )
        
        book_id = await new_book(book)
        test_books.append(book_id)
        print(f"✓ 创建测试图书{i+1}: {book_id[:16]}...")
    
    # 测试添加图书到用户详情
    added_books = []
    for i, book_id in enumerate(test_books):
        print(f"\n🔹 测试添加图书{i+1}到用户详情")
        result = await add_book_to_user_detail(user_detail_id, book_id)
        
        if result["type"] == "success":
            print(f"✓ 成功添加图书{i+1}到用户详情")
            added_books.append(book_id)
        else:
            print(f"✗ 添加图书{i+1}失败: {result['message']}")
    
    # 测试重复添加同一本图书
    if test_books:
        print(f"\n🔹 测试重复添加图书")
        result = await add_book_to_user_detail(user_detail_id, test_books[0])
        if result["type"] == "error" and "already exists" in result["message"]:
            print(f"✓ 正确处理重复添加图书: {result['message']}")
        else:
            print(f"✗ 未正确处理重复添加图书: {result}")
    
    # 测试添加到不存在的用户详情
    print(f"\n🔹 测试添加图书到不存在的用户详情")
    fake_user_id = "nonexistent_user_detail_id_12345"
    if test_books:
        result = await add_book_to_user_detail(fake_user_id, test_books[0])
        if result["type"] == "error" and "not found" in result["message"]:
            print(f"✓ 正确处理不存在的用户详情: {result['message']}")
        else:
            print(f"✗ 未正确处理不存在的用户详情: {result}")
    
    # 验证图书确实被添加到用户详情中
    if added_books:
        print(f"\n🔹 验证图书是否正确添加到用户详情")
        user_detail = await get_user_detail(user_detail_id)
        if isinstance(user_detail, UserDetail):
            print(f"✓ 用户详情中的图书列表: {len(user_detail.book_ids)} 本图书")
            for i, book_id in enumerate(user_detail.book_ids):
                print(f"  - 图书{i+1}: {book_id[:16]}...")
        else:
            print(f"✗ 无法获取用户详情进行验证: {user_detail}")
    
    return {"added_books": added_books, "all_test_books": test_books}


async def test_delete_book_from_user_detail(user_detail_id, book_info):
    """测试从用户详情删除图书ID"""
    print("\n" + "=" * 50)
    print("测试阶段：从用户详情删除图书ID")
    print("=" * 50)
    
    if not user_detail_id or not book_info or not book_info["added_books"]:
        print("⚠ 跳过删除图书测试（没有有效的数据）")
        return
    
    added_books = book_info["added_books"]
    
    # 测试删除存在的图书
    if added_books:
        book_to_delete = added_books[0]
        print(f"\n🔹 测试删除存在的图书 (ID: {book_to_delete[:16]}...)")
        result = await delete_book_from_user_detail(user_detail_id, book_to_delete)
        
        if result["type"] == "success":
            print(f"✓ 成功删除图书")
            
            # 验证图书确实被删除
            user_detail = await get_user_detail(user_detail_id)
            if isinstance(user_detail, UserDetail):
                if book_to_delete not in user_detail.book_ids:
                    print(f"✓ 验证图书已从用户详情中删除")
                    print(f"  剩余图书数量: {len(user_detail.book_ids)}")
                else:
                    print(f"✗ 图书未从用户详情中删除")
        else:
            print(f"✗ 删除图书失败: {result['message']}")
    
    # 测试删除不存在的图书
    print(f"\n🔹 测试删除不存在的图书")
    fake_book_id = "nonexistent_book_id_12345"
    result = await delete_book_from_user_detail(user_detail_id, fake_book_id)
    if result["type"] == "error" and "not found" in result["message"]:
        print(f"✓ 正确处理删除不存在的图书: {result['message']}")
    else:
        print(f"✗ 未正确处理删除不存在的图书: {result}")
    
    # 测试从不存在的用户详情删除图书
    print(f"\n🔹 测试从不存在的用户详情删除图书")
    fake_user_id = "nonexistent_user_detail_id_12345"
    if added_books:
        result = await delete_book_from_user_detail(fake_user_id, added_books[1] if len(added_books) > 1 else added_books[0])
        if result["type"] == "error" and "not found" in result["message"]:
            print(f"✓ 正确处理不存在的用户详情: {result['message']}")
        else:
            print(f"✗ 未正确处理不存在的用户详情: {result}")


async def test_delete_user_detail(user_detail_id):
    """测试删除用户详情（包括级联删除验证）"""
    print("\n" + "=" * 50)
    print("测试阶段：删除用户详情（级联删除验证）")
    print("=" * 50)
    
    if not user_detail_id:
        print("⚠ 跳过删除用户详情测试（没有有效的用户详情ID）")
        return
    
    # 首先获取用户详情，记录关联的资源ID
    print(f"\n🔹 获取用户详情的关联资源信息")
    user_detail = await get_user_detail(user_detail_id)
    if not isinstance(user_detail, UserDetail):
        print(f"✗ 无法获取用户详情: {user_detail}")
        return
    
    conversation_chat_id = user_detail.conversation_chat_history_id
    book_chat_id = user_detail.book_chat_history_id
    book_ids = user_detail.book_ids.copy()
    
    print(f"  - 对话聊天记录ID: {conversation_chat_id[:16]}...")
    print(f"  - 图书聊天记录ID: {book_chat_id[:16]}...")
    print(f"  - 关联图书数量: {len(book_ids)}")
    
    # 验证关联资源在删除前确实存在
    from module.database.chat_history import get_chat_history
    from module.database.book import get_book
    
    print(f"\n🔹 验证关联资源在删除前的存在状态")
    
    # 验证聊天记录存在
    conv_chat = await get_chat_history(conversation_chat_id)
    book_chat = await get_chat_history(book_chat_id)
    
    conv_exists = not (isinstance(conv_chat, dict) and conv_chat.get("type") == "error")
    book_exists = not (isinstance(book_chat, dict) and book_chat.get("type") == "error")
    
    print(f"  - 对话聊天记录存在: {'✓' if conv_exists else '✗'}")
    print(f"  - 图书聊天记录存在: {'✓' if book_exists else '✗'}")
    
    # 验证图书存在
    existing_books = []
    for book_id in book_ids:
        book = await get_book(book_id)
        book_exists = not (isinstance(book, dict) and book.get("type") == "error")
        if book_exists:
            existing_books.append(book_id)
        print(f"  - 图书 {book_id[:16]}... 存在: {'✓' if book_exists else '✗'}")
    
    # 测试删除存在的用户详情
    print(f"\n🔹 执行用户详情删除操作 (ID: {user_detail_id[:16]}...)")
    result = await delete_user_detail_by_id(user_detail_id)
    
    if result["type"] == "success":
        print(f"✓ 成功删除用户详情: {result['message']}")
        
        # 验证用户详情确实被删除
        verify_result = await get_user_detail(user_detail_id)
        if isinstance(verify_result, dict) and verify_result["type"] == "error":
            print(f"✓ 验证用户详情已被删除")
        else:
            print(f"✗ 用户详情未被正确删除")
        
        # 验证关联的聊天记录是否被级联删除
        print(f"\n🔹 验证关联聊天记录的级联删除")
        
        conv_chat_after = await get_chat_history(conversation_chat_id)
        book_chat_after = await get_chat_history(book_chat_id)
        
        conv_deleted = isinstance(conv_chat_after, dict) and conv_chat_after.get("type") == "error"
        book_deleted = isinstance(book_chat_after, dict) and book_chat_after.get("type") == "error"
        
        print(f"  - 对话聊天记录已删除: {'✓' if conv_deleted else '✗'}")
        print(f"  - 图书聊天记录已删除: {'✓' if book_deleted else '✗'}")
        
        # 验证关联的图书是否被级联删除
        print(f"\n🔹 验证关联图书的级联删除")
        
        books_deleted_count = 0
        for book_id in existing_books:
            book_after = await get_book(book_id)
            book_deleted = isinstance(book_after, dict) and book_after.get("type") == "error"
            if book_deleted:
                books_deleted_count += 1
            print(f"  - 图书 {book_id[:16]}... 已删除: {'✓' if book_deleted else '✗'}")
        
        # 总结级联删除验证结果
        all_chat_deleted = conv_deleted and book_deleted
        all_books_deleted = books_deleted_count == len(existing_books)
        
        if all_chat_deleted and all_books_deleted:
            print(f"\n🎉 级联删除验证成功：所有关联资源都已被正确删除")
        else:
            print(f"\n❌ 级联删除验证失败：部分关联资源未被删除")
            print(f"    聊天记录删除状态: {all_chat_deleted}")
            print(f"    图书删除状态: {all_books_deleted} ({books_deleted_count}/{len(existing_books)})")
    else:
        print(f"✗ 删除用户详情失败: {result['message']}")
    
    # 测试删除不存在的用户详情
    print(f"\n🔹 测试删除不存在的用户详情")
    fake_id = "nonexistent_user_detail_id_12345"
    result = await delete_user_detail_by_id(fake_id)
    if result["type"] == "error" and "not found" in result["message"]:
        print(f"✓ 正确处理删除不存在的用户详情: {result['message']}")
    else:
        print(f"✗ 未正确处理删除不存在的用户详情: {result}")


async def test_concurrent_operations():
    """测试并发操作"""
    print("\n" + "=" * 50)
    print("测试阶段：并发操作压力测试")
    print("=" * 50)
    
    print("\n🔹 并发创建多个用户详情")
    
    async def create_user_detail_task(task_id):
        result = await new_user_detail()
        return task_id, result
    
    # 创建10个并发任务
    tasks = [create_user_detail_task(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    
    created_user_ids = []
    for task_id, result in results:
        if isinstance(result, str) and result:
            print(f"✓ 任务{task_id}: 成功创建用户详情 {result[:16]}...")
            created_user_ids.append(result)
        else:
            print(f"✗ 任务{task_id}: 创建失败 {result}")
    
    print(f"\n总计成功创建 {len(created_user_ids)} 个用户详情")
    
    # 清理测试数据
    print(f"\n🔹 清理并发测试数据")
    for i, user_id in enumerate(created_user_ids):
        result = await delete_user_detail_by_id(user_id)
        if result["type"] == "success":
            print(f"✓ 清理用户详情{i+1}: 成功")
        else:
            print(f"✗ 清理用户详情{i+1}: 失败")


async def test_edge_cases():
    """测试边界情况"""
    print("\n" + "=" * 50)
    print("测试阶段：边界情况测试")
    print("=" * 50)
    
    # 测试空字符串作为参数
    print("\n🔹 测试空字符串参数")
    
    # 测试获取空字符串ID的用户详情
    result = await get_user_detail("")
    if isinstance(result, dict) and result["type"] == "error":
        print("✓ 正确处理空字符串用户详情ID")
    else:
        print("✗ 未正确处理空字符串用户详情ID")
    
    # 测试添加空字符串图书ID
    user_id = await new_user_detail()
    if isinstance(user_id, str):
        result = await add_book_to_user_detail(user_id, "")
        print(f"   添加空字符串图书ID结果: {result}")
        
        # 清理测试数据
        await delete_user_detail_by_id(user_id)
    
    # 测试None值（这会引发异常，需要捕获）
    print("\n🔹 测试None参数")
    try:
        result = await get_user_detail(None)  # type: ignore
        print(f"   None参数测试结果: {result}")
    except Exception as e:
        print(f"✓ 正确抛出异常: {type(e).__name__}: {e}")


async def test_data_integrity():
    """测试数据完整性"""
    print("\n" + "=" * 50)
    print("测试阶段：数据完整性测试")
    print("=" * 50)
    
    print("\n🔹 测试用户详情数据结构完整性")
    
    # 创建用户详情并验证所有字段
    user_id = await new_user_detail()
    if isinstance(user_id, str):
        user_detail = await get_user_detail(user_id)
        
        if isinstance(user_detail, UserDetail):
            print("✓ 用户详情数据结构验证:")
            print(f"  - ID存在且非空: {bool(user_detail.id)}")
            print(f"  - 对话聊天记录ID存在且非空: {bool(user_detail.conversation_chat_history_id)}")
            print(f"  - 图书聊天记录ID存在且非空: {bool(user_detail.book_chat_history_id)}")
            print(f"  - 图书ID列表已初始化: {user_detail.book_ids == []}")
            
            # 验证聊天记录ID确实存在（通过尝试访问）
            from module.database.chat_history import get_chat_history
            
            conv_result = await get_chat_history(user_detail.conversation_chat_history_id)
            book_result = await get_chat_history(user_detail.book_chat_history_id)
            
            print(f"  - 对话聊天记录有效: {not isinstance(conv_result, dict) or conv_result.get('type') != 'error'}")
            print(f"  - 图书聊天记录有效: {not isinstance(book_result, dict) or book_result.get('type') != 'error'}")
            
        # 清理测试数据
        await delete_user_detail_by_id(user_id)
    
    print("\n🔹 测试图书列表操作的完整性")
    
    # 测试多次添加和删除操作
    user_id = await new_user_detail()
    if isinstance(user_id, str):
        # 创建测试图书
        test_book = Book(id="", title="完整性测试图书", chapters=[])
        book_id = await new_book(test_book)
        
        # 多次添加和删除测试
        operations = ["add", "delete", "add", "delete", "add"]
        for i, operation in enumerate(operations):
            if operation == "add":
                result = await add_book_to_user_detail(user_id, book_id)
                expected = "success" if i == 0 or i == 2 or i == 4 else "error"
            else:  # delete
                result = await delete_book_from_user_detail(user_id, book_id)
                expected = "success" if i == 1 or i == 3 else "error"
            
            actual = result["type"]
            print(f"  操作{i+1} ({operation}): {'✓' if actual == expected else '✗'} 期望{expected}, 实际{actual}")
        
        # 清理测试数据
        await delete_user_detail_by_id(user_id)


async def test_comprehensive_workflow():
    """综合测试工作流"""
    print("\n" + "=" * 60)
    print("开始综合测试工作流")
    print("=" * 60)
    
    workflow_data = {}
    
    try:
        # 1. 创建用户详情
        print("\n🔹 步骤1: 创建用户详情")
        user_id = await new_user_detail()
        if isinstance(user_id, str):
            print(f"✓ 用户详情创建成功: {user_id[:16]}...")
            workflow_data["user_id"] = user_id
        else:
            print(f"✗ 用户详情创建失败，终止工作流")
            return
        
        # 2. 验证用户详情
        print("\n🔹 步骤2: 验证用户详情")
        user_detail = await get_user_detail(user_id)
        if isinstance(user_detail, UserDetail):
            print("✓ 用户详情验证成功")
            workflow_data["user_detail"] = user_detail
        else:
            print("✗ 用户详情验证失败")
            return
        
        # 3. 创建并添加图书
        print("\n🔹 步骤3: 创建并添加图书")
        book_ids = []
        for i in range(5):
            book = Book(id="", title=f"工作流测试图书{i+1}", chapters=[])
            book_id = await new_book(book)
            book_ids.append(book_id)
            
            add_result = await add_book_to_user_detail(user_id, book_id)
            if add_result["type"] == "success":
                print(f"✓ 图书{i+1}添加成功")
            else:
                print(f"✗ 图书{i+1}添加失败")
        
        workflow_data["book_ids"] = book_ids
        
        # 4. 验证图书列表
        print("\n🔹 步骤4: 验证图书列表")
        updated_user_detail = await get_user_detail(user_id)
        if isinstance(updated_user_detail, UserDetail):
            expected_count = len(book_ids)
            actual_count = len(updated_user_detail.book_ids)
            if actual_count == expected_count:
                print(f"✓ 图书列表验证成功: {actual_count}/{expected_count}")
            else:
                print(f"✗ 图书列表验证失败: {actual_count}/{expected_count}")
        
        # 5. 删除部分图书
        print("\n🔹 步骤5: 删除部分图书")
        books_to_delete = book_ids[:2]  # 删除前两本书
        for i, book_id in enumerate(books_to_delete):
            delete_result = await delete_book_from_user_detail(user_id, book_id)
            if delete_result["type"] == "success":
                print(f"✓ 图书{i+1}删除成功")
            else:
                print(f"✗ 图书{i+1}删除失败")
        
        # 6. 最终验证
        print("\n🔹 步骤6: 最终验证")
        final_user_detail = await get_user_detail(user_id)
        if isinstance(final_user_detail, UserDetail):
            expected_final_count = len(book_ids) - len(books_to_delete)
            actual_final_count = len(final_user_detail.book_ids)
            if actual_final_count == expected_final_count:
                print(f"✓ 最终验证成功: {actual_final_count}/{expected_final_count}")
            else:
                print(f"✗ 最终验证失败: {actual_final_count}/{expected_final_count}")
        
        print("\n🎉 综合工作流测试完成")
        
    except Exception as e:
        print(f"\n💥 工作流测试中发生异常: {type(e).__name__}: {e}")
    
    finally:
        # 清理数据
        print(f"\n🔹 清理工作流测试数据")
        if "user_id" in workflow_data:
            result = await delete_user_detail_by_id(workflow_data["user_id"])
            if result["type"] == "success":
                print("✓ 用户详情清理成功")
            else:
                print("✗ 用户详情清理失败")


async def main():
    """主测试函数"""
    print("🚀 开始用户详情数据库操作测试")
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. 基本功能测试
        print("\n" + "🔥" * 20 + " 基本功能测试 " + "🔥" * 20)
        
        # 测试创建用户详情
        user_detail_id = await test_new_user_detail()
        
        # 测试获取用户详情
        await test_get_user_detail(user_detail_id)
        
        # 测试添加图书到用户详情
        book_info = await test_add_book_to_user_detail(user_detail_id)
        
        # 测试从用户详情删除图书
        await test_delete_book_from_user_detail(user_detail_id, book_info)
        
        # 测试删除用户详情
        await test_delete_user_detail(user_detail_id)
        
        # 2. 压力测试
        print("\n" + "💪" * 20 + " 压力测试 " + "💪" * 20)
        await test_concurrent_operations()
        
        # 3. 边界情况测试
        print("\n" + "🎯" * 20 + " 边界情况测试 " + "🎯" * 20)
        await test_edge_cases()
        
        # 4. 数据完整性测试
        print("\n" + "🔐" * 20 + " 数据完整性测试 " + "🔐" * 20)
        await test_data_integrity()
        
        # 5. 综合工作流测试
        print("\n" + "🌟" * 20 + " 综合工作流测试 " + "🌟" * 20)
        await test_comprehensive_workflow()
        
        print("\n" + "🎊" * 60)
        print("🎊" + " " * 18 + "所有测试完成！" + " " * 18 + "🎊")
        print("🎊" * 60)
        
    except Exception as e:
        print(f"\n💥 测试过程中发生未捕获的异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
