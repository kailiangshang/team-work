非常好，作为架构师，我将为你撰写一份**清晰、可执行、面向开发实现的指导文档**。

---

# 📄 结构化信息生产工厂（`StructureUnderstandFactory`）  
## 开发实施指导文档（V1.0）

> **角色说明**：  
> - 架构师：定义系统结构、组件职责、输入输出、接口契约  
> - 实现者（你）：根据本文档完成代码编写与集成  

---

## 一、总体目标

构建一个名为 `StructureUnderstandFactory` 的工厂类，用于：

- 解析原始项目文档（PDF/DOCX/TXT/Markdown/PPTX）
- 提取功能/非功能需求并识别领域
- 拆解生成 WBS 任务树
- 支持用户通过修改提示词进行多轮迭代
- 将每次配置变更保存为**快照（Snapshot）**
- 支持快照回滚与全局查询
- 为后续知识图谱、多智能体模拟等下游任务提供**结构化中间数据**

> ✅ **不负责**：直接构建知识图谱或运行模拟任务。

---

## 二、核心组件清单

| 组件 | 类型 | 是否需你实现 |
|------|------|--------------|
| `BaseTool` | 抽象基类 | ✅ 是 |
| `DocParseTool` | 工具类 | ✅ 是 |
| `RequirementAndDomainAnalyzerTool` | 工具类 | ✅ 是 |
| `WbsParseTool` | 工具类 | ✅ 是 |
| `StorageBackend` | 抽象接口 | ✅ 是 |
| `FileStorageBackend` | 存储实现 | ✅ 是 |
| `SqliteStorageBackend` | 存储实现 | ✅ 是 |
| `StructureUnderstandFactory` | 核心工厂 | ✅ 是 |

---

## 三、各组件详细设计（含输入输出）

---

### 1. `BaseTool`（抽象基类）

#### 职责
- 所有工具的公共父类
- 提供统一的 LLM 调用能力

#### 接口定义

```python
from abc import ABC, abstractmethod
import json

class BaseTool(ABC):
    def __init__(self):
        self.config = {}
        self.name = self.__class__.__name__
    
    def setup(self, config: dict):
        """初始化配置"""
        self.config = config
    
    @abstractmethod
    def execute(self, input_data):
        """执行主逻辑，子类必须实现"""
        pass
    
    def get_metadata(self) -> dict:
        """返回元信息，用于快照记录"""
        return {
            "class": self.__class__.__name__,
            "config": self.config.copy()
        }
    
    def llm_call(self, prompt: str, input_data, model: str = "qwen-plus", response_format: dict = None) -> dict:
        """
        统一封装的 LLM 调用方法
        
        输入：
          - prompt: 提示词模板
          - input_data: 输入数据（任意结构）
          - model: 模型名称（默认 qwen-plus）
          - response_format: 可选，期望的 JSON 输出结构
        
        输出：
          - dict: LLM 返回的结构化结果
        
        实现建议：
          - 使用阿里云百炼平台或本地 LLM API
          - 支持缓存（基于 prompt + input hash）
          - 支持重试机制
        """
        # TODO: 由你实现 LLM 调用逻辑
        # 示例调用（伪代码）：
        # return call_llm_api(model=model, prompt=full_prompt, response_format=response_format)
        pass
```

---

### 2. `DocParseTool`

#### 职责
- 解析文档为带层级的结构化文本
- 仅首次运行，结果缓存

#### 输入
- `file_path: str`（如 `"./docs/需求文档.pdf"`）

#### 输出
```json
{
  "sections": [
    {
      "title": "1. 项目背景",
      "content": "本系统旨在...",
      "level": 1
    },
    {
      "title": "1.1 用户需求",
      "content": "用户需要登录功能...",
      "level": 2
    }
  ]
}
```

#### 实现要求
- 支持格式：PDF、DOCX、TXT、Markdown、PPTX
- 使用 `pypdf`, `python-docx`, `pptx` 等库
- 缓存路径：`{cache_dir}/{project_id}/parsed_text.json`
- 如果缓存存在，跳过解析

---

### 3. `RequirementAndDomainAnalyzerTool`

#### 职责
- 使用 LLM 提取需求并判断领域

#### 输入
- 结构化文本（来自 `DocParseTool` 输出）

