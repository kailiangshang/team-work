# TeamWork v0.2.0 部署指南

## 📋 前置要求

- Python 3.8+
- PostgreSQL 12+（可选，数据库持久化需要）
- OpenAI API Key（用于LLM功能）

## 🚀 快速部署

### 1. 安装依赖

```bash
# 进入项目目录
cd "/Users/kaiiangs/Desktop/team work"

# 安装twork核心库（开发模式）
pip install -e .

# 安装后端依赖
cd team-work/backend
pip install -r requirements.txt

# 安装前端依赖（如需）
cd ../frontend
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# LLM配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# 数据库配置（可选）
DATABASE_URL=postgresql://user:password@localhost/teamwork

# 其他配置
SECRET_KEY=your_secret_key_here
DEBUG=True
```

### 3. 数据库迁移（如使用PostgreSQL）

```bash
cd team-work/backend

# 生成迁移文件
alembic revision --autogenerate -m "Add v0.2.0 features"

# 执行迁移
alembic upgrade head
```

### 4. 启动服务

```bash
# 启动后端API
cd team-work/backend
uvicorn app.main:app --reload --port 8000

# 启动前端（Gradio界面）
cd team-work/frontend
python app.py
```

## 📦 新增模块清单

### twork核心库模块

**已创建的模块文件**:
1. `twork/parser/domain_classifier.py` ✅
2. `twork/parser/context_template_manager.py` ✅
3. `twork/parser/wbs_decomposer.py` ✅
4. `twork/estimator/complexity_analyzer.py` ✅
5. `twork/estimator/time_estimator.py` ✅
6. `twork/agent/conflict_resolver.py` ✅
7. `twork/agent/debate_simulator.py` ✅
8. `twork/generator/gantt_generator.py` ✅
9. `twork/generator/risk_analyzer.py` ✅
10. `twork/version/version_manager.py` ✅
11. `twork/version/diff_generator.py` ✅

### 后端API接口

**已创建的API文件**:
1. `backend/app/api/domain.py` ✅ - 领域识别API
2. `backend/app/api/task_tree.py` ✅ - 任务树管理API
3. `backend/app/api/estimation.py` ✅ - 时间估算API

**已创建的数据模型**:
1. `backend/app/models/domain_config.py` ✅
2. `backend/app/models/time_estimate.py` ✅

### API路由注册

在 `backend/app/main.py` 中添加：

```python
from app.api import domain, task_tree, estimation

# 注册新路由
app.include_router(domain.router)
app.include_router(task_tree.router)
app.include_router(estimation.router)
```

## 🔌 API使用示例

### 1. 领域识别

```bash
curl -X POST "http://localhost:8000/api/domain/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "user_selected_domain": "软件开发"
  }'
```

### 2. WBS任务拆解

```bash
curl -X POST "http://localhost:8000/api/task-tree/decompose" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "max_level": 4
  }'
```

### 3. 时间估算

```bash
curl -X POST "http://localhost:8000/api/estimation/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "total_days": 30,
    "team_size": 5,
    "work_hours_per_day": 8
  }'
```

## 🧪 功能测试

运行测试脚本验证核心功能：

```bash
cd "/Users/kaiiangs/Desktop/team work"
python3 test_new_features.py
```

预期输出：
- ✅ 领域分类器测试通过
- ✅ 模板管理器测试通过
- ✅ 复杂度分析器测试通过
- ✅ 时间估算器测试通过
- ✅ 冲突解决器测试通过
- ✅ 甘特图生成器测试通过
- ✅ 风险分析器测试通过
- ✅ 版本管理器测试通过

## 📊 数据库表结构

### 新增表

1. **domain_configs** - 领域配置
   - 字段：id, project_id, domain_type, confidence, keywords, template_id, template_config, extracted_context

2. **time_estimates** - 时间估算
   - 字段：id, project_id, task_id, complexity_score, base_duration, estimated_duration, confidence, is_critical_path

### 更新表

1. **tasks** - 任务表（新增字段）
   - parent_task_id - 父任务ID
   - level - 层级(1-4)
   - sort_order - 排序
   - task_type - 任务类型
   - estimated_complexity - 复杂度(1-10)

## ⚙️ 配置说明

### 领域模板配置

可在 `twork/parser/context_template_manager.py` 中添加新领域：

```python
"new_domain_v1": DomainTemplate(
    domain_type="新领域",
    template_id="new_domain_v1",
    focus_points=["关注点1", "关注点2"],
    task_types=["任务类型1", "任务类型2"],
    role_types=["角色1", "角色2"],
    extraction_patterns={},
    default_config={}
)
```

### 复杂度关键词配置

在 `twork/estimator/complexity_analyzer.py` 中调整关键词权重：

```python
TECH_KEYWORDS_WEIGHT = {
    "高复杂度": ["自定义关键词"],
    "中复杂度": ["自定义关键词"],
    "低复杂度": ["自定义关键词"]
}
```

## 🐛 故障排查

### 问题1：LLM调用失败

**解决方案**：
- 检查 `OPENAI_API_KEY` 是否正确
- 验证网络连接
- 查看API额度是否充足

### 问题2：数据库连接错误

**解决方案**：
- 确认PostgreSQL服务已启动
- 检查DATABASE_URL配置
- 运行数据库迁移

### 问题3：模块导入错误

**解决方案**：
```bash
# 重新安装twork库
pip install -e .

# 检查Python路径
export PYTHONPATH="/Users/kaiiangs/Desktop/team work:$PYTHONPATH"
```

## 📝 日志配置

在 `twork/utils/logger.py` 中配置日志级别：

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 🔐 安全建议

1. **生产环境**：
   - 不要在代码中硬编码API密钥
   - 使用环境变量或密钥管理服务
   - 启用HTTPS

2. **API限流**：
   - 配置FastAPI的rate limiting
   - 限制LLM调用频率

3. **数据验证**：
   - 所有API输入都经过Pydantic验证
   - 防止SQL注入

## 🚀 性能优化

1. **缓存策略**：
```python
# 使用Redis缓存领域识别结果
from functools import lru_cache

@lru_cache(maxsize=100)
def classify_cached(content_hash):
    return classifier.classify(content)
```

2. **异步处理**：
```python
# WBS拆解使用异步任务
from celery import Celery

@celery.task
def decompose_async(project_id):
    # 异步执行拆解
    pass
```

## 📚 更多文档

- [完整实现说明](./IMPLEMENTATION_SUMMARY.md)
- [新功能使用指南](./README_V2_FEATURES.md)
- [测试脚本](./test_new_features.py)

---

**部署完成后，访问**：
- API文档：http://localhost:8000/docs
- 前端界面：http://localhost:7860

祝部署顺利！🎉
