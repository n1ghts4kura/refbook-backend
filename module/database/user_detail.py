# user_detail.py
# 数据库 用户详情部分 定义与操作
#

import time
import hashlib
import asyncio
from pydantic import BaseModel
from pydantic.fields import Field
from typing import * # type: ignore

from .general import get_user_detail_database, Query
from .chat_history import new_chat_history

def _get_current_id(sign: int) -> str:
    """
    获取当前时间戳作为ID
    """
    return hashlib.sha256(f"this_is_salt_{int(time.time() * 1000)}_user_detail_{sign}".encode()).hexdigest()

class UserDetail(BaseModel):
    """
    用户详情模型
    """

    id: str = Field(..., description="用户详情ID")

    conversation_chat_history_id: str = Field(..., description="与机器人对话的聊天记录ID")

    book_chat_history_id: str = Field(..., description="与生成图书相关的聊天记录ID")

    book_ids: List[str] = Field(default=[], description="用户的图书ID列表")

    # 用户画像收集
    # user_portrait: Dict[str, Any] = Field(default={}, description="用户画像")

async def _new_conversation_chat_history() -> Union[str, bool]:
    """
    创建新的对话聊天记录

    Returns:
        str: 新的对话聊天记录ID
    """
    result = await new_chat_history()

    if not result or result.get("type") != "success":
        return False

    return result.get("message", "") # the empty string should not be returned, asserted.

async def _new_book_chat_history() -> Union[str, bool]:
    """
    创建新的图书相关聊天记录

    Returns:
        str: 新的图书相关聊天记录ID
    """
    result = await new_chat_history()

    if not result or result.get("type") != "success":
        return False

    return result.get("message", "") # the empty string should not be returned, asserted.

_new_user_detail_lock = asyncio.Lock()

async def new_user_detail() -> Union[str, Dict[str, str]]:
    """
    创建新的用户详情

    Returns:
        Union[UserDetail, Dict[str, str]]: 新的用户详情对象ID或错误信息
    """
    
    async with _new_user_detail_lock:
        conversation_chat_history_id = await _new_conversation_chat_history()
        if conversation_chat_history_id == False:
            return {"type": "error", "message": "Failed to create conversation chat history"}

        book_chat_history_id = await _new_book_chat_history()
        if book_chat_history_id == False:
            return {"type": "error", "message": "Failed to create book chat history"}

        # the assertions below should not fail, as we just created the chat histories.
        # the assertions are just for safety in type checking.
        assert isinstance(conversation_chat_history_id, str) and conversation_chat_history_id != "", "Conversation chat history ID should not be empty"
        assert isinstance(book_chat_history_id, str) and book_chat_history_id != "", "Book chat history ID should not be empty"

        new_user_detail = UserDetail(
            id=_get_current_id(0),
            conversation_chat_history_id=conversation_chat_history_id,
            book_chat_history_id=book_chat_history_id,
            book_ids=[]
        )

        db = get_user_detail_database()
        db.insert(new_user_detail.model_dump())

    return new_user_detail.id

_get_user_detail_lock = asyncio.Lock()

async def get_user_detail(user_detail_id: str) -> Union[UserDetail, Dict[str, str]]:
    """
    获取指定ID的用户详情

    Args:
        user_detail_id (str): 用户详情ID

    Returns:
        Union[UserDetail, Dict[str, str]]: 用户详情对象或错误信息
    """
    
    async with _get_user_detail_lock:
        db = get_user_detail_database()
        user_detail_data = db.get(Query().id == user_detail_id)

        if not user_detail_data:
            return {"type": "error", "message": "User detail not found"}

        # assert if user_detail_data is suitable for UserDetail model
        # return UserDetail(**user_detail_data) # type: ignore
        return UserDetail.model_validate(user_detail_data)

_delete_user_detail_lock = asyncio.Lock()

