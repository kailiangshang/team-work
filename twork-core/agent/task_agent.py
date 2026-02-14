"""任务Agent - 负责任务讨论和时间估算"""
from typing import Dict, Any, List
import logging

from .base_agent import BaseAgent, AgentState
from ..llm.base import BaseLLM, ChatMessage
from ..llm.prompts import PromptTemplates
from ..schemas.graph import AgentNode

logger = logging.getLogger(__name__)


class TaskAgent(BaseAgent):
    """任务Agent
    
    负责任务讨论、时间估算、协作等
    """
    
    def __init__(
        self,
        agent_node: AgentNode,
        llm: BaseLLM,
        communication_style: str = "professional",
    ):
        super().__init__(agent_node, llm)
        self.communication_style = communication_style
    
    async def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行动作
        
        根据当前上下文决定行为：
        - 如果有当前任务，进行任务相关工作
        - 否则等待分配
        """
        if not self.state.current_task_id:
            return {
                "action": "idle",
                "message": f"{self.name} 当前没有分配任务，等待工作分配。",
            }
        
        # 获取任务信息
        task = context.get("current_task")
        if not task:
            return {
                "action": "waiting",
                "message": f"{self.name} 正在等待任务详情。",
            }
        
        # 执行任务相关工作
        action_type = context.get("action_type", "work")
        
        if action_type == "discuss":
            return await self._discuss_task(task, context)
        elif action_type == "estimate":
            return await self._estimate_task(task, context)
        else:
            return await self._work_on_task(task, context)
    
    async def respond(self, message: str, context: Dict[str, Any]) -> str:
        """响应消息"""
        # 构建系统提示词
        system_prompt = PromptTemplates.get_agent_system_prompt(
            agent_name=self.name,
            role_type=self.role_type,
            personality=self.node.personality,
            skills=", ".join(self.node.capabilities),
            communication_style=self.communication_style,
            current_tasks=self._get_current_tasks_description(context),
        )
        
        # 构建对话历史
        history = []
        for msg in self.get_recent_messages(5):
            history.append(ChatMessage(
                role=msg["role"],
                content=msg["content"]
            ))
        
        # 添加新消息
        history.append(ChatMessage(role="user", content=message))
        
        # 调用LLM
        response = await self.llm.achat([
            ChatMessage(role="system", content=system_prompt),
            *history
        ])
        
        # 记录消息
        self.add_message("user", message)
        self.add_message("assistant", response.content)
        
        return response.content
    
    async def _discuss_task(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """讨论任务"""
        prompt = PromptTemplates.AGENT_TASK_DISCUSSION.format(
            task_name=task.get("name", ""),
            task_description=task.get("description", ""),
            estimated_hours=task.get("estimated_hours", 8),
            required_skills=", ".join(task.get("required_skills", [])),
        )
        
        response = await self.respond(prompt, context)
        
        return {
            "action": "discuss",
            "task_id": task.get("id"),
            "agent_id": self.id,
            "response": response,
        }
    
    async def _estimate_task(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """估算任务时间"""
        prompt = PromptTemplates.AGENT_TIME_ESTIMATION.format(
            task_name=task.get("name", ""),
            task_description=task.get("description", ""),
            complexity=task.get("complexity", 5),
        )
        
        response = await self.respond(prompt, context)
        
        return {
            "action": "estimate",
            "task_id": task.get("id"),
            "agent_id": self.id,
            "estimation": response,
        }
    
    async def _work_on_task(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        # 更新工作负载
        self.state.workload = min(100, self.state.workload + 10)
        self.state.energy = max(0, self.state.energy - 5)
        
        return {
            "action": "work",
            "task_id": task.get("id"),
            "agent_id": self.id,
            "progress": context.get("progress", 0) + 10,
            "energy": self.state.energy,
            "workload": self.state.workload,
        }
    
    def _get_current_tasks_description(self, context: Dict[str, Any]) -> str:
        """获取当前任务描述"""
        tasks = []
        
        if self.state.current_task_id:
            task = context.get("current_task", {})
            tasks.append(f"- 当前任务: {task.get('name', self.state.current_task_id)}")
        
        for task_id in self.node.assigned_tasks:
            if task_id != self.state.current_task_id:
                tasks.append(f"- 分配任务: {task_id}")
        
        return "\n".join(tasks) if tasks else "暂无分配任务"