"""LLM 基类和配置"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, AsyncIterator
from enum import Enum


class LLMProvider(Enum):
    """LLM 提供商"""
    OPENAI = "openai"
    AZURE = "azure"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


@dataclass
class LLMConfig:
    """LLM 配置"""
    provider: LLMProvider = LLMProvider.OPENAI
    api_key: str = ""
    api_base: str = ""                   # API 基础 URL
    model: str = "gpt-4o-mini"           # 模型名称
    temperature: float = 0.7             # 温度参数
    max_tokens: int = 4096               # 最大 token 数
    timeout: int = 60                    # 超时时间（秒）
    retry_count: int = 3                 # 重试次数
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider.value,
            "api_key": "***" if self.api_key else "",
            "api_base": self.api_base,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
        }


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str                         # 响应内容
    model: str = ""                      # 使用的模型
    usage: Dict[str, int] = field(default_factory=dict)  # token 使用量
    finish_reason: str = ""              # 结束原因
    latency: float = 0.0                 # 响应延迟（秒）
    
    @property
    def prompt_tokens(self) -> int:
        return self.usage.get("prompt_tokens", 0)
    
    @property
    def completion_tokens(self) -> int:
        return self.usage.get("completion_tokens", 0)
    
    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass
class ChatMessage:
    """对话消息"""
    role: str                            # system/user/assistant
    content: str
    
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


class BaseLLM(ABC):
    """LLM 基类"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
    
    @abstractmethod
    def chat(
        self,
        messages: List[ChatMessage],
        **kwargs
    ) -> LLMResponse:
        """同步对话
        
        Args:
            messages: 对话消息列表
            **kwargs: 额外参数
        
        Returns:
            LLM 响应
        """
        pass
    
    @abstractmethod
    async def achat(
        self,
        messages: List[ChatMessage],
        **kwargs
    ) -> LLMResponse:
        """异步对话"""
        pass
    
    @abstractmethod
    async def astream(
        self,
        messages: List[ChatMessage],
        **kwargs
    ) -> AsyncIterator[str]:
        """流式对话"""
        pass
    
    def simple_chat(
        self,
        system_prompt: str,
        user_message: str,
        **kwargs
    ) -> LLMResponse:
        """简单对话（单轮）"""
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_message),
        ]
        return self.chat(messages, **kwargs)
    
    async def asimple_chat(
        self,
        system_prompt: str,
        user_message: str,
        **kwargs
    ) -> LLMResponse:
        """简单异步对话"""
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_message),
        ]
        return await self.achat(messages, **kwargs)
    
    def _build_messages(
        self,
        system_prompt: Optional[str] = None,
        user_message: str = "",
        history: Optional[List[ChatMessage]] = None,
    ) -> List[ChatMessage]:
        """构建消息列表"""
        messages = []
        
        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))
        
        if history:
            messages.extend(history)
        
        if user_message:
            messages.append(ChatMessage(role="user", content=user_message))
        
        return messages