"""
更新 simulation_logs 表结构

添加新增的字段以支持详细日志记录
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text, inspect
from backend.app.config import settings
from backend.app.models.simulation_log import SimulationLog
from backend.app.database import Base

def check_column_exists(engine, table_name, column_name):
    """检查列是否存在"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def update_simulation_logs_schema():
    """更新 simulation_logs 表结构"""
    print("=" * 60)
    print("更新 simulation_logs 表结构")
    print("=" * 60)
    
    # 创建数据库引擎
    engine = create_engine(settings.database_url)
    
    # 检查表是否存在
    inspector = inspect(engine)
    if 'simulation_logs' not in inspector.get_table_names():
        print("❌ simulation_logs 表不存在，请先运行初始化脚本")
        return False
    
    # 需要添加的新列
    new_columns = {
        'timestamp': 'DATETIME',
        'event_type': 'VARCHAR(50)',
        'role_name': 'VARCHAR(100)',
        'task_name': 'VARCHAR(255)',
        'content': 'TEXT',
        'participants': 'JSON',  # SQLite 支持 JSON，PostgreSQL/MySQL 也支持
        'status': 'VARCHAR(50)',
        'progress_percentage': 'INTEGER DEFAULT 0',
        'extra_metadata': 'JSON'
    }
    
    with engine.connect() as conn:
        # 检查并添加缺失的列
        for column_name, column_type in new_columns.items():
            if check_column_exists(engine, 'simulation_logs', column_name):
                print(f"✅ 列 '{column_name}' 已存在，跳过")
            else:
                try:
                    # SQLite 的 ALTER TABLE 语法
                    if settings.database_type == "sqlite":
                        sql = f"ALTER TABLE simulation_logs ADD COLUMN {column_name} {column_type}"
                    # PostgreSQL 的语法
                    elif settings.database_type == "postgresql":
                        # PostgreSQL 使用 JSONB 而不是 JSON
                        if column_type == 'JSON':
                            column_type = 'JSONB'
                        sql = f"ALTER TABLE simulation_logs ADD COLUMN {column_name} {column_type}"
                    # MySQL 的语法
                    elif settings.database_type == "mysql":
                        sql = f"ALTER TABLE simulation_logs ADD COLUMN {column_name} {column_type}"
                    else:
                        print(f"❌ 不支持的数据库类型: {settings.database_type}")
                        return False
                    
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"✅ 成功添加列 '{column_name}' ({column_type})")
                except Exception as e:
                    print(f"❌ 添加列 '{column_name}' 失败: {str(e)}")
                    conn.rollback()
                    return False
    
    print("\n" + "=" * 60)
    print("✅ simulation_logs 表结构更新完成！")
    print("=" * 60)
    
    # 验证所有列都存在
    print("\n验证表结构...")
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('simulation_logs')]
    print(f"当前列: {', '.join(columns)}")
    
    missing_columns = []
    for column_name in new_columns.keys():
        if column_name not in columns:
            missing_columns.append(column_name)
    
    if missing_columns:
        print(f"\n❌ 仍然缺少列: {', '.join(missing_columns)}")
        return False
    else:
        print("\n✅ 所有必需的列都已存在！")
        return True

if __name__ == "__main__":
    try:
        success = update_simulation_logs_schema()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
