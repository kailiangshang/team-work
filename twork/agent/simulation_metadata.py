"""
模拟元信息数据结构

定义模拟阶段的元信息结构,用于记录用户修改、任务删除、Agent删除等操作。
支持可编辑性设计原则。
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AgentModification(BaseModel):
    """Agent修改记录"""
    agent_id: str = Field(..., description="Agent ID")
    changes: Dict[str, Any] = Field(default_factory=dict, description="修改的字段")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="修改时间")


class TaskModification(BaseModel):
    """任务修改记录"""
    task_id: str = Field(..., description="任务ID")
    changes: Dict[str, Any] = Field(default_factory=dict, description="修改的字段")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="修改时间")


class SimulationConfig(BaseModel):
    """模拟配置"""
    total_days: int = Field(30, description="总工期(天)")
    enable_env_agent: bool = Field(True, description="是否启用环境Agent")
    env_event_probability: float = Field(0.2, ge=0.0, le=1.0, description="环境事件发生概率")
    working_hours_per_day: float = Field(8.0, description="每日工作时长(小时)")


class SimulationMetadata(BaseModel):
    """
    模拟元信息
    
    记录模拟阶段的所有用户修改,支持可编辑性设计。
    只要项目前置条件(文档、需求、领域)未变,元信息可复用。
    """
    
    project_id: int = Field(..., description="项目ID")
    base_version_id: str = Field("v1.0", description="初始化版本,用于判断是否需重新初始化")
    
    simulation_config: SimulationConfig = Field(
        default_factory=SimulationConfig,
        description="模拟配置"
    )
    
    # 用户修改记录
    removed_agents: List[str] = Field(
        default_factory=list,
        description="删除的Agent ID列表"
    )
    
    removed_tasks: List[str] = Field(
        default_factory=list,
        description="删除的任务ID列表"
    )
    
    modified_agents: List[AgentModification] = Field(
        default_factory=list,
        description="修改的Agent列表"
    )
    
    modified_tasks: List[TaskModification] = Field(
        default_factory=list,
        description="修改的任务列表"
    )
    
    manual_assignments: Dict[str, str] = Field(
        default_factory=dict,
        description="用户手动指定的任务分配 {task_id: agent_id}"
    )
    
    completed_tasks: List[str] = Field(
        default_factory=list,
        description="用户标记为已完成的任务ID列表"
    )
    
    # 元数据
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="创建时间"
    )
    
    updated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="更新时间"
    )
    
    def add_removed_agent(self, agent_id: str):
        """添加删除的Agent"""
        if agent_id not in self.removed_agents:
            self.removed_agents.append(agent_id)
            self.updated_at = datetime.now().isoformat()
    
    def add_removed_task(self, task_id: str):
        """添加删除的任务"""
        if task_id not in self.removed_tasks:
            self.removed_tasks.append(task_id)
            self.updated_at = datetime.now().isoformat()
    
    def modify_agent(self, agent_id: str, changes: Dict[str, Any]):
        """记录Agent修改"""
        modification = AgentModification(agent_id=agent_id, changes=changes)
        
        # 移除旧的修改记录(如果存在)
        self.modified_agents = [
            m for m in self.modified_agents if m.agent_id != agent_id
        ]
        
        self.modified_agents.append(modification)
        self.updated_at = datetime.now().isoformat()
    
    def modify_task(self, task_id: str, changes: Dict[str, Any]):
        """记录任务修改"""
        modification = TaskModification(task_id=task_id, changes=changes)
        
        # 移除旧的修改记录(如果存在)
        self.modified_tasks = [
            m for m in self.modified_tasks if m.task_id != task_id
        ]
        
        self.modified_tasks.append(modification)
        self.updated_at = datetime.now().isoformat()
    
    def set_manual_assignment(self, task_id: str, agent_id: str):
        """设置手动任务分配"""
        self.manual_assignments[task_id] = agent_id
        self.updated_at = datetime.now().isoformat()
    
    def mark_task_completed(self, task_id: str):
        """标记任务为已完成"""
        if task_id not in self.completed_tasks:
            self.completed_tasks.append(task_id)
            self.updated_at = datetime.now().isoformat()
    
    def is_agent_removed(self, agent_id: str) -> bool:
        """检查Agent是否被删除"""
        return agent_id in self.removed_agents
    
    def is_task_removed(self, task_id: str) -> bool:
        """检查任务是否被删除"""
        return task_id in self.removed_tasks
    
    def get_agent_modifications(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取Agent的修改内容"""
        for mod in self.modified_agents:
            if mod.agent_id == agent_id:
                return mod.changes
        return None
    
    def get_task_modifications(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务的修改内容"""
        for mod in self.modified_tasks:
            if mod.task_id == task_id:
                return mod.changes
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationMetadata":
        """从字典创建"""
        return cls(**data)


def apply_metadata_to_agents(
    agents: List[Dict[str, Any]],
    metadata: SimulationMetadata
) -> List[Dict[str, Any]]:
    """
    应用元信息到Agent列表
    
    Args:
        agents: Agent列表
        metadata: 模拟元信息
        
    Returns:
        应用修改后的Agent列表
    """
    # 过滤删除的Agent
    agents = [a for a in agents if not metadata.is_agent_removed(a["agent_id"])]
    
    # 应用修改
    for agent in agents:
        agent_id = agent["agent_id"]
        modifications = metadata.get_agent_modifications(agent_id)
        if modifications:
            agent.update(modifications)
    
    return agents


def apply_metadata_to_tasks(
    tasks: List[Dict[str, Any]],
    metadata: SimulationMetadata
) -> List[Dict[str, Any]]:
    """
    应用元信息到任务列表
    
    Args:
        tasks: 任务列表
        metadata: 模拟元信息
        
    Returns:
        应用修改后的任务列表
    """
    # 过滤删除的任务
    tasks = [t for t in tasks if not metadata.is_task_removed(t["task_id"])]
    
    # 应用修改
    for task in tasks:
        task_id = task["task_id"]
        
        # 应用任务修改
        modifications = metadata.get_task_modifications(task_id)
        if modifications:
            task.update(modifications)
        
        # 标记已完成的任务
        if task_id in metadata.completed_tasks:
            task["status"] = "completed"
    
    return tasks


def apply_manual_assignments(
    agents: List[Dict[str, Any]],
    metadata: SimulationMetadata
) -> List[Dict[str, Any]]:
    """
    应用手动任务分配
    
    Args:
        agents: Agent列表
        metadata: 模拟元信息
        
    Returns:
        更新后的Agent列表
    """
    if not metadata.manual_assignments:
        return agents
    
    # 清除原有的任务分配
    for agent in agents:
        agent["assigned_tasks"] = []
    
    # 应用手动分配
    for task_id, agent_id in metadata.manual_assignments.items():
        for agent in agents:
            if agent["agent_id"] == agent_id:
                if "assigned_tasks" not in agent:
                    agent["assigned_tasks"] = []
                if task_id not in agent["assigned_tasks"]:
                    agent["assigned_tasks"].append(task_id)
                break
    
    return agents
