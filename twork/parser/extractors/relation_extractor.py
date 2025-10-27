"""
RelationExtractor - 关系提取器

从需求分析和WBS结果中提取图谱关系
"""

from typing import Dict, Any, List, Set, Tuple
from .base_extractor import BaseExtractor
from ..templates.extraction_schema import RELATION_TYPES
from ...utils.logger import get_logger

logger = get_logger(__name__)


class RelationExtractor(BaseExtractor):
    """关系提取器"""
    
    def extract(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取关系（增强版）
        
        Args:
            input_data: {
                "requirements_and_domain": 需求分析结果,
                "wbs": WBS分解结果,
                "entities": 实体列表（可选，用于验证）
            }
        
        Returns:
            {
                "edges": [
                    {
                        "source": "源实体ID",
                        "target": "目标实体ID",
                        "relation": "关系类型",
                        "properties": {...}
                    }
                ]
            }
        """
        requirements_and_domain = input_data.get("requirements_and_domain", {})
        wbs = input_data.get("wbs", {})
        entities = input_data.get("entities", {})
        
        edges = []
        edge_set: Set[Tuple[str, str, str]] = set()  # (source, target, relation) 去重
        
        # 提取任务依赖关系
        edges.extend(self._extract_task_dependencies(wbs, edge_set))
        
        # 提取任务-角色关系
        edges.extend(self._extract_task_role_relations(wbs, edge_set))
        
        # 提取任务-工具关系
        edges.extend(self._extract_task_tool_relations(wbs, edge_set))
        
        # 提取任务-需求关系
        edges.extend(self._extract_task_requirement_relations(requirements_and_domain, wbs, edge_set))
        
        # 提取角色-技能关系
        edges.extend(self._extract_role_skill_relations(requirements_and_domain, edge_set))
        
        # 提取角色-工具关系
        edges.extend(self._extract_role_tool_relations(requirements_and_domain, edge_set))
        
        # 提取任务父子关系
        edges.extend(self._extract_task_hierarchy(wbs, edge_set))
        
        # 新增：提取任务-交付物关系
        edges.extend(self._extract_task_deliverable_relations(wbs, edge_set))
        
        # 新增：提取任务-里程碑关系
        edges.extend(self._extract_task_milestone_relations(wbs, edge_set))
        
        # 新增：提取任务-风险关系
        edges.extend(self._extract_task_risk_relations(wbs, edge_set))
        
        # 新增：提取利益相关方-需求关系
        edges.extend(self._extract_stakeholder_requirement_relations(requirements_and_domain, edge_set))
        
        # 新增：提取约束-任务关系
        edges.extend(self._extract_constraint_task_relations(requirements_and_domain, wbs, edge_set))
        
        logger.info(f"关系提取完成: 共提取 {len(edges)} 条关系")
        
        return {"edges": edges}
    
    def _extract_task_dependencies(self, wbs: Dict[str, Any], edge_set: Set) -> List[Dict[str, Any]]:
        """提取任务依赖关系（DEPENDS_ON）"""
        edges = []
        
        def _extract_from_tasks(task_list: List[Dict[str, Any]]):
            """递归提取任务依赖"""
            for task in task_list:
                task_id = task.get("task_id", "")
                dependencies = task.get("dependencies", [])
                
                for dep_id in dependencies:
                    edge_key = (task_id, dep_id, "DEPENDS_ON")
                    if edge_key not in edge_set:
                        edge = {
                            "source": task_id,
                            "target": dep_id,
                            "relation": "DEPENDS_ON",
                            "properties": {
                                "dependency_type": "前置依赖"
                            }
                        }
                        edges.append(edge)
                        edge_set.add(edge_key)
                
                # 递归处理子任务
                children = task.get("children", [])
                if children:
                    _extract_from_tasks(children)
        
        _extract_from_tasks(wbs.get("tasks", []))
        
        return edges
    
    def _extract_task_role_relations(self, wbs: Dict[str, Any], edge_set: Set) -> List[Dict[str, Any]]:
        """提取任务-角色关系（REQUIRES_ROLE）"""
        edges = []
        
        def _extract_from_tasks(task_list: List[Dict[str, Any]]):
            """递归提取任务-角色关系"""
            for task in task_list:
                task_id = task.get("task_id", "")
                roles_required = task.get("roles_required", [])
                
                for role_req in roles_required:
                    role_name = role_req.get("role", "")
                    if role_name:
                        # 需要通过角色名称查找角色ID（简化处理，假设ID为ROLE-xxx或直接使用角色名）
                        edge_key = (task_id, role_name, "REQUIRES_ROLE")
                        if edge_key not in edge_set:
                            edge = {
                                "source": task_id,
                                "target": role_name,  # 这里使用角色名称，后续可能需要映射到ID
                                "relation": "REQUIRES_ROLE",
                                "properties": {
                                    "effort_percentage": role_req.get("effort_percentage", 100),
                                    "skills": role_req.get("skills", [])
                                }
                            }
                            edges.append(edge)
                            edge_set.add(edge_key)
                
                # 递归处理子任务
                children = task.get("children", [])
                if children:
                    _extract_from_tasks(children)
        
        _extract_from_tasks(wbs.get("tasks", []))
        
        return edges
    
    def _extract_task_tool_relations(self, wbs: Dict[str, Any], edge_set: Set) -> List[Dict[str, Any]]:
        """提取任务-工具关系（REQUIRES_TOOL）"""
        edges = []
        
        def _extract_from_tasks(task_list: List[Dict[str, Any]]):
            """递归提取任务-工具关系"""
            for task in task_list:
                task_id = task.get("task_id", "")
                tools_required = task.get("tools_required", [])
                
                for tool_name in tools_required:
                    if tool_name:
                        edge_key = (task_id, tool_name, "REQUIRES_TOOL")
                        if edge_key not in edge_set:
                            edge = {
                                "source": task_id,
                                "target": tool_name,  # 这里使用工具名称
                                "relation": "REQUIRES_TOOL",
                                "properties": {
                                    "usage_type": "必需"
                                }
                            }
                            edges.append(edge)
                            edge_set.add(edge_key)
                
                # 递归处理子任务
                children = task.get("children", [])
                if children:
                    _extract_from_tasks(children)
        
        _extract_from_tasks(wbs.get("tasks", []))
        
        return edges
    
    def _extract_task_requirement_relations(
        self, 
        requirements_and_domain: Dict[str, Any], 
        wbs: Dict[str, Any], 
        edge_set: Set
    ) -> List[Dict[str, Any]]:
        """提取任务-需求关系（IMPLEMENTS）"""
        edges = []
        
        # 从需求的related_entities中提取关系（如果有任务信息）
        functional_requirements = requirements_and_domain.get("functional_requirements", [])
        
        # 简化处理：假设顶层任务对应需求（实际应用中可能需要更复杂的映射逻辑）
        tasks = wbs.get("tasks", [])
        
        # 根据需求数量和任务数量建立映射（简化版本）
        for i, req in enumerate(functional_requirements):
            req_id = req.get("id", "")
            if i < len(tasks):
                task_id = tasks[i].get("task_id", "")
                edge_key = (task_id, req_id, "IMPLEMENTS")
                if edge_key not in edge_set:
                    edge = {
                        "source": task_id,
                        "target": req_id,
                        "relation": "IMPLEMENTS",
                        "properties": {
                            "implementation_status": "计划中"
                        }
                    }
                    edges.append(edge)
                    edge_set.add(edge_key)
        
        return edges
    
    def _extract_role_skill_relations(self, requirements_and_domain: Dict[str, Any], edge_set: Set) -> List[Dict[str, Any]]:
        """提取角色-技能关系（REQUIRES_SKILL）"""
        edges = []
        
        entities = requirements_and_domain.get("entities", {})
        roles = entities.get("roles", [])
        
        for role in roles:
            role_id = role.get("id", "")
            role_name = role.get("name", "")
            skills_required = role.get("skills_required", [])
            
            for skill_name in skills_required:
                if skill_name:
                    edge_key = (role_name, skill_name, "REQUIRES_SKILL")
                    if edge_key not in edge_set:
                        edge = {
                            "source": role_name,  # 这里使用角色名称
                            "target": skill_name,  # 这里使用技能名称
                            "relation": "REQUIRES_SKILL",
                            "properties": {
                                "proficiency_level": "中级"
                            }
                        }
                        edges.append(edge)
                        edge_set.add(edge_key)
        
        return edges
    
    def _extract_role_tool_relations(self, requirements_and_domain: Dict[str, Any], edge_set: Set) -> List[Dict[str, Any]]:
        """提取角色-工具关系（USES_TOOL）"""
        edges = []
        
        entities = requirements_and_domain.get("entities", {})
        skills = entities.get("skills", [])
        
        # 从技能的related_tools中提取角色-工具关系
        for skill in skills:
            skill_name = skill.get("name", "")
            related_tools = skill.get("related_tools", [])
            
            # 简化处理：假设技能和工具的关系可以推导出角色和工具的关系
            # 实际应用中可能需要更复杂的推理逻辑
            for tool_name in related_tools:
                if tool_name:
                    # 这里需要找到拥有该技能的角色
                    # 简化版本暂不实现复杂映射
                    pass
        
        return edges
    
    def _extract_task_hierarchy(self, wbs: Dict[str, Any], edge_set: Set) -> List[Dict[str, Any]]:
        """提取任务父子关系（CHILD_OF）"""
        edges = []
        
        def _extract_from_tasks(task_list: List[Dict[str, Any]]):
            """递归提取任务层级关系"""
            for task in task_list:
                task_id = task.get("task_id", "")
                parent_task_id = task.get("parent_task_id")
                
                if parent_task_id:
                    edge_key = (task_id, parent_task_id, "CHILD_OF")
                    if edge_key not in edge_set:
                        edge = {
                            "source": task_id,
                            "target": parent_task_id,
                            "relation": "CHILD_OF",
                            "properties": {
                                "level": task.get("level", 1)
                            }
                        }
                        edges.append(edge)
                        edge_set.add(edge_key)
                
                # 递归处理子任务
                children = task.get("children", [])
                if children:
                    _extract_from_tasks(children)
        
        _extract_from_tasks(wbs.get("tasks", []))
        
        return edges
    
    def _extract_task_deliverable_relations(self, wbs: Dict[str, Any], edge_set: Set) -> List[Dict[str, Any]]:
        """提取任务-交付物关系(DELIVERS)(新增)"""
        edges = []
        
        def _extract_from_tasks(task_list: List[Dict[str, Any]]):
            """递归提取任务-交付物关系"""
            for task in task_list:
                task_id = task.get("task_id", "")
                deliverables = task.get("deliverables", [])
                
                for deliv_name in deliverables:
                    if isinstance(deliv_name, str) and deliv_name:
                        edge_key = (task_id, deliv_name, "DELIVERS")
                        if edge_key not in edge_set:
                            edge = {
                                "source": task_id,
                                "target": deliv_name,
                                "relation": "DELIVERS",
                                "properties": {
                                    "delivery_type": "正式交付物"
                                }
                            }
                            edges.append(edge)
                            edge_set.add(edge_key)
                
                children = task.get("children", [])
                if children:
                    _extract_from_tasks(children)
        
        _extract_from_tasks(wbs.get("tasks", []))
        
        return edges
    
    def _extract_task_milestone_relations(self, wbs: Dict[str, Any], edge_set: Set) -> List[Dict[str, Any]]:
        """提取任务-里程碑关系(CONTRIBUTES_TO)(新增)"""
        edges = []
        # 简化处理:假设顶层任务对应里程碑(实际应用中需要更复杂的映射逻辑)
        return edges
    
    def _extract_task_risk_relations(self, wbs: Dict[str, Any], edge_set: Set) -> List[Dict[str, Any]]:
        """提取任务-风险关系(HAS_RISK)(新增)"""
        edges = []
        
        def _extract_from_tasks(task_list: List[Dict[str, Any]]):
            """递归提取任务-风险关系"""
            for task in task_list:
                task_id = task.get("task_id", "")
                risks = task.get("risks", [])
                
                for risk in risks:
                    risk_desc = risk.get("description", "")
                    if risk_desc:
                        edge_key = (task_id, risk_desc, "HAS_RISK")
                        if edge_key not in edge_set:
                            edge = {
                                "source": task_id,
                                "target": risk_desc,
                                "relation": "HAS_RISK",
                                "properties": {
                                    "probability": risk.get("probability", "中"),
                                    "impact": risk.get("impact", "中"),
                                    "mitigation": risk.get("mitigation", ""),
                                    "contingency_plan": risk.get("contingency_plan", "")
                                }
                            }
                            edges.append(edge)
                            edge_set.add(edge_key)
                
                children = task.get("children", [])
                if children:
                    _extract_from_tasks(children)
        
        _extract_from_tasks(wbs.get("tasks", []))
        
        return edges
    
    def _extract_stakeholder_requirement_relations(self, requirements_and_domain: Dict[str, Any], edge_set: Set) -> List[Dict[str, Any]]:
        """提取利益相关方-需求关系(STAKEHOLDER_OF)(新增)"""
        edges = []
        
        stakeholders = requirements_and_domain.get("stakeholders", [])
        functional_requirements = requirements_and_domain.get("functional_requirements", [])
        
        # 简化处理:假设每个利益相关方关注所有需求
        for stakeholder in stakeholders:
            stake_name = stakeholder.get("name", "")
            for req in functional_requirements:
                req_id = req.get("id", "")
                if stake_name and req_id:
                    edge_key = (stake_name, req_id, "STAKEHOLDER_OF")
                    if edge_key not in edge_set:
                        edge = {
                            "source": stake_name,
                            "target": req_id,
                            "relation": "STAKEHOLDER_OF",
                            "properties": {
                                "influence": stakeholder.get("influence", "中")
                            }
                        }
                        edges.append(edge)
                        edge_set.add(edge_key)
        
        return edges
    
    def _extract_constraint_task_relations(self, requirements_and_domain: Dict[str, Any], wbs: Dict[str, Any], edge_set: Set) -> List[Dict[str, Any]]:
        """提取约束-任务关系(CONSTRAINS)(新增)"""
        edges = []
        
        # 简化处理:假设约束对所有顶层任务都有影响
        constraints = requirements_and_domain.get("constraints", {})
        tasks = wbs.get("tasks", [])
        
        # 处理时间约束
        if "time" in constraints and constraints["time"]:
            for task in tasks:
                task_id = task.get("task_id", "")
                if task_id:
                    edge_key = ("time_constraint", task_id, "CONSTRAINS")
                    if edge_key not in edge_set:
                        edge = {
                            "source": "time_constraint",
                            "target": task_id,
                            "relation": "CONSTRAINS",
                            "properties": {
                                "constraint_type": "时间",
                                "constraint_value": constraints["time"]
                            }
                        }
                        edges.append(edge)
                        edge_set.add(edge_key)
        
        return edges
