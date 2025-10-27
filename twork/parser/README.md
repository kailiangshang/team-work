# Parser 模块 - 结构化信息生产工厂

Parser 模块实现了结构化信息生产工厂（`StructureUnderstandFactory`），用于解析项目文档、提取需求、生成WBS任务树，并支持配置快照与回滚功能。

## 模块结构

```
parser/
├── __init__.py                      # 模块导出
├── base_tool.py                     # 工具基类
├── doc_parse_tool.py                # 文档解析工具
├── requirement_analyzer_tool.py     # 需求与领域分析工具
├── wbs_parse_tool.py                # WBS任务拆解工具
├── storage_backend.py               # 存储后端（文件/数据库）
├── structure_factory.py             # 核心工厂类
└── README.md                        # 本文档
```

## 核心概念

### 工具（Tool）

所有工具继承自`BaseTool`基类，提供统一的LLM调用接口：

- **DocParseTool**: 解析文档为结构化章节
- **RequirementAndDomainAnalyzerTool**: 提取需求并识别领域
- **WbsParseTool**: 生成WBS任务树

### 存储后端（Storage Backend）

支持两种存储模式：

- **FileStorageBackend**: 文件系统存储（JSON文件）
- **SqliteStorageBackend**: SQLite数据库存储

### 快照（Snapshot）

快照记录了工厂配置的完整状态，包括：
- 工具配置
- 配置变更历史
- 下游任务关联
- 可选的输出结果

## 快速开始

### 基础使用

```python
from twork.parser import StructureUnderstandFactory
from twork.llm import OpenAIAdapter, LLMConfig

# 配置LLM
llm_config = LLMConfig(
    api_base_url="https://api.openai.com/v1",
    api_key="your-api-key",
    model_name="gpt-4"
)
llm = OpenAIAdapter(llm_config)

# 创建工厂
factory = StructureUnderstandFactory(
    project_id="P-DOC-001",
    original_file_path="./docs/需求文档.pdf",
    storage_mode="database"  # 或 "file"
)

# 配置工具的LLM适配器
factory.tools["analyzer"].setup({"llm_adapter": llm})
factory.tools["wbs"].setup({"llm_adapter": llm})

# 执行完整流程
result = factory.run()

print(result["requirements_and_domain"])
print(result["wbs"])
```

### 自定义工具配置

```python
# 自定义分析工具的提示词
custom_analyzer = RequirementAndDomainAnalyzerTool()
custom_analyzer.setup({
    "llm_adapter": llm,
    "prompt_template": "你是专业的需求分析师...",
    "temperature": 0.3
})

# 替换默认工具
factory.use_tool("analyzer", custom_analyzer)

# 自定义WBS工具配置
custom_wbs = WbsParseTool()
custom_wbs.setup({
    "llm_adapter": llm,
    "max_level": 4,  # 设置最大层级为4
    "temperature": 0.5
})

factory.use_tool("wbs", custom_wbs)
```

### 快照管理

```python
# 首次运行并保存快照
result_v1 = factory.run()
snapshot_id_1 = factory.save_snapshot("初始版本")

# 修改配置
new_wbs = WbsParseTool()
new_wbs.setup({
    "llm_adapter": llm,
    "prompt_template": "按敏捷Sprint拆解...",
    "max_level": 3
})
factory.use_tool("wbs", new_wbs)

# 再次运行并保存快照
result_v2 = factory.run()
snapshot_id_2 = factory.save_snapshot("切换为敏捷模式", include_outputs=True)

# 查询快照列表
snapshots = factory.list_snapshots()
for snap in snapshots:
    print(f"{snap['snapshot_id']}: {snap['description']}")

# 回滚到之前的版本
factory.load_from_snapshot(snapshot_id_1)
```

### 下游任务关联

```python
# 关联模拟任务
factory.link_downstream_task("simulation_id", "sim_001")

# 关联报告任务
factory.link_downstream_task("report_id", "rep_002")

# 保存快照（包含关联信息）
factory.save_snapshot("已关联下游任务")
```

## 核心API

### StructureUnderstandFactory

#### 初始化参数

```python
factory = StructureUnderstandFactory(
    project_id="P-DOC-001",          # 项目ID（必需）
    original_file_path="./doc.pdf",   # 文档路径（必需）
    cache_dir="./cache",              # 缓存目录
    storage_mode="database",          # "file" 或 "database"
    db_path="./snapshots.db",         # 数据库路径
    snapshot_dir="./snapshots"        # 快照目录
)
```

