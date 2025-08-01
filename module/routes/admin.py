# admin.py
# 管理员功能路由
# 包含清理数据库等管理操作
#

import os
import json
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..utils.config import configs

router = APIRouter()

@router.post("/clean_db")
async def clean_database() -> Dict[str, Any]:
    """
    清空所有数据库文件的数据
    
    只在DEBUG模式下可用
    
    Returns:
        dict: 包含操作结果的信息
    """
    
    # 检查是否为DEBUG模式
    if not configs.DEBUG:
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only available in DEBUG mode"
        )
    
    # 数据库文件路径
    database_dir = "database_file"
    database_files = [
        "db_book_v1.json",
        "db_chat_history_v1.json", 
        "db_user_v1.json",
        "db_user_detail_v1.json"
    ]
    
    cleaned_files = []
    failed_files = []
    
    try:
        for filename in database_files:
            file_path = os.path.join(database_dir, filename)
            
            if os.path.exists(file_path):
                try:
                    # 清空数据库文件，保留基本结构
                    empty_data = {"_default": {}}
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(empty_data, f, indent=4, ensure_ascii=False)
                    
                    cleaned_files.append(filename)
                    
                except Exception as e:
                    failed_files.append({"file": filename, "error": str(e)})
            else:
                failed_files.append({"file": filename, "error": "File does not exist"})
        
        if failed_files:
            return {
                "type": "partial_success",
                "message": f"Cleaned {len(cleaned_files)} files, {len(failed_files)} files failed",
                "cleaned_files": cleaned_files,
                "failed_files": failed_files
            }
        else:
            return {
                "type": "success", 
                "message": f"Successfully cleaned {len(cleaned_files)} database files",
                "cleaned_files": cleaned_files
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clean database: {str(e)}"
        )
