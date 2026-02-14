"""LLM 模块 - 大语言模型适配层"""
from .base import BaseLLM, LLMConfig, LLMResponse
from .openai_adapter import OpenAIAdapter
from .prompts import PromptTemplates

__all__ = ["BaseLLM", "LLMConfig", "LLMResponse", "OpenAIAdapter", "PromptTemplates"]