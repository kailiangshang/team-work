# TeamWork - AI多角色任务协同模拟系统

<p align="center">
  <img src="https://img.shields.io/badge/version-0.2.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
</p>

## 📖 项目简介

TeamWork 是一个基于大模型Agent的智能任务模拟系统,能够将任意类型的需求文档（开发需求、户外作业需求等）自动拆解为结构化任务,并通过多角色Agent模拟真实项目执行过程,生成可视化任务编排图谱和时间排期。

### ✨ v0.2.0 新特性

- **领域识别** 🎯 - 自动识别项目领域（软件开发、产品设计、市场营销、数据分析）
- **WBS拆解** 📋 - 支持多层级（1-4级）工作分解结构
- **复杂度分析** 📊 - 多维度任务复杂度评估和时间估算
- **冲突解决** ⚖️ - 自动检测和解决资源、优先级、依赖冲突
- **甘特图生成** 📈 - 自动生成项目甘特图和关键路径
- **风险分析** ⚠️ - 识别和评估项目风险
- **版本管理** 🔄 - 项目快照和版本对比

### 核心功能

- **智能文档解析** 📄 - 自动解析需求文档,提取关键信息
- **领域自动识别** 🎯 - 识别项目领域并加载对应模板
- **任务智能拆解** 🔨 - 支持简单拆解和多层级WBS拆解
- **复杂度分析** 📊 - 多维度复杂度评估和三点时间估算
- **多角色模拟** 🎭 - 基于需求动态创建角色Agent,模拟真实项目协作
- **冲突解决** ⚖️ - 自动检测和解决多种类型冲突
- **可视化编排** 📈 - 生成任务流程图谱、甘特图、CSV编排文件
- **风险分析** ⚠️ - 识别技术、资源、进度等多维度风险
- **版本管理** 🔄 - 项目快照、版本对比、变更追踪
- **灵活部署** 🚀 - 支持本地SQLite和远程数据库,Docker容器化部署

## 🏗️ 系统架构

```
team-work/
├── twork/                 # 核心技术库（可独立安装，v0.2.0）
│   ├── parser/            # 文档解析模块（6个文件）
│   │   ├── document_loader.py           # 文档加载
│   │   ├── requirement_extractor.py     # 需求提取
│   │   ├── task_decomposer.py           # 简单任务拆解
│   │   ├── domain_classifier.py         # 领域识别（新）
│   │   ├── context_template_manager.py  # 模板管理（新）
│   │   └── wbs_decomposer.py            # WBS拆解（新）
│   ├── agent/             # Agent模块（5个文件）
│   │   ├── role_generator.py            # 角色生成
│   │   ├── multi_agent_runner.py        # 多Agent运行
│   │   ├── simulation_engine.py         # 模拟引擎
│   │   ├── conflict_resolver.py         # 冲突解决（新）
│   │   └── debate_simulator.py          # 讨论模拟（新）
│   ├── generator/         # 结果生成模块（5个文件）
│   │   ├── document_generator.py        # 文档生成
│   │   ├── csv_exporter.py              # CSV导出
│   │   ├── graph_builder.py             # 图谱构建
│   │   ├── gantt_generator.py           # 甘特图（新）
│   │   └── risk_analyzer.py             # 风险分析（新）
│   ├── estimator/         # 估算模块（新增）
│   │   ├── complexity_analyzer.py       # 复杂度分析
│   │   └── time_estimator.py            # 时间估算
│   ├── version/           # 版本管理模块（新增）
│   │   ├── version_manager.py           # 版本管理
│   │   └── diff_generator.py            # 差异对比
│   ├── llm/               # LLM适配层
│   └── utils/             # 工具函数
├── backend/               # FastAPI后端服务
│   └── app/
│       ├── models/        # 数据模型
│       ├── api/           # API路由
│       └── services/      # 业务逻辑
├── frontend/              # Gradio前端界面
├── docs/                  # 文档目录（新增）
│   ├── QUICKSTART.md      # 快速开始
│   ├── FEATURES.md        # 功能说明
│   ├── MODULES.md         # 模块清单
│   └── ...                # 其他文档
├── data/                  # 数据目录
├── logs/                  # 日志目录
└── scripts/               # 工具脚本（新增）
    └── check_duplication.py  # 重复检测
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Docker & Docker Compose (可选)

### 方式一: Docker部署（推荐）

1. **克隆项目**
```bash
git clone https://github.com/yourusername/team-work.git
cd team-work
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件,配置LLM API密钥等信息
```

3. **启动服务**
```bash
docker-compose up -d
```

4. **访问应用**
- 前端界面: http://localhost:7860
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 方式二: 本地开发

1. **安装twork核心库**
```bash
pip install -e .
```

2. **安装后端依赖**
```bash
cd backend
pip install -r requirements.txt
```

3. **安装前端依赖**
```bash
cd frontend
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件
```

5. **启动后端服务**
```bash
cd backend
python -m app.main
```

6. **启动前端服务**
```bash
cd frontend
python app.py
```

## 📚 使用指南

### 1. 上传需求文档

- 支持格式: PDF、Markdown、TXT、DOCX
- 文档内容: 项目需求、目标、约束条件等

### 2. 自动解析和拆解

系统将自动:
- 提取需求关键信息
- 拆解为结构化任务列表
- 生成任务分解文档

### 3. 生成角色Agent

根据任务自动生成:
- 角色类型（如产品经理、开发工程师等）
- 角色能力和职责
- 任务分配

### 4. 运行模拟

- 按日模拟任务执行过程
- 生成角色协作讨论记录
- 记录任务进度和产出

### 5. 导出结果

生成以下文件:
- 任务分解文档（Markdown）
- 任务排期表（CSV）
- 任务关系图谱（Mermaid）
- 知识图谱三元组（JSON）

## ⚙️ 配置说明

### LLM配置

```env
LLM_API_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your_api_key
LLM_MODEL_NAME=gpt-4
LLM_TEMPERATURE=0.7
```

### 数据库配置

**SQLite模式（默认）:**
```env
DATABASE_TYPE=sqlite
SQLITE_PATH=data/db/teamwork.db
```

**PostgreSQL模式:**
```env
DATABASE_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=teamwork
DB_USERNAME=admin
DB_PASSWORD=your_password
```

## 🔧 技术栈

- **后端**: FastAPI, SQLAlchemy, Alembic
- **前端**: Gradio
- **核心**: Python, OpenAI SDK
- **数据库**: SQLite / PostgreSQL
- **部署**: Docker, Docker Compose

## 📝 API文档

启动后端服务后,访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 贡献指南

欢迎贡献代码、提出问题和建议！

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📮 联系方式

- 项目主页: https://github.com/yourusername/team-work
- 问题反馈: https://github.com/yourusername/team-work/issues

## 🙏 致谢

感谢所有贡献者和开源项目的支持！

---

**Made with ❤️ by TeamWork Team**
