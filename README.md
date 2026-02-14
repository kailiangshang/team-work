# TWork - 项目管理多Agent模拟系统

基于知识图谱的项目管理多Agent模拟系统，使用 FalkorDB + FastAPI + Next.js 构建。

## 项目架构

```
teamwork-new/
├── twork-core/          # 核心库
│   ├── schemas/         # 数据模型
│   ├── graph/           # 图谱层（FalkorDB）
│   ├── llm/             # LLM适配层
│   ├── parser/          # 文档解析器
│   ├── agent/           # Agent引擎
│   └── simulation/      # 模拟引擎
├── backend/             # FastAPI后端
│   └── app/
│       ├── main.py      # 入口
│       ├── config.py    # 配置
│       └── routers/     # API路由
├── frontend/            # Next.js前端
│   └── src/
│       └── app/         # 页面组件
└── docker-compose.yml   # Docker编排
```

## 技术栈

- **图数据库**: FalkorDB（基于Redis的图数据库）
- **后端**: FastAPI + Python 3.11
- **前端**: Next.js 14 + Ant Design 5
- **LLM**: OpenAI API（支持自定义Base URL）
- **部署**: Docker Compose

## 快速开始

### 环境要求

- Docker & Docker Compose
- Python 3.11+ (本地开发)
- Node.js 18+ (本地开发)

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，设置 OPENAI_API_KEY
```

### 2. Docker 启动（推荐）

```bash
cd teamwork-new
docker-compose up -d
```

访问：
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 3. 本地开发

**启动 FalkorDB:**
```bash
docker run -d --name falkordb -p 6379:6379 falkordb/falkordb:latest
```

**启动后端:**
```bash
cd teamwork-new/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**启动前端:**
```bash
cd teamwork-new/frontend
npm install
npm run dev
```

## 核心功能

### 1. 文档解析
- 支持 PDF、Word、Markdown 等格式
- 自动提取任务、角色、依赖关系

### 2. 知识图谱
- 基于 FalkorDB 存储项目图谱
- 支持任务依赖、角色关联等关系查询

### 3. 多Agent模拟
- TaskAgent: 执行任务模拟
- EnvironmentAgent: 模拟环境因素
- 支持并发执行和状态管理

### 4. 时间估算
- PERT三点估算
- 复杂度分析
- 历史数据学习

## API 端点

| 路径 | 描述 |
|------|------|
| `POST /api/project/` | 创建项目 |
| `GET /api/project/` | 列出项目 |
| `POST /api/simulation/start` | 启动模拟 |
| `GET /api/simulation/status/{id}` | 模拟状态 |
| `GET /api/graph/{project_id}` | 获取图谱 |

## 开发路线

- [x] 项目结构搭建
- [x] 核心库框架
- [x] 后端API框架
- [x] 前端页面框架
- [x] Docker部署配置
- [ ] 完整文档解析功能
- [ ] Agent完整实现
- [ ] 前端完整UI
- [ ] 测试覆盖

## 许可证

MIT License