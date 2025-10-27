"""
任务树管理API
提供WBS任务树的CRUD和操作接口
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from ..database import get_db
from ..models.project import Project
from ..models.task import Task
from twork.parser.wbs_decomposer import WBSDecomposer
from twork.llm.openai_adapter import OpenAIAdapter


router = APIRouter(prefix="/api/task-tree", tags=["task-tree"])


# Pydantic模型
class TaskTreeNode(BaseModel):
    """任务树节点"""
    task_id: str
    task_name: str
    description: str
    level: int
    parent_task_id: Optional[str]
    task_type: str
    estimated_complexity: int
    dependencies: List[str]
    children: List['TaskTreeNode'] = []


class WBSDecomposeRequest(BaseModel):
    """WBS拆解请求"""
    project_id: int
    max_level: int = 4
    user_constraints: Optional[dict] = None


class TaskUpdateRequest(BaseModel):
    """任务更新请求"""
    task_id: str
    task_name: Optional[str] = None
    description: Optional[str] = None
    parent_task_id: Optional[str] = None
    level: Optional[int] = None
    sort_order: Optional[int] = None
    estimated_complexity: Optional[int] = None


class TaskMoveRequest(BaseModel):
    """任务移动请求"""
    task_id: str
    new_parent_id: Optional[str] = None
    new_sort_order: int


@router.post("/decompose")
def decompose_wbs(
    request: WBSDecomposeRequest,
    db: Session = Depends(get_db)
):
    """
    执行WBS任务拆解
    
    Args:
        request: 拆解请求
        db: 数据库会话
    
    Returns:
        任务树和统计信息
    """
    # 查询项目
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 获取需求文档内容
    if not project.document_path:
        raise HTTPException(status_code=400, detail="项目未上传文档")
    
    try:
        with open(project.document_path, 'r', encoding='utf-8') as f:
            requirements = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文档失败: {str(e)}")
    
    # 获取领域配置
    from ..models.domain_config import DomainConfig
    domain_config = db.query(DomainConfig).filter(
        DomainConfig.project_id == request.project_id
    ).first()
    
    if not domain_config:
        raise HTTPException(status_code=400, detail="请先进行领域识别")
    
    # 初始化WBS拆解器
    from ..config import settings
    llm = OpenAIAdapter(api_key=settings.OPENAI_API_KEY)
    decomposer = WBSDecomposer(llm, max_level=request.max_level)
    
    # 执行拆解
    try:
        result = decomposer.decompose(
            requirements=requirements,
            domain_type=domain_config.domain_type,
            task_types=domain_config.template_config.get("task_types", []),
            template_config=domain_config.template_config,
            user_constraints=request.user_constraints
        )
        
        # 保存任务到数据库
        _save_tasks_to_db(db, request.project_id, result["task_tree"])
        
        return {
            "success": True,
            "task_tree": result["task_tree"],
            "statistics": result["statistics"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"WBS拆解失败: {str(e)}")


@router.get("/{project_id}")
def get_task_tree(project_id: int, db: Session = Depends(get_db)):
    """
    获取项目的任务树
    
    Args:
        project_id: 项目ID
        db: 数据库会话
    
    Returns:
        任务树
    """
    # 查询所有任务
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    
    if not tasks:
        return {"task_tree": [], "total_tasks": 0}
    
    # 构建树形结构
    task_dict = {task.task_id: _task_to_dict(task) for task in tasks}
    
    # 找出顶层任务
    root_tasks = []
    for task in tasks:
        if not task.parent_task_id:
            task_node = _build_task_tree(task.task_id, task_dict)
            root_tasks.append(task_node)
    
    return {
        "task_tree": root_tasks,
        "total_tasks": len(tasks)
    }


@router.put("/update")
def update_task(
    request: TaskUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    更新任务信息
    
    Args:
        request: 更新请求
        db: 数据库会话
    
    Returns:
        更新后的任务
    """
    # 查找任务
    task = db.query(Task).filter(Task.task_id == request.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 更新字段
    if request.task_name is not None:
        task.task_name = request.task_name
    if request.description is not None:
        task.description = request.description
    if request.parent_task_id is not None:
        task.parent_task_id = request.parent_task_id
    if request.level is not None:
        task.level = request.level
    if request.sort_order is not None:
        task.sort_order = request.sort_order
    if request.estimated_complexity is not None:
        task.estimated_complexity = request.estimated_complexity
    
    db.commit()
    db.refresh(task)
    
    return {"success": True, "task": _task_to_dict(task)}


@router.post("/move")
def move_task(
    request: TaskMoveRequest,
    db: Session = Depends(get_db)
):
    """
    移动任务到新位置
    
    Args:
        request: 移动请求
        db: 数据库会话
    
    Returns:
        移动结果
    """
    task = db.query(Task).filter(Task.task_id == request.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 更新父任务和排序
    task.parent_task_id = request.new_parent_id
    task.sort_order = request.new_sort_order
    
    # 如果改变了父任务，需要重新计算层级
    if request.new_parent_id:
        parent = db.query(Task).filter(Task.task_id == request.new_parent_id).first()
        if parent:
            task.level = parent.level + 1
    else:
        task.level = 1
    
    db.commit()
    
    return {"success": True, "message": "任务移动成功"}


@router.delete("/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    """
    删除任务（及其子任务）
    
    Args:
        task_id: 任务ID
        db: 数据库会话
    
    Returns:
        删除结果
    """
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 递归删除子任务
    _delete_task_recursive(db, task_id)
    
    db.commit()
    
    return {"success": True, "message": "任务删除成功"}


@router.get("/flatten/{project_id}")
def get_flattened_tasks(project_id: int, db: Session = Depends(get_db)):
    """
    获取扁平化的任务列表
    
    Args:
        project_id: 项目ID
        db: 数据库会话
    
    Returns:
        任务列表
    """
    tasks = db.query(Task).filter(
        Task.project_id == project_id
    ).order_by(Task.level, Task.sort_order).all()
    
    return {
        "tasks": [_task_to_dict(task) for task in tasks],
        "total": len(tasks)
    }


# 辅助函数
def _save_tasks_to_db(db: Session, project_id: int, task_tree: List[dict]):
    """保存任务树到数据库"""
    # 先删除旧任务
    db.query(Task).filter(Task.project_id == project_id).delete()
    
    # 递归保存
    def save_recursive(tasks: List[dict]):
        for task_data in tasks:
            task = Task(
                project_id=project_id,
                task_id=task_data["task_id"],
                task_name=task_data["task_name"],
                description=task_data.get("description", ""),
                parent_task_id=task_data.get("parent_task_id"),
                level=task_data.get("level", 1),
                task_type=task_data.get("task_type"),
                estimated_complexity=task_data.get("estimated_complexity", 5),
                dependencies=task_data.get("dependencies", []),
                required_skills=task_data.get("required_skills", [])
            )
            db.add(task)
            
            # 递归保存子任务
            if task_data.get("children"):
                save_recursive(task_data["children"])
    
    save_recursive(task_tree)
    db.commit()


def _task_to_dict(task: Task) -> dict:
    """任务模型转字典"""
    return {
        "task_id": task.task_id,
        "task_name": task.task_name,
        "description": task.description,
        "parent_task_id": task.parent_task_id,
        "level": task.level,
        "sort_order": task.sort_order,
        "task_type": task.task_type,
        "estimated_complexity": task.estimated_complexity,
        "dependencies": task.dependencies,
        "required_skills": task.required_skills,
        "duration_days": task.duration_days
    }


def _build_task_tree(task_id: str, task_dict: dict) -> dict:
    """构建任务树"""
    task = task_dict[task_id].copy()
    task["children"] = []
    
    # 找出子任务
    for tid, t in task_dict.items():
        if t.get("parent_task_id") == task_id:
            child = _build_task_tree(tid, task_dict)
            task["children"].append(child)
    
    return task


def _delete_task_recursive(db: Session, task_id: str):
    """递归删除任务"""
    # 找出所有子任务
    children = db.query(Task).filter(Task.parent_task_id == task_id).all()
    
    for child in children:
        _delete_task_recursive(db, child.task_id)
    
    # 删除自己
    db.query(Task).filter(Task.task_id == task_id).delete()
