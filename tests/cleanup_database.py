# cleanup_database.py
# 清理数据库中的垃圾数据

import os
import sys
import asyncio
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from module.database.general import (
    get_user_database, 
    get_user_detail_database, 
    get_book_database, 
    get_chat_history_database
)


def backup_database_files():
    """备份当前数据库文件"""
    import shutil
    from datetime import datetime
    
    backup_dir = os.path.join(os.path.dirname(__file__), '..', 'database_backup')
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    db_files = [
        'db_user_v1.json',
        'db_user_detail_v1.json', 
        'db_book_v1.json',
        'db_chat_history_v1.json'
    ]
    
    for db_file in db_files:
        src_path = os.path.join(os.path.dirname(__file__), '..', 'database_file', db_file)
        if os.path.exists(src_path):
            backup_path = os.path.join(backup_dir, f"{timestamp}_{db_file}")
            shutil.copy2(src_path, backup_path)
            print(f"✓ 备份: {db_file} -> {backup_path}")


def analyze_database_status():
    """分析当前数据库状态"""
    print("=" * 60)
    print("数据库状态分析")
    print("=" * 60)
    
    # 分析用户数据库
    user_db = get_user_database()
    user_count = len(user_db.all())
    print(f"用户数据库: {user_count} 条记录")
    
    # 分析用户详情数据库
    user_detail_db = get_user_detail_database()
    user_detail_count = len(user_detail_db.all())
    print(f"用户详情数据库: {user_detail_count} 条记录")
    
    # 分析图书数据库
    book_db = get_book_database()
    book_records = book_db.all()
    book_count = len(book_records)
    print(f"图书数据库: {book_count} 条记录")
    
    # 分析聊天记录数据库
    chat_db = get_chat_history_database()
    chat_records = chat_db.all()
    chat_count = len(chat_records)
    empty_chat_count = sum(1 for record in chat_records if not record.get('messages', []))
    print(f"聊天记录数据库: {chat_count} 条记录 (其中 {empty_chat_count} 条为空)")
    
    return {
        'users': user_count,
        'user_details': user_detail_count, 
        'books': book_count,
        'chats': chat_count,
        'empty_chats': empty_chat_count
    }


def identify_orphaned_data():
    """识别孤儿数据"""
    print("\n" + "=" * 60)
    print("识别孤儿数据")
    print("=" * 60)
    
    # 获取所有用户详情中引用的聊天记录ID和图书ID
    user_detail_db = get_user_detail_database()
    user_details = user_detail_db.all()
    
    referenced_chat_ids = set()
    referenced_book_ids = set()
    
    for user_detail in user_details:
        if 'conversation_chat_history_id' in user_detail:
            referenced_chat_ids.add(user_detail['conversation_chat_history_id'])
        if 'book_chat_history_id' in user_detail:
            referenced_chat_ids.add(user_detail['book_chat_history_id'])
        if 'book_ids' in user_detail:
            referenced_book_ids.update(user_detail['book_ids'])
    
    # 获取所有聊天记录ID
    chat_db = get_chat_history_database()
    all_chat_records = chat_db.all()
    all_chat_ids = {record['id'] for record in all_chat_records}
    
    # 获取所有图书ID
    book_db = get_book_database()
    all_book_records = book_db.all()
    all_book_ids = {record['id'] for record in all_book_records}
    
    # 找出孤儿数据
    orphaned_chat_ids = all_chat_ids - referenced_chat_ids
    orphaned_book_ids = all_book_ids - referenced_book_ids
    
    print(f"孤儿聊天记录: {len(orphaned_chat_ids)} 条")
    print(f"孤儿图书记录: {len(orphaned_book_ids)} 条")
    
    return {
        'orphaned_chats': orphaned_chat_ids,
        'orphaned_books': orphaned_book_ids
    }


