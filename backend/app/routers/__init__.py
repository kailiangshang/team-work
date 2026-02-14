"""API 路由模块"""
from .graph import router as graph_router
from .simulation import router as simulation_router
from .project import router as project_router
from .agent import router as agent_router

# 导出命名
graph = graph_router
simulation = simulation_router
project = project_router
agent = agent_router