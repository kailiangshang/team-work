"""
API路由模块
"""

from .upload import router as upload_router
from .task import router as task_router
from .simulation import router as simulation_router
from .config import router as config_router

__all__ = ["upload_router", "task_router", "simulation_router", "config_router"]
