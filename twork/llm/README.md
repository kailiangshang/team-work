# LLM 适配层

提供统一的大模型接口，支持OpenAI格式的API调用，包含单轮对话、多轮对话、格式化输出等功能。

## 模块结构

```
llm/
├── __init__.py          # 模块导出
├── config.py            # LLM配置数据类
├── base.py              # LLM适配器基类
└── openai_adapter.py    # OpenAI格式适配器实现
```

## 核心组件

### 1. LLMConfig (config.py)

配置数据类，用于管理LLM的所有配置参数。

**主要属性：**
- `api_base_url`: API基础URL
- `api_key`: API密钥
- `model_name`: 模型名称
- `temperature`: 温度参数（0-1）
- `max_tokens`: 最大token数
- `system_prompt`: 默认系统提示词
- `response_format`: 响应格式（JSON Schema）
- `enable_cache`: 是否启用缓存
- `cache_dir`: 缓存目录

**示例：**
```python
from twork.llm import LLMConfig

config = LLMConfig(
    api_base_url="https://api.openai.com/v1",
    api_key="your-api-key",
    model_name="gpt-4",
    temperature=0.7,
    max_tokens=2000,
    system_prompt="你是一个专业的助手",
    enable_cache=True,
    cache_dir="./llm_cache"
)
```

### 2. LLMAdapter (base.py)

LLM适配器基类，定义统一的接口。

**核心方法：**

#### `chat()` - 单轮对话
```python
response = llm.chat(
    user_prompt="写一首诗",
    system_prompt="你是一个诗人",  # 可选
    temperature=0.8,                # 可选
    use_history=False               # 是否使用对话历史
)
```

#### `chat_with_format()` - 格式化输出
```python
result = llm.chat_with_format(
    user_prompt="分析这段文本",
    system_prompt="你是分析专家",
    response_format={...}  # JSON Schema
)
# 返回解析后的dict对象
```

#### 多轮对话
```python
# 开始新对话
llm.start_conversation(system_prompt="你是客服机器人")

# 添加消息
llm.add_message("user", "你好")
llm.add_message("assistant", "您好，请问有什么可以帮您？")

# 继续对话（自动使用历史）
response = llm.chat(
    user_prompt="我想退货",
    use_history=True
)

# 获取历史
history = llm.get_history()

# 清空历史
llm.clear_history()
```

### 3. OpenAIAdapter (openai_adapter.py)

OpenAI格式的适配器实现。

**初始化：**
```python
from twork.llm import OpenAIAdapter, LLMConfig

config = LLMConfig(
    api_base_url="https://api.openai.com/v1",
    api_key="your-api-key",
    model_name="gpt-4"
)

llm = OpenAIAdapter(config)
```

**验证连接：**
```python
result = llm.validate_connection()
# 返回: {"success": True, "message": "连接成功", "latency_ms": 234}
```

## 使用示例

### 基础使用

```python
from twork.llm import OpenAIAdapter, LLMConfig

# 配置
config = LLMConfig(
    api_base_url="https://api.openai.com/v1",
    api_key="your-api-key",
    model_name="gpt-4",
    temperature=0.7
)

# 创建适配器
llm = OpenAIAdapter(config)

# 简单对话
response = llm.chat(user_prompt="介绍一下Python")
print(response)
```

### JSON格式化输出

```python
# 请求JSON格式的响应
result = llm.chat_with_format(
    user_prompt="分析这段代码的复杂度",
    system_prompt="你是代码分析专家，请用JSON格式返回分析结果"
)

print(result)  # 自动解析为dict
```

### 启用缓存

```python
config = LLMConfig(
    api_base_url="https://api.openai.com/v1",
    api_key="your-api-key",
    enable_cache=True,
    cache_dir="./cache"
)

llm = OpenAIAdapter(config)

# 第一次调用，会请求API
response1 = llm.chat(user_prompt="什么是AI?")

# 第二次调用相同内容，从缓存返回
response2 = llm.chat(user_prompt="什么是AI?")
```

### 多轮对话

```python
llm.start_conversation(system_prompt="你是Python专家")

# 第一轮
response1 = llm.chat(
    user_prompt="什么是装饰器？",
    use_history=True
)

# 第二轮（自动带上历史）
response2 = llm.chat(
    user_prompt="能举个例子吗？",
    use_history=True
)

# 查看完整对话历史
history = llm.get_history()
```

## 扩展新的LLM提供商

如需支持其他LLM提供商（如Claude、通义千问等），只需继承`LLMAdapter`并实现以下方法：

```python
from twork.llm import LLMAdapter

class CustomLLMAdapter(LLMAdapter):
    def __init__(self, config):
        super().__init__(config)
        # 初始化你的客户端
        self.client = YourLLMClient(...)
    
    def chat_completion(self, messages, temperature=None, 
                       max_tokens=None, response_format=None, **kwargs):
        """实现底层API调用"""
        # 调用你的API
        response = self.client.create_completion(...)
        
        # 转换为统一格式
        return {
            "choices": [...],
            "usage": {...}
        }
    
    def validate_connection(self):
        """实现连接验证"""
        # 测试连接
        return {"success": True, ...}
```

## 配置参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| api_base_url | str | - | API基础URL（必需） |
| api_key | str | - | API密钥（必需） |
| model_name | str | "gpt-4" | 模型名称 |
| temperature | float | 0.7 | 温度参数（0-1） |
| max_tokens | int | 2000 | 最大token数 |
| top_p | float | 1.0 | Top-p采样参数 |
| frequency_penalty | float | 0.0 | 频率惩罚 |
| presence_penalty | float | 0.0 | 存在惩罚 |
| timeout | int | 60 | 超时时间（秒） |
| max_retries | int | 3 | 最大重试次数 |
| retry_delay | float | 1.0 | 重试延迟（秒） |
| system_prompt | str | None | 默认系统提示词 |
| response_format | dict | None | 响应格式（JSON Schema） |
| enable_cache | bool | False | 是否启用缓存 |
| cache_dir | str | None | 缓存目录 |

## 最佳实践

1. **使用配置对象**：统一管理配置，便于维护和切换
2. **启用缓存**：对于重复的请求，缓存可以大幅提升性能
3. **合理设置温度**：分析类任务用低温度（0.1-0.3），创造类任务用高温度（0.7-0.9）
4. **多轮对话管理**：及时清理历史记录，避免token超限
5. **异常处理**：捕获并处理API调用异常

## 注意事项

- 缓存基于消息内容的MD5哈希，相同内容才会命中缓存
- 多轮对话的历史会累积，注意token限制
- `chat_with_format()`会自动清理markdown代码块标记
- 连接验证会发送一条测试消息，会消耗少量token
