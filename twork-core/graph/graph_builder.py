"""图谱构建器 - 从解析文档构建知识图谱"""
from typing import List, Dict, Any, Optional
import uuid
import logging

from .graph_store import GraphStore
from ..schemas.graph import (
    KnowledgeGraph, TaskNode, AgentNode, SkillNode, ToolNode,
    GraphEdge, NodeType, EdgeType
)
from ..schemas.document import ParsedDocument, ExtractedEntity, ExtractedRelation

logger = logging.getLogger(__name__)


class GraphBuilder:
    """图谱构建器
    
    从解析后的文档构建知识图谱，支持：
    - 任务节点创建
    - Agent节点创建
    - 技能/工具节点创建
    - 关系构建
    """
    
    def __init__(self, graph_store: GraphStore):
        self.store = graph_store
    
    def build_from_parsed_document(
        self, 
        project_id: str, 
        parsed_doc: ParsedDocument
    ) -> KnowledgeGraph:
        """从解析文档构建图谱
        
        Args:
            project_id: 项目ID
            parsed_doc: 解析后的文档
        
        Returns:
            构建的知识图谱
        """
        graph = KnowledgeGraph(project_id=project_id)
        
        # 1. 创建技能节点
        skill_id_map = {}
        for skill_entity in parsed_doc.skills:
            skill_id = f"S{len(skill_id_map)+1:03d}"
            skill_id_map[skill_entity.name] = skill_id
            
            skill = SkillNode(
                id=skill_id,
                name=skill_entity.name,
                category=skill_entity.properties.get("category", "general"),
            )
            graph.add_node(skill)
            self.store.save_skill(project_id, skill)
        
        # 2. 创建工具节点
        tool_id_map = {}
        for tool_entity in parsed_doc.tools:
            tool_id = f"TL{len(tool_id_map)+1:03d}"
            tool_id_map[tool_entity.name] = tool_id
            
            tool = ToolNode(
                id=tool_id,
                name=tool_entity.name,
                category=tool_entity.properties.get("category", "general"),
            )
            graph.add_node(tool)
        
        # 3. 创建任务节点（WBS）
        task_id_map = {}
        for task_entity in parsed_doc.tasks:
            task_id = task_entity.properties.get("id", f"T{len(task_id_map)+1:03d}")
            task_id_map[task_entity.name] = task_id
            
            task = TaskNode(
                id=task_id,
                name=task_entity.name,
                description=task_entity.description,
                level=task_entity.properties.get("level", 1),
                parent_id=task_entity.properties.get("parent_id"),
                duration_days=task_entity.properties.get("duration_days", 1),
                complexity=task_entity.properties.get("complexity", 3),
                priority=task_entity.properties.get("priority", 3),
                required_skills=task_entity.properties.get("required_skills", []),
                tools_needed=task_entity.properties.get("tools_needed", []),
                dependencies=task_entity.properties.get("dependencies", []),
            )
            graph.add_node(task)
            self.store.save_task(project_id, task)
        
        # 4. 创建Agent节点
        agent_id_map = {}
        for role_entity in parsed_doc.roles:
            agent_id = f"A{len(agent_id_map)+1:03d}"
            agent_id_map[role_entity.name] = agent_id
            
            agent = AgentNode(
                id=agent_id,
                name=role_entity.name,
                role_type=role_entity.properties.get("role_type", "general"),
                personality=role_entity.properties.get("personality", ""),
                capabilities=role_entity.properties.get("capabilities", []),
                tools=role_entity.properties.get("tools", []),
            )
            graph.add_node(agent)
            self.store.save_agent(project_id, agent)
        
        # 5. 创建关系
        for relation in parsed_doc.relations:
            self._create_relation(graph, relation, task_id_map, agent_id_map, skill_id_map)
        
        return graph
    
    def _create_relation(
        self,
        graph: KnowledgeGraph,
        relation: ExtractedRelation,
        task_id_map: Dict[str, str],
        agent_id_map: Dict[str, str],
        skill_id_map: Dict[str, str],
    ):
        """创建关系"""
        # 解析源和目标ID
        source_id = self._resolve_entity_id(relation.source, task_id_map, agent_id_map, skill_id_map)
        target_id = self._resolve_entity_id(relation.target, task_id_map, agent_id_map, skill_id_map)
        
        if not source_id or not target_id:
            logger.warning(f"Cannot resolve relation: {relation.source} -> {relation.target}")
            return
        
        # 解析关系类型
        try:
            edge_type = EdgeType(relation.relation_type.upper())
        except ValueError:
            logger.warning(f"Unknown relation type: {relation.relation_type}")
            return
        
        edge = GraphEdge(
            source_id=source_id,
            target_id=target_id,
            relation_type=edge_type,
            properties=relation.properties,
        )
        graph.add_edge(edge)
        
        # 同步到数据库
        self.store.client.create_edge(
            source_id=source_id,
            target_id=target_id,
            relation=edge_type.value,
            properties=relation.properties,
        )
    
    def _resolve_entity_id(
        self,
        name: str,
        task_id_map: Dict[str, str],
        agent_id_map: Dict[str, str],
        skill_id_map: Dict[str, str],
    ) -> Optional[str]:
        """解析实体ID"""
        if name in task_id_map:
            return task_id_map[name]
        if name in agent_id_map:
            return agent_id_map[name]
        if name in skill_id_map:
            return skill_id_map[name]
        # 可能已经是ID
        if name.startswith(("T", "A", "S", "TL")):
            return name
        return None
    
    def build_wbs_tree(
        self,
        project_id: str,
        tasks: List[Dict[str, Any]],
        parent_id: Optional[str] = None,
        level: int = 1,
        task_counter: Dict[str, int] = None,
    ) -> List[TaskNode]:
        """构建WBS任务树
        
        Args:
            project_id: 项目ID
            tasks: 任务数据列表
            parent_id: 父任务ID
            level: 当前层级
            task_counter: 任务计数器
        
        Returns:
            任务节点列表
        """
        if task_counter is None:
            task_counter = {"count": 0}
        
        result = []
        
        for i, task_data in enumerate(tasks, 1):
            # 生成任务ID
            if parent_id:
                task_id = f"{parent_id}-{i}"
            else:
                task_counter["count"] += 1
                task_id = f"T{task_counter['count']:03d}"
            
            task = TaskNode(
                id=task_id,
                name=task_data.get("name", f"Task {task_id}"),
                description=task_data.get("description", ""),
                level=level,
                parent_id=parent_id,
                duration_days=task_data.get("duration_days", 1),
                complexity=task_data.get("complexity", 3),
                priority=task_data.get("priority", 3),
                required_skills=task_data.get("required_skills", []),
                tools_needed=task_data.get("tools_needed", []),
                dependencies=task_data.get("dependencies", []),
            )
            
            result.append(task)
            self.store.save_task(project_id, task)
            
            # 处理子任务
            subtasks = task_data.get("subtasks", [])
            if subtasks:
                children = self.build_wbs_tree(
                    project_id=project_id,
                    tasks=subtasks,
                    parent_id=task_id,
                    level=level + 1,
                    task_counter=task_counter,
                )
                result.extend(children)
                
                # 创建父子关系
                for child in children:
                    if child.parent_id == task_id:
                        self.store.client.create_edge(
                            source_id=task_id,
                            target_id=child.id,
                            relation="PARENT_OF",
                        )
        
        return result
    
    def create_task_dependencies(
        self,
        project_id: str,
        dependencies: List[Dict[str, str]],
    ):
        """创建任务依赖关系
        
        Args:
            project_id: 项目ID
            dependencies: 依赖列表 [{"from": "T001", "to": "T002"}, ...]
        """
        for dep in dependencies:
            from_id = dep.get("from")
            to_id = dep.get("to")
            
            if from_id and to_id:
                self.store.create_dependency(
                    task_id=to_id,
                    depends_on_id=from_id,
                )
    
    def assign_agent_to_task(
        self,
        project_id: str,
        agent_id: str,
        task_id: str,
    ):
        """分配Agent到任务"""
        self.store.create_assignment(
            task_id=task_id,
            agent_id=agent_id,
        )
        
        # 更新Agent的assigned_tasks
        agent = self.store.get_agent(agent_id)
        if agent:
            if task_id not in agent.assigned_tasks:
                agent.assigned_tasks.append(task_id)
                self.store.save_agent(project_id, agent)