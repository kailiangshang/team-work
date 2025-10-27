# 数据库表结构更新问题修复

## 问题描述

运行模拟时出现数据库错误：

```
ERROR | (sqlite3.OperationalError) table simulation_logs has no column named timestamp
```

## 问题原因

[`SimulationLog`](file:///Users/kaiiangs/Desktop/team%20work/team-work/backend/app/models/simulation_log.py) 模型添加了新字段来支持详细日志记录，但数据库中的表结构没有相应更新。

**新增字段**：
- `timestamp` - 日志时间戳
- `event_type` - 事件类型（task_start, task_complete, discussion等）
- `role_name` - Agent角色名称
- `task_name` - 任务名称
- `content` - 对话内容或事件描述
- `participants` - 参与者列表（JSON）
- `status` - 状态（in_progress, completed, blocked）
- `progress_percentage` - 进度百分比
- `extra_metadata` - 扩展元数据（JSON）

## 解决方案

### 临时修复：直接在容器中执行 SQL

```bash
docker exec teamwork-backend python -c "
from app.database import engine
from sqlalchemy import text, inspect

inspector = inspect(engine)
existing_columns = [col['name'] for col in inspector.get_columns('simulation_logs')]

new_columns = {
    'timestamp': 'DATETIME',
    'event_type': 'VARCHAR(50)',
    'role_name': 'VARCHAR(100)',
    'task_name': 'VARCHAR(255)',
    'content': 'TEXT',
    'participants': 'TEXT',
    'status': 'VARCHAR(50)',
    'progress_percentage': 'INTEGER DEFAULT 0',
    'extra_metadata': 'TEXT'
}

with engine.connect() as conn:
    for col_name, col_type in new_columns.items():
        if col_name not in existing_columns:
            sql = f'ALTER TABLE simulation_logs ADD COLUMN {col_name} {col_type}'
            conn.execute(text(sql))
            conn.commit()
            print(f'✅ 添加列 {col_name}')
"
```

### 永久方案：使用数据库迁移脚本

创建了 `backend/scripts/update_simulation_logs_schema.py` 迁移脚本，支持：
- ✅ SQLite
- ✅ PostgreSQL
- ✅ MySQL

**使用方法**：
```bash
# 在容器中执行
docker exec teamwork-backend python scripts/update_simulation_logs_schema.py

# 或在本地执行
cd backend
python scripts/update_simulation_logs_schema.py
```

## 更新后的表结构

```sql
CREATE TABLE simulation_logs (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    day_number INTEGER NOT NULL,
    agent_id VARCHAR(50) NOT NULL,
    task_id VARCHAR(50),
    start_time VARCHAR(10),
    end_time VARCHAR(10),
    output TEXT,
    discussion TEXT,
    notes TEXT,
    
    -- 新增字段
    timestamp DATETIME,
    event_type VARCHAR(50),
    role_name VARCHAR(100),
    task_name VARCHAR(255),
    content TEXT,
    participants TEXT,  -- JSON字符串
    status VARCHAR(50),
    progress_percentage INTEGER DEFAULT 0,
    extra_metadata TEXT  -- JSON字符串
);
```

## 验证修复

### 1. 检查表结构

```bash
docker exec teamwork-backend python -c "
from app.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
columns = [col['name'] for col in inspector.get_columns('simulation_logs')]
print('表列:', columns)
"
```

**预期输出**：
```
表列: ['id', 'project_id', 'day_number', 'agent_id', 'task_id', 'start_time', 'end_time', 'output', 'discussion', 'notes', 'timestamp', 'event_type', 'role_name', 'task_name', 'content', 'participants', 'status', 'progress_percentage', 'extra_metadata']
```

### 2. 测试模拟

1. 上传文档
2. 拆解任务
3. 生成 Agent
4. 点击"▶️ 开始模拟"
5. 应该可以正常运行，不再出现数据库错误

## 注意事项

### 数据库迁移最佳实践

1. **使用 Alembic 进行版本化迁移**（推荐）：
   ```bash
   # 生成迁移脚本
   alembic revision --autogenerate -m "add simulation log fields"
   
   # 执行迁移
   alembic upgrade head
   ```

2. **手动迁移**（当前方案）：
   - 适用于快速修复
   - 需要手动维护 SQL
   - 可能在不同数据库间不兼容

3. **重建数据库**（开发环境）：
   ```bash
   # 删除旧数据库
   docker exec teamwork-backend rm -f /app/data/db/teamwork.db
   
   # 重启容器，自动重建
   docker-compose restart backend
   ```

### 生产环境建议

1. **备份数据库**：
   ```bash
   docker exec teamwork-backend sqlite3 /app/data/db/teamwork.db ".backup /tmp/backup.db"
   ```

2. **测试迁移**：
   - 在测试环境先执行
   - 验证数据完整性
   - 确认应用正常运行

3. **回滚计划**：
   - 保留旧表备份
   - 准备回滚脚本

## 相关文档

- [SIMULATE_STREAM_ERROR_FIX.md](./SIMULATE_STREAM_ERROR_FIX.md) - simulate_stream 方法缺失问题
- [SQLALCHEMY_FIXES.md](./SQLALCHEMY_FIXES.md) - SQLAlchemy 问题修复总结

## 更新时间

2025-10-25
