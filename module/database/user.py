# user.py
# 数据库 用户部分 定义与操作
#

import time
import hashlib
import asyncio
from pydantic import BaseModel
from pydantic.fields import Field
from typing import *  # type: ignore

from .general import get_user_database, Query
from .user_detail import new_user_detail, delete_user_detail_by_id

def _get_current_id(sign: int) -> str:
    """
    获取当前时间戳作为ID
    """
    return hashlib.sha256(f"this_is_salt_{int(time.time() * 1000)}_user_{sign}".encode()).hexdigest()

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

async def new_user(username: str, password_hash: str) -> Union[str, bool]:
    """
    创建新的用户

    Args:
        username (str): 用户名
        password_hash (str): 密码哈希

    Returns:
        str: 新的用户ID
    """
    async with _new_user_lock:
        # get new_user_detail's id
        new_user_detail_id = await new_user_detail()

        if not isinstance(new_user_detail_id, str):
            return False

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
        User: 用户信息
    """
    async with _get_user_by_id_lock:
        db = get_user_database()
        user = db.get(Query().id == user_id)

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

    """

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

