"""项目相关数据结构"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime


class ProjectStatus(Enum):
    """项目状态"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class DomainType(Enum):
    """项目领域"""
    SOFTWARE = "software"
    MARKETING = "marketing"
    DESIGN = "design"
    RESEARCH = "research"
    OTHER = "other"


@dataclass
class Project:
    """项目"""
    id: str
    name: str
    description: str = ""
    domain: DomainType = DomainType.OTHER
    status: ProjectStatus = ProjectStatus.DRAFT
    
    # 时间信息
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # 配置
    settings: Dict[str, Any] = field(default_factory=dict)
    
    # 关联ID
    document_id: Optional[str] = None
    graph_id: Optional[str] = None
    simulation_id: Optional[str] = None
    
    # 统计信息
    task_count: int = 0
    agent_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain.value,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "settings": self.settings,
            "document_id": self.document_id,
            "graph_id": self.graph_id,
            "simulation_id": self.simulation_id,
            "task_count": self.task_count,
            "agent_count": self.agent_count,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            domain=DomainType(data.get("domain", "other")),
            status=ProjectStatus(data.get("status", "draft")),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            settings=data.get("settings", {}),
            document_id=data.get("document_id"),
            graph_id=data.get("graph_id"),
            simulation_id=data.get("simulation_id"),
            task_count=data.get("task_count", 0),
            agent_count=data.get("agent_count", 0),
        )