#### 主要方法

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `run()` | 执行完整流程 | `Dict[str, Any]` |
| `use_tool(name, instance)` | 替换工具实例 | `None` |
| `save_snapshot(description, include_outputs)` | 保存快照 | `str` (snapshot_id) |
| `load_from_snapshot(snapshot_id)` | 从快照恢复 | `self` |
| `list_snapshots()` | 列出项目快照 | `List[Dict]` |
| `get_all_snapshots()` | 列出所有快照 | `List[Dict]` |
| `link_downstream_task(type, id)` | 关联下游任务 | `None` |

### 工具基类 - BaseTool

#### 核心方法

```python
class CustomTool(BaseTool):
    def execute(self, input_data):
        """实现具体逻辑"""
        # 调用LLM
        result = self.llm_call(
            prompt="your prompt template: {input}",
            input_data=input_data,
            temperature=0.7,
            response_format={...}  # 可选的JSON Schema
        )
        return result
    
    def get_metadata(self):
        """返回元信息（用于快照）"""
        return super().get_metadata()
```

### DocParseTool

支持的文档格式：
- PDF (.pdf)
- Word (.docx)
- PowerPoint (.pptx)
- Markdown (.md)
- 纯文本 (.txt)

```python
from twork.parser import DocParseTool

doc_parser = DocParseTool()
result = doc_parser.execute({
    "file_path": "./document.pdf"
})

# 输出格式
# {
#     "sections": [
#         {
#             "title": "章节标题",
#             "content": "章节内容",
#             "level": 1
#         },
#         ...
#     ]
# }
```

### RequirementAndDomainAnalyzerTool

```python
from twork.parser import RequirementAndDomainAnalyzerTool

analyzer = RequirementAndDomainAnalyzerTool()
analyzer.setup({"llm_adapter": llm})

result = analyzer.execute({
    "sections": [...]  # 来自DocParseTool的输出
})

# 输出格式
# {
#     "functional_requirements": [
#         {"id": "FR-001", "desc": "需求描述", "priority": "高"}
#     ],
#     "non_functional_requirements": [
#         {"id": "NFR-001", "type": "性能", "desc": "需求描述"}
#     ],
#     "domain": "软件开发"
# }
```

### WbsParseTool

```python
from twork.parser import WbsParseTool

wbs_tool = WbsParseTool()
wbs_tool.setup({
    "llm_adapter": llm,
    "max_level": 3  # 最大层级
})

result = wbs_tool.execute({
    "functional_requirements": [...],
    "non_functional_requirements": [...],
    "domain": "软件开发"
})

# 输出格式
# {
#     "phase": "实施阶段",
#     "tasks": [
#         {
#             "task_id": "T001",
#             "task_name": "数据库设计",
#             "description": "设计ER图",
#             "level": 1,
#             "parent_task_id": null,
#             "estimated_hours": 40,
#             "dependencies": [],
#             "children": [...]
#         }
#     ]
# }
```

## 存储后端

### FileStorageBackend

```python
from twork.parser.storage_backend import FileStorageBackend

storage = FileStorageBackend(snapshot_dir="./snapshots")

# 保存快照
snapshot_id = storage.save_snapshot("P-001", {...})

# 加载快照
data = storage.load_snapshot(snapshot_id)

# 列出快照
snapshots = storage.list_snapshots("P-001")
```

### SqliteStorageBackend

```python
from twork.parser.storage_backend import SqliteStorageBackend

storage = SqliteStorageBackend(db_path="./snapshots.db")

# API相同
snapshot_id = storage.save_snapshot("P-001", {...})
data = storage.load_snapshot(snapshot_id)
```

## 完整示例

### 示例1：基础流程

```python
from twork.parser import StructureUnderstandFactory
from twork.llm import OpenAIAdapter, LLMConfig

# 配置LLM
llm_config = LLMConfig(
    api_base_url="https://api.openai.com/v1",
    api_key="sk-xxx",
    model_name="gpt-4",
    temperature=0.7,
    enable_cache=True,
    cache_dir="./cache"
)
llm = OpenAIAdapter(llm_config)

# 创建工厂
factory = StructureUnderstandFactory(
    project_id="P-DEMO-001",
    original_file_path="./需求文档.pdf",
    storage_mode="database"
)

# 配置工具
for tool_name in ["analyzer", "wbs"]:
    factory.tools[tool_name].setup({"llm_adapter": llm})

# 运行
result = factory.run()

# 保存快照
snapshot_id = factory.save_snapshot("初始版本", include_outputs=True)
print(f"Snapshot saved: {snapshot_id}")
```

### 示例2：多次迭代

```python
# 首次运行
result_v1 = factory.run()
sid1 = factory.save_snapshot("版本1：标准模式")

# 修改为敏捷模式
from twork.parser import WbsParseTool

agile_wbs = WbsParseTool()
agile_wbs.setup({
    "llm_adapter": llm,
    "prompt_template": "请按照敏捷开发模式拆解任务，以Sprint为单位...",
    "max_level": 3
})
factory.use_tool("wbs", agile_wbs)

result_v2 = factory.run()
sid2 = factory.save_snapshot("版本2：敏捷模式")

# 对比两个版本
snapshots = factory.list_snapshots()
for snap in snapshots:
    print(f"- {snap['description']} ({snap['created_at']})")

# 回滚到版本1
factory.load_from_snapshot(sid1)
```

