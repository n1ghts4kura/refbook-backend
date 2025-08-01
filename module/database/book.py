# book.py
# 数据库 图书部分 定义与操作
#

import time
import hashlib
import asyncio
from pydantic import BaseModel
from pydantic.fields import Field
from typing import *  # type: ignore

from .general import get_book_database, Query

def _get_current_id(sign: int) -> str:
    """
    获取当前时间戳作为ID
    """
    return hashlib.sha256(f"this_is_salt_{int(time.time() * 1000)}_book_{sign}".encode()).hexdigest()

class Concept(BaseModel):
    """
    知识点
    """

    introduction: str = Field(..., description="知识点介绍")

    explanation: str = Field(..., description="知识点解释")

    conclusion: str = Field(..., description="知识点结论")

class Section(BaseModel):
    """
    小节
    """

    title: str = Field(..., description="小节标题")

    introduction: str = Field(..., description="小节介绍")

    concepts: List[Concept] = Field(default=[], description="知识点列表")

class Chapter(BaseModel):
    """
    章节
    """

    title: str = Field(..., description="章节标题")

    introduction: str = Field(..., description="章节介绍")

    sections: List[Section] = Field(default=[], description="小节列表")

class Book(BaseModel):
    """
    图书
    """

    id: str = Field(..., description="图书ID")

    title: str = Field(..., description="图书标题")

    chapters: List[Chapter] = Field(default=[], description="章节列表")

# ---

_new_book_lock = asyncio.Lock()

async def new_book(book: Book) -> str:
    """
    新建书籍(有内容)

    Args:
        book (Book): 图书对象

    Returns:
        str: 图书ID
    """

    async with _new_book_lock:
        new_id = _get_current_id(0)
        book.id = new_id
        db = get_book_database()
        db.insert(book.model_dump())
    
    return new_id

_get_book_lock = asyncio.Lock()

async def get_book(book_id: str) -> Union[Book, Dict[str, str]]:
    """
    获取指定ID的图书

    Args:
        book_id (str): 图书ID

    Returns:
        Union[Book, Dict[str, str]]: 图书对象或错误信息
    """

    async with _get_book_lock:
        db = get_book_database()
        book_data = db.get(Query().id == book_id)

        if not book_data:
            return {"type": "error", "message": "Book not found"}

        # assert if book_data is suitable for Book model
        return Book(**book_data) # type: ignore

_delete_book_lock = asyncio.Lock()

async def delete_book(book_id: str) -> Dict[str, str]:
    """
    删除指定ID的图书

    Args:
        book_id (str): 图书ID

    Returns:
        Dict[str, str]: 删除结果信息
    """

    async with _delete_book_lock:
        db = get_book_database()
        book_data = db.get(Query().id == book_id)

        if not book_data:
            return {"type": "error", "message": "Book not found"}

        db.remove(Query().id == book_id)

    return {"type": "success", "message": "Book deleted successfully"}
