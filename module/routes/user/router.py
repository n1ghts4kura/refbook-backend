# router.py
#
#

from fastapi import APIRouter

router = APIRouter()

# 导入路由模块，让路由生效
from . import login
from . import create
