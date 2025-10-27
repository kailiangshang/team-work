# 架构优化清理计划

## 已完成的合并工作

### ✅ twork核心库合并
所有模块已成功整合到 `team-work/twork/` 目录：

**Parser模块** (6个文件)
- ✅ document_loader.py (v0.1)
- ✅ requirement_extractor.py (v0.1)
- ✅ task_decomposer.py (v0.1)
- ✅ domain_classifier.py (v0.2新增)
- ✅ context_template_manager.py (v0.2新增)
- ✅ wbs_decomposer.py (v0.2新增)

**Agent模块** (5个文件)
- ✅ multi_agent_runner.py (v0.1)
- ✅ role_generator.py (v0.1)
- ✅ simulation_engine.py (v0.1)
- ✅ conflict_resolver.py (v0.2新增)
- ✅ debate_simulator.py (v0.2新增)

**Generator模块** (5个文件)
- ✅ csv_exporter.py (v0.1)
- ✅ document_generator.py (v0.1)
- ✅ graph_builder.py (v0.1)
- ✅ gantt_generator.py (v0.2新增)
- ✅ risk_analyzer.py (v0.2新增)

**Estimator模块** (2个文件，新增)
- ✅ complexity_analyzer.py (v0.2)
- ✅ time_estimator.py (v0.2)

**Version模块** (2个文件，新增)
- ✅ version_manager.py (v0.2)
- ✅ diff_generator.py (v0.2)

**LLM模块** (2个文件)
- ✅ base.py (v0.1)
- ✅ openai_adapter.py (v0.1)

**Utils模块** (1个文件)
- ✅ logger.py (v0.1)

**总计**: 31个Python文件

### ✅ 文档整合
- ✅ 创建 `team-work/docs/` 目录
- ✅ 移动 QUICKSTART.md → docs/
- ✅ 移动 PROJECT_SUMMARY.md → docs/
- ✅ 复制 DEPLOYMENT_GUIDE.md → docs/
- ✅ 复制 README_V2_FEATURES.md → docs/FEATURES.md
- ✅ 创建 docs/ARCHITECTURE.md（模块合并策略）
- ✅ 创建 docs/MODULES.md（功能清单）

### ✅ 基础设施
- ✅ 创建 data/ 目录结构（db, uploads, outputs）
- ✅ 创建 logs/ 目录
- ✅ 添加 .gitkeep 文件
- ✅ 更新 .gitignore
- ✅ 创建 scripts/check_duplication.py
- ✅ 更新 setup.py 版本号为 0.2.0
- ✅ 更新 twork/__init__.py 导出所有模块

## 可以清理的文件和目录

### 🗑️ 根目录的冗余目录
**建议操作**: 删除整个 `twork/` 目录（已合并到 team-work/twork/）

```bash
# 根目录的 twork/ 已经完全整合到 team-work/twork/
# 可以安全删除
rm -rf "/Users/kaiiangs/Desktop/team work/twork"
```

影响范围：
- ❌ 无影响，所有功能已复制到 team-work/twork/
- ✅ test_new_features.py 仍在根目录，可以继续使用

### 🗑️ 根目录的冗余文档
这些文档已经整合到 team-work/docs/ 或不再需要：

```bash
# 已复制到 team-work/docs/
rm "/Users/kaiiangs/Desktop/team work/DEPLOYMENT_GUIDE.md"
rm "/Users/kaiiangs/Desktop/team work/README_V2_FEATURES.md"
rm "/Users/kaiiangs/Desktop/team work/MODULE_MERGE_STRATEGY.md"

# 临时文档，可以删除或归档
rm "/Users/kaiiangs/Desktop/team work/IMPLEMENTATION_SUMMARY.md"
rm "/Users/kaiiangs/Desktop/team work/PROJECT_COMPLETION_REPORT.md"
```

### 📦 建议保留的文件
- ✅ test_new_features.py（测试脚本，仍有用）
- ✅ team-work/（主项目目录）

## 最终目录结构预览

```
/Users/kaiiangs/Desktop/team work/
├── team-work/                      # 唯一的项目目录
│   ├── twork/                      # 统一的核心库（v0.2.0）
│   │   ├── parser/                 # 6个文件
│   │   ├── agent/                  # 5个文件
│   │   ├── generator/              # 5个文件
│   │   ├── estimator/              # 2个文件（新增）
│   │   ├── version/                # 2个文件（新增）
│   │   ├── llm/                    # 2个文件
│   │   ├── utils/                  # 1个文件
│   │   └── __init__.py
│   ├── backend/                    # 后端服务
│   ├── frontend/                   # 前端界面
│   ├── docs/                       # 文档目录
│   │   ├── QUICKSTART.md
│   │   ├── PROJECT_SUMMARY.md
│   │   ├── DEPLOYMENT_GUIDE.md
│   │   ├── FEATURES.md
│   │   ├── ARCHITECTURE.md
│   │   └── MODULES.md
│   ├── data/                       # 数据目录
│   │   ├── db/
│   │   ├── uploads/
│   │   └── outputs/
│   ├── logs/                       # 日志目录
│   ├── scripts/                    # 脚本目录
│   │   └── check_duplication.py
│   ├── docker-compose.yml
│   ├── setup.py
│   ├── .gitignore
│   └── README.md
└── test_new_features.py            # 测试脚本（根目录）
```

## 清理执行脚本

```bash
#!/bin/bash
# 架构优化清理脚本

cd "/Users/kaiiangs/Desktop/team work"

echo "开始清理冗余文件..."

# 1. 删除根目录的 twork/ 目录
echo "删除根目录 twork/ 目录..."
rm -rf twork/

# 2. 删除根目录的冗余文档
echo "删除冗余文档..."
rm -f DEPLOYMENT_GUIDE.md
rm -f README_V2_FEATURES.md
rm -f MODULE_MERGE_STRATEGY.md
rm -f IMPLEMENTATION_SUMMARY.md
rm -f PROJECT_COMPLETION_REPORT.md

echo "清理完成！"
echo "保留的文件："
ls -la | grep -E "^d|test_new_features.py"
```

## 验证清单

清理前请确认：
- [ ] team-work/twork/ 包含所有31个模块文件
- [ ] team-work/docs/ 包含所有文档
- [ ] backend 导入路径正确
- [ ] .gitignore 已更新
- [ ] 代码重复检测通过
- [ ] 所有功能已测试

清理后验证：
- [ ] 根目录只剩 team-work/ 和 test_new_features.py
- [ ] team-work/ 可以正常运行
- [ ] Docker 构建成功
- [ ] 测试通过

## 回滚方案

如果清理后出现问题，可以从Git历史恢复：

```bash
# 如果使用了Git
git checkout HEAD -- twork/
git checkout HEAD -- *.md

# 如果没有Git，建议清理前先备份
cp -r twork twork.backup
```
