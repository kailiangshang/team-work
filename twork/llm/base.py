"""
LLM基础适配器接口

定义统一的大模型调用接口，支持单轮对话、多轮对话、格式化输出等功能。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
import json
import hashlib
import time
from pathlib import Path
from .config import LLMConfig


class LLMAdapter(ABC):
    """LLM适配器基类"""
    
    def __init__(self, config: Union[LLMConfig, Dict[str, Any]]):
        """
        初始化LLM适配器
        
        Args:
            config: LLM配置对象或配置字典
        """
        if isinstance(config, dict):
            self.config = LLMConfig.from_dict(config)
        else:
            self.config = config
        
        # 历史消息（用于多轮对话）
        self.conversation_history: List[Dict[str, str]] = []
        
        # 缓存
        self._cache: Dict[str, Any] = {}
        if self.config.enable_cache and self.config.cache_dir:
            self._cache_dir = Path(self.config.cache_dir)
            self._cache_dir.mkdir(parents=True, exist_ok=True)
    
    def chat(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        use_history: bool = False,
        **kwargs
    ) -> str:
        """
        单轮对话接口（高级封装）
        
        Args:
            user_prompt: 用户提示词
            system_prompt: 系统提示词（如果为None则使用配置中的）
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式（JSON Schema）
            use_history: 是否使用对话历史
            **kwargs: 其他参数
            
        Returns:
            模型响应内容（字符串）
        """
        # 构建消息列表
        messages = []
        
        # 添加系统提示词
        sys_prompt = system_prompt or self.config.system_prompt
        if sys_prompt:
            messages.append({"role": "system", "content": sys_prompt})
        
        # 添加历史对话
        if use_history:
            messages.extend(self.conversation_history)
        
        # 添加用户消息
        messages.append({"role": "user", "content": user_prompt})
        
        # 调用底层接口
        response = self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
            **kwargs
        )
        
        # 提取响应内容
        content = response["choices"][0]["message"]["content"]
        
        # 更新对话历史
        if use_history:
            self.conversation_history.append({"role": "user", "content": user_prompt})
            self.conversation_history.append({"role": "assistant", "content": content})
        
        return content
    
    def chat_with_format(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        格式化输出的对话接口（返回JSON对象）
        
        Args:
            user_prompt: 用户提示词
            system_prompt: 系统提示词
            response_format: 响应格式（JSON Schema）
            **kwargs: 其他参数
            
        Returns:
            解析后的JSON对象
        """
        content = self.chat(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            response_format=response_format,
            temperature=0.3,  # 使用较低温度以获得更稳定的JSON输出
            **kwargs
        )
        
        # 清理可能的markdown代码块标记
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        # 解析JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM返回的内容无法解析为JSON: {e}\nContent: {content}")
    
    def start_conversation(self, system_prompt: Optional[str] = None):
        """
        开始新的多轮对话
        
        Args:
            system_prompt: 系统提示词
        """
        self.conversation_history = []
        if system_prompt:
            self.conversation_history.append({"role": "system", "content": system_prompt})
    
    def add_message(self, role: str, content: str):
        """
        添加消息到对话历史
        
        Args:
            role: 角色（user/assistant/system）
            content: 消息内容
        """
        self.conversation_history.append({"role": role, "content": content})
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        获取对话历史
        
        Returns:
            对话历史列表
        """
        return self.conversation_history.copy()
    
    def clear_history(self):
        """清除对话历史"""
        self.conversation_history = []
    
    def _generate_cache_key(self, messages: List[Dict[str, str]], **params) -> str:
        """
        生成缓存键
        
        Args:
            messages: 消息列表
            **params: 其他参数
            
        Returns:
            缓存键（MD5哈希）
        """
        cache_data = {
            "messages": messages,
            "model": self.config.model_name,
            **params
        }
        cache_str = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        从缓存获取结果
        
        Args:
            cache_key: 缓存键
            
        Returns:
            缓存的结果，如果不存在则返回None
        """
        if not self.config.enable_cache:
            return None
        
        # 内存缓存
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # 文件缓存
        if self.config.cache_dir:
            cache_file = self._cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._cache[cache_key] = data
                    return data
        
        return None
    
    def _save_to_cache(self, cache_key: str, result: Dict[str, Any]):
        """
        保存结果到缓存
        
        Args:
            cache_key: 缓存键
            result: 结果数据
        """
        if not self.config.enable_cache:
            return
        
        # 内存缓存
        self._cache[cache_key] = result
        
        # 文件缓存
        if self.config.cache_dir:
            cache_file = self._cache_dir / f"{cache_key}.json"
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
    
    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        聊天补全接口（底层实现）
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            temperature: 温度参数，如果为None则使用配置中的值
            max_tokens: 最大token数，如果为None则使用配置中的值
            response_format: 响应格式（JSON Schema）
            **kwargs: 其他参数
            
        Returns:
            返回格式:
            {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "..."
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 200,
                    "total_tokens": 300
                }
            }
        """
        pass
    
    @abstractmethod
    def validate_connection(self) -> Dict[str, Any]:
        """
        验证连接
        
        Returns:
            {
                "success": bool,
                "message": str,
                "latency_ms": int,
                "model_info": dict
            }
        """
        pass
