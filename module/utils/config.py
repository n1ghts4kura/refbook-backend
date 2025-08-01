# config.py
# 应用配置
#

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    
    SECRET_KEY = os.getenv("SECRET_KEY", "why_there_is_no_secret_key_wtf_bro_you_should_set_it")

    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    ALGORITHM = os.getenv("ALGORITHM", "HS256")

configs = Config()
