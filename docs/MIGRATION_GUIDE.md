# 快速迁移指南

## 升级步骤

### 1. 拉取最新代码
```bash
cd /path/to/team-work
git pull origin main
```

### 2. 更新前端依赖
```bash
cd frontend
pip install sseclient-py>=1.8.0
```

### 3. 重启服务
```bash
# 方式1: Docker Compose（推荐）
docker-compose down
docker-compose up --build -d

# 方式2: 手动重启
# 终端1 - 后端
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 终端2 - 前端
cd frontend
python app.py
```

### 4. 验证功能

#### 测试1: 任务拆解
1. 上传文档
2. 点击"执行任务拆解"
3. 检查是否返回200（无500错误）
4. 尝试下载任务清单文件

#### 测试2: 流式模拟
1. 生成Agent
2. 设置工期为65天（测试长工期场景）
3. 启用环境干扰Agent
4. 点击"开始模拟"
5. 观察：
   - 日志表格是否实时更新
   - 是否出现超时错误
   - 模拟完成后是否显示完整日志

#### 测试3: Agent编辑
1. 生成Agent后，编辑表格：
   - 取消勾选某个Agent
   - 修改角色名称
   - 修改项目工期
2. 点击"保存修改"
3. 重新运行模拟，验证修改生效

## 新API端点

### 1. 流式模拟
```bash
POST /api/simulation/run-stream
Content-Type: application/json

{
  "project_id": 1,
  "enable_env_agent": true,
  "env_event_probability": 0.2
}

# 返回: text/event-stream
```

### 2. Agent批量更新
```bash
PUT /api/agent/batch-update
Content-Type: application/json

{
  "project_id": 1,
  "agents": [
    {
      "agent_id": "agent_001",
      "role_name": "高级开发工程师",
      "enabled": true
    }
  ],
  "total_days": 45
}
```

### 3. Agent列表
```bash
GET /api/agent/list/1
```

## 常见问题

### Q1: 升级后模拟仍然超时？
**A**: 检查前端是否安装了 `sseclient-py`：
```bash
pip list | grep sseclient
```

如果未安装：
```bash
pip install sseclient-py
```

### Q2: Agent编辑按钮不显示？
**A**: 清除浏览器缓存或强制刷新（Ctrl+Shift+R / Cmd+Shift+R）

### Q3: 任务拆解仍然返回500？
**A**: 检查数据库连接和日志：
```bash
docker-compose logs backend | grep "任务拆解"
```

### Q4: SSE连接失败？
**A**: 检查防火墙和代理设置，确保不阻止长连接

## 回滚方案

如果遇到严重问题需要回滚：

```bash
# 1. 回滚代码
git checkout <previous_commit_hash>

# 2. 重启服务
docker-compose down
docker-compose up -d

# 3. 通知团队
```

## 技术支持

遇到问题请检查：
1. `backend/logs/app.log` - 后端日志
2. 浏览器控制台 - 前端错误
3. `docker-compose logs` - 容器日志

---

**升级时间**: 约5分钟  
**停机时间**: 约30秒  
**风险等级**: 低
