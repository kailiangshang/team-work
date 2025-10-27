"""
数据库连接管理
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from .config import settings

# 创建数据库引擎
if settings.database_type == "sqlite":
    # 确保SQLite数据库目录存在
    db_path = Path(settings.sqlite_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},  # SQLite特殊配置
        echo=settings.debug,
    )
else:
    engine = create_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        pool_pre_ping=True,  # 连接前检查
        echo=settings.debug,
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话（依赖注入）
    
    Yields:
        数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表"""
    # 导入所有模型
    from .models import (
        project, task, agent, simulation_log, config, 
        domain_config, time_estimate, agent_execution_log, daily_summary
    )
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
