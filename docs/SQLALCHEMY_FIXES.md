# SQLAlchemy 问题修复总结

## 概述

本文档总结了在 TeamWork 项目中遇到的所有 SQLAlchemy 相关问题及其解决方案。

## 问题列表

### 1. 模型未导入导致关系解析失败

#### 错误信息
```
InvalidRequestError: When initializing mapper Mapper[Project(projects)], 
expression 'DomainConfig' failed to locate a name ('DomainConfig').
```

#### 根本原因
- `DomainConfig` 和 `TimeEstimate` 模型文件存在
- 但未在 `app/models/__init__.py` 中导入
- SQLAlchemy 无法解析 `Project` 模型中的关系引用

#### 解决方案
在 `backend/app/models/__init__.py` 中添加导入:

```python
from .domain_config import DomainConfig
from .time_estimate import TimeEstimate

__all__ = [
    "Project",
    "Task",
    "Agent",
    "SimulationLog",
    "Config",
    "DomainConfig",     # 新增
    "TimeEstimate"      # 新增
]
```

#### 最佳实践
**所有 SQLAlchemy 模型必须在 `__init__.py` 中显式导入**,确保:
1. ORM 映射注册成功
2. 关系引用能够正确解析
3. 避免循环导入问题

---

### 2. 使用保留字段名 metadata

#### 错误信息
```
InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

#### 根本原因
- SQLAlchemy Declarative Base 使用 `metadata` 属性存储表的元数据
- 不能用作模型的列名
- `SimulationLog` 模型中定义了 `metadata = Column(JSON, ...)`

#### 解决方案

**1. 修改模型定义**

`backend/app/models/simulation_log.py`:
```python
# 修改前
metadata = Column(JSON, nullable=True)  # ❌ 错误!

# 修改后  
extra_metadata = Column(JSON, nullable=True)  # ✅ 正确
```

**2. 数据库迁移**

如果数据库已有数据,需要重命名列:

**PostgreSQL**:
```sql
ALTER TABLE simulation_logs 
RENAME COLUMN metadata TO extra_metadata;
```

**SQLite**:
需要重建表(见迁移脚本)

**MySQL**:
```sql
ALTER TABLE simulation_logs 
CHANGE COLUMN metadata extra_metadata JSON;
```

**3. 使用迁移脚本**

```bash
docker exec -it teamwork-backend python scripts/migrate_metadata_column.py
```

#### SQLAlchemy 保留字段列表

以下字段名不能用作列名:
- `metadata` - 表元数据
- `__table__` - 表对象引用
- `__mapper__` - mapper 对象引用
- `__tablename__` - 表名(可用作类属性但不能作为列)
- `query` - 查询对象(在某些扩展中)

#### 命名建议

当需要存储元数据时,推荐使用:
- `extra_metadata` ✅
- `meta_data` ✅
- `custom_metadata` ✅
- `attributes` ✅
- `properties` ✅

---

## 数据库配置问题

### 3. PostgreSQL 数据库名称不匹配

#### 错误信息
```
FATAL: database "admin" does not exist
```

#### 根本原因
- Docker Compose 环境变量配置不一致
- PostgreSQL 用户名默认为 `admin`
- 但数据库名是 `teamwork`
- healthcheck 尝试连接不存在的数据库

#### 解决方案

**修改 `docker-compose.yml`**:

```yaml
postgres:
  environment:
    # 修改前
    - POSTGRES_USER=${DB_USERNAME:-admin}      # ❌
    - POSTGRES_PASSWORD=${DB_PASSWORD:-password}
    
    # 修改后
    - POSTGRES_USER=${DB_USERNAME:-teamwork_user}  # ✅
    - POSTGRES_PASSWORD=${DB_PASSWORD:-teamwork_pass}
  
  healthcheck:
    # 修改前
    test: ["CMD-SHELL", "pg_isready -U ${DB_USERNAME:-admin}"]  # ❌
    
    # 修改后
    test: ["CMD-SHELL", "pg_isready -U ${DB_USERNAME:-teamwork_user} -d ${DB_NAME:-teamwork}"]  # ✅
```

**后端环境变量**:
```yaml
backend:
  environment:
    - DATABASE_TYPE=postgresql  # 默认使用 PostgreSQL
    - DB_USERNAME=${DB_USERNAME:-teamwork_user}
    - DB_PASSWORD=${DB_PASSWORD:-teamwork_pass}
