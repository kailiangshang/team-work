"""OpenAI 适配器"""
import time
import asyncio
from typing import List, AsyncIterator
import logging

from .base import BaseLLM, LLMConfig, LLMResponse, ChatMessage

logger = logging.getLogger(__name__)


class OpenAIAdapter(BaseLLM):
    """OpenAI 适配器
    
    支持 OpenAI API 和兼容的 API（如 Azure OpenAI、本地模型）
    """
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self._client = None
    
    def _get_client(self):
        """获取 OpenAI 客户端（延迟初始化）"""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.config.api_key,
                    base_url=self.config.api_base or None,
                    timeout=self.config.timeout,
                )
            except ImportError:
                raise ImportError("Please install openai: pip install openai")
        return self._client
    
    def chat(self, messages: List[ChatMessage], **kwargs) -> LLMResponse:
        """同步对话"""
        client = self._get_client()
        
        start_time = time.time()
        
        response = client.chat.completions.create(
            model=kwargs.get("model", self.config.model),
            messages=[m.to_dict() for m in messages],
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
        )
        
        latency = time.time() - start_time
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
            },
            finish_reason=response.choices[0].finish_reason,
            latency=latency,
        )
    
    async def achat(self, messages: List[ChatMessage], **kwargs) -> LLMResponse:
        """异步对话"""
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.api_base or None,
            timeout=self.config.timeout,
        )
        
        start_time = time.time()
        
        response = await client.chat.completions.create(
            model=kwargs.get("model", self.config.model),
            messages=[m.to_dict() for m in messages],
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
        )
        
        latency = time.time() - start_time
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
            },
            finish_reason=response.choices[0].finish_reason,
            latency=latency,
        )
    
    async def astream(self, messages: List[ChatMessage], **kwargs) -> AsyncIterator[str]:
        """流式对话"""
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.api_base or None,
            timeout=self.config.timeout,
        )
        
        stream = await client.chat.completions.create(
            model=kwargs.get("model", self.config.model),
            messages=[m.to_dict() for m in messages],
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            stream=True,
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content