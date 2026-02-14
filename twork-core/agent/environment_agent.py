"""环境Agent - 模拟项目环境中的随机事件"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import random
import logging
from datetime import datetime

from .base_agent import BaseAgent
from ..llm.base import BaseLLM, ChatMessage
from ..llm.prompts import PromptTemplates
from ..schemas.graph import AgentNode

logger = logging.getLogger(__name__)


@dataclass
class EnvironmentEvent:
    """环境事件"""
    event_type: str                           # 事件类型
    description: str                          # 事件描述
    impact_level: str = "medium"              # 影响级别: low/medium/high
    affected_tasks: List[str] = field(default_factory=list)      # 受影响的任务
    affected_agents: List[str] = field(default_factory=list)     # 受影响的Agent
    suggested_actions: List[str] = field(default_factory=list)   # 建议行动
    timestamp: datetime = field(default_factory=datetime.now)


class EnvironmentAgent(BaseAgent):
    """环境Agent
    
    负责模拟项目环境中的随机事件：
    - 需求变更
    - 资源变动
    - 技术问题
    - 外部因素
    """
    
    EVENT_TYPES = [
        "requirement_change",    # 需求变更
        "resource_change",       # 资源变动
        "technical_issue",       # 技术问题
        "external_factor",       # 外部因素
    ]
    
    def __init__(
        self,
        llm: BaseLLM,
        event_probability: float = 0.2,
    ):
        # 创建虚拟的AgentNode
        node = AgentNode(
            id="ENV",
            name="环境模拟器",
            role_type="environment",
            personality="客观、专业",
            capabilities=[{"name": "事件生成"}, {"name": "风险分析"}],
            tools=[],
        )
        super().__init__(node, llm)
        self.event_probability = event_probability
        self.generated_events: List[EnvironmentEvent] = []
    
    async def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行动作 - 可能生成环境事件"""
        current_day = context.get("current_day", 1)
        total_days = context.get("total_days", 30)
        
        # 判断是否生成事件
        if not self._should_generate_event(current_day, total_days):
            return {
                "action": "no_event",
                "message": "今日无特殊事件",
            }
        
        # 生成事件
        event = await self._generate_event(context)
        
        if event:
            self.generated_events.append(event)
            return {
                "action": "event",
                "event": {
                    "event_type": event.event_type,
                    "description": event.description,
                    "impact_level": event.impact_level,
                    "affected_tasks": event.affected_tasks,
                    "affected_agents": event.affected_agents,
                    "suggested_actions": event.suggested_actions,
                },
            }
        
        return {"action": "no_event"}
    
    async def respond(self, message: str, context: Dict[str, Any]) -> str:
        """响应消息"""
        messages = [
            ChatMessage(role="system", content=PromptTemplates.ENV_AGENT_SYSTEM),
            ChatMessage(role="user", content=message),
        ]
        
        response = await self.llm.achat(messages)
        return response.content
    
    def _should_generate_event(self, current_day: int, total_days: int) -> bool:
        """判断是否应该生成事件"""
        # 基础概率
        prob = self.event_probability
        
        # 项目中期风险更高
        progress = current_day / total_days
        if 0.3 <= progress <= 0.6:
            prob *= 1.5
        
        return random.random() < prob
    
    async def _generate_event(self, context: Dict[str, Any]) -> Optional[EnvironmentEvent]:
        """生成环境事件"""
        prompt = PromptTemplates.ENV_EVENT_TEMPLATE.format(
            current_day=context.get("current_day", 1),
            total_days=context.get("total_days", 30),
            completed_tasks=context.get("completed_tasks", []),
            in_progress_tasks=context.get("in_progress_tasks", []),
            event_probability=self.event_probability,
        )
        
        response = await self.respond(prompt, context)
        
        # 解析响应
        event = self._parse_event_response(response, context)
        return event
    
    def _parse_event_response(self, response: str, context: Dict[str, Any]) -> Optional[EnvironmentEvent]:
        """解析事件响应"""
        # 简单解析 - 实际应该更智能
        lines = response.strip().split("\n")
        
        if not lines or "无事件" in response or "正常" in response:
            return None
        
        # 随机选择事件类型
        event_type = random.choice(self.EVENT_TYPES)
        
        return EnvironmentEvent(
            event_type=event_type,
            description=response[:200],
            impact_level=random.choice(["low", "medium", "high"]),
            affected_tasks=context.get("in_progress_tasks", [])[:1],
            affected_agents=[],
            suggested_actions=["评估影响", "调整计划"],
        )