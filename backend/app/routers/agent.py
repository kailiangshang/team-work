"""Agent API 路由"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel

router = APIRouter()


class AgentInfo(BaseModel):
    """Agent 信息"""
    id: str
    name: str
    role: str
    status: str = "idle"
    skills: List[str] = []


# 存储 Agent
agents: Dict[str, AgentInfo] = {}


@router.get("/")
async def list_agents() -> List[Dict]:
    """列出所有 Agent"""
    return [a.model_dump() for a in agents.values()]


@router.get("/{agent_id}")
async def get_agent(agent_id: str) -> AgentInfo:
    """获取 Agent 详情"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents[agent_id]


@router.post("/{agent_id}/chat")
async def chat_with_agent(agent_id: str, message: str) -> Dict[str, Any]:
    """与 Agent 对话"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # TODO: 实现与 Agent 的对话
    return {
        "agent_id": agent_id,
        "response": "This is a placeholder response.",
    }


@router.get("/{agent_id}/tasks")
async def get_agent_tasks(agent_id: str) -> List[Dict]:
    """获取 Agent 的任务列表"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # TODO: 实现获取任务
    return []