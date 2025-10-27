"""
LLM配置数据类

提供统一的LLM配置管理。
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class LLMConfig:
    """LLM配置数据类"""
    
    # 基础配置
    api_base_url: str
    api_key: str
    model_name: str = "gpt-4"
    
    # 生成参数
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    # 超时与重试
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # 系统提示词
    system_prompt: Optional[str] = None
    
    # 响应格式（JSON Schema）
    response_format: Optional[Dict[str, Any]] = None
    
    # 缓存配置
    enable_cache: bool = False
    cache_dir: Optional[str] = None
    
    # 其他参数
    extra_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "api_base_url": self.api_base_url,
            "api_key": self.api_key,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "system_prompt": self.system_prompt,
            "response_format": self.response_format,
            "enable_cache": self.enable_cache,
            "cache_dir": self.cache_dir,
            "extra_params": self.extra_params,
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "LLMConfig":
        """从字典创建配置对象"""
        return cls(**{k: v for k, v in config_dict.items() if k in cls.__dataclass_fields__})
    
    def copy(self) -> "LLMConfig":
        """创建配置副本"""
        return LLMConfig(
            api_base_url=self.api_base_url,
            api_key=self.api_key,
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            timeout=self.timeout,
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
            system_prompt=self.system_prompt,
            response_format=self.response_format,
            enable_cache=self.enable_cache,
            cache_dir=self.cache_dir,
            extra_params=self.extra_params.copy(),
        )
