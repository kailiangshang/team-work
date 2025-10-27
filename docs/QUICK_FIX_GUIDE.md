# 快速修复指南

## 问题总结

本次修复解决了以下问题:

1. ✅ **SQLAlchemy关系映射错误** - DomainConfig 和 TimeEstimate 模型未导入
2. ✅ **PostgreSQL数据库配置错误** - 数据库用户名和密码配置不一致
3. ✅ **SQLAlchemy保留字段冲突** - SimulationLog.metadata 字段名与 SQLAlchemy 保留字冲突
4. ✅ **数据库初始化** - 添加数据库初始化脚本

## 修复内容

### 1. 模型导入修复

**文件**: `backend/app/models/__init__.py`

添加了缺失的模型导入:
```python
from .domain_config import DomainConfig
from .time_estimate import TimeEstimate
```

这解决了 SQLAlchemy 错误:
```
InvalidRequestError: When initializing mapper Mapper[Project(projects)], 
expression 'DomainConfig' failed to locate a name ('DomainConfig').
```

### 2. 数据库配置修复

**文件**: `docker-compose.yml`

**修改前**:
```yaml
environment:
  - POSTGRES_USER=${DB_USERNAME:-admin}
  - POSTGRES_PASSWORD=${DB_PASSWORD:-password}
```

**修改后**:
```yaml
environment:
  - POSTGRES_USER=${DB_USERNAME:-teamwork_user}
  - POSTGRES_PASSWORD=${DB_PASSWORD:-teamwork_pass}
```

**原因**: 
- 之前使用 `admin` 作为默认用户名,但数据库名是 `teamwork`
- healthcheck 尝试连接 `admin` 数据库导致失败

### 3. SQLAlchemy 保留字段修复

**文件**: `backend/app/models/simulation_log.py`

**错误信息**:
```
InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

**原因**: 
- `metadata` 是 SQLAlchemy 的保留字段，用于存储表的元数据
- 不能用作模型的列名

**解决方案**: 
将 `metadata` 列重命名为 `extra_metadata`:

```python
# 修改前
metadata = Column(JSON, nullable=True)  # 扩展元数据

# 修改后
extra_metadata = Column(JSON, nullable=True)  # 扩展元数据
```

**数据库迁移**:
如果数据库中已经存在记录，需要运行迁移脚本:

```bash
docker exec -it teamwork-backend python scripts/migrate_metadata_column.py
```

### 4. 环境变量配置

**修改点**:
1. 将默认数据库类型从 `sqlite` 改为 `postgresql`
2. 为数据库用户名和密码添加默认值
3. 修复 healthcheck 命令

**文件**: `.env.example`

提供了完整的配置模板,包括:
- 数据库配置
- LLM配置(支持OpenAI和阿里云)
- 服务端口配置
- 日志和文件上传配置

### 4. 数据库初始化脚本

**文件**: `backend/scripts/init_db.py`

新增功能:
- 自动创建所有数据库表
- 验证表是否正确创建
- 详细的日志输出

## 使用方法

### 方法1: 重新启动服务(推荐)

```bash
cd /Users/kaiiangs/Desktop/team\ work/team-work

# 停止并删除旧容器和数据卷
# 注意: -v 会删除所有数据，请确认备份
Docker-compose down -v

# 重新构建并启动
docker-compose up --build
```

**重要**: 如果你之前有生产数据，使用方法2或方法3保留数据。

### 方法2: 保留数据重启(适用于有生产数据)

如果想保留现有数据:

```bash
# 只停止容器
docker-compose down

# 重新启动
docker-compose up --build
```

**然后运行迁移脚本**:

```bash
# 迁移 metadata 字段
docker exec -it teamwork-backend python scripts/migrate_metadata_column.py

# 重启后端以应用更改
docker-compose restart backend
```

### 方法3: 手动初始化数据库(适用于新安装)

```bash
# 进入后端容器
docker exec -it teamwork-backend bash

# 运行初始化脚本
python scripts/init_db.py

# 退出容器
exit
```

## 配置说明

### 创建 .env 文件

```bash
cd /Users/kaiiangs/Desktop/team\ work/team-work
cp .env.example .env
```

编辑 `.env` 文件,填写实际配置:

```env
# 数据库配置
DATABASE_TYPE=postgresql
DB_NAME=teamwork
DB_USERNAME=teamwork_user
DB_PASSWORD=your_secure_password

