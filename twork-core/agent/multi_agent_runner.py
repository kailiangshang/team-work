"""多Agent运行器 - 协调多个Agent进行项目模拟"""
from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime

from .base_agent import BaseAgent
from .task_agent import TaskAgent
from .environment_agent import EnvironmentAgent
from ..llm.base import BaseLLM
from ..schemas.graph import AgentNode, TaskNode
from ..schemas.simulation import SimulationState, SimulationLog

logger = logging.getLogger(__name__)


class MultiAgentRunner:
    """多Agent运行器
    
    协调多个Agent进行项目模拟：
    - 管理Agent池
    - 分配任务
    - 收集对话
    - 生成日志
    """
    
    def __init__(
        self,
        llm: BaseLLM,
        agents: List[TaskAgent] = None,
        environment_agent: EnvironmentAgent = None,
    ):
        self.llm = llm
        self.agents: Dict[str, TaskAgent] = {}
        self.environment_agent = environment_agent or EnvironmentAgent(llm)
        self.logs: List[SimulationLog] = []
        
        if agents:
            for agent in agents:
                self.agents[agent.id] = agent
    
    def add_agent(self, agent: TaskAgent):
        """添加Agent"""
        self.agents[agent.id] = agent
    
    def get_agent(self, agent_id: str) -> Optional[TaskAgent]:
        """获取Agent"""
        return self.agents.get(agent_id)
    
    async def run_discussion(
        self,
        task: TaskNode,
        agent_ids: List[str],
        rounds: int = 3,
    ) -> List[Dict[str, Any]]:
        """运行任务讨论
        
        Args:
            task: 任务节点
            agent_ids: 参与讨论的Agent ID列表
            rounds: 讨论轮数
        
        Returns:
            讨论记录列表
        """
        discussions = []
        context = {
            "current_task": task.to_dict(),
            "action_type": "discuss",
        }
        
        for round_num in range(rounds):
            for agent_id in agent_ids:
                agent = self.get_agent(agent_id)
                if not agent:
                    continue
                
                result = await agent.act(context)
                
                discussions.append({
                    "round": round_num + 1,
                    "agent_id": agent_id,
                    "agent_name": agent.name,
                    "response": result.get("response", ""),
                    "timestamp": datetime.now().isoformat(),
                })
                
                # 记录日志
                self._log(
                    agent_id=agent_id,
                    action="discuss",
                    content=result.get("response", ""),
                    metadata={"task_id": task.id, "round": round_num + 1},
                )
        
        return discussions
    
    async def run_time_estimation(
        self,
        task: TaskNode,
        agent_ids: List[str],
    ) -> Dict[str, Any]:
        """运行时间估算
        
        让多个Agent对任务进行时间估算
        """
        estimations = []
        context = {
            "current_task": task.to_dict(),
            "action_type": "estimate",
        }
        
        for agent_id in agent_ids:
            agent = self.get_agent(agent_id)
            if not agent:
                continue
            
            result = await agent.act(context)
            
            estimations.append({
                "agent_id": agent_id,
                "agent_name": agent.name,
                "estimation": result.get("estimation", ""),
            })
        
        # 汇总估算结果
        return {
            "task_id": task.id,
            "estimations": estimations,
            "consensus": self._calculate_consensus(estimations),
        }
    
    async def run_day_simulation(
        self,
        day: int,
        tasks: List[TaskNode],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """运行单日模拟
        
        Args:
            day: 当前天数
            tasks: 当日任务列表
            context: 模拟上下文
        
        Returns:
            当日模拟结果
        """
        daily_results = {
            "day": day,
            "agent_actions": [],
            "events": [],
            "completed_tasks": [],
        }
        
        # 1. 检查环境事件
        env_context = {
            **context,
            "current_day": day,
        }
        env_result = await self.environment_agent.act(env_context)
        
        if env_result.get("action") == "event":
            daily_results["events"].append(env_result["event"])
        
        # 2. 让每个Agent执行任务
        for agent_id, agent in self.agents.items():
            if agent.state.current_task_id:
                task = next((t for t in tasks if t.id == agent.state.current_task_id), None)
                if task:
                    action_result = await agent.act({
                        **context,
                        "current_task": task.to_dict(),
                        "action_type": "work",
                    })
                    daily_results["agent_actions"].append(action_result)
        
        return daily_results
    
    def assign_task(self, task_id: str, agent_id: str):
        """分配任务给Agent"""
        agent = self.get_agent(agent_id)
        if agent:
            agent.assign_task(task_id)
    
    def _calculate_consensus(self, estimations: List[Dict]) -> Dict[str, Any]:
        """计算估算共识"""
        if not estimations:
            return {"method": "none", "value": 0}
        
        # 简单取平均 - 实际应该更智能
        return {
            "method": "average",
            "estimation_count": len(estimations),
        }
    
    def _log(
        self,
        agent_id: str,
        action: str,
        content: str,
        metadata: Dict = None,
    ):
        """记录日志"""
        log = SimulationLog(
            agent_id=agent_id,
            action=action,
            content=content,
            metadata=metadata or {},
        )
        self.logs.append(log)
    
    def get_logs(self, agent_id: str = None) -> List[SimulationLog]:
        """获取日志"""
        if agent_id:
            return [log for log in self.logs if log.agent_id == agent_id]
        return self.logs