# security.py
# 安全相关的工具函数定义
#

from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from .config import configs

# 密码哈希上下文
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配哈希值"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码的哈希值"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=configs.ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    """创建JWT访问令牌"""
    to_encode = data.copy()
    
    # 设置过期时间
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    
    return jwt.encode(
        to_encode,
        configs.SECRET_KEY,
        algorithm=configs.ALGORITHM
    )

def decode_token(token: str):
    """解码并验证JWT令牌"""
    try:
        payload = jwt.decode(
            token, 
            configs.SECRET_KEY, 
            algorithms=[configs.ALGORITHM]
        )
        return payload
    except:
        return None
