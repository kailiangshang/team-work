"""
Agent API

处理Agent相关的API请求。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from ..database import get_db
from ..models.agent import Agent
from ..models.project import Project
from twork.utils.logger import get_logger

router = APIRouter()
logger = get_logger("agent_api")


class AgentUpdateRequest(BaseModel):
    """Agent更新请求"""
    agent_id: str
    role_name: str = None
    role_type: str = None
    capabilities: List[str] = None
    assigned_tasks: List[str] = None
    personality: str = None
    enabled: bool = True  # 是否启用该Agent


class BatchAgentUpdateRequest(BaseModel):
    """批量Agent更新请求"""
    project_id: int
    agents: List[AgentUpdateRequest]
    total_days: int = None  # 可选：同时更新项目工期


@router.put("/batch-update")
async def batch_update_agents(
    request: BatchAgentUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    批量更新Agent
    
    Args:
        request: 请求参数
        db: 数据库会话
        
    Returns:
        更新结果
    """
    try:
        logger.info(f"批量更新Agent: project_id={request.project_id}, count={len(request.agents)}")
        
        # 验证项目存在
        project = db.query(Project).filter(Project.id == request.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        updated_agents = []
        disabled_agents = []
        enabled_agents = []
        
        for agent_update in request.agents:
            # 查找Agent
            agent = db.query(Agent).filter(
                Agent.project_id == request.project_id,
                Agent.agent_id == agent_update.agent_id
            ).first()
            
            if not agent:
                logger.warning(f"Agent不存在: {agent_update.agent_id}")
                continue
            
            # 更新字段
            if agent_update.role_name is not None:
                agent.role_name = agent_update.role_name
            if agent_update.role_type is not None:
                agent.role_type = agent_update.role_type
            if agent_update.capabilities is not None:
                agent.capabilities = agent_update.capabilities
            if agent_update.assigned_tasks is not None:
                agent.assigned_tasks = agent_update.assigned_tasks
            if agent_update.personality is not None:
                agent.personality = agent_update.personality
            
            # 如果禁用Agent，清空其任务分配
            if not agent_update.enabled:
                agent.assigned_tasks = []
                disabled_agents.append(agent.role_name)
                logger.info(f"禁用Agent: {agent.role_name} ({agent.agent_id})")
            else:
                enabled_agents.append(agent.role_name)
            
            updated_agents.append(agent)
        
        # 更新项目工期
        if request.total_days is not None:
            project.total_days = request.total_days
            logger.info(f"更新项目工期: {request.total_days}天")
        
        db.commit()
        
        # 详细日志输出
        logger.info(f"配置保存完成 - 启用: {len(enabled_agents)}个, 禁用: {len(disabled_agents)}个")
        if disabled_agents:
            logger.info(f"已禁用的Agents: {', '.join(disabled_agents)}")
        
        return {
            "updated_count": len(updated_agents),
            "enabled_count": len(enabled_agents),
            "disabled_count": len(disabled_agents),
            "disabled_agents": disabled_agents,
            "enabled_agents": enabled_agents,
            "total_days": project.total_days,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"批量更新Agent失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.get("/list/{project_id}")
async def list_agents(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    获取项目的Agent列表
    
    Args:
        project_id: 项目ID
        db: 数据库会话
        
    Returns:
        Agent列表
    """
    try:
        agents = db.query(Agent).filter(Agent.project_id == project_id).all()
        
        agent_list = [
            {
                "agent_id": a.agent_id,
                "role_name": a.role_name,
                "role_type": a.role_type,
                "capabilities": a.capabilities or [],
                "assigned_tasks": a.assigned_tasks or [],
                "personality": a.personality or "",
                "enabled": len(a.assigned_tasks or []) > 0  # 根据是否有分配任务判断是否启用
            }
            for a in agents
        ]
        
        return {
            "agents": agent_list,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}/{agent_id}")
async def delete_agent(
    project_id: int,
    agent_id: str,
    db: Session = Depends(get_db)
):
    """
    删除Agent
    
    Args:
        project_id: 项目ID
        agent_id: Agent ID
        db: 数据库会话
        
    Returns:
        删除结果
    """
    try:
        agent = db.query(Agent).filter(
            Agent.project_id == project_id,
            Agent.agent_id == agent_id
        ).first()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent不存在")
        
        db.delete(agent)
        db.commit()
        
        logger.info(f"删除Agent: {agent_id}")
        
        return {
            "status": "success",
            "message": f"已删除Agent: {agent_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
