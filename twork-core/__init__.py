"""TWork Core - 核心库

核心模块包括：
- schemas: 数据模型
- graph: 知识图谱层
- llm: LLM 适配层
- parser: 文档解析器
- agent: Agent 引擎
- simulation: 模拟引擎
"""

from .schemas import *
from .graph import FalkorDBClient as GraphClient, GraphStore, GraphBuilder
from .llm import BaseLLM, LLMConfig, OpenAIAdapter, PromptTemplates
from .parser import DocumentParser, EntityExtractor
from .agent import BaseAgent, TaskAgent, EnvironmentAgent, MultiAgentRunner
from .simulation import SimulationEngine, StateManager

__version__ = "1.0.0"

__all__ = [
    # Graph
    "GraphClient",
    "GraphStore", 
    "GraphBuilder",
    # LLM
    "BaseLLM",
    "LLMConfig",
    "OpenAIAdapter",
    "PromptTemplates",
    # Parser
    "DocumentParser",
    "EntityExtractor",
    # Agent
    "BaseAgent",
    "TaskAgent",
    "EnvironmentAgent",
    "MultiAgentRunner",
    # Simulation
    "SimulationEngine",
    "StateManager",
]