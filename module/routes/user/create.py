# create.py
# 创建新用户
#

from pydantic import BaseModel

from ...database import user as user_db
from .router import router
from ...utils.security import get_password_hash
from ...utils import log


class UserCreateRequest(BaseModel):
    username: str
    password: str


@router.post("/create")
async def create_user(user: UserCreateRequest):
    """
    创建新用户
    
    Args:
        username (str): 用户名
        password (str): 密码

        Returns:
            dict: 包含创建成功的用户信息
    """

    log.info("first check if the user already exists")
    existing_user = await user_db.get_user_by_username(user.username)
    if not isinstance(existing_user, dict):
        log.error(f"User [{existing_user.username}] already exists.")
        return {
            "type": "failed",
            "message": "User already exists."
        }

    log.info("the user doesn't exist, so now create a new one")
    new_user = await user_db.new_user(user.username, get_password_hash(user.password))
    if isinstance(new_user, dict):
        reason = new_user.get("message", "Failed to create user")
        log.warning(f"-> {reason}")
        return {
            "type": "failed",
            "message": new_user.get("message", reason)
        }
    
    # successfully created the user
    log.info(f"successfully created user [{user.username}]")
    return {
        "type": "success"
    }
