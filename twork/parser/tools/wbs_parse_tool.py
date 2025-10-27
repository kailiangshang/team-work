"""
WbsParseTool - WBS任务拆解工具（增强版）

基于需求和领域生成多层级WBS任务树，包含详细的资源、风险、质量标准等信息。
支持提取角色分配、工具需求、技能要求等图谱构建所需数据。
"""

from typing import Dict, Any, List, Optional
import json
from .base_tool import BaseTool
from ..templates.extraction_schema import get_json_schema_for_wbs
from ..templates.domain_template import get_template_by_domain
from ...utils.logger import get_logger

logger = get_logger(__name__)


class WbsParseTool(BaseTool):
    """WBS任务拆解工具"""
    
    DEFAULT_PROMPT_TEMPLATE = """你是一个专业的项目管理专家，擅长进行工作分解结构(WBS)设计和资源规划。

需求信息:
{input}

领域类型: {domain}
最大层级: {max_level}

领域上下文（供参考）:
{domain_context}

已识别的实体（供参考）:
角色: {roles}
工具: {tools}
技能: {skills}

请根据以上信息生成详细的WBS任务分解结构，包含任务、资源、风险等信息。

输出JSON Schema（严格遵循）:

{{
  "phase": "阶段名称",
  "total_estimated_hours": 总工时数,
  "tasks": [
    {{
      "task_id": "T001",
      "task_name": "任务名称",
      "description": "详细描述",
      "level": 1,
      "parent_task_id": null,
      "task_type": "任务类型",
      "estimated_hours": 工时,
      "estimated_complexity": 1-10,
      "dependencies": ["依赖任务ID"],
      "prerequisite": "前置条件描述",
      "deliverables": ["交付物1", "交付物2"],
      "roles_required": [
        {{
          "role": "角色名称",
          "effort_percentage": 工作量百分比,
          "skills": ["所需技能"],
          "concurrent_tasks": 可并行任务数,
          "preferred_schedule": "工作日/全天候"
        }}
      ],
      "tools_required": [
        {{
          "tool": "工具名称",
          "usage": "主框架/辅助工具",
          "setup_time": 环境配置时间(小时),
          "proficiency_required": "初级/中级/高级"
        }}
      ],
      "quality_standards": [
        {{
          "standard": "质量标准",
          "target": "目标值",
          "verification": "验证方法"
        }}
      ],
      "risks": [
        {{
          "description": "风险描述",
          "probability": "低/中/高",
          "impact": "低/中/高",
          "mitigation": "缓解措施",
          "contingency_plan": "应急预案",
          "owner": "负责人角色"
        }}
      ],
      "time_estimation": {{
        "optimistic": 乐观估算(小时),
        "most_likely": 最可能估算(小时),
        "pessimistic": 悲观估算(小时),
        "confidence": 0.0-1.0
      }},
      "acceptance_criteria": [
        "验收标准1",
        "验收标准2"
      ],
      "test_strategy": {{
        "unit_test": true/false,
        "integration_test": true/false,
        "coverage_target": 85
      }},
      "progress_tracking": {{
        "status": "未开始",
        "completion": 0,
        "blockers": []
      }},
      "children": [...]
    }}
  ],
  "resource_summary": {{
    "total_roles": [
      {{
        "role": "角色名称",
        "total_hours": 总工时,
        "task_count": 任务数,
        "peak_concurrency": 峰值并发数,
        "utilization_rate": 0.85,
        "skill_gaps": ["技能缺口"]
      }}
    ],
    "total_tools": [
      {{
        "tool": "工具名称",
        "tasks": ["T001", "T002"],
        "setup_cost": 配置成本(小时),
        "license_cost": 许可成本
      }}
    ],
    "critical_path": [
      {{
        "task_id": "T001",
        "duration": 80,
        "float": 0,
        "sequence": 1
      }}
    ],
    "timeline": {{
      "total_duration_hours": 640,
      "parallel_efficiency": 0.7,
      "estimated_calendar_days": 45,
      "buffer": 10
    }},
    "cost_estimation": {{
      "labor_cost": 400000,
      "tool_cost": 5000,
      "infrastructure_cost": 10000,
      "total": 415000,
      "currency": "CNY"
    }}
  }}
}}

要求:
1. 任务层级不超过{max_level}层
2. 为每个任务明确分配角色和工作量百分比，包括增强字段
3. 列出所需的工具和技能（从已识别实体中选择），包括配置时间和熟练度要求
4. 识别潜在风险并提供缓解措施和应急预案
5. 指明任务的前置条件、交付物和验收标准
6. 使用三点估算法提供时间估算（乐观、最可能、悲观）
7. 为适用的任务添加测试策略
8. 计算资源汇总信息，包括增强的角色统计、时间线和成本估算
9. task_id格式: T001, T001-1, T001-1-1
10. task_type应从领域常见任务类型中选择
11. 只输出JSON格式，不要包含其他文字
"""
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行WBS拆解（增强版）
        
        Args:
            input_data: {
                "functional_requirements": List[Dict],
                "non_functional_requirements": List[Dict],
                "domain": str,
                "domain_confidence": float (可选),
                "entities": Dict (可选，包含roles, tools, skills)
            }
        
        Returns:
            {
                "phase": str,
                "total_estimated_hours": int,
                "tasks": List[Dict],
                "resource_summary": Dict
            }
        """
        domain = input_data.get("domain", "其他")
        max_level = self.config.get("max_level", 3)
        
        logger.info(f"开始WBS拆解: domain={domain}, max_level={max_level}")
        
        # 获取领域模板
        template = get_template_by_domain(domain)
        
        # 准备输入数据
        requirements_text = self._format_requirements(input_data)
        
        # 提取实体信息（用于提示LLM）
        entities = input_data.get("entities", {})
        roles = [r.get("name", "") for r in entities.get("roles", [])]
        tools = [t.get("name", "") for t in entities.get("tools", [])]
        skills = [s.get("name", "") for s in entities.get("skills", [])]
        
        # 如果没有实体，使用领域模板的默认值
        if not roles:
            roles = [r.get("name", "") for r in template.default_roles]
        if not tools:
            tools = [t.get("name", "") for t in template.common_tools]
        if not skills:
            skills = [s.get("name", "") for s in template.common_skills]
        
        # 获取提示词模板
        prompt_template = self.config.get("prompt_template", self.DEFAULT_PROMPT_TEMPLATE)
        
        # 调用LLM
        result = self.llm_call(
            prompt=prompt_template,
            input_data=requirements_text,
            temperature=self.config.get("temperature", 0.5),
            response_format=self.config.get("response_format"),
            domain=domain,
            max_level=max_level,
            domain_context=template.domain_context,
            roles=", ".join(roles[:10]),  # 限制长度
            tools=", ".join(tools[:15]),
            skills=", ".join(skills[:15])
        )
        
        # 验证结果
        self._validate_result(result)
        
        # 后处理：补充缺失字段
        result = self._post_process_result(result)
        
        # 统计任务数量和工时
        task_count = self._count_tasks(result.get("tasks", []))
        total_hours = result.get("total_estimated_hours", 0)
        
        logger.info(f"WBS拆解完成: phase={result.get('phase')}, "
                   f"total_tasks={task_count}, total_hours={total_hours}")
        
        return result
    
    def _format_requirements(self, input_data: Dict[str, Any]) -> str:
        """
        格式化需求为文本
        
        Args:
            input_data: 需求数据
            
        Returns:
            格式化的文本
        """
        parts = []
        
        # 功能需求
        parts.append("## 功能需求")
        for req in input_data.get("functional_requirements", []):
            parts.append(f"- [{req.get('id')}] {req.get('desc')} (优先级: {req.get('priority', '中')})")
        
        # 非功能需求
        parts.append("\n## 非功能需求")
        for req in input_data.get("non_functional_requirements", []):
            parts.append(f"- [{req.get('id')}] ({req.get('type')}) {req.get('desc')}")
        
        return "\n".join(parts)
    
    def _validate_result(self, result: Dict[str, Any]):
        """
        验证WBS结果（增强版）
        
        Args:
            result: WBS结果
            
        Raises:
            ValueError: 如果结果格式不正确
        """
        if "phase" not in result:
            raise ValueError("WBS结果缺少phase字段")
        
        if "tasks" not in result or not isinstance(result["tasks"], list):
            raise ValueError("WBS结果缺少tasks字段或格式不正确")
        
        # 验证任务格式
        for task in result["tasks"]:
            self._validate_task(task)
        
        # 验证resource_summary（可选）
        if "resource_summary" in result:
            summary = result["resource_summary"]
            if not isinstance(summary, dict):
                logger.warning("resource_summary应为字典类型")
    
    def _validate_task(self, task: Dict[str, Any], parent_id: Optional[str] = None):
        """
        递归验证任务格式
        
        Args:
            task: 任务对象
            parent_id: 父任务ID
        """
        required_fields = [
            "task_id", "task_name", "description", "level",
            "parent_task_id", "estimated_hours", "dependencies"
        ]
        
        for field in required_fields:
            if field not in task:
                logger.warning(f"任务 {task.get('task_id', 'unknown')} 缺少必需字段: {field}")
        
        # 验证父任务ID
        if parent_id is not None and task.get("parent_task_id") != parent_id:
            logger.warning(f"任务 {task.get('task_id')} 的parent_task_id不匹配")
        
        # 递归验证子任务
        children = task.get("children", [])
        if children:
            for child in children:
                self._validate_task(child, task.get("task_id"))
    
    def _count_tasks(self, tasks: List[Dict[str, Any]]) -> int:
        """
        递归统计任务数量
        
        Args:
            tasks: 任务列表
            
        Returns:
            任务总数
        """
        count = len(tasks)
        for task in tasks:
            count += self._count_tasks(task.get("children", []))
        return count
    
    def _post_process_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        后处理结果：补充缺失字段和计算汇总信息
        
        Args:
            result: WBS结果
            
        Returns:
            处理后的结果
        """
        # 补充total_estimated_hours（如果缺失）
        if "total_estimated_hours" not in result:
            total_hours = self._calculate_total_hours(result.get("tasks", []))
            result["total_estimated_hours"] = total_hours
        
        # 补充resource_summary（如果缺失）
        if "resource_summary" not in result:
            result["resource_summary"] = self._calculate_resource_summary(result.get("tasks", []))
        
        return result
    
    def _calculate_total_hours(self, tasks: List[Dict[str, Any]]) -> int:
        """
        递归计算总工时
        
        Args:
            tasks: 任务列表
            
        Returns:
            总工时
        """
        total = 0
        for task in tasks:
            total += task.get("estimated_hours", 0)
            total += self._calculate_total_hours(task.get("children", []))
        return total
    
    def _calculate_resource_summary(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算资源汇总信息
        
        Args:
            tasks: 任务列表
            
        Returns:
            资源汇总信息
        """
        role_stats = {}  # {role_name: {total_hours: x, task_count: y}}
        tool_set = set()
        
        def _collect_resources(task_list: List[Dict[str, Any]]):
            """递归收集资源信息"""
            for task in task_list:
                # 收集角色信息
                for role_req in task.get("roles_required", []):
                    role_name = role_req.get("role", "")
                    if role_name:
                        if role_name not in role_stats:
                            role_stats[role_name] = {"total_hours": 0, "task_count": 0}
                        
                        # 计算该角色在此任务的工时
                        task_hours = task.get("estimated_hours", 0)
                        effort_pct = role_req.get("effort_percentage", 100)
                        role_hours = task_hours * effort_pct / 100
                        
                        role_stats[role_name]["total_hours"] += role_hours
                        role_stats[role_name]["task_count"] += 1
                
                # 收集工具信息
                for tool_name in task.get("tools_required", []):
                    if tool_name:
                        tool_set.add(tool_name)
                
                # 递归处理子任务
                _collect_resources(task.get("children", []))
        
        _collect_resources(tasks)
        
        # 构建汇总结果
        total_roles = [
            {
                "role": role_name,
                "total_hours": int(stats["total_hours"]),
                "task_count": stats["task_count"]
            }
            for role_name, stats in role_stats.items()
        ]
        
        return {
            "total_roles": total_roles,
            "total_tools": list(tool_set),
            "critical_path": []  # 关键路径需要更复杂的算法，这里暂时留空
        }
