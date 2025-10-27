"""
文档解析模块（增强版）

负责加载、解析需求文档，提取关键信息并拆解为结构化任务。
实现了结构化信息生产工厂（StructureUnderstandFactory）。
简化版本：专注于单次解析识别，移除了backend依赖和存储功能。
增强版本：集成图谱提取器，支持实体和关系提取。
"""

# 新架构 - 核心工具模块
from .tools.base_tool import BaseTool
from .tools.doc_parse_tool import DocParseTool
from .tools.requirement_analyzer_tool import RequirementAndDomainAnalyzerTool
from .tools.wbs_parse_tool import WbsParseTool

# 模板管理
from .templates.domain_template import (
    DomainTemplateV2,
    get_template_by_domain,
    get_template_by_id,
    SOFTWARE_DEV_TEMPLATE,
    OUTDOOR_CONSTRUCTION_TEMPLATE,
    MARKETING_CAMPAIGN_TEMPLATE,
    RESEARCH_PROJECT_TEMPLATE,
    DEFAULT_TEMPLATE
)
from .templates.extraction_schema import (
    ENTITY_TYPES,
    RELATION_TYPES,
    get_json_schema_for_requirement_analysis,
    get_json_schema_for_wbs
)

# 提取器
from .extractors.base_extractor import BaseExtractor
from .extractors.entity_extractor import EntityExtractor
from .extractors.relation_extractor import RelationExtractor

# 结构化工厂
from .structure_factory import StructureUnderstandFactory

__all__ = [
    # 新架构 - 工具
    "BaseTool",
    "DocParseTool",
    "RequirementAndDomainAnalyzerTool",
    "WbsParseTool",
    
    # 模板管理
    "DomainTemplateV2",
    "get_template_by_domain",
    "get_template_by_id",
    "SOFTWARE_DEV_TEMPLATE",
    "OUTDOOR_CONSTRUCTION_TEMPLATE",
    "MARKETING_CAMPAIGN_TEMPLATE",
    "RESEARCH_PROJECT_TEMPLATE",
    "DEFAULT_TEMPLATE",
    
    # 提取Schema
    "ENTITY_TYPES",
    "RELATION_TYPES",
    "get_json_schema_for_requirement_analysis",
    "get_json_schema_for_wbs",
    
    # 提取器
    "BaseExtractor",
    "EntityExtractor",
    "RelationExtractor",
    
    # 结构化工厂
    "StructureUnderstandFactory",
]
