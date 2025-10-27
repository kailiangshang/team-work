"""
BaseTool - 工具基类

所有工具的公共父类，提供统一的LLM调用能力。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
from ...llm.base import LLMAdapter


class BaseTool(ABC):
    """工具基类"""
    
    def __init__(self):
        """初始化工具"""
        self.config: Dict[str, Any] = {}
        self.name = self.__class__.__name__
        self.llm: Optional[LLMAdapter] = None
    
    def setup(self, config: Dict[str, Any]):
        """
        初始化配置
        
        Args:
            config: 配置字典，可能包含:
                - llm_adapter: LLM适配器实例
                - prompt_template: 提示词模板
                - model: 模型名称
                - temperature: 温度参数
                - ... 其他工具特定配置
        """
        self.config = config.copy()
        
        # 如果配置中包含LLM适配器，则使用它
        if "llm_adapter" in config:
            self.llm = config["llm_adapter"]
    
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """
        执行主逻辑，子类必须实现
        
        Args:
            input_data: 输入数据（格式由子类定义）
            
        Returns:
            执行结果（格式由子类定义）
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        返回元信息，用于快照记录
        
        Returns:
            元信息字典
        """
        return {
            "class": self.__class__.__name__,
            "config": self._serialize_config()
        }
    
    def _serialize_config(self) -> Dict[str, Any]:
        """
        序列化配置（排除不可序列化的对象如LLM适配器）
        
        Returns:
            可序列化的配置字典
        """
        serialized = {}
        for key, value in self.config.items():
            if key == "llm_adapter":
                # 不序列化LLM适配器对象本身
                continue
            try:
                json.dumps(value)  # 测试是否可序列化
                serialized[key] = value
            except (TypeError, ValueError):
                # 跳过不可序列化的值
                continue
        return serialized
    
    def llm_call(
        self,
        prompt: str,
        input_data: Any,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **extra_context
    ) -> Dict[str, Any]:
        """
        统一封装的LLM调用方法
        
        Args:
            prompt: 提示词模板
            input_data: 输入数据（任意结构）
            model: 模型名称（可选，默认使用配置中的）
            temperature: 温度参数（可选）
            response_format: 期望的JSON输出结构（可选）
            **extra_context: 额外的上下文参数（如domain_context等），会传递给提示词格式化
        
        Returns:
            LLM返回的结构化结果（dict）
        
        Raises:
            ValueError: 如果LLM适配器未配置
        """
        if not self.llm:
            raise ValueError(f"{self.name}: LLM适配器未配置，请在setup中提供llm_adapter")
        
        # 格式化输入数据为字符串
        if isinstance(input_data, dict) or isinstance(input_data, list):
            input_str = json.dumps(input_data, ensure_ascii=False, indent=2)
        else:
            input_str = str(input_data)
        
        # 合并配置和额外上下文
        format_kwargs = {**self.config, **extra_context}
        
        # 构建完整提示词
        full_prompt = prompt.format(input=input_str, **format_kwargs)
        
        # 调用LLM
        if response_format or self.config.get("response_format"):
            # 需要JSON格式输出
            return self.llm.chat_with_format(
                user_prompt=full_prompt,
                system_prompt=self.config.get("system_prompt"),
                response_format=response_format or self.config.get("response_format"),
                temperature=temperature or self.config.get("temperature")
            )
        else:
            # 普通文本输出
            content = self.llm.chat(
                user_prompt=full_prompt,
                system_prompt=self.config.get("system_prompt"),
                temperature=temperature or self.config.get("temperature")
            )
            return {"content": content}
