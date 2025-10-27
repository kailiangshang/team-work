"""
文件下载API

处理文件下载相关的API请求。
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import os
from ..config import settings
from ..utils.file_handler import FilePermissionHandler
from twork.utils.logger import get_logger

router = APIRouter()
logger = get_logger("download_api")


@router.get("/{file_type}/{project_id}")
async def download_file(
    file_type: str,
    project_id: int
):
    """
    下载文件
    
    Args:
        file_type: 文件类型 (requirements_md, breakdown_md, tasks_json, tree_json, csv, graph_md, graph_json)
        project_id: 项目ID
        
    Returns:
        文件响应
    """
    try:
        output_dir = Path(settings.output_dir) / f"project_{project_id}"
        
        # 文件类型映射
        file_map = {
            "requirements_md": "requirements.md",
            "breakdown_md": "task_breakdown.md",
            "tasks_json": "tasks.json",
            "tree_json": "task_tree.json",
            "csv": "schedule.csv",
            "graph_md": "graph.md",
            "graph_json": "graph_triplets.json"
        }
        
        if file_type not in file_map:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file_type}。支持的类型: {', '.join(file_map.keys())}"
            )
        
        file_path = output_dir / file_map[file_type]
        
        # 检查文件是否存在
        if not file_path.exists():
            logger.warning(f"文件不存在: {file_path}")
            raise HTTPException(
                status_code=404,
                detail=f"文件不存在: {file_map[file_type]}"
            )
        
        # 检查文件读权限
        if not FilePermissionHandler.ensure_readable(str(file_path)):
            logger.error(f"文件无读权限: {file_path}")
            
            # 记录权限信息用于调试
            ownership = FilePermissionHandler.check_path_ownership(str(file_path))
            logger.error(f"文件所有者信息: {ownership}")
            
            raise HTTPException(
                status_code=500,
                detail=f"文件权限错误，请联系管理员。文件: {file_map[file_type]}"
            )
        
        logger.info(f"下载文件: {file_path}")
        
        return FileResponse(
            path=str(file_path),
            filename=file_map[file_type],
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")
