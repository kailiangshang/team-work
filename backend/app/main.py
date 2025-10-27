"""
FastAPI主应用
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_db
from twork.utils.logger import setup_logger

# 设置日志
setup_logger(
    log_file=settings.log_file,
    log_level=settings.log_level
)

# 创建FastAPI应用
app = FastAPI(
    title="TeamWork API",
    description="AI多角色任务协同模拟系统API",
    version="0.1.0",
    debug=settings.debug
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    # 初始化数据库
    init_db()
    print(f"TeamWork API启动成功，监听端口: {settings.backend_port}")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "TeamWork API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


# 导入API路由
from .api import upload, task, simulation, config, download, agent, graph

# 注册路由
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(task.router, prefix="/api/task", tags=["task"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["simulation"])
app.include_router(config.router, prefix="/api/config", tags=["config"])
app.include_router(download.router, prefix="/api/download", tags=["download"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(graph.router, prefix="/api/graph", tags=["graph"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug
    )
