"""项目 API 路由"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel

router = APIRouter()


class ProjectCreate(BaseModel):
    """创建项目请求"""
    name: str
    description: str = ""
    total_days: int = 30


class Project(BaseModel):
    """项目"""
    id: str
    name: str
    description: str
    status: str = "draft"
    total_days: int = 30


# 存储项目
projects: Dict[str, Project] = {}


@router.post("/")
async def create_project(request: ProjectCreate) -> Dict[str, Any]:
    """创建项目"""
    import uuid
    project_id = str(uuid.uuid4())[:8]
    
    project = Project(
        id=project_id,
        name=request.name,
        description=request.description,
        total_days=request.total_days,
    )
    projects[project_id] = project
    
    return project.model_dump()


@router.get("/")
async def list_projects() -> List[Dict]:
    """列出所有项目"""
    return [p.model_dump() for p in projects.values()]


@router.get("/{project_id}")
async def get_project(project_id: str) -> Project:
    """获取项目详情"""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects[project_id]


@router.put("/{project_id}")
async def update_project(project_id: str, request: ProjectCreate) -> Project:
    """更新项目"""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects[project_id]
    project.name = request.name
    project.description = request.description
    project.total_days = request.total_days
    
    return project


@router.delete("/{project_id}")
async def delete_project(project_id: str) -> Dict[str, Any]:
    """删除项目"""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    del projects[project_id]
    return {"message": "Project deleted", "project_id": project_id}