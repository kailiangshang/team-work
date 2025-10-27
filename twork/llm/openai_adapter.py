"""
OpenAI格式适配器

提供OpenAI API格式的大模型调用接口。
"""

import time
from typing import List, Dict, Any, Optional, Union
from openai import OpenAI
from .base import LLMAdapter
from .config import LLMConfig
from ..utils.logger import get_logger

logger = get_logger("openai_adapter")


class OpenAIAdapter(LLMAdapter):
    """OpenAI格式适配器"""
    
    def __init__(self, config: Union[LLMConfig, Dict[str, Any]]):
        """初始化OpenAI适配器"""
        super().__init__(config)
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.api_base_url,
            timeout=self.config.timeout,
        )
        
        logger.info(f"OpenAI适配器初始化完成: model={self.config.model_name}, base_url={self.config.api_base_url}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        调用聊天补全API
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式
            **kwargs: 其他参数
            
        Returns:
            API响应结果
        """
        temp = temperature if temperature is not None else self.config.temperature
        tokens = max_tokens if max_tokens is not None else self.config.max_tokens
        
        # 检查缓存
        cache_key = None
        if self.config.enable_cache:
            cache_key = self._generate_cache_key(messages, temperature=temp, max_tokens=tokens)
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.debug("From cache")
                return cached_result
        
        try:
            logger.debug(f"发送聊天请求: messages={len(messages)}, temp={temp}, max_tokens={tokens}")
            
            # 构建请求参数
            request_params = {
                "model": self.config.model_name,
                "messages": messages,
                "temperature": temp,
                "max_tokens": tokens,
                **kwargs
            }
            
            # 添加响应格式
            if response_format:
                request_params["response_format"] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(**request_params)
            
            # 转换为字典格式
            result = {
                "choices": [
                    {
                        "message": {
                            "role": choice.message.role,
                            "content": choice.message.content,
                        },
                        "finish_reason": choice.finish_reason,
                    }
                    for choice in response.choices
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                } if response.usage else None,
            }
            
            # 保存到缓存
            if cache_key:
                self._save_to_cache(cache_key, result)
            
            logger.debug(f"收到响应: tokens={result.get('usage', {}).get('total_tokens', 0)}")
            return result
            
        except Exception as e:
            logger.error(f"聊天请求失败: {str(e)}")
            raise
    
    def validate_connection(self) -> Dict[str, Any]:
        """
        验证连接
        
        Returns:
            连接验证结果
        """
        try:
            start_time = time.time()
            
            # 发送测试请求
            response = self.chat_completion(
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"连接验证成功: latency={latency_ms}ms")
            
            return {
                "success": True,
                "message": "连接成功",
                "latency_ms": latency_ms,
                "model_info": {
                    "model_name": self.config.model_name,
                    "api_base_url": self.config.api_base_url,
                }
            }
            
        except Exception as e:
            logger.error(f"连接验证失败: {str(e)}")
            return {
                "success": False,
                "message": f"连接失败: {str(e)}",
                "latency_ms": 0,
                "model_info": None
            }
