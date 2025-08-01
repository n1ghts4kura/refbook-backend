# user.py
# 数据库 用户部分 定义与操作
#

import time
import hashlib
import asyncio
import uuid
import threading
from pydantic import BaseModel
from pydantic.fields import Field
from typing import *  # type: ignore

from .general import get_user_database, Query
from .user_detail import new_user_detail, delete_user_detail_by_id

# 使用线程锁确保ID生成的线程安全
_id_generation_lock = threading.Lock()

def _get_current_id(sign: int) -> str:
    """
    生成唯一ID，结合时间戳和UUID确保唯一性
    """
    with _id_generation_lock:
        timestamp = int(time.time() * 1000000)  # 微秒级时间戳
        unique_id = str(uuid.uuid4())
        return hashlib.sha256(f"salt_{timestamp}_{unique_id}_{sign}_user".encode()).hexdigest()

class User(BaseModel):
    """
    用户模型
    """

    id: str = Field(..., description="用户ID")

    username: str = Field(..., description="用户名")
    
    password_hash: str = Field(..., description="密码哈希")

    user_detail_id: str = Field(..., description="用户详情ID")

# ---

_new_user_lock = asyncio.Lock()

async def new_user(username: str, password_hash: str) -> Union[str, Dict[str, str]]:
    """
    创建新的用户

    Args:
        username (str): 用户名
        password_hash (str): 密码哈希

    Returns:
        str: 新的用户ID 或 Dict[str, str]: 错误信息
    """
    # 输入验证
    if not username or not username.strip():
        return {"type": "error", "message": "Username cannot be empty"}
    
    if not password_hash or not password_hash.strip():
        return {"type": "error", "message": "Password hash cannot be empty"}
    
    # 去除用户名首尾空格
    username = username.strip()
    
    async with _new_user_lock:
        # get new_user_detail's id
        new_user_detail_id = await new_user_detail()

        if not isinstance(new_user_detail_id, str):
            return {"type": "error", "message": "Failed to create user detail"}

        user_id = _get_current_id(1)
        user = User(id=user_id, username=username, password_hash=password_hash, user_detail_id=new_user_detail_id)

        get_user_database().insert(user.model_dump())

    return user_id

_get_user_by_id_lock = asyncio.Lock()

async def get_user_by_id(user_id: str) -> Union[User, Dict[str, str]]:
    """
    根据用户ID获取用户信息

    Args:
        user_id (str): 用户ID

    Returns:
        User: 用户信息 或 Dict[str, str]: 错误信息
    """
    # 输入验证
    if not user_id or not user_id.strip():
        return {"type": "error", "message": "User ID cannot be empty"}
    
    user_id = user_id.strip()
    
    async with _get_user_by_id_lock:
        db = get_user_database()
        user = db.get(Query().id == user_id)

        if not user:
            return {"type": "error", "message": "User not found"}

        return User.model_validate(user)

async def get_user_by_username(username: str) -> Union[User, Dict[str, str]]:
    """
    根据用户名获取用户信息

    Args:
        username (str): 用户名

    Returns:
        User: 用户信息 或 Dict[str, str]: 错误信息
    """
    # 输入验证
    if not username or not username.strip():
        return {"type": "error", "message": "Username cannot be empty"}
    
    username = username.strip()
    
    db = get_user_database()
    user = db.get(Query().username == username)

    if not user:
        return {"type": "error", "message": "User not found"}

    return User.model_validate(user)

_delete_user_by_id_lock = asyncio.Lock()

async def delete_user_by_id(user_id: str) -> Dict[str, str]:
    """
    根据用户ID删除用户

    Args:
        user_id (str): 用户ID

    Returns:
        Dict[str, str]: 操作结果
    """
    # 输入验证
    if not user_id or not user_id.strip():
        return {"type": "error", "message": "User ID cannot be empty"}
    
    user_id = user_id.strip()
    rsp = {"type": "error", "message": ""}

    async with _delete_user_by_id_lock:
        db = get_user_database()

        # first, get the user
        user = db.get(Query().id == user_id)

        if not user or len(user) == 0:
            rsp["message"] = "User not found"
            return rsp

        user = User.model_validate(user)

        # second, delete the user detail
        detail_rsp = await delete_user_detail_by_id(user.user_detail_id)

        if isinstance(detail_rsp, dict) and detail_rsp.get("type") == "error":
            rsp["message"] = detail_rsp.get("message", "Failed to delete user detail")
            return rsp

        db.remove(Query().id == user_id)

        rsp["type"] = "success"
    
    return rsp

