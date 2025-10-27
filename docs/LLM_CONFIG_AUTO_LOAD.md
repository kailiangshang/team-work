# LLM 配置自动加载功能

## 问题描述

用户反馈：每次刷新页面后，LLM 配置表单都是空的，需要重新手动输入配置信息，非常不便。

**用户期望**：配置好 LLM 后，刷新页面时能自动加载之前保存的配置。

## 解决方案

### 1. 后端支持

后端已经提供了获取配置的 API：

```http
GET /api/config/llm
```

**响应示例**：
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

**注意**：出于安全考虑，API Key 不会返回完整值，只返回是否已配置的布尔标志。

### 2. 前端实现

#### 新增函数：`load_llm_config()`

```python
def load_llm_config():
    """从后端加载LLM配置"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/config/llm",
            timeout=10
        )
        
        if response.status_code == 200:
            config = response.json()
            # 返回配置值，用于填充表单
            # 注意：API Key 不会返回完整值，只返回是否已配置的标志
            return (
                config.get("api_base_url", "https://api.openai.com/v1"),
                "" if not config.get("api_key_configured") else "********",  # 已配置则显示占位符
                config.get("model_name", "gpt-4"),
                config.get("temperature", 0.7),
                config.get("max_tokens", 2000),
                config.get("timeout", 60),
                "ℹ️ 已加载保存的配置" if config.get("api_key_configured") else "⚠️ 请配置 LLM API"
            )
        else:
            # 返回默认值
            return (
                "https://api.openai.com/v1",
                "",
                "gpt-4",
                0.7,
                2000,
                60,
                "⚠️ 无法加载配置，请手动输入"
            )
            
    except Exception as e:
        # 返回默认值
        return (
            "https://api.openai.com/v1",
            "",
            "gpt-4",
            0.7,
            2000,
            60,
            f"⚠️ 加载配置失败: {str(e)}"
        )
```

#### 新增按钮：🔄 加载配置

在"⚙️ 系统配置"标签页中添加了"🔄 加载配置"按钮，用户可以手动点击重新加载配置。

```python
with gr.Row():
    test_llm_btn = gr.Button("🔌 测试连接", variant="secondary")
    save_llm_btn = gr.Button("💾 保存配置", variant="primary")
    load_config_btn = gr.Button("🔄 加载配置", variant="secondary")  # 新增
```

#### 事件绑定

**手动加载**：
```python
# 配置LLM - 加载配置
load_config_btn.click(
    load_llm_config,
    inputs=[],
    outputs=[api_url, api_key, model_name, temperature, max_tokens, timeout_input, llm_result]
)
```

**自动加载**（页面加载时）：
```python
# 页面加载时自动加载配置
app.load(
    load_llm_config,
    inputs=[],
    outputs=[api_url, api_key, model_name, temperature, max_tokens, timeout_input, llm_result]
)
```

### 3. 使用流程

#### 首次配置

1. 打开浏览器访问 http://localhost:7860
2. 切换到"⚙️ 系统配置"标签页
3. 填写 LLM 配置：
   - API Base URL: `https://api.openai.com/v1`
   - API Key: `sk-xxxxx`
   - 模型名称: `gpt-4`
   - 温度: `0.7`
   - 最大Token数: `2000`
   - 超时时间: `60`
4. 点击"🔌 测试连接"验证配置
5. 点击"💾 保存配置"保存到后端

#### 后续使用

1. **刷新页面时**：
   - ✅ 配置自动加载并填充到表单
   - ✅ API URL、模型名称、参数都会恢复
   - ℹ️ API Key 显示为 `********`（占位符，表示已配置）

2. **手动重新加载**：
   - 点击"🔄 加载配置"按钮
   - 从后端重新获取最新配置

### 4. 安全性说明

**API Key 不会返回完整值**：
- 后端 API 只返回 `api_key_configured: true/false` 标志
- 前端显示 `********` 占位符表示已配置
- 如果需要修改 API Key，直接输入新的即可

**为什么这样设计？**
- 防止 API Key 在网络传输中泄露
- 符合安全最佳实践
- 用户可以看到"已配置"状态，但看不到具体的密钥

### 5. 配置持久化

配置保存在后端的 `Settings` 对象中（内存中），重启后会丢失。

**建议**：
1. 使用环境变量配置（推荐）：
   ```bash
   export LLM_API_BASE_URL="https://api.openai.com/v1"
   export LLM_API_KEY="sk-xxxxx"
   export LLM_MODEL_NAME="gpt-4"
   ```

2. 或在 `.env` 文件中配置：
   ```env
   LLM_API_BASE_URL=https://api.openai.com/v1
   LLM_API_KEY=sk-xxxxx
   LLM_MODEL_NAME=gpt-4
   LLM_TEMPERATURE=0.7
   LLM_MAX_TOKENS=2000
   ```

### 6. 测试验证

#### 测试步骤

1. ✅ **首次配置**
   - 打开配置页面
   - 看到默认值（或环境变量的值）
   - 填写 API 配置
   - 保存配置

2. ✅ **刷新页面**
   - 按 F5 或 Ctrl+R 刷新
   - 自动加载之前的配置
   - API Key 显示为 `********`
   - 其他字段正确填充

3. ✅ **手动加载**
   - 修改表单内容（不保存）
   - 点击"🔄 加载配置"
   - 恢复到保存的配置

4. ✅ **修改配置**
   - 修改任意字段
   - 点击"💾 保存配置"
   - 刷新页面验证新配置已生效

## 修改文件

- `frontend/app.py`
  - 添加 `load_llm_config()` 函数（第454-497行）
  - 添加"🔄 加载配置"按钮
  - 添加按钮事件绑定
  - 添加页面加载时的自动调用

## 相关 API

- `GET /api/config/llm` - 获取 LLM 配置
- `POST /api/config/llm` - 保存 LLM 配置
- `POST /api/config/test-llm` - 测试 LLM 连接

## 注意事项

1. **API Key 占位符**：如果看到 `********`，说明已经配置了 API Key
2. **需要修改 API Key**：直接输入新的值，保存即可覆盖
3. **配置未生效**：点击"🔄 加载配置"手动刷新
4. **后端重启后**：需要重新配置（除非使用环境变量）

## 更新时间

2025-10-25
