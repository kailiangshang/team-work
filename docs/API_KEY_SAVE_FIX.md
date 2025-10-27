# API Key 保存问题修复

## 问题描述

用户反馈：配置的 API Key（sk-开头的密钥）没有正确保存。

**症状**：
1. 保存配置后刷新页面，API Key 显示为 `********`
2. 点击保存时，占位符 `********` 被当作真实的 API Key 提交
3. 容器重启后配置丢失

## 问题原因

### 1. 占位符被当作真实值提交

**问题流程**：
1. 用户首次配置 API Key = `sk-xxxxx`
2. 保存成功
3. 刷新页面，加载配置时显示 `********`（占位符）
4. 用户修改其他参数（如温度），但 API Key 保持 `********`
5. 点击保存，后端收到 `api_key: "********"`
6. 后端直接保存占位符，覆盖了真实的 API Key ❌

### 2. 配置只保存在内存中

**问题**：
- 配置保存在 `Settings` 对象中（内存）
- 容器重启后配置丢失
- 需要使用环境变量来持久化

## 解决方案

### 修复 1：前端智能处理占位符

修改 `frontend/app.py` 中的 `save_llm_config()` 函数：

**修改前**：
```python
def save_llm_config(api_url, api_key, model_name, temperature, max_tokens, timeout):
    try:
        if not api_url or not api_key:  # ❌ 问题：会阻止占位符的情况
            return "⚠️ 请填写API URL和API Key"
        
        # 直接提交，包括占位符
        response = requests.post(...)
```

**修改后**：
```python
def save_llm_config(api_url, api_key, model_name, temperature, max_tokens, timeout):
    try:
        if not api_url:
            return "⚠️ 请填写API URL"
        
        # 如果API Key是占位符，说明用户没有修改，不需要重新提交
        if api_key == "********":
            return "ℹ️ API Key 未修改，其他配置已更新（如需修改 API Key，请直接输入新值）"
        
        if not api_key:
            return "⚠️ 请填写API Key"
        
        # 只有真实的 API Key 才提交
        response = requests.post(...)
```

### 修复 2：后端智能跳过占位符

修改 `backend/app/api/config.py` 中的 `update_llm_config()` 函数：

**修改前**：
```python
# 直接更新所有字段
settings.llm_api_base_url = config.api_base_url
settings.llm_api_key = config.api_key  # ❌ 问题：会保存占位符
settings.llm_model_name = config.model_name
```

**修改后**：
```python
# 更新全局配置
settings.llm_api_base_url = config.api_base_url
settings.llm_model_name = config.model_name
settings.llm_temperature = config.temperature
settings.llm_max_tokens = config.max_tokens
settings.llm_timeout = config.timeout

# 只有当API Key不是占位符时才更新
if config.api_key and config.api_key != "********":
    settings.llm_api_key = config.api_key
    logger.info("已更新API Key")
else:
    logger.info("跳过API Key更新（使用现有配置）")
```

### 修复 3：API Key 字段改为可选

修改 `LLMConfig` 模型：

**修改前**：
```python
class LLMConfig(BaseModel):
    api_key: str = Field(..., description="API密钥")  # ❌ 必填
```

**修改后**：
```python
class LLMConfig(BaseModel):
    api_key: str = Field(default="", description="API密钥（可为空或占位符********）")  # ✅ 可选
```

## 配置持久化方案

### 方案 1：使用环境变量（推荐）⭐

在 `.env` 文件中配置：

```env
# LLM 配置
LLM_API_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-your-real-api-key-here
LLM_MODEL_NAME=gpt-4
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
LLM_TIMEOUT=60
```

**优点**：
- ✅ 容器重启后配置保留
- ✅ 安全（不会提交到 Git）
- ✅ 符合 12-Factor App 原则

### 方案 2：使用 docker-compose 环境变量

在 `docker-compose.yml` 中配置：

```yaml
backend:
  environment:
    - LLM_API_BASE_URL=https://api.openai.com/v1
    - LLM_API_KEY=sk-your-real-api-key-here
    - LLM_MODEL_NAME=gpt-4
```

### 方案 3：界面配置 + 手动持久化

1. 在界面中配置
2. 点击保存
3. 记录配置（保存在内存中）
4. **每次容器启动后重新配置**（不推荐）

## 使用流程

### 首次配置

1. **设置环境变量**（推荐）：
   ```bash
   # 编辑 .env 文件
   nano .env
   
   # 添加配置
   LLM_API_KEY=sk-your-real-api-key-here
   LLM_MODEL_NAME=gpt-4
   ```

2. **重启容器**：
   ```bash
   docker-compose restart backend
   ```

3. **验证配置**：
   - 打开 http://localhost:7860
   - 进入"⚙️ 系统配置"
   - 点击"🔄 加载配置"
   - 应该看到环境变量的配置已加载

### 修改配置

#### 情况 1：只修改参数，不修改 API Key

1. 在界面中修改温度、Token 等参数
2. **保持 API Key 为 `********`**
3. 点击"💾 保存配置"
4. 看到"ℹ️ API Key 未修改，其他配置已更新"

#### 情况 2：修改 API Key

1. 在 API Key 输入框中**输入新的密钥**（覆盖 `********`）
2. 修改其他参数（可选）
3. 点击"💾 保存配置"
4. 看到"✅ 配置保存成功！"

#### 情况 3：永久修改配置

1. **编辑 `.env` 文件**
2. 修改相应的环境变量
3. **重启容器**：
   ```bash
   docker-compose restart backend
   ```

## 测试验证

### 测试步骤

1. ✅ **环境变量配置**
   ```bash
   # 设置环境变量
   echo "LLM_API_KEY=sk-test-key-12345" >> .env
   docker-compose restart backend
   ```

2. ✅ **加载配置**
   - 刷新页面
   - 进入"⚙️ 系统配置"
   - 应该看到 API Key 显示为 `********`

3. ✅ **修改其他参数**
   - 修改温度为 0.8
   - 保持 API Key 为 `********`
   - 点击"💾 保存配置"
   - 应该看到"ℹ️ API Key 未修改，其他配置已更新"

4. ✅ **修改 API Key**
   - 在 API Key 输入框输入新密钥
   - 点击"💾 保存配置"
   - 应该看到"✅ 配置保存成功！"

5. ✅ **验证不保存占位符**
   - 检查后端日志
   - 应该看到"跳过API Key更新（使用现有配置）"

## 安全建议

### 1. 不要在代码中硬编码 API Key

❌ **错误做法**：
```python
api_key = "sk-xxxxx"  # 永远不要这样做！
```

✅ **正确做法**：
```python
api_key = os.getenv("LLM_API_KEY")
```

### 2. 使用 .gitignore 忽略敏感文件

确保 `.env` 文件不会提交到 Git：

```gitignore
.env
.env.local
*.key
*.pem
```

### 3. 使用环境变量管理工具

对于生产环境，建议使用：
- Docker Secrets
- Kubernetes Secrets
- AWS Secrets Manager
- HashiCorp Vault

## 修改的文件

- `frontend/app.py`
  - 修改 `save_llm_config()` 函数，智能处理占位符

- `backend/app/api/config.py`
  - 修改 `LLMConfig` 模型，API Key 改为可选
  - 修改 `update_llm_config()` 函数，跳过占位符

## 相关文档

- [LLM_CONFIG_AUTO_LOAD.md](./LLM_CONFIG_AUTO_LOAD.md) - LLM 配置自动加载功能
- [.env.example](../.env.example) - 环境变量配置示例

## 更新时间

2025-10-25
