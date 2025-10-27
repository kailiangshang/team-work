"""
EntityExtractor - 实体提取器

从需求分析和WBS结果中提取图谱实体（任务、角色、工具、技能、需求）
"""

from typing import Dict, Any, List, Set
from .base_extractor import BaseExtractor
from ..templates.extraction_schema import ENTITY_TYPES
from ...utils.logger import get_logger

logger = get_logger(__name__)


class EntityExtractor(BaseExtractor):
    """实体提取器"""
    
    def extract(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取实体（增强版）
        
        Args:
            input_data: {
                "requirements_and_domain": 需求分析结果,
                "wbs": WBS分解结果
            }
        
        Returns:
            {
                "nodes": [
                    {
                        "id": "实体唯一ID",
                        "type": "TASK/ROLE/TOOL/SKILL/REQUIREMENT/DELIVERABLE/MILESTONE/RISK/STAKEHOLDER/CONSTRAINT",
                        "properties": {...}
                    }
                ]
            }
        """
        requirements_and_domain = input_data.get("requirements_and_domain", {})
        wbs = input_data.get("wbs", {})
        
        nodes = []
        
        # 提取需求实体
        nodes.extend(self._extract_requirements(requirements_and_domain))
        
        # 提取任务实体
        nodes.extend(self._extract_tasks(wbs))
        
        # 提取角色实体
        nodes.extend(self._extract_roles(requirements_and_domain, wbs))
        
        # 提取工具实体
        nodes.extend(self._extract_tools(requirements_and_domain, wbs))
        
        # 提取技能实体
        nodes.extend(self._extract_skills(requirements_and_domain))
        
        # 新增：提取交付物实体
        nodes.extend(self._extract_deliverables(requirements_and_domain, wbs))
        
        # 新增：提取里程碑实体
        nodes.extend(self._extract_milestones(requirements_and_domain))
        
        # 新增：提取风险实体
        nodes.extend(self._extract_risks(requirements_and_domain, wbs))
        
        # 新增：提取利益相关方实体
        nodes.extend(self._extract_stakeholders(requirements_and_domain))
        
        # 新增：提取约束条件实体
        nodes.extend(self._extract_constraints(requirements_and_domain))
        
        logger.info(f"实体提取完成: 共提取 {len(nodes)} 个实体")
        
        return {"nodes": nodes}
    
    def _extract_requirements(self, requirements_and_domain: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取需求实体"""
        nodes = []
        
        # 功能需求
        for req in requirements_and_domain.get("functional_requirements", []):
            node = {
                "id": req.get("id", self._generate_id("REQ", len(nodes))),
                "type": "REQUIREMENT",
                "properties": {
                    "name": req.get("name", ""),
                    "description": req.get("description", req.get("desc", "")),
                    "priority": req.get("priority", "中"),
                    "requirement_type": "功能需求",
                    "acceptance_criteria": req.get("acceptance_criteria", [])
                }
            }
            nodes.append(node)
        
        # 非功能需求
        for req in requirements_and_domain.get("non_functional_requirements", []):
            node = {
                "id": req.get("id", self._generate_id("REQ", len(nodes))),
                "type": "REQUIREMENT",
                "properties": {
                    "name": req.get("type", ""),
                    "description": req.get("description", req.get("desc", "")),
                    "priority": "中",
                    "requirement_type": "非功能需求",
                    "metric": req.get("metric", ""),
                    "measurement": req.get("measurement", "")
                }
            }
            nodes.append(node)
        
        return nodes
    
    def _extract_tasks(self, wbs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取任务实体（递归）"""
        nodes = []
        tasks = wbs.get("tasks", [])
        
        def _extract_task_node(task: Dict[str, Any]) -> Dict[str, Any]:
            """提取单个任务节点"""
            node = {
                "id": task.get("task_id", self._generate_id("T", len(nodes))),
                "type": "TASK",
                "properties": {
                    "task_name": task.get("task_name", ""),
                    "description": task.get("description", ""),
                    "task_type": task.get("task_type", ""),
                    "level": task.get("level", 1),
                    "estimated_hours": task.get("estimated_hours", 0),
                    "estimated_complexity": task.get("estimated_complexity", 1),
                    "prerequisite": task.get("prerequisite", ""),
                    "deliverables": task.get("deliverables", []),
                    "quality_standards": task.get("quality_standards", []),
                    "parent_task_id": task.get("parent_task_id")
                }
            }
            return node
        
        def _recursive_extract(task_list: List[Dict[str, Any]]):
            """递归提取任务"""
            for task in task_list:
                nodes.append(_extract_task_node(task))
                
                # 递归处理子任务
                children = task.get("children", [])
                if children:
                    _recursive_extract(children)
        
        _recursive_extract(tasks)
        
        return nodes
    
    def _extract_roles(self, requirements_and_domain: Dict[str, Any], wbs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取角色实体（去重）"""
        nodes = []
        role_set: Set[str] = set()
        
        # 从需求分析结果中提取角色
        entities = requirements_and_domain.get("entities", {})
        for role in entities.get("roles", []):
            role_name = role.get("name", "")
            if role_name and role_name not in role_set:
                node = {
                    "id": role.get("id", self._generate_id("ROLE", len(nodes))),
                    "type": "ROLE",
                    "properties": {
                        "name": role_name,
                        "responsibilities": role.get("responsibilities", []),
                        "skills_required": role.get("skills_required", [])
                    }
                }
                nodes.append(node)
                role_set.add(role_name)
        
        # 从WBS任务中提取角色（补充）
        def _extract_roles_from_tasks(task_list: List[Dict[str, Any]]):
            """从任务列表中提取角色"""
            for task in task_list:
                for role_req in task.get("roles_required", []):
                    role_name = role_req.get("role", "")
                    if role_name and role_name not in role_set:
                        node = {
                            "id": self._generate_id("ROLE", len(nodes)),
                            "type": "ROLE",
                            "properties": {
                                "name": role_name,
                                "responsibilities": [],
                                "skills_required": role_req.get("skills", [])
                            }
                        }
                        nodes.append(node)
                        role_set.add(role_name)
                
                # 递归处理子任务
                children = task.get("children", [])
                if children:
                    _extract_roles_from_tasks(children)
        
        _extract_roles_from_tasks(wbs.get("tasks", []))
        
        return nodes
    
    def _extract_tools(self, requirements_and_domain: Dict[str, Any], wbs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取工具实体（去重）"""
        nodes = []
        tool_set: Set[str] = set()
        
        # 从需求分析结果中提取工具
        entities = requirements_and_domain.get("entities", {})
        for tool in entities.get("tools", []):
            tool_name = tool.get("name", "")
            if tool_name and tool_name not in tool_set:
                node = {
                    "id": tool.get("id", self._generate_id("TOOL", len(nodes))),
                    "type": "TOOL",
                    "properties": {
                        "name": tool_name,
                        "category": tool.get("category", ""),
                        "version": tool.get("version", ""),
                        "purpose": tool.get("purpose", "")
                    }
                }
                nodes.append(node)
                tool_set.add(tool_name)
        
        # 从WBS任务中提取工具（补充）
        def _extract_tools_from_tasks(task_list: List[Dict[str, Any]]):
            """从任务列表中提取工具"""
            for task in task_list:
                for tool_name in task.get("tools_required", []):
                    if tool_name and tool_name not in tool_set:
                        node = {
                            "id": self._generate_id("TOOL", len(nodes)),
                            "type": "TOOL",
                            "properties": {
                                "name": tool_name,
                                "category": "",
                                "version": "",
                                "purpose": ""
                            }
                        }
                        nodes.append(node)
                        tool_set.add(tool_name)
                
                # 递归处理子任务
                children = task.get("children", [])
                if children:
                    _extract_tools_from_tasks(children)
        
        _extract_tools_from_tasks(wbs.get("tasks", []))
        
        return nodes
    
    def _extract_skills(self, requirements_and_domain: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取技能实体"""
        nodes = []
        skill_set: Set[str] = set()
        
        # 从需求分析结果中提取技能
        entities = requirements_and_domain.get("entities", {})
        for skill in entities.get("skills", []):
            skill_name = skill.get("name", "")
            if skill_name and skill_name not in skill_set:
                node = {
                    "id": skill.get("id", self._generate_id("SKILL", len(nodes))),
                    "type": "SKILL",
                    "properties": {
                        "name": skill_name,
                        "level": skill.get("level", "中级"),
                        "related_tools": skill.get("related_tools", []),
                        "training_required": skill.get("training_required", False),
                        "certification": skill.get("certification", "")
                    }
                }
                nodes.append(node)
                skill_set.add(skill_name)
        
        return nodes
    
    def _extract_deliverables(self, requirements_and_domain: Dict[str, Any], wbs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取交付物实体（新增）"""
        nodes = []
        deliverable_set: Set[str] = set()
        
        # 从需求分析结果中提取交付物
        entities = requirements_and_domain.get("entities", {})
        for deliv in entities.get("deliverables", []):
            deliv_name = deliv.get("name", "")
            if deliv_name and deliv_name not in deliverable_set:
                node = {
                    "id": deliv.get("id", self._generate_id("DELIV", len(nodes))),
                    "type": "DELIVERABLE",
                    "properties": {
                        "name": deliv_name,
                        "type": deliv.get("type", ""),
                        "format": deliv.get("format", ""),
                        "owner": deliv.get("owner", ""),
                        "description": deliv.get("description", "")
                    }
                }
                nodes.append(node)
                deliverable_set.add(deliv_name)
        
        # 从WBS任务中提取交付物（补充）
        def _extract_from_tasks(task_list: List[Dict[str, Any]]):
            """ 从任务列表中提取交付物 """
            for task in task_list:
                for deliv_name in task.get("deliverables", []):
                    if isinstance(deliv_name, str) and deliv_name and deliv_name not in deliverable_set:
                        node = {
                            "id": self._generate_id("DELIV", len(nodes)),
                            "type": "DELIVERABLE",
                            "properties": {
                                "name": deliv_name,
                                "type": "",
                                "format": "",
                                "owner": "",
                                "description": ""
                            }
                        }
                        nodes.append(node)
                        deliverable_set.add(deliv_name)
                
                # 递归处理子任务
                children = task.get("children", [])
                if children:
                    _extract_from_tasks(children)
        
        _extract_from_tasks(wbs.get("tasks", []))
        
        return nodes
    
    def _extract_milestones(self, requirements_and_domain: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取里程碑实体（新增）"""
        nodes = []
        milestone_set: Set[str] = set()
        
        # 从需求分析结果中提取里程碑
        entities = requirements_and_domain.get("entities", {})
        for milestone in entities.get("milestones", []):
            mile_name = milestone.get("name", "")
            if mile_name and mile_name not in milestone_set:
                node = {
                    "id": milestone.get("id", self._generate_id("MILE", len(nodes))),
                    "type": "MILESTONE",
                    "properties": {
                        "name": mile_name,
                        "date": milestone.get("date", ""),
                        "criteria": milestone.get("criteria", []),
                        "description": milestone.get("description", "")
                    }
                }
                nodes.append(node)
                milestone_set.add(mile_name)
        
        return nodes
    
    def _extract_risks(self, requirements_and_domain: Dict[str, Any], wbs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取风险实体（新增）"""
        nodes = []
        risk_set: Set[str] = set()
        
        # 从需求分析结果中提取风险
        for risk in requirements_and_domain.get("risks", []):
            risk_desc = risk.get("risk", risk.get("description", ""))
            if risk_desc and risk_desc not in risk_set:
                node = {
                    "id": self._generate_id("RISK", len(nodes)),
                    "type": "RISK",
                    "properties": {
                        "description": risk_desc,
                        "probability": risk.get("probability", "中"),
                        "impact": risk.get("impact", "中"),
                        "category": risk.get("category", ""),
                        "source": "需求层面"
                    }
                }
                nodes.append(node)
                risk_set.add(risk_desc)
        
        # 从WBS任务中提取风险（补充）
        def _extract_from_tasks(task_list: List[Dict[str, Any]]):
            """ 从任务列表中提取风险 """
            for task in task_list:
                for risk in task.get("risks", []):
                    risk_desc = risk.get("description", "")
                    if risk_desc and risk_desc not in risk_set:
                        node = {
                            "id": self._generate_id("RISK", len(nodes)),
                            "type": "RISK",
                            "properties": {
                                "description": risk_desc,
                                "probability": risk.get("probability", "中"),
                                "impact": risk.get("impact", "中"),
                                "category": risk.get("category", ""),
                                "mitigation": risk.get("mitigation", ""),
                                "contingency_plan": risk.get("contingency_plan", ""),
                                "owner": risk.get("owner", ""),
                                "source": "任务层面"
                            }
                        }
                        nodes.append(node)
                        risk_set.add(risk_desc)
                
                # 递归处理子任务
                children = task.get("children", [])
                if children:
                    _extract_from_tasks(children)
        
        _extract_from_tasks(wbs.get("tasks", []))
        
        return nodes
    
    def _extract_stakeholders(self, requirements_and_domain: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取利益相关方实体（新增）"""
        nodes = []
        stakeholder_set: Set[str] = set()
        
        # 从需求分析结果中提取利益相关方
        for stakeholder in requirements_and_domain.get("stakeholders", []):
            stake_name = stakeholder.get("name", "")
            if stake_name and stake_name not in stakeholder_set:
                node = {
                    "id": self._generate_id("STAKE", len(nodes)),
                    "type": "STAKEHOLDER",
                    "properties": {
                        "name": stake_name,
                        "role": stakeholder.get("role", ""),
                        "interests": stakeholder.get("interests", []),
                        "influence": stakeholder.get("influence", "中")
                    }
                }
                nodes.append(node)
                stakeholder_set.add(stake_name)
        
        return nodes
    
    def _extract_constraints(self, requirements_and_domain: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取约束条件实体（新增）"""
        nodes = []
        
        # 从需求分析结果中提取约束条件
        constraints = requirements_and_domain.get("constraints", {})
        
        # 处理各种类型的约束
        constraint_types = [
            ("time", "时间"),
            ("budget", "预算"),
            ("team_size", "资源"),
            ("compliance", "合规")
        ]
        
        for const_key, const_type in constraint_types:
            if const_key in constraints:
                const_value = constraints[const_key]
                if const_value:
                    if isinstance(const_value, list):
                        # 处理列表类型（如compliance）
                        for i, item in enumerate(const_value):
                            node = {
                                "id": self._generate_id("CONST", len(nodes)),
                                "type": "CONSTRAINT",
                                "properties": {
                                    "type": const_type,
                                    "description": str(item),
                                    "impact": "高"
                                }
                            }
                            nodes.append(node)
                    else:
                        # 处理字符串类型
                        node = {
                            "id": self._generate_id("CONST", len(nodes)),
                            "type": "CONSTRAINT",
                            "properties": {
                                "type": const_type,
                                "description": str(const_value),
                                "impact": "高"
                            }
                        }
                        nodes.append(node)
        
        return nodes
