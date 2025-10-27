# API 优化说明

## 概述

本次优化主要解决了两个关键问题:
1. 文档上传失败(500错误)的问题
2. LLM配置动态修改功能

## 优化详情

### 1. 文档上传优化 (`backend/app/api/upload.py`)

#### 问题
- 上传失败时只返回简单的500错误,没有详细的错误信息
- 缺少文件验证(类型、大小)
- 没有详细的日志记录,难以排查问题

#### 解决方案

**添加详细的错误处理:**
```python
# 文件类型验证
allowed_extensions = [".pdf", ".md", ".txt", ".docx"]
if file_ext not in allowed_extensions:
    raise HTTPException(
        status_code=400,
        detail=f"不支持的文件类型: {file_ext}"
    )

# 文件大小验证
max_size = settings.max_upload_size_mb * 1024 * 1024
if file_size > max_size:
    raise HTTPException(
        status_code=400,
        detail=f"文件过大: {file_size / 1024 / 1024:.2f}MB"
    )
```

**添加详细日志:**
```python
logger.info(f"开始上传文档: {file.filename}")
logger.info(f"保存文件到: {file_path}")
logger.info(f"项目创建成功: project_id={project.id}")
logger.info(f"文档解析成功: project_id={project.id}")
```

**改进错误响应:**
```python
except HTTPException:
    raise  # 重新抛出HTTP异常
except Exception as e:
    logger.error(f"上传文档失败: {str(e)}")
    logger.error(f"错误堆栈: {traceback.format_exc()}")
    raise HTTPException(
        status_code=500,
        detail=f"上传失败: {str(e)}"
    )
```

### 2. LLM配置管理优化 (`backend/app/api/config.py`)

#### 新增功能

**获取当前LLM配置:**
```http
GET /api/config/llm
```

响应示例:
```json
{
  "api_base_url": "https://api.openai.com/v1",
  "model_name": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 2000,
  "timeout": 60,
  "api_key_configured": true
}
```

**动态更新LLM配置:**
```http
POST /api/config/llm
Content-Type: application/json

{
  "api_base_url": "https://api.openai.com/v1",
  "api_key": "sk-xxx",
  "model_name": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 2000,
  "timeout": 60
}
```

响应示例:
```json
{
  "success": true,
  "message": "LLM配置更新成功",
  "config": {
    "api_base_url": "https://api.openai.com/v1",
    "model_name": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000,
    "timeout": 60
  }
}
```

**改进的测试LLM连接:**
- 添加timeout参数
- 增强错误处理
- 详细的日志记录

### 3. 前端优化 (`frontend/app.py`)

#### 文件上传优化

**改进的错误处理:**
```python
# 检查文件是否选择
if file is None:
    return "⚠️ 请选择要上传的文件", ...

# 增加超时时间
response = requests.post(
    f"{BACKEND_URL}/api/upload/document",
    files=files,
    timeout=120  # 2分钟超时
)

# 详细的错误信息
if response.status_code != 200:
    error_detail = response.json().get("detail", "未知错误")
    return f"❌ 上传失败 ({response.status_code}): {error_detail}", ...

# 处理网络异常
except requests.exceptions.Timeout:
    return "❌ 请求超时,请检查网络连接或后端服务是否正常", ...
except requests.exceptions.ConnectionError:
    return f"❌ 无法连接到后端服务: {BACKEND_URL}", ...
```

#### 新增LLM配置界面

**完整的配置表单:**
- API Base URL输入框
- API Key密码输入框
- 模型名称输入框
- 温度滑块 (0.0-2.0)
- 最大Token数滑块 (100-8000)
- 超时时间滑块 (10-300秒)

**测试连接功能:**
```python
def test_llm_connection(api_url, api_key, model_name, temperature, max_tokens):
    """测试LLM连接并返回详细结果"""
    response = requests.post(
        f"{BACKEND_URL}/api/config/test-llm",
        json={...},
        timeout=30
    )
    
    if result.get("success"):
        return f"""✅ 连接成功!
        
- **延迟**: {result.get('latency_ms', 0)}ms
- **模型**: {result.get('model_info', {}).get('model_name', 'N/A')}
- **API URL**: {result.get('model_info', {}).get('api_base_url', 'N/A')}
"""
```

