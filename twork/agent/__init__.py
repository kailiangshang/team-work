"""
Agent模块

负责角色Agent生成、多Agent协同和任务模拟执行。
支持模拟元信息,实现可编辑性设计。
"""

from .role_generator import RoleGenerator
from .multi_agent_runner import MultiAgentRunner
from .simulation_engine import SimulationEngine
from .conflict_resolver import ConflictResolver
from .debate_simulator import DebateSimulator
from .simulation_metadata import (
    SimulationMetadata,
    SimulationConfig,
    AgentModification,
    TaskModification,
    apply_metadata_to_agents,
    apply_metadata_to_tasks,
    apply_manual_assignments
)

__all__ = [
    "RoleGenerator",
    "MultiAgentRunner",
    "SimulationEngine",
    "ConflictResolver",
    "DebateSimulator",
    "SimulationMetadata",
    "SimulationConfig",
    "AgentModification",
    "TaskModification",
    "apply_metadata_to_agents",
    "apply_metadata_to_tasks",
    "apply_manual_assignments",
]
