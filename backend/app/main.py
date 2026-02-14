"""FastAPI 后端主入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .config import settings
from .routers import graph, simulation, project, agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Starting up...")
    # 初始化资源
    yield
    logger.info("Shutting down...")
    # 清理资源


app = FastAPI(
    title="TWork API",
    description="项目管理多Agent模拟系统 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(graph, prefix="/api/graph", tags=["Graph"])
app.include_router(simulation, prefix="/api/simulation", tags=["Simulation"])
app.include_router(project, prefix="/api/project", tags=["Project"])
app.include_router(agent, prefix="/api/agent", tags=["Agent"])


@app.get("/")
async def root():
    return {"message": "TWork API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}