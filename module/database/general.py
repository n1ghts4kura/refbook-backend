# general.py
# 数据库 基本操作
#

import os
import tinydb

Query = tinydb.Query

ROOT_DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'database_file')

USER_DB_PATH = f'{ROOT_DB_PATH}/db_user_v1.json'
USER_DETAIL_DB_PATH = f'{ROOT_DB_PATH}/db_user_detail_v1.json'
BOOK_DB_PATH = f'{ROOT_DB_PATH}/db_book_v1.json'
CHAT_HISTORY_DB_PATH = f'{ROOT_DB_PATH}/db_chat_history_v1.json'

_user_database = tinydb.TinyDB(USER_DB_PATH, indent=4, ensure_ascii=False, encoding='utf-8')

def get_user_database():
    """获取用户数据库实例"""
    return _user_database

_user_detail_database = tinydb.TinyDB(USER_DETAIL_DB_PATH, indent=4, ensure_ascii=False, encoding='utf-8')

def get_user_detail_database():
    """获取用户详情数据库实例"""
    return _user_detail_database

_book_database = tinydb.TinyDB(BOOK_DB_PATH, indent=4, ensure_ascii=False, encoding='utf-8')

def get_book_database():
    """获取图书数据库实例"""
    return _book_database

_chat_history_database = tinydb.TinyDB(CHAT_HISTORY_DB_PATH, indent=4, ensure_ascii=False, encoding='utf-8')

def get_chat_history_database():
    """获取聊天记录数据库实例"""
    return _chat_history_database

__all__ = ['get_user_database', 'get_book_database', 'get_user_detail_database', 'get_chat_history_database']
