# 模拟执行错误修复

## 问题描述

点击"▶️ 开始模拟"按钮时出现以下错误：

### 错误 1: ModuleNotFoundError
```
ModuleNotFoundError: No module named 'sseclient'
```

### 错误 2: NameError
```
NameError: name 'run_simulation' is not defined. Did you mean: 'handle_simulation'?
```

## 问题原因

### 1. 缺少 sseclient-py 依赖

虽然 `frontend/requirements.txt` 中包含了 `sseclient-py>=1.8.0`，但容器中没有安装该模块。

**可能原因**：
- 使用了旧的 Docker 镜像缓存
- 之前构建时 requirements.txt 中没有这个依赖
- 容器启动后手动修改了 requirements.txt 但没有重新构建

### 2. 回退逻辑错误

`run_simulation_stream()` 函数在 `ImportError` 时尝试调用不存在的 `run_simulation()` 函数：

```python
except ImportError:
    # 如果没有sseclient，回退到同步方式
    return run_simulation(project_id, enable_env_agent, env_probability)[:2]  # ❌ 错误
```

**问题**：`run_simulation()` 函数在之前的重构中已被删除。

## 解决方案

### 1. 临时修复：在运行中的容器安装依赖

```bash
docker exec teamwork-frontend pip install sseclient-py
docker-compose restart frontend
```

### 2. 永久修复：修复回退逻辑

修改 `frontend/app.py` 中的 `run_simulation_stream()` 函数，将回退逻辑改为直接调用同步 API：

**修改前** (第312-313行):
```python
except ImportError:
    # 如果没有sseclient，回退到同步方式
    return run_simulation(project_id, enable_env_agent, env_probability)[:2]
```

**修改后**:
```python
except ImportError:
    # 如果没有sseclient，使用同步方式
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/simulation/run",
            json={
                "project_id": project_id,
                "enable_env_agent": enable_env_agent,
                "env_event_probability": env_probability
            },
            timeout=300  # 5分钟超时
        )
        response.raise_for_status()
        
        result = response.json()
        logs = result.get("logs", [])
        
        # 转换为DataFrame
        if logs:
            df_data = []
            for log in logs:
                df_data.append({
                    "时间": log.get("timestamp", ""),
                    "角色": log.get("role_name", ""),
                    "事件类型": log.get("event_type", ""),
                    "任务": log.get("task_name", "") or log.get("task_id", ""),
                    "内容": log.get("content", "")[:100] + "..." if len(log.get("content", "")) > 100 else log.get("content", ""),
                    "状态": log.get("status", ""),
                    "进度(%)": log.get("progress_percentage", "")
                })
            df = pd.DataFrame(df_data)
        else:
            df = pd.DataFrame(columns=["时间", "角色", "事件类型", "任务", "内容", "状态", "进度(%)"])
        
        summary_info = f"## 模拟执行完成！\n\n"
        summary_info += f"**总日志数**: {len(logs)}\n\n"
        
        return summary_info, df
        
    except Exception as e:
        return f"❌ 模拟失败: {str(e)}", None
```

### 3. 长期修复：重新构建镜像

为了确保下次启动容器时自动包含所有依赖：

```bash
cd /Users/kaiiangs/Desktop/team\ work/team-work
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

## 修改的文件

- `frontend/app.py`
  - 修复了 `run_simulation_stream()` 函数的回退逻辑（第312-351行）
  - 直接调用同步 API 而不是不存在的函数

## 技术细节

### SSE (Server-Sent Events) 流式传输

项目使用 SSE 来实现模拟过程的实时进度反馈：

**优点**：
- ✅ 实时显示模拟进度
- ✅ 可以显示每一天的模拟日志
- ✅ 用户体验更好

**依赖**：
- `sseclient-py` 库用于解析 SSE 事件流

### 回退机制

如果 `sseclient-py` 不可用，系统会自动回退到同步 API：

1. **流式 API**（推荐）：`POST /api/simulation/run-stream`
   - 使用 SSE 实时推送进度
   - 支持进度条显示
   
2. **同步 API**（回退）：`POST /api/simulation/run`
   - 等待模拟完成后一次性返回结果
   - 无进度显示

## 验证测试

### 测试步骤

1. ✅ **检查依赖安装**
   ```bash
   docker exec teamwork-frontend pip list | grep sseclient
   # 应该看到: sseclient-py  1.8.0
   ```

2. ✅ **测试流式模拟**
   - 上传文档并完成前置步骤
   - 点击"▶️ 开始模拟"
   - 应该看到实时进度和日志

3. ✅ **测试回退机制**（可选）
   - 如果 sseclient 不可用，应该自动使用同步 API
   - 仍然能完成模拟，只是没有实时进度

### 预期结果

- ✅ 不再出现 `ModuleNotFoundError: No module named 'sseclient'`
- ✅ 不再出现 `NameError: name 'run_simulation' is not defined`
- ✅ 模拟可以正常运行并返回结果
- ✅ 可以看到 Agent 对话日志

## 相关依赖

`frontend/requirements.txt` 中的关键依赖：

```txt
gradio>=4.0.0
requests>=2.31.0
pandas>=2.0.0
sseclient-py>=1.8.0  # SSE 客户端，用于流式传输
```

## 注意事项

1. **容器重启后依赖保持**：
   - 通过 `docker exec` 安装的依赖在容器重启后会丢失
   - 需要重新构建镜像才能永久保存

2. **推荐的部署流程**：
   ```bash
   # 修改代码后
   docker-compose build frontend
   docker-compose up -d frontend
   ```

3. **开发环境**：
   - 使用 volume 挂载代码时，代码修改会立即生效
   - 但依赖修改需要重新构建镜像

## 更新时间

2025-10-25

## 相关问题

- [DATAFRAME_FIX.md](./DATAFRAME_FIX.md) - DataFrame 布尔值判断问题
- [LLM_CONFIG_AUTO_LOAD.md](./LLM_CONFIG_AUTO_LOAD.md) - LLM 配置自动加载功能
