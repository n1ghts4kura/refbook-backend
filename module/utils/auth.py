# auth.py
# 登录验证
#

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from jose import JWTError
from datetime import timedelta

from . import security
from .config import configs
from ..database.user import get_user_by_username

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/user/token",
    scopes={
        "me": "Read your own user data",
        "admin": "Full access"
    }
)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    """获取当前认证用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = security.decode_token(token)
        if payload is None:
            raise credentials_exception
            
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        username_str: str = str(username)
            
        # 检查令牌是否被撤销（可扩展实现）
        # if is_token_revoked(token):
        #     raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_username(username_str)

    if isinstance(user, dict):
        raise credentials_exception

    return user

async def authenticate_user(
    username: str, 
    password: str
):
    """用户认证"""
    user = await get_user_by_username(username)
    if isinstance(user, dict):
        return None
    
    try:
        if not security.verify_password(password, user.password_hash):
            return None
    except Exception as e:
        # 记录密码验证错误，可能是哈希格式问题
        print(f"Password verification error for user {username}: {e}")
        return None
    
    return user