def clean_orphaned_data(orphaned_data, confirm=True):
    """清理孤儿数据"""
    if confirm:
        print(f"\n准备清理:")
        print(f"- {len(orphaned_data['orphaned_chats'])} 条孤儿聊天记录")
        print(f"- {len(orphaned_data['orphaned_books'])} 条孤儿图书记录")
        
        response = input("\n确定要清理这些数据吗？(y/N): ")
        if response.lower() != 'y':
            print("取消清理操作")
            return
    
    print("\n开始清理孤儿数据...")
    
    # 清理孤儿聊天记录
    chat_db = get_chat_history_database()
    cleaned_chats = 0
    for chat_id in orphaned_data['orphaned_chats']:
        from module.database.general import Query
        result = chat_db.remove(Query().id == chat_id)
        if result:
            cleaned_chats += 1
    
    print(f"✓ 清理了 {cleaned_chats} 条孤儿聊天记录")
    
    # 清理孤儿图书记录
    book_db = get_book_database()
    cleaned_books = 0
    for book_id in orphaned_data['orphaned_books']:
        from module.database.general import Query
        result = book_db.remove(Query().id == book_id)
        if result:
            cleaned_books += 1
    
    print(f"✓ 清理了 {cleaned_books} 条孤儿图书记录")


async def test_cascade_delete():
    """测试级联删除功能"""
    print("\n" + "=" * 60)
    print("测试级联删除功能")
    print("=" * 60)
    
    from module.database.user_detail import new_user_detail, delete_user_detail
    from module.database.book import new_book, Book
    from module.database.user_detail import add_book_to_user_detail
    
    # 创建测试用户详情
    print("🔹 创建测试用户详情...")
    user_id = await new_user_detail()
    if isinstance(user_id, dict):
        print(f"✗ 创建失败: {user_id}")
        return
    
    print(f"✓ 创建成功: {user_id[:16]}...")
    
    # 创建测试图书并添加到用户详情
    print("🔹 创建测试图书...")
    test_book = Book(id="", title="级联删除测试图书", chapters=[])
    book_id = await new_book(test_book)
    print(f"✓ 图书创建成功: {book_id[:16]}...")
    
    # 添加图书到用户详情
    add_result = await add_book_to_user_detail(user_id, book_id)
    if add_result["type"] == "success":
        print("✓ 图书添加到用户详情成功")
    else:
        print(f"✗ 图书添加失败: {add_result}")
    
    # 记录删除前的状态
    print("\n🔹 删除前状态:")
    status_before = analyze_database_status()
    
    # 执行级联删除
    print("\n🔹 执行级联删除...")
    delete_result = await delete_user_detail(user_id)
    if delete_result["type"] == "success":
        print("✓ 级联删除成功")
    else:
        print(f"✗ 级联删除失败: {delete_result}")
    
    # 记录删除后的状态
    print("\n🔹 删除后状态:")
    status_after = analyze_database_status()
    
    # 比较状态变化
    print("\n🔹 状态变化:")
    print(f"用户详情: {status_before['user_details']} -> {status_after['user_details']} ({status_after['user_details'] - status_before['user_details']})")
    print(f"图书: {status_before['books']} -> {status_after['books']} ({status_after['books'] - status_before['books']})")
    print(f"聊天记录: {status_before['chats']} -> {status_after['chats']} ({status_after['chats'] - status_before['chats']})")


async def main():
    """主函数"""
    print("🚀 数据库清理和级联删除测试工具")
    print("="*60)
    
    # 1. 备份数据库文件
    print("1. 备份当前数据库文件...")
    backup_database_files()
    
    # 2. 分析当前状态
    print("\n2. 分析当前数据库状态...")
    current_status = analyze_database_status()
    
    # 3. 识别孤儿数据
    print("\n3. 识别孤儿数据...")
    orphaned_data = identify_orphaned_data()
    
    # 4. 清理孤儿数据
    if orphaned_data['orphaned_chats'] or orphaned_data['orphaned_books']:
        print("\n4. 清理孤儿数据...")
        clean_orphaned_data(orphaned_data, confirm=True)
        
        print("\n清理后状态:")
        analyze_database_status()
    else:
        print("\n4. 没有发现孤儿数据，跳过清理")
    
    # 5. 测试级联删除功能
    print("\n5. 测试级联删除功能...")
    await test_cascade_delete()
    
    print("\n🎉 所有操作完成！")


if __name__ == "__main__":
    asyncio.run(main())
