"""图数据结构定义 - 核心数据模型"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class NodeType(Enum):
    """节点类型"""
    TASK = "task"
    AGENT = "agent"
    SKILL = "skill"
    TOOL = "tool"
    DOMAIN = "domain"
    EVENT = "event"


class EdgeType(Enum):
    """边类型（关系）"""
    # 任务关系
    DEPENDS_ON = "depends_on"         # 任务依赖
    PARENT_OF = "parent_of"           # 父子任务
    
    # Agent关系
    ASSIGNED_TO = "assigned_to"       # 任务分配给Agent
    CAN_PERFORM = "can_perform"       # Agent具备某技能
    
    # 技能关系
    REQUIRES = "requires"             # 任务需要某技能
    HAS_SKILL = "has_skill"           # Agent拥有某技能
    
    # 工具关系
    NEEDS_TOOL = "needs_tool"         # 任务需要某工具
    CAN_USE = "can_use"               # Agent可以使用某工具
    
    # 领域关系
    BELONGS_TO = "belongs_to"         # 任务属于某领域


@dataclass
class GraphNode:
    """图谱节点基类"""
    id: str                           # 唯一标识 (T001, A001, S001...)
    type: NodeType                    # 节点类型
    name: str                         # 显示名称
    properties: Dict[str, Any] = field(default_factory=dict)
    
    # 向量表示（用于语义检索）
    embedding: Optional[List[float]] = None
    
    # 层级关系（用于WBS）
    level: Optional[int] = None       # WBS层级 (1-4)
    parent_id: Optional[str] = None   # 父节点ID
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "properties": self.properties,
            "embedding": self.embedding,
            "level": self.level,
            "parent_id": self.parent_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphNode":
        """从字典创建"""
        data["type"] = NodeType(data["type"])
        return cls(**data)


@dataclass
class TaskNode(GraphNode):
    """任务节点"""
    type: NodeType = field(default=NodeType.TASK, init=False)
    
    # 任务特有属性
    description: str = ""
    duration_days: int = 1
    estimated_hours: float = 0.0
    complexity: int = 1              # 1-10
    status: str = "pending"           # pending/in_progress/completed
    priority: int = 1                 # 1-10
    
    # 技能和工具需求
    required_skills: List[Dict[str, Any]] = field(default_factory=list)  # [{"skill": "Python", "level": 3}]
    tools_needed: List[str] = field(default_factory=list)
    
    # 依赖关系（存储在properties中，便于图数据库查询）
    dependencies: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """初始化后处理"""
        # 确保type是TASK
        self.type = NodeType.TASK
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base = super().to_dict()
        base.update({
            "description": self.description,
            "duration_days": self.duration_days,
            "estimated_hours": self.estimated_hours,
            "complexity": self.complexity,
            "status": self.status,
            "priority": self.priority,
            "required_skills": self.required_skills,
            "tools_needed": self.tools_needed,
            "dependencies": self.dependencies,
        })
        return base


@dataclass
class AgentNode(GraphNode):
    """Agent节点"""
    type: NodeType = field(default=NodeType.AGENT, init=False)
    
    # Agent特有属性
    role_type: str = ""               # 角色类型 (开发/测试/设计...)
    personality: str = ""             # 性格描述
    capabilities: List[Dict[str, Any]] = field(default_factory=list)  # 能力列表
    available_hours: float = 8.0      # 每日可用工时
    fatigue_threshold: float = 8.0    # 疲劳阈值
    org_level: int = 4                # 组织层级 (1-4)
    communication_style: str = "direct"  # 沟通风格
    tools: List[str] = field(default_factory=list)
    assigned_tasks: List[str] = field(default_factory=list)  # 已分配任务ID列表
    
    def __post_init__(self):
        self.type = NodeType.AGENT
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "role_type": self.role_type,
            "personality": self.personality,
            "capabilities": self.capabilities,
            "available_hours": self.available_hours,
            "fatigue_threshold": self.fatigue_threshold,
            "org_level": self.org_level,
            "communication_style": self.communication_style,
            "tools": self.tools,
            "assigned_tasks": self.assigned_tasks,
        })
        return base


@dataclass
class SkillNode(GraphNode):
    """技能节点"""
    type: NodeType = field(default=NodeType.SKILL, init=False)
    
    # 技能特有属性
    category: str = ""                # 技能类别 (技术/管理/设计...)
    proficiency_levels: List[int] = field(default_factory=list)  # 熟练度等级 (1-5)
    related_tasks: List[str] = field(default_factory=list)
    related_agents: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.type = NodeType.SKILL
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "category": self.category,
            "proficiency_levels": self.proficiency_levels,
            "related_tasks": self.related_tasks,
            "related_agents": self.related_agents,
        })
        return base


@dataclass
class ToolNode(GraphNode):
    """工具节点"""
    type: NodeType = field(default=NodeType.TOOL, init=False)
    
    # 工具特有属性
    category: str = ""                # 工具类别 (IDE/框架/平台...)
    related_skills: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.type = NodeType.TOOL
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "category": self.category,
            "related_skills": self.related_skills,
        })
        return base


@dataclass
class GraphEdge:
    """图谱边"""
    source_id: str                    # 起始节点ID
    target_id: str                    # 目标节点ID
    relation_type: EdgeType           # 关系类型
    weight: float = 1.0               # 权重
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type.value,
            "weight": self.weight,
            "properties": self.properties,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphEdge":
        data["relation_type"] = EdgeType(data["relation_type"])
        return cls(**data)


@dataclass
class KnowledgeGraph:
    """知识图谱"""
    project_id: str
    nodes: Dict[str, GraphNode] = field(default_factory=dict)
    edges: List[GraphEdge] = field(default_factory=list)
    version: int = 1
    
    def add_node(self, node: GraphNode):
        """添加节点"""
        self.nodes[node.id] = node
    
    def add_edge(self, edge: GraphEdge):
        """添加边"""
        self.edges.append(edge)
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """获取节点"""
        return self.nodes.get(node_id)
    
    def get_neighbors(
        self, 
        node_id: str, 
        relation_type: Optional[EdgeType] = None
    ) -> List[GraphNode]:
        """获取邻居节点"""
        neighbor_ids = []
        for edge in self.edges:
            if edge.source_id == node_id:
                if relation_type is None or edge.relation_type == relation_type:
                    neighbor_ids.append(edge.target_id)
            elif edge.target_id == node_id:
                if relation_type is None or edge.relation_type == relation_type:
                    neighbor_ids.append(edge.source_id)
        
        return [self.nodes[nid] for nid in neighbor_ids if nid in self.nodes]
    
    def get_outgoing_edges(
        self, 
        node_id: str, 
        relation_type: Optional[EdgeType] = None
    ) -> List[GraphEdge]:
        """获取出边"""
        edges = []
        for edge in self.edges:
            if edge.source_id == node_id:
                if relation_type is None or edge.relation_type == relation_type:
                    edges.append(edge)
        return edges
    
    def get_incoming_edges(
        self, 
        node_id: str, 
        relation_type: Optional[EdgeType] = None
    ) -> List[GraphEdge]:
        """获取入边"""
        edges = []
        for edge in self.edges:
            if edge.target_id == node_id:
                if relation_type is None or edge.relation_type == relation_type:
                    edges.append(edge)
        return edges
    
    def find_path(self, start_id: str, end_id: str) -> List[str]:
        """查找两点之间的路径（BFS）"""
        if start_id not in self.nodes or end_id not in self.nodes:
            return []
        
        queue = [(start_id, [start_id])]
        visited = {start_id}
        
        while queue:
            node_id, path = queue.pop(0)
            
            if node_id == end_id:
                return path
            
            for neighbor in self.get_neighbors(node_id):
                if neighbor.id not in visited:
                    visited.add(neighbor.id)
                    queue.append((neighbor.id, path + [neighbor.id]))
        
        return []
    
    def get_tasks(self) -> List[TaskNode]:
        """获取所有任务节点"""
        return [n for n in self.nodes.values() if n.type == NodeType.TASK]
    
    def get_agents(self) -> List[AgentNode]:
        """获取所有Agent节点"""
        return [n for n in self.nodes.values() if n.type == NodeType.AGENT]
    
    def get_skills(self) -> List[SkillNode]:
        """获取所有技能节点"""
        return [n for n in self.nodes.values() if n.type == NodeType.SKILL]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "project_id": self.project_id,
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "edges": [e.to_dict() for e in self.edges],
            "version": self.version,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeGraph":
        """从字典创建"""
        graph = cls(project_id=data["project_id"], version=data.get("version", 1))
        
        # 重建节点
        for node_id, node_data in data.get("nodes", {}).items():
            node_type = NodeType(node_data["type"])
            if node_type == NodeType.TASK:
                node = TaskNode(
                    id=node_data["id"],
                    name=node_data["name"],
                    description=node_data.get("description", ""),
                    duration_days=node_data.get("duration_days", 1),
                    estimated_hours=node_data.get("estimated_hours", 0.0),
                    complexity=node_data.get("complexity", 1),
                    status=node_data.get("status", "pending"),
                    priority=node_data.get("priority", 1),
                    required_skills=node_data.get("required_skills", []),
                    tools_needed=node_data.get("tools_needed", []),
                    dependencies=node_data.get("dependencies", []),
                    properties=node_data.get("properties", {}),
                    level=node_data.get("level"),
                    parent_id=node_data.get("parent_id"),
                )
            elif node_type == NodeType.AGENT:
                node = AgentNode(
                    id=node_data["id"],
                    name=node_data["name"],
                    role_type=node_data.get("role_type", ""),
                    personality=node_data.get("personality", ""),
                    capabilities=node_data.get("capabilities", []),
                    available_hours=node_data.get("available_hours", 8.0),
                    properties=node_data.get("properties", {}),
                )
            elif node_type == NodeType.SKILL:
                node = SkillNode(
                    id=node_data["id"],
                    name=node_data["name"],
                    category=node_data.get("category", ""),
                    properties=node_data.get("properties", {}),
                )
            else:
                node = GraphNode(
                    id=node_data["id"],
                    type=node_type,
                    name=node_data["name"],
                    properties=node_data.get("properties", {}),
                )
            graph.add_node(node)
        
        # 重建边
        for edge_data in data.get("edges", []):
            edge = GraphEdge.from_dict(edge_data)
            graph.add_edge(edge)
        
        return graph