"""
数据库迁移脚本: 重命名 agent_execution_logs.metadata 为 extra_metadata

由于 'metadata' 是 SQLAlchemy 的保留字段,需要重命名为 'extra_metadata'
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine
from sqlalchemy import text, inspect
from twork.utils.logger import get_logger

logger = get_logger("migrate_agent_logs")


def check_column_exists(table_name: str, column_name: str) -> bool:
    """检查列是否存在"""
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception as e:
        logger.error(f"检查列失败: {str(e)}")
        return False


def migrate():
    """执行迁移"""
    logger.info("=" * 60)
    logger.info("开始迁移 agent_execution_logs.metadata 字段")
    logger.info("=" * 60)
    
    try:
        with engine.connect() as conn:
            # 检查表是否存在
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if 'agent_execution_logs' not in tables:
                logger.info("✅ agent_execution_logs 表不存在,无需迁移")
                return True
            
            # 检查旧列是否存在
            has_old_column = check_column_exists('agent_execution_logs', 'metadata')
            has_new_column = check_column_exists('agent_execution_logs', 'extra_metadata')
            
            if not has_old_column and has_new_column:
                logger.info("✅ 已经完成迁移,extra_metadata 列存在")
                return True
            
            if not has_old_column and not has_new_column:
                logger.info("✅ 两个列都不存在,表结构将由 ORM 创建")
                return True
            
            if has_old_column:
                logger.info(f"发现旧列 'metadata',开始重命名...")
                
                # PostgreSQL
                if 'postgresql' in str(engine.url):
                    conn.execute(text(
                        "ALTER TABLE agent_execution_logs "
                        "RENAME COLUMN metadata TO extra_metadata"
                    ))
                    conn.commit()
                    logger.info("✅ PostgreSQL: 列重命名成功")
                
                # SQLite (需要重建表)
                elif 'sqlite' in str(engine.url):
                    logger.info("SQLite 数据库需要重建表...")
                    
                    # 1. 创建新表
                    conn.execute(text("""
                        CREATE TABLE agent_execution_logs_new (
                            id INTEGER PRIMARY KEY,
                            project_id INTEGER NOT NULL,
                            day_number INTEGER NOT NULL,
                            agent_id VARCHAR(50) NOT NULL,
                            role_name VARCHAR(100),
                            task_id VARCHAR(50),
                            task_name VARCHAR(255),
                            action_type VARCHAR(50) NOT NULL,
                            start_time TIME,
                            end_time TIME,
                            content TEXT,
                            output TEXT,
                            extra_metadata JSON,
                            created_at DATETIME NOT NULL,
                            FOREIGN KEY (project_id) REFERENCES projects(id)
                        )
                    """))
                    
                    # 2. 复制数据
                    conn.execute(text("""
                        INSERT INTO agent_execution_logs_new 
                        SELECT id, project_id, day_number, agent_id, role_name,
                               task_id, task_name, action_type, start_time, end_time,
                               content, output, metadata, created_at
                        FROM agent_execution_logs
                    """))
                    
                    # 3. 删除旧表
                    conn.execute(text("DROP TABLE agent_execution_logs"))
                    
                    # 4. 重命名新表
                    conn.execute(text("ALTER TABLE agent_execution_logs_new RENAME TO agent_execution_logs"))
                    
                    conn.commit()
                    logger.info("✅ SQLite: 表重建成功")
                
                # MySQL
                elif 'mysql' in str(engine.url):
                    conn.execute(text(
                        "ALTER TABLE agent_execution_logs "
                        "CHANGE COLUMN metadata extra_metadata JSON"
                    ))
                    conn.commit()
                    logger.info("✅ MySQL: 列重命名成功")
                
                else:
                    logger.warning(f"未知数据库类型: {engine.url}")
                    return False
            
            logger.info("\n✅ 迁移完成!")
            return True
            
    except Exception as e:
        logger.error(f"❌ 迁移失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def verify():
    """验证迁移结果"""
    logger.info("\n验证迁移结果...")
    
    try:
        has_new = check_column_exists('agent_execution_logs', 'extra_metadata')
        has_old = check_column_exists('agent_execution_logs', 'metadata')
        
        if has_new and not has_old:
            logger.info("✅ 验证成功: extra_metadata 列存在, metadata 列已删除")
            return True
        elif has_old:
            logger.error("❌ 验证失败: metadata 列仍然存在")
            return False
        else:
            logger.info("ℹ️  表不存在或列未创建")
            return True
            
    except Exception as e:
        logger.error(f"验证失败: {str(e)}")
        return False


def main():
    """主函数"""
    if migrate():
        if verify():
            logger.info("\n🎉 迁移和验证都成功完成!")
            return 0
        else:
            logger.error("\n⚠️  迁移完成但验证失败")
            return 1
    else:
        logger.error("\n❌ 迁移失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