```

---

## 完整修复清单

### 文件修改

| 文件 | 修改内容 | 原因 |
|------|---------|------|
| `backend/app/models/__init__.py` | 添加 DomainConfig, TimeEstimate 导入 | 解决关系解析失败 |
| `backend/app/models/simulation_log.py` | metadata → extra_metadata | 避免保留字冲突 |
| `docker-compose.yml` | 修复数据库用户名和healthcheck | 解决数据库连接问题 |
| `.env.example` | 添加完整配置模板 | 提供配置参考 |

### 新增文件

| 文件 | 用途 |
|------|------|
| `backend/scripts/init_db.py` | 数据库初始化脚本 |
| `backend/scripts/migrate_metadata_column.py` | metadata 字段迁移脚本 |
| `docs/QUICK_FIX_GUIDE.md` | 快速修复指南 |
| `docs/SQLALCHEMY_FIXES.md` | 本文档 |

---

## 预防措施

### 1. 代码审查检查项

在添加新模型时,检查:
- [ ] 模型是否在 `__init__.py` 中导入
- [ ] 字段名是否使用了 SQLAlchemy 保留字
- [ ] 关系引用的模型名称是否正确
- [ ] 外键约束是否正确定义

### 2. 自动化检查

可以添加 pre-commit hook:

```python
# .git/hooks/pre-commit
import re
import sys

RESERVED_NAMES = ['metadata', '__table__', '__mapper__']

def check_model_files():
    # 检查模型文件中的保留字使用
    errors = []
    
    for file in get_staged_python_files():
        if '/models/' in file:
            with open(file) as f:
                content = f.read()
                for reserved in RESERVED_NAMES:
                    if re.search(rf'{reserved}\s*=\s*Column', content):
                        errors.append(f"{file}: 使用了保留字段名 '{reserved}'")
    
    return errors

if __name__ == '__main__':
    errors = check_model_files()
    if errors:
        print('\n'.join(errors))
        sys.exit(1)
```

### 3. 单元测试

添加模型验证测试:

```python
def test_all_models_imported():
    """确保所有模型都被导入"""
    from app.models import __all__
    
    expected_models = [
        'Project', 'Task', 'Agent', 'SimulationLog',
        'Config', 'DomainConfig', 'TimeEstimate'
    ]
    
    for model in expected_models:
        assert model in __all__


def test_no_reserved_field_names():
    """确保没有使用保留字段名"""
    from sqlalchemy import inspect
    from app.models import Base
    
    reserved = ['metadata', '__table__', '__mapper__']
    
    for mapper in Base.registry.mappers:
        columns = [c.name for c in inspect(mapper.class_).columns]
        for col in columns:
            assert col not in reserved, f"{mapper.class_.__name__}.{col} 使用了保留字"
```

---

## 故障排查指南

### 症状: 模型关系解析失败

1. **检查导入**
   ```bash
   grep -r "from .xxx import Xxx" backend/app/models/__init__.py
   ```

2. **验证模型名称**
   ```python
   # 在 Python shell 中
   from app.models import *
   print(Project.__mapper__.relationships)
   ```

3. **检查循环导入**
   ```bash
   python -c "from app.models import *"
   ```

### 症状: 保留字段错误

1. **搜索保留字使用**
   ```bash
   grep -rn "metadata\s*=" backend/app/models/
   grep -rn "__table__\s*=" backend/app/models/
   ```

2. **检查数据库schema**
   ```sql
   -- PostgreSQL
   \d simulation_logs
   
   -- 查看列名
   SELECT column_name FROM information_schema.columns 
   WHERE table_name = 'simulation_logs';
   ```

### 症状: 数据库连接失败

1. **检查环境变量**
   ```bash
   docker exec -it teamwork-backend env | grep DB_
   ```

2. **测试数据库连接**
   ```bash
   docker exec -it teamwork-postgres psql -U teamwork_user -d teamwork -c "SELECT 1;"
   ```

3. **查看 PostgreSQL 日志**
   ```bash
   docker-compose logs postgres | grep FATAL
   ```

---

## 参考资料

- [SQLAlchemy ORM 文档](https://docs.sqlalchemy.org/en/14/orm/)
- [Declarative Base 文档](https://docs.sqlalchemy.org/en/14/orm/declarative_base.html)
- [SQLAlchemy 最佳实践](https://docs.sqlalchemy.org/en/14/orm/tutorial.html)
- [PostgreSQL Docker 官方镜像](https://hub.docker.com/_/postgres)

---

## 总结

遇到 SQLAlchemy 问题时,按以下顺序排查:

1. **模型导入** - 确保所有模型都在 `__init__.py` 中
2. **字段命名** - 避免使用保留字
3. **数据库配置** - 检查环境变量和连接信息
4. **迁移脚本** - 对于现有数据库,运行迁移
5. **重建容器** - 清除缓存后重新构建

**记住**: 大多数 SQLAlchemy 错误都是配置问题,仔细检查模型定义和导入即可解决!
