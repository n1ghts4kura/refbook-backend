# create.py
# 创建新用户
#

from pydantic import BaseModel

from ...database import user as user_db
from .router import router

class UserCreateRequest(BaseModel):
    username: str
    password: str

@router.post("/create")
async def create_user(user: UserCreateRequest):
    """
    创建新用户
    
    Args:
        user (UserCreateRequest): 用户创建请求体，包含用户名和密码

        Returns:
            dict: 包含创建成功的用户信息
    """

    # first check if the user already exists
    existing_user = await user_db.get_user_by_username(user.username)
    if isinstance(existing_user, dict):
        return {
            "type": "failed",
            "message": existing_user.get("message", "User already exists")
        }

    # the user doesn't exist, so now create a new one
    new_user = await user_db.new_user(user.username, user.password)
    if isinstance(new_user, dict):
        return {
            "type": "failed",
            "message": new_user.get("message", "Failed to create user")
        }
    
    # successfully created the user
    return {
        "type": "success"
    }
