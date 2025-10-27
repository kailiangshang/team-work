"""
BaseExtractor - 提取器基类

所有提取器的公共父类，提供统一的提取接口。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseExtractor(ABC):
    """提取器基类"""
    
    def __init__(self):
        """初始化提取器"""
        self.name = self.__class__.__name__
    
    @abstractmethod
    def extract(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行提取逻辑，子类必须实现
        
        Args:
            input_data: 输入数据（格式由子类定义）
            
        Returns:
            提取结果（格式由子类定义）
        """
        pass
    
    def validate(self, result: Dict[str, Any]) -> bool:
        """
        验证提取结果
        
        Args:
            result: 提取结果
            
        Returns:
            是否通过验证
        """
        return True
    
    def _generate_id(self, prefix: str, index: int) -> str:
        """
        生成实体或关系的唯一ID
        
        Args:
            prefix: ID前缀
            index: 索引编号
            
        Returns:
            唯一ID字符串
        """
        return f"{prefix}-{index:03d}"
