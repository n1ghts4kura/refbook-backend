# chat_history.py
# 数据库 聊天记录部分 定义与操作
#

import time
import asyncio
from pydantic import BaseModel
from pydantic.fields import Field
from typing import * # type: ignore

from .general import get_chat_history_database, Query

def _get_current_id(sign: int) -> str:
    """
    获取当前时间戳作为ID
    """
    return f"this_is_salt_{int(time.time() * 1000)}_chat_history_{sign}"

class ChatMessage(BaseModel):
    """
    单条聊天信息
    """

    id: str = Field(..., description="消息ID")

    role: Literal["human", "bot"] = Field(..., description="消息角色")

    content: str = Field(..., description="消息内容")

class ChatHistory(BaseModel):
    """
    聊天记录模型
    """
    
    id: str = Field(..., description="聊天记录ID")

    messages: List[ChatMessage] = Field(default=[], description="聊天消息列表")

# ---

_new_chat_history_lock = asyncio.Lock()

async def new_chat_history() -> Dict[str, Any]:
    """
    创建新的聊天记录

    Returns:
        Dict[str, Any]: 创建的聊天记录ID

        **成功**: "type": "success", "message": " _**<具体id>**_ "},

        **错误**: ？？不知道哦.
    """

    result = {
        "type": "error",
        "message": "",
    }

    async with _new_chat_history_lock:
        db = get_chat_history_database()
        new_id = _get_current_id(0) # Remember to change the sign for different types of ids
        db.insert(ChatHistory(
            id = new_id,
            messages = []
        ).model_dump())

    result["type"] = "success"
    result["message"] = new_id

    return result

_get_chat_history_lock = asyncio.Lock()

async def get_chat_history(chat_history_id: str) -> Union[ChatHistory, Dict[str, str]]:
    """
    获取指定ID的聊天记录

    Args:
        chat_history_id (str): 聊天记录ID

    Returns:
        Union[ChatHistory, Dict[str, str]]: 聊天记录或错误信息

        **成功**: ChatHistory 对象

        **错误**: "type": "error", "message": "<...>

    """

    result = {
        "type": "error",
        "message": "",
    }

    async with _get_chat_history_lock:
        db = get_chat_history_database()
        chat_history = db.search(Query().id == chat_history_id)

        if not chat_history or len(chat_history) == 0:
            result["message"] = "Chat history not found"
            return result

        if len(chat_history) > 1:
            result["message"] = "Multiple chat histories found, please check the database"
            return result
        
        chat_history = chat_history[0]
        try:
            assert isinstance(chat_history, dict), "Chat history must be a dictionary"
            chat_history = ChatHistory(**chat_history)
        except AssertionError as e:
            result["message"] = f"Chat history is not valid: {e}"
            return result

    return chat_history

_new_chat_message_lock = asyncio.Lock()

async def new_chat_message(
    chat_history_id: str,
    role: Literal["human", "bot"],
    content: str,
) -> Dict[str, Any]:
    """
    添加新的聊天消息到指定的聊天记录中
    
    Args:
        chat_history_id (str): 聊天记录ID
        role (Literal["human", "bot"]): 消息角色
        content (str): 消息内容

    Returns:
        Dict[str, Any]: 添加的结果

        **成功**: "type": "success", "message": " _**<具体id>**_ "},

        **错误**: "type": "error", "message": "<...>"} if failed
    """

    result = {
        "type": "error",
        "message": "",
    }

    async with _new_chat_message_lock:
        db = get_chat_history_database()
        chat_history = db.search(Query().id == chat_history_id)

        if not chat_history or len(chat_history) == 0:
            result["message"] = "Chat history not found"
            return result

        if len(chat_history) > 1:
            result["message"] = "Multiple chat histories found, please check the database"
            return result

        chat_history = chat_history[0]
        current_messages: List[ChatMessage] = chat_history.get("messages", [0])
        try:
            assert all( isinstance(msg, ChatMessage) for msg in current_messages ), \
                "Chat messages must be of type ChatMessage"
        except AssertionError as e:
            result["message"] = f"Chat messages are not valid: {e}"
            return result

        new_id = _get_current_id(1) # Remember to change the sign for different types of ids
        current_messages.append(ChatMessage(
            id=new_id,
            role=role,
            content=content
        ))

        db.update({ "messages": current_messages }, Query().id == chat_history_id)

        result["type"] = "success"
        result["message"] = new_id

    return result

