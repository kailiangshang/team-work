"""
LLM适配层

提供统一的大模型接口，支持OpenAI格式的API调用。
"""

from .config import LLMConfig
from .base import LLMAdapter
from .openai_adapter import OpenAIAdapter

__all__ = ["LLMConfig", "LLMAdapter", "OpenAIAdapter"]
