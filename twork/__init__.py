"""
TeamWork - AI多角色任务协同模拟系统核心库

这是一个基于大模型Agent的智能任务模拟系统核心技术模块。
能够将任意类型的需求文档自动拆解为结构化任务，并通过多角色Agent模拟真实项目执行过程。

主要功能:
- 文档解析与需求提取
- 领域分类与WBS拆解
- 任务智能拆解
- 多角色Agent生成与协同模拟
- 冲突解决与讨论模拟
- 复杂度分析与时间估算
- 任务编排图谱生成
- 甘特图与风险分析
- 版本管理与差异对比
- 结果可视化输出
"""

__version__ = "0.3.0"
__author__ = "TeamWork Team"

# Parser模块
from .parser import (
    StructureUnderstandFactory,
    DocParseTool,
    RequirementAndDomainAnalyzerTool,
    WbsParseTool,
    DomainTemplateV2,
    get_template_by_domain,
    EntityExtractor,
    RelationExtractor,
)

# Agent模块
from .agent import (
    RoleGenerator,
    MultiAgentRunner,
    SimulationEngine,
    ConflictResolver,
    DebateSimulator,
)

# Generator模块
from .generator import (
    DocumentGenerator,
    CSVExporter,
    GraphBuilder,
    GanttGenerator,
    RiskAnalyzer,
)

# Estimator模块
from .estimator import (
    ComplexityAnalyzer,
    TimeEstimator,
)

# Version模块
from .version import (
    VersionManager,
    DiffGenerator,
)

# LLM模块
from .llm import LLMAdapter, OpenAIAdapter

__all__ = [
    # Parser
    "StructureUnderstandFactory",
    "DocParseTool",
    "RequirementAndDomainAnalyzerTool",
    "WbsParseTool",
    "DomainTemplateV2",
    "get_template_by_domain",
    "EntityExtractor",
    "RelationExtractor",
    # Agent
    "RoleGenerator",
    "MultiAgentRunner",
    "SimulationEngine",
    "ConflictResolver",
    "DebateSimulator",
    # Generator
    "DocumentGenerator",
    "CSVExporter",
    "GraphBuilder",
    "GanttGenerator",
    "RiskAnalyzer",
    # Estimator
    "ComplexityAnalyzer",
    "TimeEstimator",
    # Version
    "VersionManager",
    "DiffGenerator",
    # LLM
    "LLMAdapter",
    "OpenAIAdapter",
]