# LLM配置(根据实际使用的服务选择)

# 选项1: OpenAI
LLM_API_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-your-openai-key
LLM_MODEL_NAME=gpt-4

# 选项2: 阿里云通义千问
# LLM_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# LLM_API_KEY=sk-your-dashscope-key
# LLM_MODEL_NAME=qwen-plus
```

## 验证修复

### 1. 检查后端日志

```bash
docker-compose logs -f backend
```

应该看到:
```
INFO:     Application startup complete.
TeamWork API启动成功，监听端口: 8000
```

### 2. 检查数据库连接

```bash
docker-compose logs postgres
```

应该看到:
```
database system is ready to accept connections
```

不应该再看到:
```
FATAL: database "admin" does not exist
```

### 3. 测试文档上传

访问前端: http://localhost:7860

1. 配置LLM(如果还没配置)
2. 上传测试文档
3. 应该成功解析,不再出现500错误

### 4. 检查数据库表

```bash
# 进入PostgreSQL容器
docker exec -it teamwork-postgres psql -U teamwork_user -d teamwork

# 列出所有表
\dt

# 应该看到:
# - projects
# - tasks
# - agents
# - simulation_logs
# - configs
# - domain_configs
# - time_estimates

# 退出
\q
```

## 常见问题

### Q1: 仍然看到 "database admin does not exist" 错误

**解决方法**:
```bash
# 完全清除数据库卷
docker-compose down -v
docker volume rm teamwork_postgres_data

# 重新启动
docker-compose up --build
```

### Q2: SQLAlchemy 仍然报错找不到 DomainConfig 或 metadata 保留字错误

**解决方法**:
```bash
# 重建容器以清除Python缓存
docker-compose build --no-cache backend
docker-compose up backend
```

如果还是报 metadata 错误:
```bash
# 进入容器检查代码
docker exec -it teamwork-backend bash

# 查看 SimulationLog 模型
grep -n "metadata" app/models/simulation_log.py

# 应该看到 extra_metadata 而不是 metadata
```

### Q3: 上传文档失败,提示 LLM 配置错误

**解决方法**:
1. 进入前端配置页面
2. 填写正确的 LLM API 信息
3. 点击"测试连接"验证
4. 点击"保存配置"

### Q4: 如何切换到 SQLite 而不是 PostgreSQL

编辑 `docker-compose.yml`:
```yaml
environment:
  - DATABASE_TYPE=sqlite
```

或在 `.env` 文件中设置:
```env
DATABASE_TYPE=sqlite
SQLITE_PATH=/app/data/db/teamwork.db
```

## 数据库迁移

如果以后需要修改数据库结构,可以使用 Alembic:

```bash
# 进入后端容器
docker exec -it teamwork-backend bash

# 创建迁移
alembic revision --autogenerate -m "describe your changes"

# 应用迁移
alembic upgrade head
```

## 性能优化建议

### PostgreSQL调优

在 `docker-compose.yml` 中添加 PostgreSQL 配置:

```yaml
postgres:
  command: 
    - "postgres"
    - "-c"
    - "shared_buffers=256MB"
    - "-c"
    - "max_connections=100"
```

### 数据库连接池

在 `backend/app/config.py` 中已配置:
```python
db_pool_size: int = Field(default=10, gt=0)
```

可根据实际负载调整。

## 监控建议

### 添加 PostgreSQL 监控

可以添加 pgAdmin 服务:

```yaml
pgadmin:
  image: dpage/pgadmin4
  environment:
    PGADMIN_DEFAULT_EMAIL: admin@teamwork.com
    PGADMIN_DEFAULT_PASSWORD: admin
  ports:
    - "5050:80"
  networks:
    - teamwork-network
```

访问 http://localhost:5050 管理数据库。

## 回滚方案

如果修复导致问题,可以回滚:

```bash
# 停止服务
docker-compose down

# 恢复到之前的配置
git checkout docker-compose.yml backend/app/models/__init__.py

# 重新启动
docker-compose up
```

## 联系支持

如果问题仍然存在:
1. 收集日志: `docker-compose logs > logs.txt`
2. 记录错误截图
3. 提供 `.env` 配置(隐藏敏感信息)
