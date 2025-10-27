# TeamWork 快速启动指南

## 🎯 5分钟快速体验

本指南将帮助你在5分钟内启动并体验TeamWork系统。

## 前置准备

确保你已安装:
- Docker Desktop (推荐) 或 Python 3.8+
- OpenAI API密钥或兼容的LLM API

## 方式一: Docker快速启动（推荐）

### 1. 下载项目

```bash
git clone https://github.com/yourusername/team-work.git
cd team-work
```

### 2. 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件,至少配置以下项:
# LLM_API_KEY=your_openai_api_key
```

**最小配置示例:**
```env
LLM_API_KEY=sk-xxxxxxxxxxxx
DATABASE_TYPE=sqlite
```

### 3. 一键启动

```bash
docker-compose up -d
```

等待1-2分钟,容器启动完成后:

- 🌐 访问前端: http://localhost:7860
- 🔧 访问API文档: http://localhost:8000/docs

### 4. 开始使用

1. 打开浏览器访问 http://localhost:7860
2. 上传一个需求文档（支持PDF/MD/TXT/DOCX）
3. 点击"上传并解析"
4. 按照界面提示依次:
   - 拆解任务
   - 生成角色Agent
   - 开始模拟
   - 生成输出文件

## 方式二: 本地Python启动

### 1. 安装依赖

```bash
# 安装核心库
pip install -e .

# 安装后端依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd ../frontend
pip install -r requirements.txt
```

### 2. 配置环境

```bash
# 在项目根目录
cp .env.example .env
# 编辑.env文件,配置LLM_API_KEY
```

### 3. 启动后端

```bash
# 终端1: 启动后端
cd backend
python -m app.main
```

### 4. 启动前端

```bash
# 终端2: 启动前端
cd frontend
python app.py
```

### 5. 访问应用

- 前端: http://localhost:7860
- 后端API: http://localhost:8000

## 🔍 测试示例

准备一个简单的需求文档进行测试:

**示例文档 (test-requirement.md):**

```markdown
# 在线图书管理系统

## 项目目标
开发一个简单的在线图书管理系统,支持图书的增删改查功能。

## 核心需求
1. 用户可以浏览图书列表
2. 管理员可以添加、编辑、删除图书
3. 支持按书名、作者搜索图书
4. 图书信息包括:书名、作者、ISBN、出版日期、简介

## 技术要求
- 后端: Python FastAPI
- 前端: React
- 数据库: PostgreSQL

## 交付物
- 完整的源代码
- API文档
- 部署文档
- 用户手册
```

将此文档保存为 `test-requirement.md` 并上传到系统进行测试。

## ⚙️ 常见配置

### 使用自定义LLM API

如果你使用的不是OpenAI API,而是兼容的API服务:

```env
LLM_API_BASE_URL=https://your-api-endpoint.com/v1
LLM_API_KEY=your_api_key
LLM_MODEL_NAME=your-model-name
```

### 使用PostgreSQL数据库

```env
DATABASE_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=teamwork
DB_USERNAME=your_username
DB_PASSWORD=your_password
```

### 调整日志级别

```env
LOG_LEVEL=DEBUG  # 可选: DEBUG, INFO, WARNING, ERROR
```

## 🛠️ 常见问题

### 1. Docker容器启动失败

**检查端口占用:**
```bash
# 检查8000和7860端口是否被占用
lsof -i :8000
lsof -i :7860

# 如果被占用,可以修改docker-compose.yml中的端口映射
```

### 2. LLM连接失败

**检查API配置:**
- 确认API密钥正确
- 确认API地址可访问
- 检查网络连接

### 3. 文档解析失败

**支持的文件格式:**
- PDF (需要文本内容,不支持纯图片PDF)
- Markdown (.md)
- 文本文件 (.txt)
- Word文档 (.docx)

### 4. 查看日志

**Docker模式:**
```bash
# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend
```

**本地模式:**
```bash
# 日志文件位置
tail -f logs/teamwork.log
```

## 🔄 停止和重启

### Docker模式

```bash
# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 重启服务
docker-compose restart

# 重新构建并启动
docker-compose up -d --build
```

### 本地模式

在各个终端按 `Ctrl+C` 停止服务

## 📊 验证安装

访问以下URL验证各组件:

1. **后端健康检查:** http://localhost:8000/health
   - 应返回: `{"status": "healthy"}`

2. **API文档:** http://localhost:8000/docs
   - 应显示Swagger UI界面

3. **前端界面:** http://localhost:7860
   - 应显示Gradio界面

## 🎓 下一步

安装成功后,建议:

1. 阅读 [README.md](README.md) 了解详细功能
2. 查看 [API文档](http://localhost:8000/docs) 了解接口
3. 尝试上传自己的需求文档

## 💡 小贴士

- **首次使用**: 建议使用简单的需求文档进行测试
- **模拟时间**: 模拟过程可能需要几分钟,取决于任务数量和LLM响应速度
- **数据保存**: SQLite数据库文件保存在 `data/db/` 目录
- **输出文件**: 生成的文件保存在 `data/outputs/project_<id>/` 目录

## 📞 获取帮助

如遇问题:
1. 查看日志文件
2. 访问 [Issues](https://github.com/yourusername/team-work/issues)
3. 查看 [FAQ](https://github.com/yourusername/team-work/wiki/FAQ)

---

**祝使用愉快!** 🎉
