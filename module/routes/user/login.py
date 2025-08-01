# login.py
# 处理用户登录的逻辑
# 返回token
#

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from .router import router
from ...utils import auth, security

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    # 处理用户登录的逻辑
    # 返回token

    user = await auth.authenticate_user(form.username, form.password)
    if not user:
        return {
            "type": "failed",
            "message": "Invalid username or password"
        }

    access_token = security.create_access_token(
        data={"sub": user.username, "scopes": form.scopes}
    )

    return {
        "type": "success",
        "message": access_token
    }
