# SQLAlchemy 保留字段修复文档

## 问题描述

后端服务启动时报错:
```
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

## 根本原因

在 `AgentExecutionLog` 模型中使用了 `metadata` 作为列名,这是 SQLAlchemy Declarative API 的保留字段名,导致模型定义冲突。

根据项目规范(memory: `e6ab093f-6d80-4b87-9e1c-1b5e5daf29c6`):
> 在 SQLAlchemy Declarative API 中,禁止使用 'metadata'、'__table__'、'__mapper__' 等作为模型属性名,这些是框架保留字段。应使用 'extra_metadata'、'meta_data' 等替代名称。

## 修复方案

### 1. 更新模型定义

修改 `backend/app/models/agent_execution_log.py`:
- 将 `metadata` 字段重命名为 `extra_metadata`
- 更新 `to_dict()` 方法中的字段名

### 2. 更新服务层引用

修改 `backend/app/services/simulation_service.py`:
- 更新所有 `AgentExecutionLog` 创建时的字段名
- 更新查询结果的字段引用

### 3. 数据库迁移

创建迁移脚本 `backend/scripts/migrate_agent_execution_logs.py`:
- 支持 PostgreSQL、SQLite、MySQL 三种数据库
- 自动检测并重命名现有表的列
- 包含验证逻辑确保迁移成功

### 4. 更新 Dockerfile

修改 `backend/Dockerfile`:
- 添加 scripts 目录的复制,使迁移脚本可在容器中使用

## 修改文件列表

1. `backend/app/models/agent_execution_log.py` - 模型定义
2. `backend/app/services/simulation_service.py` - 服务层(2处引用)
3. `backend/scripts/migrate_agent_execution_logs.py` - 新增迁移脚本
4. `backend/Dockerfile` - 添加 scripts 目录复制

## 执行步骤

1. 停止后端服务
   ```bash
   docker-compose stop backend
   ```

2. 重新构建镜像
   ```bash
   docker-compose build backend
   ```

3. 启动服务
   ```bash
   docker-compose up -d backend
   ```

4. 运行数据库迁移(如果有现有数据)
   ```bash
   docker-compose exec backend python /app/scripts/migrate_agent_execution_logs.py
   ```

## 验证结果

- ✅ 后端服务正常启动,无 SQLAlchemy 错误
- ✅ 数据库迁移成功完成
- ✅ `extra_metadata` 列存在,`metadata` 列已删除
- ✅ 所有容器正常运行

## 相关问题

同样的问题在 `SimulationLog` 模型中也曾出现过,已通过 `migrate_metadata_column.py` 脚本修复。建议在创建新模型时注意避免使用 SQLAlchemy 保留字段名。

## 预防措施

1. 在代码审查时检查是否使用了保留字段名
2. 参考项目规范中的命名规范
3. 使用 IDE 或 linter 工具检测潜在冲突

## 修复时间

2025-10-26

## 修复人员

AI Assistant (Qoder)