#### 输出
```json
{
  "functional_requirements": [
    {"id": "FR-001", "desc": "用户可登录", "priority": "高"}
  ],
  "non_functional_requirements": [
    {"id": "NFR-001", "type": "性能", "desc": "响应<1s"}
  ],
  "domain": "软件开发"
}
```

#### 实现方式
- 继承 `BaseTool`
- 在 `execute()` 中使用 `self.llm_call()` 发起请求
- `config` 中包含 `prompt_template` 和 `model`

---

### 4. `WbsParseTool`

#### 职责
- 基于需求和领域，生成三层 WBS 任务树

#### 输入
- 需求列表 + 领域标签

#### 输出
```json
{
  "phase": "实施阶段",
  "tasks": [
    {
      "task_id": "T-001",
      "name": "数据库设计",
      "subtasks": [
        { "task_id": "T-001-01", "name": "ER图设计", "estimated_hours": 8 }
      ]
    }
  ]
}
```

#### 实现方式
- 继承 `BaseTool`
- 使用 `self.llm_call()`，支持自定义 `prompt_template`
- 可内置模板（如“敏捷”、“瀑布”）

---

### 5. `StorageBackend`（抽象接口）

#### 职责
- 定义存储后端契约

#### 接口定义

```python
class StorageBackend:
    def save_snapshot(self, project_id: str, data: dict) -> str:
        """保存快照，返回 snapshot_id"""
        pass
    
    def load_snapshot(self, snapshot_id: str) -> dict:
        """加载快照，不存在返回 None"""
        pass
    
    def list_snapshots(self, project_id: str) -> list:
        """返回某项目的快照摘要列表"""
        pass
    
    def get_all_snapshots(self) -> list:
        """返回所有项目的快照摘要（全局）"""
        pass
    
    def exists(self, snapshot_id: str) -> bool:
        """判断快照是否存在"""
        pass
```

---

### 6. `FileStorageBackend`

#### 实现方式
- 将快照保存为 JSON 文件
- 路径：`{snapshot_dir}/{project_id}/snap_{timestamp}_{rand}.json`
- `list_snapshots` 扫描目录生成摘要

---

### 7. `SqliteStorageBackend`

#### 实现方式
- 数据库文件：`db_path`（默认 `./snapshots.db`）
- 表名：`snapshots`

#### 表结构（DDL）
```sql
CREATE TABLE IF NOT EXISTS snapshots (
    snapshot_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    description TEXT,
    changes TEXT, -- JSON array of change objects
    data_json TEXT NOT NULL, -- full snapshot
    summary_json TEXT NOT NULL -- summary for listing
);
```

#### 方法映射
- `save_snapshot` → INSERT 或 REPLACE
- `load_snapshot` → SELECT by id
- `list_snapshots` → SELECT WHERE project_id = ?
- `get_all_snapshots` → SELECT * FROM snapshots ORDER BY created_at DESC

---

### 8. `StructureUnderstandFactory`（核心）

#### 初始化参数

```python
def __init__(
    self,
    project_id: str,
    original_file_path: str,
    cache_dir: str = "./cache",
    storage_mode: str = "database",  # "file" or "database"
    db_path: str = "./snapshots.db",
    snapshot_dir: str = "./snapshots"
):
```

#### 核心属性
- `project_id`: str
- `original_file_path`: str
- `cache_dir`: str
- `storage_backend`: `StorageBackend` 实例
- `tools`: dict of tools (`{"doc_parse": tool, "analyzer": tool, "wbs": tool}`)
- `current_snapshot_id`: str
- `downstream_task_ids`: dict (e.g., `{"simulation_id": "sim_001"}`)

---

#### 核心方法

| 方法 | 输入 | 输出 | 说明 |
|------|------|------|------|
| `run()` | —— | `dict` | 执行完整流程，返回 `{requirements_and_domain, wbs}` |
| `use_tool(name, instance)` | `str`, `BaseTool` | —— | 替换某个工具 |
| `save_snapshot(description: str)` | `str` | `snapshot_id: str` | 保存当前配置为快照，自动提取变更 |
| `load_from_snapshot(snapshot_id: str)` | `str` | `self` | 恢复配置，不重新解析文档 |
| `list_snapshots()` | —— | `List[dict]` | 当前项目的快照摘要 |
| `get_all_snapshots()` | —— | `List[dict]` | 所有项目的快照摘要（全局） |
| `link_downstream_task(task_type: str, task_id: str)` | `str`, `str` | —— | 关联下游任务 ID |

