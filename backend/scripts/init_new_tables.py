"""
数据库初始化脚本

创建新增的agent_execution_logs和daily_summaries表。
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import Base, engine
from app.models import (
    Project, Task, Agent, SimulationLog, Config, DomainConfig, TimeEstimate,
    AgentExecutionLog, DailySummary
)


def init_new_tables():
    """初始化新表"""
    print("开始创建新表...")
    
    # 只创建新表，不影响现有表
    AgentExecutionLog.__table__.create(bind=engine, checkfirst=True)
    DailySummary.__table__.create(bind=engine, checkfirst=True)
    
    print("✅ 新表创建完成!")
    print("  - agent_execution_logs")
    print("  - daily_summaries")


def init_all_tables():
    """初始化所有表"""
    print("开始创建所有表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 所有表创建完成!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库初始化脚本")
    parser.add_argument(
        "--mode",
        choices=["new", "all"],
        default="new",
        help="初始化模式: new=只创建新表, all=创建所有表"
    )
    
    args = parser.parse_args()
    
    if args.mode == "new":
        init_new_tables()
    else:
        init_all_tables()