### 示例3：自定义工具

```python
from twork.parser.base_tool import BaseTool

class CustomRequirementTool(BaseTool):
    """自定义需求分析工具"""
    
    def execute(self, input_data):
        sections = input_data.get("sections", [])
        
        # 合并文本
        full_text = "\n\n".join([
            f"{s['title']}\n{s['content']}" 
            for s in sections
        ])
        
        # 调用LLM
        result = self.llm_call(
            prompt="""分析以下需求文档，提取关键信息：
            
            {input}
            
            请返回JSON格式：
            {{
                "requirements": [...],
                "domain": "...",
                "priority_features": [...]
            }}
            """,
            input_data=full_text,
            temperature=0.3
        )
        
        return result

# 使用自定义工具
custom_tool = CustomRequirementTool()
custom_tool.setup({"llm_adapter": llm})
factory.use_tool("analyzer", custom_tool)
```

## 缓存机制

文档解析结果会自动缓存在 `{cache_dir}/{project_id}/parsed_text.json`，避免重复解析。

如需重新解析文档，删除缓存文件即可：
```python
import shutil
from pathlib import Path

cache_file = Path(f"./cache/{factory.project_id}/parsed_text.json")
if cache_file.exists():
    cache_file.unlink()
```

## 快照数据结构

### 完整快照
```json
{
  "snapshot_id": "snap_20251026_a1b2c3",
  "project_id": "P-DOC-001",
  "created_at": "2025-10-26T19:00:00Z",
  "description": "调整了WBS提示词",
  "changes": [
    {
      "tool": "wbs",
      "field": "prompt_template",
      "old": "标准模板",
      "new": "敏捷开发模板"
    }
  ],
  "tools": {
    "analyzer": {"class": "...", "config": {...}},
    "wbs": {"class": "...", "config": {...}}
  },
  "downstream_tasks": {
    "simulation_id": "sim_001"
  },
  "outputs": {
    "requirements_and_domain": {...},
    "wbs": {...}
  }
}
```

### 快照摘要
```json
{
  "snapshot_id": "snap_20251026_a1b2c3",
  "project_id": "P-DOC-001",
  "created_at": "2025-10-26T19:00:00Z",
  "description": "调整了WBS提示词",
  "change_count": 1,
  "changed_tool": "wbs",
  "change_type": "prompt_template",
  "linked_tasks": {"simulation_id": "sim_001"}
}
```

## 最佳实践

1. **合理使用快照**：在关键配置变更后保存快照，便于回滚
2. **工具配置分离**：将LLM适配器配置与工具配置分离
3. **缓存管理**：定期清理过期缓存
4. **错误处理**：捕获并处理工具执行异常
5. **日志记录**：启用日志以追踪执行过程

## 常见问题

### Q: 如何切换存储模式？
A: 在创建工厂时指定`storage_mode`参数：
```python
# 文件存储
factory = StructureUnderstandFactory(..., storage_mode="file")

# 数据库存储
factory = StructureUnderstandFactory(..., storage_mode="database")
```

### Q: 快照是否包含文档内容？
A: 快照不包含原始文档内容，只包含配置和可选的处理结果。文档解析结果缓存在cache目录。

### Q: 如何清空项目的所有快照？
A: 
```python
# 文件模式：删除目录
import shutil
shutil.rmtree(f"./snapshots/{project_id}")

# 数据库模式：执行SQL
import sqlite3
conn = sqlite3.connect("./snapshots.db")
conn.execute("DELETE FROM snapshots WHERE project_id = ?", (project_id,))
conn.commit()
```

### Q: 工具可以共享LLM适配器吗？
A: 可以，多个工具可以共享同一个LLM适配器实例：
```python
for tool in factory.tools.values():
    tool.setup({"llm_adapter": llm})
```

## 进阶用法

### 批量处理多个文档

```python
projects = [
    ("P-001", "./doc1.pdf"),
    ("P-002", "./doc2.docx"),
    ("P-003", "./doc3.md"),
]

results = {}
for project_id, file_path in projects:
    factory = StructureUnderstandFactory(
        project_id=project_id,
        original_file_path=file_path
    )
    
    # 配置工具
    for tool in factory.tools.values():
        tool.setup({"llm_adapter": llm})
    
    # 运行并保存
    results[project_id] = factory.run()
    factory.save_snapshot("批量处理")
```

### 导出结果

```python
import json

result = factory.run()

# 导出为JSON
with open("result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
```
