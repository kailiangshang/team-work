"""
Version模块 - 版本管理与差异对比

主要功能:
- 项目快照创建
- 版本历史管理
- 版本差异对比
- 变更追踪
"""

from .version_manager import VersionManager
from .diff_generator import DiffGenerator

__all__ = [
    "VersionManager",
    "DiffGenerator",
]
