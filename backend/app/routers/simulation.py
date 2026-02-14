"""模拟 API 路由"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from pydantic import BaseModel

router = APIRouter()


class SimulationRequest(BaseModel):
    """模拟请求"""
    project_id: str
    total_days: int = 30
    enable_env_agent: bool = True


class SimulationStatus(BaseModel):
    """模拟状态"""
    project_id: str
    status: str
    current_day: int
    total_days: int
    progress: float


# 存储模拟状态
simulations: Dict[str, SimulationStatus] = {}


@router.post("/start")
async def start_simulation(request: SimulationRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """启动模拟"""
    project_id = request.project_id
    
    # 初始化状态
    simulations[project_id] = SimulationStatus(
        project_id=project_id,
        status="running",
        current_day=0,
        total_days=request.total_days,
        progress=0.0,
    )
    
    # TODO: 在后台启动模拟任务
    # background_tasks.add_task(run_simulation, request)
    
    return {
        "message": "Simulation started",
        "project_id": project_id,
    }


@router.post("/pause/{project_id}")
async def pause_simulation(project_id: str) -> Dict[str, Any]:
    """暂停模拟"""
    if project_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulations[project_id].status = "paused"
    return {"message": "Simulation paused", "project_id": project_id}


@router.post("/resume/{project_id}")
async def resume_simulation(project_id: str) -> Dict[str, Any]:
    """恢复模拟"""
    if project_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulations[project_id].status = "running"
    return {"message": "Simulation resumed", "project_id": project_id}


@router.get("/status/{project_id}")
async def get_status(project_id: str) -> SimulationStatus:
    """获取模拟状态"""
    if project_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    return simulations[project_id]


@router.get("/result/{project_id}")
async def get_result(project_id: str) -> Dict[str, Any]:
    """获取模拟结果"""
    # TODO: 实现结果获取
    return {
        "project_id": project_id,
        "daily_results": [],
    }


@router.get("/logs/{project_id}")
async def get_logs(project_id: str, day: int = None) -> List[Dict]:
    """获取模拟日志"""
    # TODO: 实现日志获取
    return []