_get_chat_message_by_id_lock = asyncio.Lock()

async def get_chat_message_by_id(chat_history_id: str, message_id: str) -> Union[ChatMessage, Dict[str, str]]:
    """
    获取指定聊天记录中的指定消息

    Args:
        chat_history_id (str): 聊天记录ID
        message_id (str): 消息ID

    Returns:
        Union[ChatMessage, Dict[str, str]]: 消息或错误信息

        **成功**: ChatMessage 对象

        **错误**: "type": "error", "message": "<...>"
    """

    async with _get_chat_message_by_id_lock:
        db = get_chat_history_database()
        chat_history = db.search(Query().id == chat_history_id)

        if not chat_history or len(chat_history) == 0:
            return {"type": "error", "message": "Chat history not found"}

        if len(chat_history) > 1:
            return {"type": "error", "message": "Multiple chat histories found, please check the database"}

        chat_history = chat_history[0]
        messages = chat_history.get("messages", [])

        for message in messages:
            if message.id == message_id:
                return ChatMessage(**message)

        return {"type": "error", "message": "Message not found"}

_get_chat_message_by_index_lock = asyncio.Lock()

async def get_chat_message_by_index(chat_history_id: str, index: int) -> Union[ChatMessage, Dict[str, str]]:
    """
    获取指定聊天记录中的指定索引的消息

    Args:
        chat_history_id (str): 聊天记录ID
        index (int): 消息索引

    Returns:
        Union[ChatMessage, Dict[str, str]]: 消息或错误信息

        **成功**: ChatMessage 对象

        **错误**: "type": "error", "message": "<...>"
    """

    async with _get_chat_message_by_index_lock:
        db = get_chat_history_database()
        chat_history = db.search(Query().id == chat_history_id)

        if not chat_history or len(chat_history) == 0:
            return {"type": "error", "message": "Chat history not found"}

        if len(chat_history) > 1:
            return {"type": "error", "message": "Multiple chat histories found, please check the database"}

        chat_history = chat_history[0]
        messages = chat_history.get("messages", [])

        if index < 0 or index >= len(messages):
            return {"type": "error", "message": "Index out of range"}

        return ChatMessage(**messages[index])

_delete_chat_history_lock = asyncio.Lock()

async def delete_chat_history(chat_history_id: str) -> Dict[str, str]:
    """
    删除指定ID的聊天记录

    Args:
        chat_history_id (str): 聊天记录ID

    Returns:
        Dict[str, str]: 删除结果

        **成功**: "type": "success", "message": ""},

        **错误**: "type": "error", "message": "<...>"
    """

    result = {
        "type": "error",
        "message": "",
    }

    async with _delete_chat_history_lock:
        db = get_chat_history_database()
        chat_history = db.search(Query().id == chat_history_id)

        if not chat_history or len(chat_history) == 0:
            result["message"] = "Chat history not found"
            return result

        db.remove(Query().id == chat_history_id)
        
        result["type"] = "success"

    return result

_delete_chat_message_lock = asyncio.Lock()

async def delete_chat_message(chat_history_id: str, message_id: str) -> Dict[str, str]:
    """
    删除指定聊天记录中的指定消息

    Args:
        chat_history_id (str): 聊天记录ID
        message_id (str): 消息ID

    Returns:
        Dict[str, str]: 删除结果

        **成功**: "type": "success", "message": ""},

        **错误**: "type": "error", "message": "<...>"
    """

    result = {
        "type": "error",
        "message": "",
    }

    async with _delete_chat_message_lock:
        db = get_chat_history_database()
        chat_history = db.search(Query().id == chat_history_id)

        if not chat_history or len(chat_history) == 0:
            result["message"] = "Chat history not found"
            return result

        if len(chat_history) > 1:
            result["message"] = "Multiple chat histories found, please check the database"
            return result

        chat_history = chat_history[0]
        messages = chat_history.get("messages", [])

        for i, message in enumerate(messages):
            if message.id == message_id:
                del messages[i]
                db.update({"messages": messages}, Query().id == chat_history_id)
                result["type"] = "success"
                return result

        result["message"] = "Message not found"
    
    return result

__all__ = [
    "ChatMessage",
    "ChatHistory",
    "new_chat_history",
    "get_chat_history",
    "new_chat_message",
    "get_chat_message_by_id",
    "get_chat_message_by_index",
    "delete_chat_history",
    "delete_chat_message"
]
