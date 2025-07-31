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

    id: str = Field(..., description="用户ID")

    books: List[str] = Field(default=[], description="用户书籍列表")

    chat_history: List[]

    # 用户画像收集
    # user_portrait: Dict[str, Any] = Field(default={}, description="用户画像")
