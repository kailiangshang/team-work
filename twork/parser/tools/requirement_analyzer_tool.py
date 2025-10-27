"""
RequirementAndDomainAnalyzerTool - 需求与领域分析工具（增强版）

使用LLM从结构化文本中提取需求、领域和图谱实体信息。
支持提取角色、工具、技能等实体，为下游图谱构建提供数据。
"""

from typing import Dict, Any, List, Optional
import json
from .base_tool import BaseTool
from ..templates.extraction_schema import get_json_schema_for_requirement_analysis
from ..templates.domain_template import get_template_by_domain
from ...utils.logger import get_logger

logger = get_logger(__name__)


class RequirementAndDomainAnalyzerTool(BaseTool):
    """需求与领域分析工具"""
    
    DEFAULT_PROMPT_TEMPLATE = """你是一个专业的需求分析与实体识别专家。请深度分析以下文档，提取需求信息和关键实体。

文档内容:
{input}

领域上下文（供参考）:
{domain_context}

请按照以下JSON Schema输出结果（必须严格遵循格式）:

{{
  "domain": "领域类型（软件开发/户外施工/营销活动/研究项目/其他）",
  "domain_confidence": 0.0-1.0,
  "functional_requirements": [
    {{
      "id": "FR-XXX",
      "name": "需求简称",
      "description": "详细描述",
      "priority": "高/中/低",
      "acceptance_criteria": ["验收标准1", "验收标准2"],
      "related_entities": {{
        "roles": ["角色名称"],
        "tools": ["工具名称"],
        "skills": ["技能名称"]
      }}
    }}
  ],
  "non_functional_requirements": [
    {{
      "id": "NFR-XXX",
      "type": "性能/安全/可用性/可扩展性/可维护性",
      "description": "详细描述",
      "metric": "量化指标",
      "measurement": "测量方法"
    }}
  ],
  "entities": {{
    "roles": [
      {{
        "id": "ROLE-XXX",
        "name": "角色名称",
        "responsibilities": ["职责1", "职责2"],
        "skills_required": ["技能1", "技能2"],
        "experience_level": "经验要求",
        "availability": "全职/兼职",
        "quantity": 需要人数
      }}
    ],
    "tools": [
      {{
        "id": "TOOL-XXX",
        "name": "工具名称",
        "category": "工具类别",
        "version": "版本要求",
        "purpose": "用途说明",
        "license": "开源/商业",
        "cost": "成本范围",
        "learning_curve": "低/中/高"
      }}
    ],
    "skills": [
      {{
        "id": "SKILL-XXX",
        "name": "技能名称",
        "level": "初级/中级/高级/专家",
        "related_tools": ["工具1", "工具2"],
        "training_required": true/false,
        "certification": "认证要求"
      }}
    ],
    "deliverables": [
      {{
        "id": "DELIV-XXX",
        "name": "交付物名称",
        "type": "文档/代码/设计/报告",
        "format": "格式",
        "owner": "负责角色"
      }}
    ],
    "milestones": [
      {{
        "id": "MILE-XXX",
        "name": "里程碑名称",
        "date": "预期时间",
        "criteria": ["达成标准1", "达成标准2"]
      }}
    ]
  }},
  "tech_stack": {{
    "frontend": ["技杲1", "技杲2"],
    "backend": ["技杲1", "技杲2"],
    "database": ["技杲1", "技杲2"],
    "deployment": ["技杲1", "技杲2"]
  }},
  "constraints": {{
    "time": "时间约束",
    "budget": "预算约束",
    "team_size": "团队规模",
    "compliance": ["合规要求1", "合规要求2"]
  }},
  "success_criteria": [
    {{
      "criterion": "成功标准",
      "target": "目标值",
      "measurement": "测量方法"
    }}
  ],
  "stakeholders": [
    {{
      "name": "相关方名称",
      "role": "决策者/参与者/受益者",
      "interests": ["关注点1", "关注点2"],
      "influence": "高/中/低"
    }}
  ],
  "assumptions": [
    "假设条件1",
    "假设条件2"
  ],
  "risks": [
    {{
      "risk": "风险描述",
      "probability": "低/中/高",
      "impact": "低/中/高",
      "category": "技术风险/资源风险/进度风险"
    }}
  ]
}}

提取要求:
1. 从文档中识别所有功能需求和非功能需求
2. 为每个需求提取关联的角色、工具、技能
3. 提取项目涉及的所有角色、工具、技能实体，包括增强字段
4. 识别技术栈信息
5. 提取项目约束条件（时间、预算、团队、合规）
6. 识别成功标准和衡量方式
7. 提取利益相关方及其关注点
8. 识别项目假设条件
9. 识别需求层面的潜在风险
10. 确保实体ID唯一且格式规范
11. domain_confidence为领域判断的置信度（0-1）
12. 只输出JSON格式，不要包含其他文字
"""
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析需求与领域（增强版）
        
        Args:
            input_data: {
                "sections": List[Dict]  # 来自DocParseTool的输出
            }
        
        Returns:
            {
                "domain": str,
                "domain_confidence": float,
                "functional_requirements": List[Dict],
                "non_functional_requirements": List[Dict],
                "entities": {
                    "roles": List[Dict],
                    "tools": List[Dict],
                    "skills": List[Dict]
                },
                "tech_stack": Dict[str, List[str]]
            }
        """
        sections = input_data.get("sections", [])
        
        if not sections:
            raise ValueError("输入数据中没有sections")
        
        # 将sections合并为文本
        full_text = self._merge_sections(sections)
        
        logger.info("开始分析需求与领域")
        
        # 获取提示词模板
        prompt_template = self.config.get("prompt_template", self.DEFAULT_PROMPT_TEMPLATE)
        
        # 准备领域上下文（通用说明）
        domain_context = self.config.get("domain_context", """请根据文档内容识别领域类型。
