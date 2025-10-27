# Parser模块快速开始指南

## 重构后的新结构

```
parser/
├── tools/                        # 所有基础工具
│   ├── base_tool.py
│   ├── doc_parse_tool.py
│   ├── requirement_analyzer_tool.py
│   └── wbs_parse_tool.py
├── templates/                    # 领域模板
│   └── context_template_manager.py
├── structure_factory.py          # 简化版工厂（移除了存储功能）
└── ... (其他旧文件保持兼容)
```

## 快速使用

### 1. 基本用法

```python
from twork.parser import StructureUnderstandFactory
from twork.llm import OpenAIAdapter, LLMConfig

# 配置LLM
llm_config = LLMConfig(
    api_base_url="https://api.openai.com/v1",
    api_key="your-api-key",
    model_name="gpt-3.5-turbo"
)
llm = OpenAIAdapter(llm_config)

# 创建工厂（注意：参数已简化）
factory = StructureUnderstandFactory(
    project_id="my-project",
    original_file_path="./requirements.pdf"
)

# 配置工具
factory.tools["analyzer"].setup({"llm_adapter": llm})
factory.tools["wbs"].setup({"llm_adapter": llm})

# 执行
result = factory.run()

# 获取结果
requirements = result["requirements_and_domain"]
wbs = result["wbs"]
```

### 2. 测试环境

进入测试目录：
```bash
cd twork/test/test-parser
```

#### 方式A：使用Docker（推荐）
```bash
# 运行启动脚本
./run_test.sh

# 或手动运行
docker-compose build
docker-compose run test-parser
```

#### 方式B：本地运行
```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量（可选）
export OPENAI_API_KEY=your-key

# 运行测试
python test.py
```

## 主要变更

### ✅ 保留的功能
- ✅ 文档解析（PDF, DOCX, PPTX, MD, TXT）
- ✅ 需求提取和领域识别
- ✅ WBS任务分解
- ✅ 缓存机制
- ✅ 工具配置管理

### ❌ 移除的功能
- ❌ 快照保存/加载
- ❌ 存储后端（文件/数据库）
- ❌ 配置变更检测
- ❌ 下游任务关联

### 🔄 API变更

#### 初始化参数简化
```python
# 旧版本
factory = StructureUnderstandFactory(
    project_id="...",
    original_file_path="...",
    storage_mode="database",      # 已移除
    db_path="./snapshots.db",     # 已移除
)

# 新版本
factory = StructureUnderstandFactory(
    project_id="...",
    original_file_path="..."
)
```

#### 移除的方法
- `save_snapshot()` ❌
- `load_from_snapshot()` ❌
- `list_snapshots()` ❌
- `link_downstream_task()` ❌

## 测试文件

测试环境包含以下示例文档：
- `data/sample.md` - 团队协作系统需求
- `data/sample.txt` - 电商平台需求
- 自动生成的PDF、DOCX、PPTX文件

## 文档

- [完整API文档](./README.md)
- [重构总结](./REFACTORING_SUMMARY.md)
- [测试环境说明](../test/test-parser/README.md)

## 常见问题

**Q: 为什么移除了存储功能？**  
A: 专注于单一职责 - Parser专注于解析识别，存储可在更高层实现。

**Q: 如何运行测试？**  
A: 进入 `test-parser/` 目录，运行 `./run_test.sh`。

**Q: 旧代码还能用吗？**  
A: `run()` 方法的输出格式保持不变，但需要移除快照相关调用。

## 下一步

1. 查看测试示例了解用法
2. 阅读 API 文档了解详细功能
3. 尝试用自己的文档进行测试
