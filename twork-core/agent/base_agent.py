"""Agent 基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..llm.base import BaseLLM, ChatMessage
from ..schemas.graph import AgentNode

logger = logging.getLogger(__name__)


@dataclass
class AgentState:
    """Agent 状态"""
    current_task_id: Optional[str] = None
    energy: float = 100.0              # 精力值 0-100
    mood: float = 50.0                 # 心情值 0-100
    workload: float = 0.0              # 工作负载 0-100
    completed_tasks: List[str] = field(default_factory=list)
    messages: List[Dict[str, Any]] = field(default_factory=list)


class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(
        self,
        agent_node: AgentNode,
        llm: BaseLLM,
    ):
        self.node = agent_node
        self.llm = llm
        self.state = AgentState()
    
    @property
    def id(self) -> str:
        return self.node.id
    
    @property
    def name(self) -> str:
        return self.node.name
    
    @property
    def role_type(self) -> str:
        return self.node.role_type
    
    @abstractmethod
    async def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行动作"""
        pass
    
    @abstractmethod
    async def respond(self, message: str, context: Dict[str, Any]) -> str:
        """响应消息"""
        pass
    
    def update_state(self, **kwargs):
        """更新状态"""
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
    
    def assign_task(self, task_id: str):
        """分配任务"""
        self.state.current_task_id = task_id
        if task_id not in self.node.assigned_tasks:
            self.node.assigned_tasks.append(task_id)
    
    def complete_task(self, task_id: str):
        """完成任务"""
        if task_id in self.node.assigned_tasks:
            self.node.assigned_tasks.remove(task_id)
        if task_id not in self.state.completed_tasks:
            self.state.completed_tasks.append(task_id)
        if self.state.current_task_id == task_id:
            self.state.current_task_id = None
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """添加消息记录"""
        self.state.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        })
    
    def get_recent_messages(self, n: int = 10) -> List[Dict[str, Any]]:
        """获取最近的消息"""
        return self.state.messages[-n:]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "role_type": self.role_type,
            "personality": self.node.personality,
            "capabilities": self.node.capabilities,
            "tools": self.node.tools,
            "state": {
                "current_task_id": self.state.current_task_id,
                "energy": self.state.energy,
                "mood": self.state.mood,
                "workload": self.state.workload,
                "completed_tasks": self.state.completed_tasks,
            },
        }