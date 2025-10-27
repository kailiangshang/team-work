# TWork - AI多角色任务协同模拟系统核心库

[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)](https://github.com/yourusername/team-work)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

TWork 是一个基于大模型Agent的智能任务模拟系统核心技术模块。它能够将任意类型的需求文档自动拆解为结构化任务，并通过多角色Agent模拟真实项目执行过程，提供复杂度分析、时间估算、风险预测等全方位的项目管理支持。

## ✨ 核心特性

- 🤖 **智能文档解析**：自动加载和解析多种格式需求文档（PDF、Word、Markdown）
- 📊 **WBS任务拆解**：基于领域分类的工作分解结构（WBS）智能拆解 **[新增循环依赖检测]** 🆕
- 👥 **多角色Agent模拟**：自动生成角色并模拟真实项目执行过程 **[增强技能匹配]** 🆕
- 🔄 **智能任务分配**：基于技能匹配和负载均衡的任务重新分配 **[全新功能]** 🆕
- 🔍 **复杂度分析**：智能评估任务复杂度和时间成本
- 📈 **甘特图生成**：自动生成项目进度甘特图
- ⚠️ **风险分析**：识别潜在风险并提供缓解策略
- 🔄 **版本管理**：项目快照创建与版本差异对比
- 📦 **结果可视化**：生成PDF报告、CSV编排文件和可视化图谱

## 🆕 v0.3.0 新增功能

### 1. WBS 任务拆解增强
- ✅ **循环依赖检测**: `validate_dependencies()` 方法，使用 DFS 算法检测任务依赖闭环
- ✅ **依赖验证**: 自动验证依赖任务是否存在
- ✅ **错误报告**: 详细的依赖错误信息

### 2. Agent 角色生成增强
- ✅ **基于任务树生成**: `generate_roles()` 方法，直接从任务树生成 Agent
- ✅ **技能自动提取**: 从任务的 `required_skills` 字段提取技能需求
- ✅ **工具映射**: 基于领域自动加载预设工具库
- ✅ **任务重新分配**: `reassign_tasks()` 方法，处理 Agent 删除后的任务重分配
- ✅ **智能推荐**: `recommend_assignments()` 方法，支持技能匹配和负载均衡策略

### 3. 数据结构增强
- ✅ **Agent 技能等级**: `{"skill_name": str, "proficiency_level": 1-5}`
- ✅ **组织层级**: `org_level` (1=EXECUTIVE, 2=MANAGER, 3=LEAD, 4=MEMBER)
- ✅ **沟通风格**: `communication_style` 字段
- ✅ **任务技能需求**: `required_skills` 字段
- ✅ **任务工具需求**: `tools_needed` 字段

## 📦 安装

### 通过pip安装（推荐）

```bash
pip install twork
```

### 从源码安装

```bash
git clone https://github.com/yourusername/team-work.git
cd team-work
pip install -e .
```

### Docker环境中使用

在Docker容器中，建议通过PYTHONPATH环境变量引入twork，而非pip安装：

```dockerfile
# Dockerfile示例
COPY twork /app/twork
ENV PYTHONPATH="/app:${PYTHONPATH}"
```

## 🚀 快速开始

### v0.3.0 新版快速使用（推荐）

```python
from twork.parser import DocumentLoader, RequirementExtractor, DomainClassifier, WBSDecomposer
from twork.agent import RoleGenerator
from twork.generator import GraphBuilder
from twork.llm import OpenAIAdapter
import json

# 1. 初始化 LLM
llm = OpenAIAdapter(api_key="your-key")

# 2. 加载文档
loader = DocumentLoader()
doc_result = loader.load(file_path="/path/to/doc.pdf")

# 3. 提取需求
extractor = RequirementExtractor(llm_adapter=llm)
requirements = extractor.extract(document_content=doc_result["content"])

# 4. 领域分类
classifier = DomainClassifier()
domain_result = classifier.classify(
    content=requirements["project_description"],
    user_selected_domain=None  # 可手动指定领域
)

# 5. WBS 任务拆解
decomposer = WBSDecomposer(llm_adapter=llm, max_level=4)
wbs_result = decomposer.decompose(
    requirements=json.dumps(requirements),
    domain_type=domain_result["domain_type"],
    task_types=["需求分析", "开发", "测试"],
    template_config={},
    user_constraints={"total_days": 30, "team_size": 5}
)

task_tree = wbs_result["task_tree"]

# 6. 验证依赖关系（新功能）🆕
is_valid, errors = decomposer.validate_dependencies(task_tree)
if not is_valid:
    print("依赖错误:", errors)

# 7. 生成角色（增强版）🆕
generator = RoleGenerator(llm_adapter=llm)
agents = generator.generate_roles(
    task_tree=task_tree,
    domain_type=domain_result["domain_type"],
    team_size_hint=5
)

# 8. 智能任务分配推荐（新功能）🆕
recommendations = generator.recommend_assignments(
    agents=agents,
    task_tree=task_tree,
    strategy="skill_match"  # 或 "workload_balance"
)

# 9. Agent 删除后重新分配（新功能）🆕
# removed_agent = agents.pop(1)  # 删除 Agent
# orphan_tasks = removed_agent.get("assigned_tasks", [])
# agents = generator.reassign_tasks(
#     agents=agents,
#     task_tree=task_tree,
#     orphan_tasks=orphan_tasks
# )

# 10. 构建图谱
builder = GraphBuilder()
flat_tasks = decomposer.flatten_tree(task_tree)
triplets = builder.build_triplets(tasks=flat_tasks, agents=agents)

# 11. 导出结果
builder.export_triplets(triplets, "graph_triplets.json")
builder.export_mermaid(flat_tasks, agents, "graph.md")

print("图谱初始化完成!")
```

### 基本使用

```python
import twork

# 1. 加载需求文档
loader = twork.DocumentLoader()
document = loader.load("requirements.pdf")

# 2. 提取需求
extractor = twork.RequirementExtractor(llm_config)
requirements = extractor.extract(document)

# 3. 领域分类
classifier = twork.DomainClassifier(llm_config)
domain = classifier.classify(requirements)

# 4. WBS拆解
wbs_decomposer = twork.WBSDecomposer(llm_config)
wbs_structure = wbs_decomposer.decompose(requirements, domain)

# 5. 任务拆解
decomposer = twork.TaskDecomposer(llm_config)
tasks = decomposer.decompose(wbs_structure)

# 6. 生成执行角色
role_gen = twork.RoleGenerator(llm_config)
roles = role_gen.generate(tasks)

# 7. 运行多Agent模拟
runner = twork.MultiAgentRunner(llm_config)
simulation_result = runner.run(tasks, roles)

# 8. 生成甘特图
gantt_gen = twork.GanttGenerator()
gantt_gen.generate(tasks, "output/gantt.png")

# 9. 风险分析
risk_analyzer = twork.RiskAnalyzer(llm_config)
risks = risk_analyzer.analyze(tasks, simulation_result)
```

### 完整工作流示例

```python
from twork import (
    DocumentLoader,
    RequirementExtractor,
    DomainClassifier,
    WBSDecomposer,
    TaskDecomposer,
    RoleGenerator,
    SimulationEngine,
    GanttGenerator,
    RiskAnalyzer,
    DocumentGenerator
)

# LLM配置
llm_config = {
    "api_key": "your-api-key",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4"
}

# 完整流程
def process_project(requirements_file, output_dir):
    # 文档加载与需求提取
    loader = DocumentLoader()
    doc = loader.load(requirements_file)
    
    extractor = RequirementExtractor(llm_config)
    requirements = extractor.extract(doc)
    
    # 领域分类与WBS拆解
    classifier = DomainClassifier(llm_config)
    domain = classifier.classify(requirements)
    
    wbs = WBSDecomposer(llm_config)
    wbs_structure = wbs.decompose(requirements, domain)
    
    # 任务拆解
    decomposer = TaskDecomposer(llm_config)
    tasks = decomposer.decompose(wbs_structure)
    
    # Agent模拟
    engine = SimulationEngine(llm_config)
    simulation = engine.simulate(tasks)
    
    # 生成结果
    gantt = GanttGenerator()
    gantt.generate(tasks, f"{output_dir}/gantt.png")
    
    risk = RiskAnalyzer(llm_config)
    risks = risk.analyze(tasks, simulation)
    
    doc_gen = DocumentGenerator()
    doc_gen.generate_report(tasks, simulation, risks, f"{output_dir}/report.pdf")
    
    return {
        "tasks": tasks,
        "simulation": simulation,
        "risks": risks
    }

# 执行
result = process_project("requirements.pdf", "output/project_1")
```

## 📚 模块说明

### Parser - 文档解析模块

负责加载、解析需求文档，提取关键信息并拆解为结构化任务。

- **DocumentLoader**: 支持PDF、Word、Markdown等格式文档加载
- **RequirementExtractor**: 提取文档中的需求信息
- **DomainClassifier**: 自动识别项目领域类型
- **WBSDecomposer**: 工作分解结构（WBS）智能拆解 **[增强]** 🆕
- **TaskDecomposer**: 将需求拆解为可执行的结构化任务
- **ContextTemplateManager**: 管理不同领域的上下文模板

```python
from twork.parser import DocumentLoader, RequirementExtractor, DomainClassifier, WBSDecomposer

# 文档加载
loader = DocumentLoader()
doc = loader.load("requirements.pdf")
# 返回: {"content": str, "file_name": str, "file_type": str, "file_size": int}

# 需求提取
extractor = RequirementExtractor(llm_adapter=llm)
requirements = extractor.extract(doc["content"])
# 返回: {project_name, project_description, main_objectives, key_requirements, constraints, expected_deliverables}

# 领域分类
classifier = DomainClassifier()
domain_result = classifier.classify(
    content=requirements["project_description"],
    user_selected_domain=None  # 可手动指定: "软件开发"
)
# 返回: {domain_type, confidence, keywords, template_id, all_scores}

# WBS 任务拆解（增强版）🆕
decomposer = WBSDecomposer(llm_adapter=llm, max_level=4)
wbs_result = decomposer.decompose(
    requirements=json.dumps(requirements),
    domain_type=domain_result["domain_type"],
    task_types=["需求分析", "开发", "测试"],
    template_config={},
    user_constraints={"total_days": 30, "team_size": 5}
)
# 返回: {"task_tree": List[Dict], "statistics": Dict}

# 验证依赖关系（新功能）🆕
is_valid, errors = decomposer.validate_dependencies(wbs_result["task_tree"])
if not is_valid:
    print("依赖错误:", errors)
    # 示例: ["检测到循环依赖: T001 -> T002 -> T001"]

# 展平任务树
flat_tasks = decomposer.flatten_tree(wbs_result["task_tree"])
# 返回: List[Dict]  # 所有任务的扁平列表

# 查找任务
task = decomposer.get_task_by_id(wbs_result["task_tree"], "T001-1")
```

**任务树数据结构**:
```python
[
    {
        "task_id": "T001",
        "task_name": "需求分析阶段",
        "description": "完成项目需求调研和分析",
        "level": 1,
        "parent_task_id": null,
        "task_type": "需求分析",
        "estimated_complexity": 5,
        "dependencies": [],
        "required_skills": [  # 新: 技能需求
            {"skill_name": "需求分析", "proficiency_level": 3}
        ],
        "tools_needed": ["Axure", "JIRA"],  # 新: 工具需求
        "children": [...]
    }
]
```

### Agent - 智能Agent模块

负责角色Agent生成、多Agent协同和任务模拟执行。

- **RoleGenerator**: 根据任务自动生成合适的执行角色 **[增强]** 🆕
- **MultiAgentRunner**: 多Agent协同执行框架
- **SimulationEngine**: 任务执行模拟引擎
- **ConflictResolver**: 冲突识别与解决
- **DebateSimulator**: 讨论场景模拟

```python
from twork.agent import RoleGenerator

# 基于任务树生成 Agent（新方法）🆕
generator = RoleGenerator(llm_adapter=llm)
agents = generator.generate_roles(
    task_tree=task_tree,
    domain_type="软件开发",
    team_size_hint=5
)

# 智能任务分配推荐（新）🆕
recommendations = generator.recommend_assignments(
    agents=agents,
    task_tree=task_tree,
    strategy="skill_match"  # 技能匹配策略
    # strategy="workload_balance"  # 负载均衡策略
)
# 返回: {"T001-1": "A003", "T001-2": "A001", ...}

# 任务重新分配（新）🆕
# 当删除 Agent 时，重新分配其任务
agents = generator.reassign_tasks(
    agents=agents,
    task_tree=task_tree,
    orphan_tasks=["T002-1", "T002-2"]  # 需要重新分配的任务
)

# 模拟引擎（原有功能）
from twork.agent import SimulationEngine

engine = SimulationEngine(llm_adapter=llm)
simulation = engine.simulate(
    agents=agents,
    tasks=tasks,
    total_days=30,
    enable_env_agent=True,  # 启用环境事件
    env_event_probability=0.2
)
```

**Agent 配置结构（增强版）**:
```python
{
    "agent_id": "A001",
    "role_name": "后端工程师",
    "role_type": "开发",
    "capabilities": [  # 新: 技能等级
        {"skill_name": "Python", "proficiency_level": 5},
        {"skill_name": "FastAPI", "proficiency_level": 4}
    ],
    "available_hours_per_day": 8.0,
    "fatigue_threshold": 8.0,
    "personality": "专业、注重细节",
    "assigned_tasks": [],
    "org_level": 3,  # 新: 组织层级 (1=EXECUTIVE, 2=MANAGER, 3=LEAD, 4=MEMBER)
    "communication_style": "direct",  # 新: 沟通风格
    "tools": ["VS Code", "Docker"]  # 新: 工具
}
```

### Estimator - 复杂度分析与估算模块

主要功能：任务复杂度分析、工期时间估算、关键路径识别。

- **ComplexityAnalyzer**: 分析任务复杂度
- **TimeEstimator**: 估算任务执行时间

```python
from twork import ComplexityAnalyzer, TimeEstimator

analyzer = ComplexityAnalyzer(llm_config)
complexity = analyzer.analyze(tasks)

estimator = TimeEstimator(llm_config)
time_estimate = estimator.estimate(tasks)
```

### Generator - 结果生成模块

负责生成PDF/Markdown文档、CSV编排文件和任务图谱。

- **DocumentGenerator**: 生成项目报告（PDF/Markdown）
- **CSVExporter**: 导出任务编排CSV文件
- **GraphBuilder**: 构建任务依赖图谱
- **GanttGenerator**: 生成甘特图
- **RiskAnalyzer**: 项目风险分析

```python
from twork import GanttGenerator, RiskAnalyzer, DocumentGenerator

# 甘特图生成
gantt = GanttGenerator()
gantt.generate(tasks, "output/gantt.png")

# 风险分析
risk = RiskAnalyzer(llm_config)
risks = risk.analyze(tasks, simulation)

# 文档生成
doc_gen = DocumentGenerator()
doc_gen.generate_report(tasks, simulation, risks, "output/report.pdf")
```

### Version - 版本管理模块

主要功能：项目快照创建、版本历史管理、版本差异对比、变更追踪。

- **VersionManager**: 管理项目版本快照
- **DiffGenerator**: 生成版本差异报告

```python
from twork import VersionManager, DiffGenerator

# 创建版本快照
vm = VersionManager()
vm.create_snapshot(project_id, tasks, "v1.0.0")

# 对比版本差异
diff_gen = DiffGenerator()
diff = diff_gen.compare("v1.0.0", "v1.1.0")
```

### LLM - 大模型适配层

提供统一的大模型接口，支持OpenAI格式的API调用。

- **LLMAdapter**: 抽象基类
- **OpenAIAdapter**: OpenAI API适配器

```python
from twork import OpenAIAdapter

llm = OpenAIAdapter(
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",
    model="gpt-4"
)

response = llm.chat([
    {"role": "user", "content": "分析这个任务的复杂度"}
])
```

### Utils - 工具函数模块

提供日志管理、文件处理等通用工具函数。

- **setup_logger / get_logger**: 日志管理
- **FilePermissionHandler**: 文件权限处理（Docker环境友好）

```python
from twork.utils import get_logger, FilePermissionHandler

# 日志
logger = get_logger(__name__)
logger.info("开始处理任务")

# 文件处理
handler = FilePermissionHandler()
handler.ensure_writable("output/results.json")
```

## 🏗️ 架构设计

```
twork/
├── parser/          # 文档解析与任务拆解
├── agent/           # 多Agent协同与模拟
├── estimator/       # 复杂度分析与时间估算
├── generator/       # 结果生成与可视化
├── version/         # 版本管理与差异对比
├── llm/             # 大模型适配层
└── utils/           # 通用工具函数
```

### 设计原则

1. **模块化设计**：各模块职责清晰，低耦合高内聚
2. **统一接口**：通过LLM适配层统一大模型调用接口
3. **可扩展性**：支持自定义领域模板和角色配置
4. **容器友好**：通过PYTHONPATH引入，避免重复安装
5. **文件处理统一**：使用utils/file_handler统一管理文件操作

## 🔧 配置说明

### LLM配置

```python
llm_config = {
    "api_key": "your-api-key",           # API密钥
    "base_url": "https://api.openai.com/v1",  # API地址
    "model": "gpt-4",                     # 模型名称
    "temperature": 0.7,                   # 温度参数（可选）
    "max_tokens": 4000,                   # 最大token数（可选）
}
```

### 环境变量

```bash
# .env 文件
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4
```

## 📖 高级用法

### 自定义领域模板

```python
from twork import ContextTemplateManager

template_manager = ContextTemplateManager()
template_manager.add_template(
    domain="custom_domain",
    template={
        "wbs_levels": ["阶段", "模块", "任务"],
        "role_types": ["架构师", "开发工程师", "测试工程师"],
        # ... 其他配置
    }
)
```

### 冲突解决自定义策略

```python
from twork import ConflictResolver

resolver = ConflictResolver(llm_config)
conflicts = resolver.detect(simulation_logs)
resolutions = resolver.resolve(conflicts, strategy="voting")  # 投票策略
```

### 批量项目处理

```python
from twork import DocumentLoader, TaskDecomposer

def batch_process(project_files):
    results = {}
    for project_file in project_files:
        loader = DocumentLoader()
        doc = loader.load(project_file)
        # ... 处理逻辑
        results[project_file] = processed_data
    return results
```

## 🐳 Docker集成

在Docker环境中使用twork时，推荐通过PYTHONPATH引入：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 复制twork核心库
COPY twork /app/twork

# 设置Python路径
ENV PYTHONPATH="/app:${PYTHONPATH}"

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 应用代码
COPY . .

CMD ["python", "main.py"]
```

**注意**：修改twork核心库代码后，需要重新构建Docker镜像：

```bash
docker-compose build backend
docker-compose up -d
```

## 🤝 贡献指南

我们欢迎任何形式的贡献！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 开发规范

- 代码风格：遵循PEP 8规范
- 文档：所有公共API必须包含docstring
- 测试：新功能需要配套单元测试
- 日志：使用loguru统一日志管理

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](../LICENSE) 文件了解详情

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

## 📞 联系我们

- 项目主页：https://github.com/kailiangshang/team-work
- 问题反馈：https://github.com/kailiangshang/team-work/issues
- 邮箱：shangkl@enn.cn

---

**版本**: 0.3.0  
**最后更新**: 2025-10-26

## 📝 更新日志

### v0.3.0 (2025-10-26)

**新增功能**:
- ✅ WBSDecomposer: 新增 `validate_dependencies()` 方法，支持循环依赖检测
- ✅ RoleGenerator: 新增 `generate_roles()` 方法，基于任务树生成 Agent
- ✅ RoleGenerator: 新增 `reassign_tasks()` 方法，支持任务重新分配
- ✅ RoleGenerator: 新增 `recommend_assignments()` 方法，支持技能匹配和负载均衡策略
- ✅ 技能自动提取与映射功能
- ✅ 工具需求自动提取(基于领域)

**数据结构增强**:
- ✅ Agent 配置支持技能等级: `{"skill_name": str, "proficiency_level": 1-5}`
- ✅ Agent 配置支持组织层级: `org_level`
- ✅ Agent 配置支持沟通风格: `communication_style`
- ✅ 任务支持技能需求: `required_skills`
- ✅ 任务支持工具需求: `tools_needed`

**文档与示例**:
- ✅ 新增 `/examples/graph_init_demo.py` - 图谱初始化流程完整示例
- ✅ 新增 `/docs/IMPLEMENTATION_SUMMARY_GRAPH_INIT.md` - 实施摘要文档
- ✅ 更新 README 文档，新增 v0.3.0 功能介绍

### v0.2.0
- 基础功能实现
- 文档解析、需求提取、WBS 拆解
- Agent 生成、模拟引擎
- 图谱构建、甘特图生成
