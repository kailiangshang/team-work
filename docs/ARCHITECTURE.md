# TeamWork 模块合并策略

## 架构分析结果

### v0.1 (team-work/twork/) - 旧版核心库
```
twork/
├── parser/
│   ├── document_loader.py       # 文档加载器
│   ├── requirement_extractor.py # 需求提取器
│   └── task_decomposer.py       # 任务拆解器
├── agent/
│   ├── multi_agent_runner.py    # 多Agent运行器
│   ├── role_generator.py        # 角色生成器
│   └── simulation_engine.py     # 模拟引擎
├── generator/
│   ├── csv_exporter.py          # CSV导出器
│   ├── document_generator.py    # 文档生成器
│   └── graph_builder.py         # 图谱构建器
├── llm/
│   ├── base.py                  # 基础接口
│   └── openai_adapter.py        # OpenAI适配器
└── utils/
    └── logger.py                # 日志工具
```

### v0.2 (twork/) - 新版核心库
```
twork/
├── parser/
│   ├── domain_classifier.py           # 领域分类器
│   ├── context_template_manager.py    # 模板管理器
│   └── wbs_decomposer.py              # WBS拆解器
├── agent/
│   ├── conflict_resolver.py           # 冲突解决器
│   └── debate_simulator.py            # 讨论模拟器
├── generator/
│   ├── gantt_generator.py             # 甘特图生成器
│   └── risk_analyzer.py               # 风险分析器
├── estimator/
│   ├── complexity_analyzer.py         # 复杂度分析器
│   └── time_estimator.py              # 时间估算器
└── version/
    ├── version_manager.py             # 版本管理器
    └── diff_generator.py              # 差异生成器
```

## 合并策略矩阵

| 模块 | v0.1文件 | v0.2文件 | 处理方式 | 目标位置 |
|------|---------|---------|----------|----------|
| **parser** | document_loader.py | - | ✅ 保留 | team-work/twork/parser/ |
| **parser** | requirement_extractor.py | - | ✅ 保留 | team-work/twork/parser/ |
| **parser** | task_decomposer.py | - | ✅ 保留 | team-work/twork/parser/ |
| **parser** | - | domain_classifier.py | ✅ 复制 | team-work/twork/parser/ |
| **parser** | - | context_template_manager.py | ✅ 复制 | team-work/twork/parser/ |
| **parser** | - | wbs_decomposer.py | ✅ 复制 | team-work/twork/parser/ |
| **agent** | multi_agent_runner.py | - | ✅ 保留 | team-work/twork/agent/ |
| **agent** | role_generator.py | - | ✅ 保留 | team-work/twork/agent/ |
| **agent** | simulation_engine.py | - | ✅ 保留 | team-work/twork/agent/ |
| **agent** | - | conflict_resolver.py | ✅ 复制 | team-work/twork/agent/ |
| **agent** | - | debate_simulator.py | ✅ 复制 | team-work/twork/agent/ |
| **generator** | csv_exporter.py | - | ✅ 保留 | team-work/twork/generator/ |
| **generator** | document_generator.py | - | ✅ 保留 | team-work/twork/generator/ |
| **generator** | graph_builder.py | - | ✅ 保留 | team-work/twork/generator/ |
| **generator** | - | gantt_generator.py | ✅ 复制 | team-work/twork/generator/ |
| **generator** | - | risk_analyzer.py | ✅ 复制 | team-work/twork/generator/ |
| **estimator** | - | complexity_analyzer.py | ✅ 复制 | team-work/twork/estimator/ |
| **estimator** | - | time_estimator.py | ✅ 复制 | team-work/twork/estimator/ |
| **version** | - | version_manager.py | ✅ 复制 | team-work/twork/version/ |
| **version** | - | diff_generator.py | ✅ 复制 | team-work/twork/version/ |
| **llm** | base.py | - | ✅ 保留 | team-work/twork/llm/ |
| **llm** | openai_adapter.py | - | ✅ 保留 | team-work/twork/llm/ |
| **utils** | logger.py | - | ✅ 保留 | team-work/twork/utils/ |

## 合并后目标结构