async def delete_user_detail(user_detail_id: str) -> Dict[str, str]:
    """
    删除指定ID的用户详情（级联删除关联的聊天记录和图书）

    Args:
        user_detail_id (str): 用户详情ID

    Returns:
        Dict[str, str]: 删除结果信息
    """
    
    async with _delete_user_detail_lock:
        db = get_user_detail_database()
        
        # 首先获取用户详情，确保存在并获取关联的资源ID
        user_detail_data = db.get(Query().id == user_detail_id)
        if not user_detail_data:
            return {"type": "error", "message": "User detail not found"}
        
        user_detail = UserDetail(**user_detail_data)  # type: ignore
        
        # 导入必要的删除函数
        from .chat_history import delete_chat_history
        from .book import delete_book
        
        # 删除关联的聊天记录
        try:
            await delete_chat_history(user_detail.conversation_chat_history_id)
            await delete_chat_history(user_detail.book_chat_history_id)
        except Exception as e:
            # 聊天记录删除失败不应该阻止用户详情删除，只记录错误
            print(f"Warning: Failed to delete chat histories: {e}")
        
        # 删除关联的图书
        for book_id in user_detail.book_ids:
            try:
                await delete_book(book_id)
            except Exception as e:
                # 图书删除失败不应该阻止用户详情删除，只记录错误
                print(f"Warning: Failed to delete book {book_id}: {e}")
        
        # 最后删除用户详情本身
        result = db.remove(Query().id == user_detail_id)
        if len(result) == 0:
            return {"type": "error", "message": "User detail not found"}

    return {"type": "success", "message": "User detail deleted successfully"}

_add_book_lock = asyncio.Lock()

async def add_book_to_user_detail(user_detail_id: str, book_id: str) -> Dict[str, str]:
    """
    将图书ID添加到用户详情中

    Args:
        user_detail_id (str): 用户详情ID
        book_id (str): 图书ID

    Returns:
        Dict[str, str]: 添加结果信息

        **成功**: "type": "success", "message": ""},

        **错误**: "type": "error", "message": "<...>"
    """
    
    result = {
        "type": "error",
        "message": "",
    }

    # 验证输入参数
    if not book_id or not book_id.strip():
        result["message"] = "Book ID cannot be empty"
        return result

    async with _add_book_lock:
        db = get_user_detail_database()
        user_detail_data = db.get(Query().id == user_detail_id)

        if not user_detail_data:
            result["message"] = "User detail not found"
            return result

        user_detail = UserDetail(**user_detail_data)  # type: ignore

        if book_id in user_detail.book_ids:
            result["message"] = "Book already exists in user detail"
            return result

        user_detail.book_ids.append(book_id)
        db.update(user_detail.model_dump(), Query().id == user_detail_id)

        result["type"] = "success"

    return result

_delete_book_from_user_detail_lock = asyncio.Lock()

async def delete_book_from_user_detail(user_detail_id: str, book_id: str) -> Dict[str, str]:
    """
    从用户详情中删除图书ID（同时物理删除图书，因为每本书只属于一个用户）

    Args:
        user_detail_id (str): 用户详情ID
        book_id (str): 图书ID

    Returns:
        Dict[str, str]: 删除结果信息

        **成功**: "type": "success", "message": ""},

        **错误**: "type": "error", "message": "<...>"
    """
    
    result = {
        "type": "error",
        "message": "",
    }

    async with _delete_book_from_user_detail_lock:
        db = get_user_detail_database()
        user_detail_data = db.get(Query().id == user_detail_id)

        if not user_detail_data:
            result["message"] = "User detail not found"
            return result

        user_detail = UserDetail(**user_detail_data)  # type: ignore

        if book_id not in user_detail.book_ids:
            result["message"] = "Book not found in user detail"
            return result

        # 先从用户详情中移除图书引用
        user_detail.book_ids.remove(book_id)
        db.update(user_detail.model_dump(), Query().id == user_detail_id)

        # 然后物理删除图书（因为每本书只属于一个用户）
        try:
            from .book import delete_book
            delete_result = await delete_book(book_id)
            if isinstance(delete_result, dict) and delete_result.get("type") == "error":
                # 图书删除失败，但用户详情已经更新，记录警告但返回成功
                print(f"Warning: Book {book_id} removed from user detail but physical deletion failed: {delete_result.get('message', 'Unknown error')}")
        except Exception as e:
            # 图书删除异常，记录警告但返回成功（用户详情已经更新）
            print(f"Warning: Book {book_id} removed from user detail but physical deletion failed with exception: {e}")

        result["type"] = "success"
        result["message"] = "Book removed from user detail and deleted successfully"

    return result
