"""
模板管理模块

包含各种领域的上下文模板。
"""

from .domain_template import (
    DomainTemplateV2,
    get_template_by_domain,
    get_template_by_id,
    DOMAIN_TEMPLATES,
    SOFTWARE_DEV_TEMPLATE,
    OUTDOOR_CONSTRUCTION_TEMPLATE,
    MARKETING_CAMPAIGN_TEMPLATE,
    RESEARCH_PROJECT_TEMPLATE,
    DEFAULT_TEMPLATE
)

from .extraction_schema import (
    get_json_schema_for_requirement_analysis,
    get_json_schema_for_wbs
)

__all__ = [
    "DomainTemplateV2",
    "get_template_by_domain",
    "get_template_by_id",
    "DOMAIN_TEMPLATES",
    "SOFTWARE_DEV_TEMPLATE",
    "OUTDOOR_CONSTRUCTION_TEMPLATE",
    "MARKETING_CAMPAIGN_TEMPLATE",
    "RESEARCH_PROJECT_TEMPLATE",
    "DEFAULT_TEMPLATE",
    "get_json_schema_for_requirement_analysis",
    "get_json_schema_for_wbs"
]