```
team-work/
├── twork/                          # 统一的核心库
│   ├── parser/                     # 文档解析模块（6个文件）
│   │   ├── __init__.py
│   │   ├── document_loader.py      # [v0.1] 文档加载器
│   │   ├── requirement_extractor.py # [v0.1] 需求提取器
│   │   ├── task_decomposer.py      # [v0.1] 任务拆解器
│   │   ├── domain_classifier.py    # [v0.2] 领域分类器
│   │   ├── context_template_manager.py # [v0.2] 模板管理器
│   │   └── wbs_decomposer.py       # [v0.2] WBS拆解器
│   ├── agent/                      # Agent模块（5个文件）
│   │   ├── __init__.py
│   │   ├── multi_agent_runner.py   # [v0.1] 多Agent运行器
│   │   ├── role_generator.py       # [v0.1] 角色生成器
│   │   ├── simulation_engine.py    # [v0.1] 模拟引擎
│   │   ├── conflict_resolver.py    # [v0.2] 冲突解决器
│   │   └── debate_simulator.py     # [v0.2] 讨论模拟器
│   ├── generator/                  # 结果生成模块（5个文件）
│   │   ├── __init__.py
│   │   ├── csv_exporter.py         # [v0.1] CSV导出器
│   │   ├── document_generator.py   # [v0.1] 文档生成器
│   │   ├── graph_builder.py        # [v0.1] 图谱构建器
│   │   ├── gantt_generator.py      # [v0.2] 甘特图生成器
│   │   └── risk_analyzer.py        # [v0.2] 风险分析器
│   ├── estimator/                  # 时间估算模块（新增）
│   │   ├── __init__.py
│   │   ├── complexity_analyzer.py  # [v0.2] 复杂度分析器
│   │   └── time_estimator.py       # [v0.2] 时间估算器
│   ├── version/                    # 版本管理模块（新增）
│   │   ├── __init__.py
│   │   ├── version_manager.py      # [v0.2] 版本管理器
│   │   └── diff_generator.py       # [v0.2] 差异生成器
│   ├── llm/                        # LLM适配层
│   │   ├── __init__.py
│   │   ├── base.py                 # [v0.1] 基础接口
│   │   └── openai_adapter.py       # [v0.1] OpenAI适配器
│   ├── utils/                      # 工具函数
│   │   ├── __init__.py
│   │   └── logger.py               # [v0.1] 日志工具
│   └── __init__.py                 # 统一导出接口
├── backend/                        # 后端服务（位置不变）
├── frontend/                       # 前端界面（位置不变）
└── ...
```

## 执行计划

### 阶段1：准备工作（5个任务）
1. ✅ 创建 MODULE_MERGE_STRATEGY.md
2. ⏳ 创建新增模块目录（estimator, version）
3. ⏳ 更新 twork/__init__.py 导出接口
4. ⏳ 备份原有代码到 backup/ 目录
5. ⏳ 创建 .gitignore 规则

### 阶段2：复制v0.2新模块（7个文件）
1. ⏳ 复制 domain_classifier.py
2. ⏳ 复制 context_template_manager.py
3. ⏳ 复制 wbs_decomposer.py
4. ⏳ 复制 conflict_resolver.py
5. ⏳ 复制 debate_simulator.py
6. ⏳ 复制 gantt_generator.py
7. ⏳ 复制 risk_analyzer.py

### 阶段3：集成新模块（2个模块）
1. ⏳ 集成 estimator 模块（complexity_analyzer.py, time_estimator.py）
2. ⏳ 集成 version 模块（version_manager.py, diff_generator.py）

### 阶段4：更新导入和文档
1. ⏳ 更新各模块 __init__.py
2. ⏳ 更新 backend 导入路径
3. ⏳ 更新文档和测试

### 阶段5：清理
1. ⏳ 删除根目录 twork/ 文件夹
2. ⏳ 更新 .gitignore
3. ⏳ 运行测试验证

## 依赖关系图

```
twork核心库（可独立安装）
├── llm/           # 基础层：LLM适配
├── utils/         # 基础层：工具函数
├── parser/        # 业务层：依赖 llm, utils
├── estimator/     # 业务层：依赖 llm, utils
├── agent/         # 业务层：依赖 llm, utils, parser
├── generator/     # 业务层：依赖 utils, parser, estimator
└── version/       # 业务层：依赖 utils

backend服务
├── models/        # 数据层
├── services/      # 业务层：依赖 twork
└── api/           # 接口层：依赖 services
```

## 冲突检测

### 无冲突模块（互补功能）
- ✅ parser：v0.1和v0.2功能完全不重叠
- ✅ agent：v0.1和v0.2功能完全不重叠
- ✅ generator：v0.1和v0.2功能完全不重叠
- ✅ estimator：仅v0.2存在
- ✅ version：仅v0.2存在

### 需要注意的点
- ⚠️ 确保 llm 模块接口统一
- ⚠️ 确保 utils 工具函数不重复
- ⚠️ 检查 backend 依赖的模块是否都已迁移

## 验证清单

- [ ] 所有v0.1模块文件已保留
- [ ] 所有v0.2模块文件已复制
- [ ] estimator和version模块已集成
- [ ] twork/__init__.py导出所有类
- [ ] backend导入路径已更新
- [ ] 测试通过
- [ ] 文档已更新
