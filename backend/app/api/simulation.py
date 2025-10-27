"""
模拟API

处理任务模拟相关的API请求。
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import asyncio
import json
import csv
from pathlib import Path
from typing import Optional
from ..database import get_db
from ..services.simulation_service import SimulationService
from twork.utils.logger import get_logger

router = APIRouter()
logger = get_logger("simulation_api")


class SimulationRequest(BaseModel):
    """模拟请求"""
    project_id: int
    enable_env_agent: bool = True  # 是否启用环境Agent
    env_event_probability: float = 0.2  # 环境事件概率


@router.post("/run")
async def run_simulation(
    request: SimulationRequest,
    db: Session = Depends(get_db)
):
    """
    运行模拟
    
    Args:
        request: 请求参数
        db: 数据库会话
        
    Returns:
        模拟结果
    """
    try:
        service = SimulationService(db)
        result = service.run_simulation(
            request.project_id,
            enable_env_agent=request.enable_env_agent,
            env_event_probability=request.env_event_probability
        )
        
        return {
            "logs": result.get("logs", []),
            "detailed_logs": result.get("detailed_logs", []),
            "env_events": result.get("env_events", []),
            "env_summary": result.get("env_summary"),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-outputs")
async def generate_outputs(
    request: SimulationRequest,
    db: Session = Depends(get_db)
):
    """
    生成输出文件
    
    Args:
        request: 请求参数
        db: 数据库会话
        
    Returns:
        输出文件路径
    """
    try:
        service = SimulationService(db)
        outputs = service.generate_outputs(request.project_id)
        
        return {
            "outputs": outputs,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/{project_id}")
async def get_simulation_logs(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    获取模拟日志
    
    Args:
        project_id: 项目ID
        db: 数据库会话
        
    Returns:
        详细日志列表
    """
    try:
        service = SimulationService(db)
        logs = service.get_detailed_logs(project_id)
        
        return {
            "logs": logs,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-stream")
async def run_simulation_stream(
    request: SimulationRequest,
    db: Session = Depends(get_db)
):
    """
    流式运行模拟（SSE）
    
    Args:
        request: 请求参数
        db: 数据库会话
        
    Returns:
        SSE流
    """
    async def event_generator():
        try:
            logger.info(f"开始流式模拟: project_id={request.project_id}")
            service = SimulationService(db)
            
            # 使用流式方法
            async for chunk in service.run_simulation_stream(
                request.project_id,
                enable_env_agent=request.enable_env_agent,
                env_event_probability=request.env_event_probability
            ):
                # SSE格式：data: {json}\n\n
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)  # 避免过快推送
            
            logger.info("模拟完成")
            
        except Exception as e:
            logger.error(f"模拟异常: {str(e)}", exc_info=True)
            error_data = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )


@router.get("/daily-summaries/{project_id}")
async def get_daily_summaries(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    获取项目的每日摘要
    
    Args:
        project_id: 项目ID
        db: 数据库会话
        
    Returns:
        每日摘要列表
    """
    try:
        service = SimulationService(db)
        summaries = service.get_daily_summaries(project_id)
        
        return {
            "summaries": summaries,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"获取每日摘要失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-logs/{project_id}")
async def get_agent_execution_logs(
    project_id: int,
    agent_id: Optional[str] = Query(None, description="筛选特定Agent"),
    day_number: Optional[int] = Query(None, description="筛选特定天数"),
    db: Session = Depends(get_db)
):
    """
    获取Agent执行日志
    
    Args:
        project_id: 项目ID
        agent_id: Agent ID（可选）
        day_number: 天数（可选）
        db: 数据库会话
        
    Returns:
        Agent执行日志列表
    """
    try:
        service = SimulationService(db)
        logs = service.get_agent_execution_logs(
            project_id,
            agent_id=agent_id,
            day_number=day_number
        )
        
        return {
            "logs": logs,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"获取Agent日志失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export-agent-logs/{project_id}")
async def export_agent_logs(
    project_id: int,
    agent_id: Optional[str] = Query(None, description="筛选特定Agent"),
    format: str = Query("json", regex="^(json|csv|md)$", description="导出格式: json, csv, md"),
    db: Session = Depends(get_db)
):
    """
    导出Agent执行日志
    
    Args:
        project_id: 项目ID
        agent_id: Agent ID（可选）
        format: 导出格式
        db: 数据库会话
        
    Returns:
        文件下载响应
    """
    try:
        service = SimulationService(db)
        logs = service.get_agent_execution_logs(project_id, agent_id=agent_id)
        
        if not logs:
            raise HTTPException(status_code=404, detail="未找到日志数据")
        
        # 创建临时文件
        from ..config import settings
        output_dir = Path(settings.output_dir) / f"project_{project_id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            file_path = output_dir / "agent_logs.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
            media_type = "application/json"
            
        elif format == "csv":
            file_path = output_dir / "agent_logs.csv"
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                if logs:
                    writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                    writer.writeheader()
                    writer.writerows(logs)
            media_type = "text/csv"
            
        elif format == "md":
            file_path = output_dir / "agent_logs.md"
            md_content = service.export_agent_logs_markdown(logs)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            media_type = "text/markdown"
        
        return FileResponse(
            path=str(file_path),
            filename=file_path.name,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出日志失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
