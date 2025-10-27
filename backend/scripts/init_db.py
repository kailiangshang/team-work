"""
数据库初始化脚本

确保所有必要的表和数据被正确创建
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, Base, init_db
from app.models import (
    Project,
    Task,
    Agent,
    SimulationLog,
    Config,
    DomainConfig,
    TimeEstimate
)
from twork.utils.logger import get_logger

logger = get_logger("db_init")


def create_tables():
    """创建所有表"""
    logger.info("开始创建数据库表...")
    
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功！")
        
        # 显示创建的表
        logger.info(f"已创建的表: {list(Base.metadata.tables.keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"创建数据库表失败: {str(e)}")
        return False


def verify_tables():
    """验证表是否存在"""
    logger.info("验证数据库表...")
    
    try:
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        logger.info(f"现有表: {existing_tables}")
        
        expected_tables = [
            "projects",
            "tasks",
            "agents",
            "simulation_logs",
            "configs",
            "domain_configs",
            "time_estimates"
        ]
        
        missing_tables = [t for t in expected_tables if t not in existing_tables]
        
        if missing_tables:
            logger.warning(f"缺少的表: {missing_tables}")
            return False
        else:
            logger.info("✅ 所有表都已存在")
            return True
            
    except Exception as e:
        logger.error(f"验证表失败: {str(e)}")
        return False


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("TeamWork 数据库初始化")
    logger.info("=" * 60)
    
    # 初始化数据库
    init_db()
    
    # 创建表
    if create_tables():
        # 验证表
        if verify_tables():
            logger.info("\n✅ 数据库初始化成功！")
            return 0
        else:
            logger.error("\n❌ 数据库验证失败")
            return 1
    else:
        logger.error("\n❌ 数据库初始化失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
