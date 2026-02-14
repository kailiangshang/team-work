"""图谱存储层 - 高级封装"""
from typing import Optional, List, Dict, Any
import json
import logging

from .client import FalkorDBClient
from ..schemas.graph import (
    KnowledgeGraph, GraphNode, TaskNode, AgentNode, SkillNode, ToolNode,
    GraphEdge, NodeType, EdgeType
)

logger = logging.getLogger(__name__)


class GraphStore:
    """图谱存储层
    
    提供高级别的图谱操作接口，封装 FalkorDB 客户端。
    """
    
    def __init__(self, client: FalkorDBClient):
        self.client = client
    
    # ==================== 项目图谱管理 ====================
    
    def create_project_graph(self, project_id: str) -> bool:
        """创建项目图谱"""
        # 存储项目元信息
        return self.client.create_node(
            label="Project",
            node_id=project_id,
            properties={"id": project_id, "type": "project_root"}
        )
    
    def delete_project_graph(self, project_id: str) -> bool:
        """删除项目图谱"""
        # 删除所有相关节点
        query = """
        MATCH (n {project_id: $project_id})
        DETACH DELETE n
        """
        try:
            self.client.execute_query(query, {"project_id": project_id})
            return True
        except Exception as e:
            logger.error(f"Failed to delete project graph: {e}")
            return False
    
    # ==================== 任务节点操作 ====================
    
    def save_task(self, project_id: str, task: TaskNode) -> bool:
        """保存任务节点"""
        properties = {
            "project_id": project_id,
            "name": task.name,
            "description": task.description,
            "duration_days": task.duration_days,
            "estimated_hours": task.estimated_hours,
            "complexity": task.complexity,
            "status": task.status,
            "priority": task.priority,
            "level": task.level or 1,
            "parent_id": task.parent_id or "",
            "required_skills": json.dumps(task.required_skills),
            "tools_needed": json.dumps(task.tools_needed),
            "dependencies": json.dumps(task.dependencies),
        }
        
        # 移除 None 值
        properties = {k: v for k, v in properties.items() if v is not None}
        
        return self.client.create_node(
            label="Task",
            node_id=task.id,
            properties=properties
        )
    
    def get_task(self, task_id: str) -> Optional[TaskNode]:
        """获取任务节点"""
        data = self.client.get_node(task_id, label="Task")
        if not data:
            return None
        
        return self._parse_task_node(data)
    
    def get_project_tasks(self, project_id: str) -> List[TaskNode]:
        """获取项目所有任务"""
        nodes = self.client.find_nodes(
            label="Task",
            where=f"n.project_id = '{project_id}'",
            limit=1000
        )
        return [self._parse_task_node(n) for n in nodes]
    
    def update_task_status(self, task_id: str, status: str) -> bool:
        """更新任务状态"""
        return self.client.update_node(task_id, {"status": status})
    
    def _parse_task_node(self, data: Dict[str, Any]) -> TaskNode:
        """解析任务节点数据"""
        required_skills = data.get("required_skills", "[]")
        if isinstance(required_skills, str):
            required_skills = json.loads(required_skills)
        
        tools_needed = data.get("tools_needed", "[]")
        if isinstance(tools_needed, str):
            tools_needed = json.loads(tools_needed)
        
        dependencies = data.get("dependencies", "[]")
        if isinstance(dependencies, str):
            dependencies = json.loads(dependencies)
        
        return TaskNode(
            id=data["id"],
            name=data.get("name", ""),
            description=data.get("description", ""),
            duration_days=data.get("duration_days", 1),
            estimated_hours=data.get("estimated_hours", 0.0),
            complexity=data.get("complexity", 1),
            status=data.get("status", "pending"),
            priority=data.get("priority", 1),
            level=data.get("level"),
            parent_id=data.get("parent_id") or None,
            required_skills=required_skills,
            tools_needed=tools_needed,
            dependencies=dependencies,
        )
    
    # ==================== Agent节点操作 ====================
    
    def save_agent(self, project_id: str, agent: AgentNode) -> bool:
        """保存Agent节点"""
        properties = {
            "project_id": project_id,
            "name": agent.name,
            "role_type": agent.role_type,
            "personality": agent.personality,
            "capabilities": json.dumps(agent.capabilities),
            "available_hours": agent.available_hours,
            "fatigue_threshold": agent.fatigue_threshold,
            "org_level": agent.org_level,
            "communication_style": agent.communication_style,
            "tools": json.dumps(agent.tools),
            "assigned_tasks": json.dumps(agent.assigned_tasks),
        }
        
        return self.client.create_node(
            label="Agent",
            node_id=agent.id,
            properties=properties
        )
    
    def get_agent(self, agent_id: str) -> Optional[AgentNode]:
        """获取Agent节点"""
        data = self.client.get_node(agent_id, label="Agent")
        if not data:
            return None
        
        return self._parse_agent_node(data)
    
    def get_project_agents(self, project_id: str) -> List[AgentNode]:
        """获取项目所有Agent"""
        nodes = self.client.find_nodes(
            label="Agent",
            where=f"n.project_id = '{project_id}'",
            limit=100
        )
        return [self._parse_agent_node(n) for n in nodes]
    
    def _parse_agent_node(self, data: Dict[str, Any]) -> AgentNode:
        """解析Agent节点数据"""
        capabilities = data.get("capabilities", "[]")
        if isinstance(capabilities, str):
            capabilities = json.loads(capabilities)
        
        tools = data.get("tools", "[]")
        if isinstance(tools, str):
            tools = json.loads(tools)
        
        assigned_tasks = data.get("assigned_tasks", "[]")
        if isinstance(assigned_tasks, str):
            assigned_tasks = json.loads(assigned_tasks)
        
        return AgentNode(
            id=data["id"],
            name=data.get("name", ""),
            role_type=data.get("role_type", ""),
            personality=data.get("personality", ""),
            capabilities=capabilities,
            available_hours=data.get("available_hours", 8.0),
            fatigue_threshold=data.get("fatigue_threshold", 8.0),
            org_level=data.get("org_level", 4),
            communication_style=data.get("communication_style", "direct"),
            tools=tools,
            assigned_tasks=assigned_tasks,
        )
    
    # ==================== 技能节点操作 ====================
    
    def save_skill(self, project_id: str, skill: SkillNode) -> bool:
        """保存技能节点"""
        properties = {
            "project_id": project_id,
            "name": skill.name,
            "category": skill.category,
        }
        
        return self.client.create_node(
            label="Skill",
            node_id=skill.id,
            properties=properties
        )
    
    def get_project_skills(self, project_id: str) -> List[SkillNode]:
        """获取项目所有技能"""
        nodes = self.client.find_nodes(
            label="Skill",
            where=f"n.project_id = '{project_id}'",
            limit=100
        )
        return [SkillNode(
            id=n["id"],
            name=n.get("name", ""),
            category=n.get("category", ""),
        ) for n in nodes]
    
    # ==================== 关系操作 ====================
    
    def create_dependency(self, task_id: str, depends_on_id: str) -> bool:
        """创建任务依赖关系"""
        return self.client.create_edge(
            source_id=task_id,
            target_id=depends_on_id,
            relation="DEPENDS_ON"
        )
    
    def create_assignment(self, task_id: str, agent_id: str) -> bool:
        """创建任务分配关系"""
        return self.client.create_edge(
            source_id=agent_id,
            target_id=task_id,
            relation="ASSIGNED_TO"
        )
    
    def create_skill_relation(self, task_id: str, skill_id: str) -> bool:
        """创建任务技能需求关系"""
        return self.client.create_edge(
            source_id=task_id,
            target_id=skill_id,
            relation="REQUIRES"
        )
    
    def create_agent_skill(self, agent_id: str, skill_id: str, level: int = 3) -> bool:
        """创建Agent技能关系"""
        return self.client.create_edge(
            source_id=agent_id,
            target_id=skill_id,
            relation="HAS_SKILL",
            properties={"level": level}
        )
    
    # ==================== 查询操作 ====================
    
    def get_task_dependencies(self, task_id: str) -> List[str]:
        """获取任务的所有依赖"""
        neighbors = self.client.get_neighbors(
            node_id=task_id,
            relation="DEPENDS_ON",
            direction="out"
        )
        return [n["id"] for n in neighbors]
    
    def get_task_assignee(self, task_id: str) -> Optional[str]:
        """获取任务的负责人"""
        neighbors = self.client.get_neighbors(
            node_id=task_id,
            relation="ASSIGNED_TO",
            direction="in"
        )
        if neighbors:
            return neighbors[0]["id"]
        return None
    
    def get_agent_tasks(self, agent_id: str) -> List[str]:
        """获取Agent的所有任务"""
        neighbors = self.client.get_neighbors(
            node_id=agent_id,
            relation="ASSIGNED_TO",
            direction="out"
        )
        return [n["id"] for n in neighbors]
    
    def find_assignable_agents(self, task_id: str) -> List[str]:
        """找到可以执行任务的Agent（基于技能匹配）"""
        query = """
        MATCH (t:Task {id: $task_id})-[:REQUIRES]->(s:Skill)<-[:HAS_SKILL]-(a:Agent)
        RETURN DISTINCT a.id
        """
        
        result = self.client.execute_query(query, {"task_id": task_id})
        
        agents = []
        if result and result.result_set:
            for row in result.result_set:
                agents.append(row[0])
        
        return agents
    
    def get_ready_tasks(self, project_id: str) -> List[str]:
        """获取就绪任务（所有依赖都已完成）"""
        query = """
        MATCH (t:Task {project_id: $project_id, status: 'pending'})
        WHERE NOT (t)-[:DEPENDS_ON]->(:Task WHERE status <> 'completed')
        RETURN t.id
        """
        
        result = self.client.execute_query(query, {"project_id": project_id})
        
        tasks = []
        if result and result.result_set:
            for row in result.result_set:
                tasks.append(row[0])
        
        return tasks
    
    # ==================== 导出操作 ====================
    
    def export_graph(self, project_id: str) -> KnowledgeGraph:
        """导出完整图谱"""
        graph = KnowledgeGraph(project_id=project_id)
        
        # 导出所有任务
        tasks = self.get_project_tasks(project_id)
        for task in tasks:
            graph.add_node(task)
        
        # 导出所有Agent
        agents = self.get_project_agents(project_id)
        for agent in agents:
            graph.add_node(agent)
        
        # 导出所有技能
        skills = self.get_project_skills(project_id)
        for skill in skills:
            graph.add_node(skill)
        
        # 导出关系
        query = f"""
        MATCH (n {{project_id: '{project_id}'}})-[r]->(m {{project_id: '{project_id}'}})
        RETURN n.id, type(r), m.id
        """
        
        result = self.client.execute_query(query)
        if result and result.result_set:
            for row in result.result_set:
                edge = GraphEdge(
                    source_id=row[0],
                    relation_type=EdgeType(row[1]),
                    target_id=row[2],
                )
                graph.add_edge(edge)
        
        return graph