"""
UI组件模块
"""

from .upload_panel import create_upload_panel
from .discussion_panel import create_discussion_panel
from .graph_panel import create_graph_panel
from .config_panel import create_config_panel

__all__ = [
    "create_upload_panel",
    "create_discussion_panel",
    "create_graph_panel",
    "create_config_panel",
]