---

#### `run()` 执行流程

```text
1. 检查缓存是否存在 parsed_text.json
   - 是 → 读取缓存
   - 否 → 执行 DocParseTool.execute() → 保存缓存

2. 执行 analyzer.execute(parsed_text)
3. 执行 wbs.execute(requirements_output)
4. 返回结果字典
```

---

#### `save_snapshot()` 逻辑

1. 比较当前 `tools` 与上一次快照的 `tools` 配置
2. 生成 `changes` 数组，记录变更字段（如 `analyzer.prompt_template`）
3. 构造快照对象（含 `outputs` 可选）
4. 调用 `storage_backend.save_snapshot()`
5. 更新 `current_snapshot_id`

---

## 四、快照数据结构

### 完整快照（Full Snapshot）

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
    "analyzer": { "class": "...", "config": { ... } },
    "wbs": { "class": "...", "config": { ... } }
  },
  "downstream_tasks": {
    "simulation_id": "sim_001",
    "report_id": "rep_002"
  },
  "outputs": {
    "requirements_and_domain": { ... },
    "wbs": { ... }
  }
}
```

### 快照摘要（Summary，用于列表展示）

```json
[
  {
    "snapshot_id": "snap_20251026_a1b2c3",
    "project_id": "P-DOC-001",
    "created_at": "2025-10-26T19:00:00Z",
    "description": "调整了WBS提示词",
    "changed_tool": "wbs",
    "change_type": "prompt_template",
    "before": "标准模板",
    "after": "敏捷开发模板",
    "linked_simulation": "sim_001",
    "linked_report": "rep_002"
  }
]
```

---

## 五、文件系统布局

```
./
├── cache/
│    └── {project_id}/
│         └── parsed_text.json
│
├── snapshots/
│    └── {project_id}/
│         ├── snap_20251026_a1b2c3.json
│         └── snap_20251027_d4e5f6.json
│
└── snapshots.db  (SQLite database)
```

---

## 六、开发顺序建议

1. ✅ 实现 `BaseTool`（含 `llm_call` mock）
2. ✅ 实现 `DocParseTool`（测试 PDF/DOCX 解析）
3. ✅ 实现 `RequirementAndDomainAnalyzerTool` 和 `WbsParseTool`
4. ✅ 实现 `StorageBackend` 接口
5. ✅ 实现 `FileStorageBackend` 和 `SqliteStorageBackend`
6. ✅ 实现 `StructureUnderstandFactory` 核心逻辑
7. ✅ 集成测试：`run` → `save_snapshot` → `list_snapshots` → `load_from_snapshot`

---

## 七、交付物

你完成后应提供：

- 一套可运行的 Python 模块
- 每个类有清晰 docstring
- 支持 `pip install` 或直接导入
- 包含 `__init__.py`
- 提供一个 `example.py` 示例脚本

---

## 八、示例使用代码（`example.py`）

```python
from structure_factory import StructureUnderstandFactory
from tools import DocParseTool, RequirementAndDomainAnalyzerTool, WbsParseTool

factory = StructureUnderstandFactory(
    project_id="P-DOC-001",
    original_file_path="./docs/需求文档.pdf",
    storage_mode="database"
)

# 首次运行
result = factory.run()

# 修改 WBS 提示词
wbs = WbsParseTool()
wbs.setup({"prompt_template": "按敏捷Sprint拆解...", "model": "qwen-max"})
factory.use_tool("wbs", wbs)

# 再次运行
result_v2 = factory.run()

# 保存快照
sid = factory.save_snapshot("切换为敏捷模式")

# 关联下游
factory.link_downstream_task("simulation_id", "sim_001")
factory.save_snapshot("已关联模拟任务")

# 查询
snaps = factory.list_snapshots()
all_snaps = factory.get_all_snapshots()

print(f"共 {len(all_snaps)} 个快照")
```

---

✅ **此文档为最终实施蓝图**，你可据此开始编码。
