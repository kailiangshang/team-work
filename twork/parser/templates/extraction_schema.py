"""
提取Schema定义

定义需求分析和WBS拆解的输出数据结构Schema，用于验证和标准化LLM输出。
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class RequirementSchema:
    """需求Schema"""
    id: str
    name: str
    description: str
    priority: str  # 高/中/低
    acceptance_criteria: List[str] = field(default_factory=list)
    related_entities: Dict[str, List[str]] = field(default_factory=dict)  # roles, tools, skills


@dataclass
class NonFunctionalRequirementSchema:
    """非功能需求Schema"""
    id: str
    type: str  # 性能/安全/可用性/可扩展性/可维护性
    description: str
    metric: str
    measurement: str


@dataclass
class RoleSchema:
    """角色Schema（增强版）"""
    id: str
    name: str
    responsibilities: List[str] = field(default_factory=list)
    skills_required: List[str] = field(default_factory=list)
    experience_level: Optional[str] = None           # 新增：经验级别
    availability: Optional[str] = None               # 新增：可用性
    quantity: int = 1                                # 新增：需要人数


@dataclass
class ToolSchema:
    """工具Schema（增强版）"""
    id: str
    name: str
    category: str
    version: Optional[str] = None
    purpose: Optional[str] = None
    license: Optional[str] = None                    # 新增：许可证
    cost: Optional[str] = None                       # 新增：成本
    learning_curve: Optional[str] = None             # 新增：学习曲线


@dataclass
class SkillSchema:
    """技能Schema（增强版）"""
    id: str
    name: str
    level: str  # 初级/中级/高级/专家
    related_tools: List[str] = field(default_factory=list)
    training_required: bool = False                  # 新增：是否需要培训
    certification: Optional[str] = None              # 新增：认证要求


@dataclass
class DeliverableSchema:
    """交付物Schema（新增）"""
    id: str
    name: str
    type: str  # 文档/代码/设计/报告
    format: Optional[str] = None
    owner: Optional[str] = None
    description: Optional[str] = None


@dataclass
class MilestoneSchema:
    """里程碑Schema（新增）"""
    id: str
    name: str
    date: Optional[str] = None
    criteria: List[str] = field(default_factory=list)
    description: Optional[str] = None


@dataclass
class StakeholderSchema:
    """利益相关方Schema（新增）"""
    id: str
    name: str
    role: str  # 决策者/参与者/受益者
    interests: List[str] = field(default_factory=list)
    influence: str = "中"  # 高/中/低


@dataclass
class ConstraintSchema:
    """约束条件Schema（新增）"""
    id: str
    type: str  # 时间/预算/资源/技术/合规
    description: str
    impact: str = "中"  # 高/中/低


@dataclass
class RequirementAnalysisSchema:
    """需求分析输出Schema（增强版）"""
    domain: str
    domain_confidence: float
    functional_requirements: List[Dict[str, Any]] = field(default_factory=list)
    non_functional_requirements: List[Dict[str, Any]] = field(default_factory=list)
    entities: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    tech_stack: Dict[str, List[str]] = field(default_factory=dict)
    
    # 新增字段
    constraints: Dict[str, Any] = field(default_factory=dict)           # 约束条件
    success_criteria: List[Dict[str, Any]] = field(default_factory=list)  # 成功标准
    stakeholders: List[Dict[str, Any]] = field(default_factory=list)   # 利益相关方
    assumptions: List[str] = field(default_factory=list)               # 假设条件
    risks: List[Dict[str, Any]] = field(default_factory=list)          # 需求层面风险


@dataclass
class RoleRequirement:
    """任务角色需求"""
    role: str
    effort_percentage: int  # 工作量百分比
    skills: List[str] = field(default_factory=list)


@dataclass
class RiskSchema:
    """风险Schema"""
    description: str
    probability: str  # 低/中/高
    impact: str  # 低/中/高
    mitigation: str  # 缓解措施


@dataclass
class TaskSchema:
    """任务Schema（递归结构，增强版）"""
    task_id: str
    task_name: str
    description: str
    level: int
    parent_task_id: Optional[str] = None
    task_type: Optional[str] = None
    estimated_hours: int = 0
    estimated_complexity: int = 1  # 1-10
    dependencies: List[str] = field(default_factory=list)
    prerequisite: Optional[str] = None
    deliverables: List[str] = field(default_factory=list)
    roles_required: List[Dict[str, Any]] = field(default_factory=list)
    tools_required: List[str] = field(default_factory=list)
    quality_standards: List[str] = field(default_factory=list)
    risks: List[Dict[str, Any]] = field(default_factory=list)
    children: List[Dict[str, Any]] = field(default_factory=list)
    
    # 新增字段
    time_estimation: Optional[Dict[str, Any]] = None                # 三点估算
    acceptance_criteria: List[str] = field(default_factory=list)   # 验收标准
    test_strategy: Optional[Dict[str, Any]] = None                 # 测试策略
    progress_tracking: Optional[Dict[str, Any]] = None             # 进度跟踪


@dataclass
class ResourceSummarySchema:
    """资源汇总Schema（增强版）"""
    total_roles: List[Dict[str, Any]] = field(default_factory=list)
    total_tools: List[str] = field(default_factory=list)
    critical_path: List[str] = field(default_factory=list)
    
    # 新增字段
    timeline: Optional[Dict[str, Any]] = None           # 时间线信息
    cost_estimation: Optional[Dict[str, Any]] = None    # 成本估算


@dataclass
class WBSSchema:
    """WBS输出Schema"""
    phase: str
    total_estimated_hours: int
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    resource_summary: Dict[str, Any] = field(default_factory=dict)


# 实体类型定义（增强版）
ENTITY_TYPES = {
    "TASK": "T",
    "ROLE": "ROLE",
    "TOOL": "TOOL",
    "SKILL": "SKILL",
    "REQUIREMENT": "REQ",
    "DELIVERABLE": "DELIV",      # 新增：交付物
    "MILESTONE": "MILE",          # 新增：里程碑
    "RISK": "RISK",               # 新增：风险
    "STAKEHOLDER": "STAKE",       # 新增：利益相关方
    "CONSTRAINT": "CONST"         # 新增：约束条件
}

# 关系类型定义（增强版）
RELATION_TYPES = {
    # 现有关系
    "DEPENDS_ON": {"source": "TASK", "target": "TASK"},
    "REQUIRES_ROLE": {"source": "TASK", "target": "ROLE"},
    "REQUIRES_TOOL": {"source": "TASK", "target": "TOOL"},
    "REQUIRES_SKILL": {"source": "ROLE", "target": "SKILL"},
    "USES_TOOL": {"source": "ROLE", "target": "TOOL"},
    "IMPLEMENTS": {"source": "TASK", "target": "REQUIREMENT"},
    "CHILD_OF": {"source": "TASK", "target": "TASK"},
    
    # 新增关系
    "DELIVERS": {"source": "TASK", "target": "DELIVERABLE"},
    "CONTRIBUTES_TO": {"source": "TASK", "target": "MILESTONE"},
    "HAS_RISK": {"source": "TASK", "target": "RISK"},
    "MITIGATES": {"source": "TASK", "target": "RISK"},
    "ASSIGNED_TO": {"source": "TASK", "target": "ROLE"},
    "OWNS": {"source": "ROLE", "target": "DELIVERABLE"},
    "STAKEHOLDER_OF": {"source": "STAKEHOLDER", "target": "REQUIREMENT"},
    "CONSTRAINS": {"source": "CONSTRAINT", "target": "TASK"},
    "REQUIRES_SKILL_FOR_TOOL": {"source": "TOOL", "target": "SKILL"},
    "REPLACES": {"source": "TOOL", "target": "TOOL"},          # 备选工具
    "CONFLICTS_WITH": {"source": "TASK", "target": "TASK"},   # 资源冲突
    "ENABLES": {"source": "TASK", "target": "TASK"}           # 使能关系
}


def get_json_schema_for_requirement_analysis() -> Dict[str, Any]:
    """获取需求分析的JSON Schema"""
    return {
        "type": "object",
        "properties": {
            "domain": {"type": "string"},
            "domain_confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "functional_requirements": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "priority": {"type": "string", "enum": ["高", "中", "低"]},
                        "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
                        "related_entities": {
                            "type": "object",
                            "properties": {
                                "roles": {"type": "array", "items": {"type": "string"}},
                                "tools": {"type": "array", "items": {"type": "string"}},
                                "skills": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    },
                    "required": ["id", "name", "description", "priority"]
                }
            },
            "non_functional_requirements": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "type": {"type": "string"},
                        "description": {"type": "string"},
                        "metric": {"type": "string"},
                        "measurement": {"type": "string"}
                    },
                    "required": ["id", "type", "description"]
                }
            },
            "entities": {
                "type": "object",
                "properties": {
                    "roles": {"type": "array", "items": {"type": "object"}},
                    "tools": {"type": "array", "items": {"type": "object"}},
                    "skills": {"type": "array", "items": {"type": "object"}}
                }
            },
            "tech_stack": {
                "type": "object",
                "properties": {
                    "frontend": {"type": "array", "items": {"type": "string"}},
                    "backend": {"type": "array", "items": {"type": "string"}},
                    "database": {"type": "array", "items": {"type": "string"}},
                    "deployment": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "required": ["domain", "domain_confidence", "functional_requirements"]
    }


def get_json_schema_for_wbs() -> Dict[str, Any]:
    """获取WBS的JSON Schema"""
    task_schema = {
        "type": "object",
        "properties": {
            "task_id": {"type": "string"},
            "task_name": {"type": "string"},
            "description": {"type": "string"},
            "level": {"type": "integer"},
            "parent_task_id": {"type": ["string", "null"]},
            "task_type": {"type": "string"},
            "estimated_hours": {"type": "number"},
            "estimated_complexity": {"type": "integer", "minimum": 1, "maximum": 10},
            "dependencies": {"type": "array", "items": {"type": "string"}},
            "prerequisite": {"type": "string"},
            "deliverables": {"type": "array", "items": {"type": "string"}},
            "roles_required": {"type": "array", "items": {"type": "object"}},
            "tools_required": {"type": "array", "items": {"type": "string"}},
            "quality_standards": {"type": "array", "items": {"type": "string"}},
            "risks": {"type": "array", "items": {"type": "object"}},
            "children": {"type": "array"}
        },
        "required": ["task_id", "task_name", "description", "level"]
    }
    
    return {
        "type": "object",
        "properties": {
            "phase": {"type": "string"},
            "total_estimated_hours": {"type": "number"},
            "tasks": {"type": "array", "items": task_schema},
            "resource_summary": {
                "type": "object",
                "properties": {
                    "total_roles": {"type": "array", "items": {"type": "object"}},
                    "total_tools": {"type": "array", "items": {"type": "string"}},
                    "critical_path": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "required": ["phase", "tasks"]
    }
