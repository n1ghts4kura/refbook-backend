import sys
import asyncio
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from module.database.chat_history import *

async def test1():
    pass

tests = [test1(), ]

if __name__ == "__main__":
    index = 0
    asyncio.run(tests[index])