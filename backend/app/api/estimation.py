"""
时间估算API
提供任务工期估算和调整接口
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from ..database import get_db
from ..models.project import Project
from ..models.task import Task
from ..models.time_estimate import TimeEstimate
from twork.estimator import ComplexityAnalyzer, TimeEstimator


router = APIRouter(prefix="/api/estimation", tags=["estimation"])


# Pydantic模型
class EstimationRequest(BaseModel):
    """估算请求"""
    project_id: int
    total_days: Optional[int] = None
    team_size: int = 5
    work_hours_per_day: int = 8


class EstimationResponse(BaseModel):
    """估算响应"""
    total_estimated_days: float
    team_size: int
    work_hours_per_day: int
    critical_path: List[str]
    task_estimates: List[dict]


class TaskEstimateUpdateRequest(BaseModel):
    """任务估算更新请求"""
    task_id: str
    estimated_duration: float
    adjustment_reason: Optional[str] = None


@router.post("/calculate", response_model=EstimationResponse)
def calculate_estimation(
    request: EstimationRequest,
    db: Session = Depends(get_db)
):
    """
    计算项目时间估算
    
    Args:
        request: 估算请求
        db: 数据库会话
    
    Returns:
        估算结果
    """
    # 查询项目
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 查询所有任务
    tasks = db.query(Task).filter(Task.project_id == request.project_id).all()
    if not tasks:
        raise HTTPException(status_code=400, detail="项目还没有任务")
    
    # 转换为字典格式
    task_list = []
    for task in tasks:
        task_list.append({
            "task_id": task.task_id,
            "task_name": task.task_name,
            "description": task.description,
            "required_skills": task.required_skills or [],
            "dependencies": task.dependencies or [],
            "estimated_complexity": task.estimated_complexity or 5
        })
    
    # 执行估算
    complexity_analyzer = ComplexityAnalyzer()
    estimator = TimeEstimator(complexity_analyzer)
    
    result = estimator.estimate(
        tasks=task_list,
        total_days=request.total_days,
        team_size=request.team_size,
        work_hours_per_day=request.work_hours_per_day
    )
    
    # 保存估算结果到数据库
    _save_estimates_to_db(
        db=db,
        project_id=request.project_id,
        estimates=result["task_estimates"],
        critical_path=result["critical_path"],
        team_size=request.team_size
    )
    
    # 更新项目总工期
    project.total_days = int(result["total_estimated_days"])
    db.commit()
    
    return EstimationResponse(**result)


@router.get("/{project_id}")
def get_estimation(project_id: int, db: Session = Depends(get_db)):
    """
    获取项目的估算结果
    
    Args:
        project_id: 项目ID
        db: 数据库会话
    
    Returns:
        估算结果列表
    """
    estimates = db.query(TimeEstimate).filter(
        TimeEstimate.project_id == project_id
    ).all()
    
    if not estimates:
        return {"estimates": [], "total": 0}
    
    # 计算汇总
    total_estimated = sum(e.estimated_duration for e in estimates)
    critical_tasks = [e.task_id for e in estimates if e.is_critical_path]
    
    return {
        "estimates": [e.to_dict() for e in estimates],
        "total": len(estimates),
        "summary": {
            "total_estimated_days": round(total_estimated, 1),
            "critical_path_count": len(critical_tasks),
            "critical_path": critical_tasks,
            "avg_complexity": round(
                sum(e.complexity_score for e in estimates) / len(estimates), 2
            )
        }
    }


@router.put("/update")
def update_task_estimate(
    request: TaskEstimateUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    更新任务估算
    
    Args:
        request: 更新请求
        db: 数据库会话
    
    Returns:
        更新结果
    """
    estimate = db.query(TimeEstimate).filter(
        TimeEstimate.task_id == request.task_id
    ).first()
    
    if not estimate:
        raise HTTPException(status_code=404, detail="任务估算不存在")
    
    # 更新估算
    estimate.estimated_duration = request.estimated_duration
    if request.adjustment_reason:
        estimate.adjustment_reason = request.adjustment_reason
    
    # 同步更新任务的duration_days
    task = db.query(Task).filter(Task.task_id == request.task_id).first()
    if task:
        task.duration_days = int(request.estimated_duration)
    
    db.commit()
    db.refresh(estimate)
    
    return {"success": True, "estimate": estimate.to_dict()}


@router.get("/critical-path/{project_id}")
def get_critical_path(project_id: int, db: Session = Depends(get_db)):
    """
    获取关键路径
    
    Args:
        project_id: 项目ID
        db: 数据库会话
    
    Returns:
        关键路径任务列表
    """
    critical_tasks = db.query(TimeEstimate).filter(
        TimeEstimate.project_id == project_id,
        TimeEstimate.is_critical_path == 1
    ).all()
    
    return {
        "critical_path": [e.task_id for e in critical_tasks],
        "total_duration": sum(e.estimated_duration for e in critical_tasks),
        "tasks": [e.to_dict() for e in critical_tasks]
    }


@router.post("/recalculate/{project_id}")
def recalculate_estimation(
    project_id: int,
    total_days: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    重新计算估算（当任务或约束变化时）
    
    Args:
        project_id: 项目ID
        total_days: 新的总工期约束
        db: 数据库会话
    
    Returns:
        新的估算结果
    """
    # 创建估算请求
    request = EstimationRequest(
        project_id=project_id,
        total_days=total_days,
        team_size=5,
        work_hours_per_day=8
    )
    
    return calculate_estimation(request, db)


# 辅助函数
def _save_estimates_to_db(
    db: Session,
    project_id: int,
    estimates: List[dict],
    critical_path: List[str],
    team_size: int
):
    """保存估算结果到数据库"""
    # 删除旧估算
    db.query(TimeEstimate).filter(TimeEstimate.project_id == project_id).delete()
    
    # 保存新估算
    team_efficiency = 1.0 - (team_size - 1) * 0.05
    team_efficiency = max(0.7, team_efficiency)
    
    for estimate_data in estimates:
        estimate = TimeEstimate(
            project_id=project_id,
            task_id=estimate_data["task_id"],
            complexity_score=estimate_data["complexity_score"],
            base_duration=estimate_data["base_duration"],
            estimated_duration=estimate_data["estimated_duration"],
            team_efficiency_factor=team_efficiency,
            confidence=estimate_data.get("confidence", 0.8),
            is_critical_path=1 if estimate_data["task_id"] in critical_path else 0
        )
        db.add(estimate)
    
    db.commit()
