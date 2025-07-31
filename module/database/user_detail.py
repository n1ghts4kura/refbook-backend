# user_detail.py
# 数据库 用户详情部分 定义与操作
#

from pydantic import BaseModel
from pydantic.fields import Field
from typing import * # type: ignore

from .general import get_user_detail_database

class UserDetail(BaseModel):
    """
    用户详情模型
    """

    id: str = Field(..., description="用户详情ID")

    chat_history_id: str = Field(..., description="关联的聊天记录ID")

    # 用户画像收集
    # user_portrait: Dict[str, Any] = Field(default={}, description="用户画像")

    