常见领域：软件开发、户外施工、营销活动、研究项目等。""")
        
        # 调用LLM
        result = self.llm_call(
            prompt=prompt_template,
            input_data=full_text,
            temperature=self.config.get("temperature", 0.3),
            response_format=self.config.get("response_format"),
            domain_context=domain_context
        )
        
        # 验证结果
        self._validate_result(result)
        
        # 使用领域模板补充默认实体（如果实体不足）
        result = self._enrich_with_domain_template(result)
        
        logger.info(f"需求分析完成: domain={result.get('domain')} (confidence={result.get('domain_confidence', 0)}), "
                   f"FR={len(result.get('functional_requirements', []))}, "
                   f"NFR={len(result.get('non_functional_requirements', []))}, "
                   f"Roles={len(result.get('entities', {}).get('roles', []))}, "
                   f"Tools={len(result.get('entities', {}).get('tools', []))}, "
                   f"Skills={len(result.get('entities', {}).get('skills', []))}")
        
        return result
    
    def _merge_sections(self, sections: List[Dict[str, Any]]) -> str:
        """
        合并章节为完整文本
        
        Args:
            sections: 章节列表
            
        Returns:
            合并后的文本
        """
        parts = []
        for section in sections:
            title = section.get("title", "")
            content = section.get("content", "")
            level = section.get("level", 1)
            
            # 添加标题
            if title:
                parts.append(f"{'#' * level} {title}")
            
            # 添加内容
            if content:
                parts.append(content)
            
            parts.append("")  # 空行分隔
        
        return "\n".join(parts)
    
    def _validate_result(self, result: Dict[str, Any]):
        """
        验证分析结果（增强版）
        
        Args:
            result: 分析结果
            
        Raises:
            ValueError: 如果结果格式不正确
        """
        # 必需字段
        required_fields = ["functional_requirements", "non_functional_requirements", "domain"]
        
        for field in required_fields:
            if field not in result:
                raise ValueError(f"分析结果缺少必需字段: {field}")
        
        # 验证需求格式（兼容旧格式desc和新格式description）
        for req in result.get("functional_requirements", []):
            if "id" not in req:
                logger.warning(f"功能需求缺少ID: {req}")
            if "description" not in req and "desc" not in req:
                logger.warning(f"功能需求缺少描述: {req}")
        
        for req in result.get("non_functional_requirements", []):
            if "id" not in req:
                logger.warning(f"非功能需求缺少ID: {req}")
            if "description" not in req and "desc" not in req:
                logger.warning(f"非功能需求缺少描述: {req}")
        
        # 验证领域
        valid_domains = ["软件开发", "户外施工", "营销活动", "研究项目", "其他"]
        if result.get("domain") not in valid_domains:
            logger.warning(f"未识别的领域类型: {result.get('domain')}")
        
        # 验证domain_confidence
        if "domain_confidence" in result:
            confidence = result.get("domain_confidence")
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                logger.warning(f"domain_confidence值无效: {confidence}，应为0-1之间的数值")
        
        # 验证实体结构
        if "entities" in result:
            entities = result.get("entities", {})
            if not isinstance(entities, dict):
                logger.warning("entities字段应为字典类型")
        
        # 验证新增字段（可选）
        optional_fields = ["constraints", "success_criteria", "stakeholders", "assumptions", "risks"]
        for field in optional_fields:
            if field in result:
                if field == "constraints" and not isinstance(result[field], dict):
                    logger.warning(f"{field}字段应为字典类型")
                elif field != "constraints" and field != "assumptions" and not isinstance(result[field], list):
                    logger.warning(f"{field}字段应为列表类型")
                elif field == "assumptions" and not isinstance(result[field], list):
                    logger.warning(f"{field}字段应为列表类型")
    
    def _enrich_with_domain_template(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用领域模板补充默认实体
        
        Args:
            result: 分析结果
            
        Returns:
            补充后的结果
        """
        domain = result.get("domain", "其他")
        
        # 获取领域模板
        template = get_template_by_domain(domain)
        
        # 确保entities字段存在
        if "entities" not in result:
            result["entities"] = {}
        
        entities = result["entities"]
        
        # 如果没有提取到角色，使用模板默认角色
        if not entities.get("roles"):
            entities["roles"] = template.default_roles
            logger.info(f"使用领域模板补充默认角色: {len(template.default_roles)}个")
        
        # 如果没有提取到工具，使用模板常用工具
        if not entities.get("tools"):
            entities["tools"] = template.common_tools
            logger.info(f"使用领域模板补充常用工具: {len(template.common_tools)}个")
        
        # 如果没有提取到技能，使用模板常用技能
        if not entities.get("skills"):
            entities["skills"] = template.common_skills
            logger.info(f"使用领域模板补充常用技能: {len(template.common_skills)}个")
        
        return result
