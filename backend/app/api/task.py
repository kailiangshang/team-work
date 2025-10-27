"""
任务API

处理任务相关的API请求。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from pathlib import Path
import json
from ..database import get_db
from ..services.project_service import ProjectService
from ..config import settings
from twork.utils.logger import get_logger

router = APIRouter()
logger = get_logger("task_api")


class DecomposeRequest(BaseModel):
    """任务拆解请求"""
    project_id: int


@router.post("/decompose")
async def decompose_tasks(
    request: DecomposeRequest,
    db: Session = Depends(get_db)
):
    """
    拆解任务（修复版）
    
    Args:
        request: 请求参数
        db: 数据库会话
        
    Returns:
        任务列表和文件路径
    """
    try:
        logger.info(f"开始拆解任务: project_id={request.project_id}")
        
        service = ProjectService(db)
        tasks = service.decompose_tasks(request.project_id)
        
        # 准备输出目录
        output_dir = Path(settings.output_dir) / f"project_{request.project_id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件（确保异常处理）
        try:
            # 生成Markdown文件
            breakdown_md_path = output_dir / "task_breakdown.md"
            with open(breakdown_md_path, "w", encoding="utf-8") as f:
                f.write("# 任务拆解结果\n\n")
                f.write(f"总任务数: {len(tasks)}\n\n")
                
                for task in tasks:
                    f.write(f"## {task['task_id']}: {task['task_name']}\n\n")
                    f.write(f"**描述**: {task.get('description', '')}\n\n")
                    f.write(f"**工期**: {task.get('duration_days', 1)}天\n\n")
                    if task.get('required_skills'):
                        f.write(f"**所需技能**: {', '.join(task['required_skills'])}\n\n")
                    if task.get('dependencies'):
                        f.write(f"**依赖**: {', '.join(task['dependencies'])}\n\n")
                    f.write("---\n\n")
            
            # 生成JSON文件
            tasks_json_path = output_dir / "tasks.json"
            with open(tasks_json_path, "w", encoding="utf-8") as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
            
            # 构建任务树
            task_tree = service.build_task_tree(tasks)
            tree_json_path = output_dir / "task_tree.json"
            with open(tree_json_path, "w", encoding="utf-8") as f:
                json.dump(task_tree, f, ensure_ascii=False, indent=2)
            
            logger.info(f"任务拆解完成: {len(tasks)}个任务")
            
            return {
                "tasks": tasks,
                "task_tree": task_tree,
                "files": {
                    "breakdown_md": str(breakdown_md_path),
                    "tasks_json": str(tasks_json_path),
                    "tree_json": str(tree_json_path)
                },
                "status": "success"
            }
            
        except IOError as e:
            logger.error(f"文件生成失败: {str(e)}")
            # 即使文件生成失败也返回任务数据
            return {
                "tasks": tasks,
                "task_tree": service.build_task_tree(tasks),
                "files": {},
                "status": "partial_success",
                "message": "任务拆解成功但文件生成失败"
            }
        
    except Exception as e:
        logger.error(f"任务拆觥异常: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"任务拆觥失败: {str(e)}")


@router.post("/generate-agents")
async def generate_agents(
    request: DecomposeRequest,
    db: Session = Depends(get_db)
):
    """
    生成Agent
    
    Args:
        request: 请求参数
        db: 数据库会话
        
    Returns:
        Agent列表
    """
    try:
        service = ProjectService(db)
        agents = service.generate_agents(request.project_id)
        
        return {
            "agents": agents,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/project/{project_id}")
async def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """获取项目信息"""
    try:
        service = ProjectService(db)
        project = service.get_project(project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        return {
            "id": project.id,
            "name": project.name,
            "status": project.status,
            "total_days": project.total_days
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