**保存配置功能:**
```python
def save_llm_config(api_url, api_key, model_name, temperature, max_tokens, timeout):
    """保存LLM配置到后端"""
    response = requests.post(
        f"{BACKEND_URL}/api/config/llm",
        json={...},
        timeout=10
    )
```

## 使用示例

### 1. 测试后端API

使用提供的测试脚本:
```bash
cd /Users/kaiiangs/Desktop/team\ work/team-work
python test_api.py
```

### 2. 配置LLM

在前端界面:
1. 进入"⚙️ 配置"标签页
2. 填写API信息:
   - API Base URL: `https://api.openai.com/v1`
   - API Key: 你的OpenAI API密钥
   - 模型名称: `gpt-4` 或 `gpt-3.5-turbo`
3. 调整参数(可选):
   - 温度: 0.7 (推荐)
   - 最大Token数: 2000 (推荐)
   - 超时时间: 60秒
4. 点击"🔌 测试连接"验证配置
5. 点击"💾 保存配置"应用更改

### 3. 上传文档

1. 进入"📄 文档上传"标签页
2. 选择文档文件(支持 PDF, MD, TXT, DOCX)
3. 点击"上传并解析"
4. 查看详细的错误信息(如果失败)

## 错误处理改进

### 常见错误及解决方法

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `❌ 无法连接到后端服务` | 后端未启动 | 启动Docker容器: `docker-compose up` |
| `❌ 请求超时` | 网络慢或文档太大 | 检查网络连接,或减小文档大小 |
| `不支持的文件类型` | 文件格式不正确 | 使用PDF/MD/TXT/DOCX格式 |
| `文件过大` | 超过50MB限制 | 压缩文件或分割文档 |
| `❌ 连接失败: Unauthorized` | API Key错误 | 检查并更新API Key |
| `❌ 连接失败: timeout` | API响应慢 | 增加超时时间设置 |

## 日志查看

### 后端日志

查看容器日志:
```bash
docker-compose logs -f backend
```

查看应用日志文件:
```bash
tail -f logs/teamwork.log
```

### 前端日志

查看容器日志:
```bash
docker-compose logs -f frontend
```

## 性能优化建议

1. **文件上传**
   - 建议文档大小 < 10MB
   - 使用纯文本或Markdown格式获得最快速度
   - PDF文档会稍慢,因为需要OCR提取

2. **LLM配置**
   - 对于简单任务使用 `gpt-3.5-turbo` 节省成本
   - 复杂任务使用 `gpt-4` 获得更好质量
   - 调整温度: 0.3-0.5 获得稳定输出, 0.7-1.0 获得创意输出

3. **超时设置**
   - 本地部署的模型: 30-60秒
   - 云端API: 60-120秒
   - 网络不稳定时: 120-300秒

## API参考

### 完整API列表

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/config/llm` | GET | 获取LLM配置 |
| `/api/config/llm` | POST | 更新LLM配置 |
| `/api/config/test-llm` | POST | 测试LLM连接 |
| `/api/config/test-db` | POST | 测试数据库连接 |
| `/api/upload/document` | POST | 上传需求文档 |
| `/api/task/decompose` | POST | 拆解任务 |
| `/api/task/generate-agents` | POST | 生成角色Agent |
| `/api/simulation/run` | POST | 运行模拟 |
| `/api/simulation/generate-outputs` | POST | 生成输出文件 |

## 后续改进计划

1. [ ] 添加文档预览功能
2. [ ] 支持批量上传文档
3. [ ] 添加配置导入/导出功能
4. [ ] 实现配置版本管理
5. [ ] 添加API使用统计和成本跟踪
6. [ ] 支持更多LLM提供商(Anthropic, Google, etc.)
