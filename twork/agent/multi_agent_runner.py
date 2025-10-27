"""
多Agent运行器

协调多个Agent的运行。
"""

from typing import Dict, Any, List
from ..utils.logger import get_logger

logger = get_logger("multi_agent_runner")


class MultiAgentRunner:
    """多Agent运行器"""
    
    def __init__(self):
        """初始化多Agent运行器"""
        self.agents = []
        logger.info("多Agent运行器初始化完成")
    
    def load_agents(self, agents: List[Dict[str, Any]]) -> None:
        """
        加载Agent配置
        
        Args:
            agents: Agent配置列表
        """
        self.agents = agents
        logger.info(f"加载了{len(agents)}个Agent")
    
    def get_agent_by_id(self, agent_id: str) -> Dict[str, Any]:
        """
        根据ID获取Agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent配置字典
        """
        for agent in self.agents:
            if agent["agent_id"] == agent_id:
                return agent
        return None
    
    def get_agents_by_role_type(self, role_type: str) -> List[Dict[str, Any]]:
        """
        根据角色类型获取Agent列表
        
        Args:
            role_type: 角色类型
            
        Returns:
            Agent配置列表
        """
        return [
            agent for agent in self.agents
            if agent.get("role_type") == role_type
        ]
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """
        获取所有Agent
        
        Returns:
            所有Agent配置列表
        """
        return self.agents
