# simulate_stream 方法缺失错误修复

## 问题描述

点击"▶️ 开始模拟"按钮时出现错误：

```
❌ 模拟错误: 'SimulationEngine' object has no attribute 'simulate_stream'
```

## 问题原因

### 根本原因：Docker 容器中的代码未更新

虽然本地代码文件 `twork/agent/simulation_engine.py` 中包含了 `simulate_stream()` 方法（第309-434行），但 **Docker 容器中的代码是旧版本**。

**为什么会这样？**

1. **twork 目录是通过 COPY 命令复制到镜像中的**：
   ```dockerfile
   COPY twork ./twork
   ```

2. **代码修改后需要重新构建镜像**：
   - 修改本地文件不会自动更新容器
   - 需要执行 `docker-compose build` 重新构建
   - 不同于 volume 挂载的目录（如 `backend/app`）

3. **容器使用的是构建时的快照**：
   - 启动容器时使用的是镜像中的代码
   - 本地修改只影响源文件，不影响运行中的容器

### 验证问题

**检查本地文件**：
```bash
grep -n "def simulate_stream" twork/agent/simulation_engine.py
# 输出: 309:    def simulate_stream(
```

**检查容器中的文件**：
```bash
docker exec teamwork-backend grep -n "def simulate_stream" /app/twork/agent/simulation_engine.py
# 输出为空 ❌ 说明容器中没有这个方法
```

## 解决方案

### 步骤 1：重新构建后端镜像

```bash
cd "/Users/kaiiangs/Desktop/team work/team-work"
docker-compose build backend
```

**过程**：
- 复制最新的 twork 目录到镜像
- 安装所有 Python 依赖
- 复制后端代码
- 创建数据目录

**耗时**：约 1-2 分钟

### 步骤 2：重启后端容器

```bash
docker-compose up -d backend
```

### 步骤 3：验证修复

```bash
docker exec teamwork-backend grep -n "def simulate_stream" /app/twork/agent/simulation_engine.py
# 输出: 310:    def simulate_stream(  ✅
```

## 技术细节

### twork 库的引入方式

根据项目规范，twork 库通过以下方式引入：

1. **不使用 pip 安装**：
   - 避免重复安装
   - 避免"造轮子"

2. **通过 COPY 复制到镜像**：
   ```dockerfile
   COPY twork ./twork
   ```

3. **通过 PYTHONPATH 引入**：
   ```dockerfile
   ENV PYTHONPATH="/app:${PYTHONPATH}"
   ```

**优点**：
- ✅ 开发和生产使用同一份代码
- ✅ 避免版本不一致
- ✅ 修改后重新构建即可

**缺点**：
- ❌ 修改 twork 代码后需要重新构建镜像
- ❌ 不如 volume 挂载方便（但更安全）

### Volume vs COPY 对比

| 方式 | backend/app | twork |
|------|------------|-------|
| 引入方式 | Volume 挂载 | COPY 复制 |
| 修改后生效 | 立即（热重载） | 需重新构建 |
| 适用场景 | 频繁修改的应用代码 | 核心库（稳定） |
| 配置 | `volumes:` | `COPY` |

**示例配置**：
```yaml
# docker-compose.yml
backend:
  build: .
  volumes:
    - ./backend/app:/app/app  # 挂载，立即生效
  # twork 通过 COPY 复制，需重新构建
```

## 完整的 simulate_stream 方法

位置：`twork/agent/simulation_engine.py` (第309-434行)

```python
def simulate_stream(
    self,
    agents: List[Dict[str, Any]],
    tasks: List[Dict[str, Any]],
    total_days: int,
    enable_env_agent: bool = True,
    env_event_probability: float = 0.2
):
    """
    流式模拟项目执行（生成器）
    
    Args:
        agents: 角色配置列表
        tasks: 任务列表
        total_days: 总工期
        enable_env_agent: 是否启用环境Agent
        env_event_probability: 环境事件概率
        
    Yields:
        每天的模拟结果
    """
    # 实现细节...
```

**功能**：
- 逐天模拟项目执行
- 实时 yield 每天的结果
- 支持 SSE 流式推送
- 支持环境事件注入

## 预防措施

### 何时需要重新构建镜像？

**必须重新构建**：
1. ✅ 修改了 `twork/` 目录下的任何文件
2. ✅ 修改了 `requirements.txt` 依赖
3. ✅ 修改了 `Dockerfile`
4. ✅ 修改了系统级配置

**不需要重新构建**（自动生效）：
1. ❌ 修改了 `backend/app/` 下的文件（volume 挂载）
2. ❌ 修改了 `.env` 环境变量
3. ❌ 修改了 `docker-compose.yml` 的环境变量

### 开发流程建议

**修改 twork 核心库后**：
```bash
# 1. 修改代码
vim twork/agent/simulation_engine.py

# 2. 重新构建
docker-compose build backend

# 3. 重启容器
docker-compose up -d backend

# 4. 验证修复
docker-compose logs -f backend
```

**快速重启（不重新构建）**：
```bash
# 仅适用于修改了 backend/app/ 下的代码
docker-compose restart backend
```

## 测试验证

### 测试步骤

1. ✅ **验证方法存在**
   ```bash
   docker exec teamwork-backend python -c "from twork.agent import SimulationEngine; print(hasattr(SimulationEngine, 'simulate_stream'))"
   # 输出: True
   ```

2. ✅ **运行模拟**
   - 上传文档
   - 拆解任务
   - 生成 Agent
   - 点击"▶️ 开始模拟"
   - 应该看到实时进度和日志

3. ✅ **检查日志**
   ```bash
   docker-compose logs backend | grep "开始流式模拟"
   ```

### 预期结果

- ✅ 不再出现 `'SimulationEngine' object has no attribute 'simulate_stream'`
- ✅ 模拟可以正常运行
- ✅ 可以看到实时进度条
- ✅ 可以看到 Agent 对话日志

## 相关文档

- [SIMULATION_ERROR_FIX.md](./SIMULATION_ERROR_FIX.md) - 模拟执行错误修复（依赖问题）
- [DATAFRAME_FIX.md](./DATAFRAME_FIX.md) - DataFrame 布尔值判断问题
- [API_KEY_SAVE_FIX.md](./API_KEY_SAVE_FIX.md) - API Key 保存问题

## 更新时间

2025-10-25
