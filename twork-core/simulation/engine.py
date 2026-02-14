"""模拟引擎 - 核心模拟逻辑"""
from typing import Dict, Any, List, Optional, Callable
import asyncio
import logging
from datetime import datetime

from ..llm.base import BaseLLM
from ..schemas.graph import TaskNode, AgentNode, KnowledgeGraph
from ..schemas.simulation import (
    SimulationConfig, SimulationResult, SimulationStatus,
    DailySimulationResult, TaskGroup, DialogueLog, TaskAssignment,
    TimeEstimate, DailySchedule
)
from ..agent.task_agent import TaskAgent
from ..agent.environment_agent import EnvironmentAgent
from ..agent.multi_agent_runner import MultiAgentRunner
from ..graph.graph_store import GraphStore

logger = logging.getLogger(__name__)


class SimulationEngine:
    """模拟引擎
    
    核心功能：
    1. 基于知识图谱运行项目模拟
    2. 多Agent协作
    3. 时间估算与调度
    4. 环境事件模拟
    """
    
    def __init__(
        self,
        llm: BaseLLM,
        graph_store: GraphStore,
        config: SimulationConfig = None,
    ):
        self.llm = llm
        self.graph_store = graph_store
        self.config = config or SimulationConfig()
        
        self.runner: Optional[MultiAgentRunner] = None
        self.result: Optional[SimulationResult] = None
        self._on_progress: Optional[Callable] = None
    
    def set_progress_callback(self, callback: Callable):
        """设置进度回调"""
        self._on_progress = callback
    
    async def run(
        self,
        project_id: str,
        graph: KnowledgeGraph,
    ) -> SimulationResult:
        """运行模拟
        
        Args:
            project_id: 项目ID
            graph: 知识图谱
        
        Returns:
            模拟结果
        """
        # 初始化结果
        self.result = SimulationResult(
            project_id=project_id,
            config=self.config,
            status=SimulationStatus.RUNNING,
            started_at=datetime.now().isoformat(),
        )
        
        try:
            # 1. 初始化Agent
            await self._initialize_agents(graph)
            
            # 2. 按天运行模拟
            for day in range(1, self.config.total_days + 1):
                if self.result.status == SimulationStatus.PAUSED:
                    break
                
                daily_result = await self._run_day(day, graph)
                self.result.daily_results.append(daily_result)
                self.result.current_day = day
                
                # 回调进度
                if self._on_progress:
                    self._on_progress(day, self.config.total_days, daily_result)
            
            self.result.status = SimulationStatus.COMPLETED
            self.result.completed_at = datetime.now().isoformat()
        
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            self.result.status = SimulationStatus.FAILED
            self.result.error_message = str(e)
        
        return self.result
    
    async def _initialize_agents(self, graph: KnowledgeGraph):
        """初始化Agent"""
        agents = []
        
        for node in graph.nodes:
            if isinstance(node, AgentNode):
                agent = TaskAgent(
                    agent_node=node,
                    llm=self.llm,
                )
                agents.append(agent)
        
        self.runner = MultiAgentRunner(
            llm=self.llm,
            agents=agents,
        )
    
    async def _run_day(
        self,
        day: int,
        graph: KnowledgeGraph,
    ) -> DailySimulationResult:
        """运行单日模拟"""
        result = DailySimulationResult(day=day)
        
        # 1. 获取当日可执行的任务
        executable_tasks = self._get_executable_tasks(day, graph)
        
        # 2. 分组任务
        task_groups = self._group_tasks(executable_tasks, graph)
        result.task_groups = task_groups
        
        # 3. 为每个任务组运行讨论
        for group in task_groups:
            dialogue = await self._run_group_discussion(group, day, graph)
            result.dialogue_logs.append(dialogue)
        
        # 4. 环境事件
        if self.config.enable_env_agent:
            events = await self._check_environment_events(day, result)
            result.env_events = events
        
        # 5. 更新任务状态
        for group in task_groups:
            for task_id in group.task_ids:
                # 模拟任务完成
                result.completed_tasks.append(task_id)
        
        return result
    
    def _get_executable_tasks(self, day: int, graph: KnowledgeGraph) -> List[TaskNode]:
        """获取当日可执行的任务"""
        tasks = []
        
        for node in graph.nodes:
            if isinstance(node, TaskNode):
                # 简单逻辑：按任务的开始时间判断
                # 实际应该基于依赖关系
                if node.level == 1:  # 顶层任务
                    tasks.append(node)
        
        return tasks
    
    def _group_tasks(
        self,
        tasks: List[TaskNode],
        graph: KnowledgeGraph,
    ) -> List[TaskGroup]:
        """任务分组"""
        groups = []
        
        # 简单分组：每个任务一个组
        for i, task in enumerate(tasks):
            group = TaskGroup(
                group_id=f"G{day:02d}-{i+1:02d}",
                task_ids=[task.id],
                required_skills=task.required_skills,
            )
            groups.append(group)
        
        return groups
    
    async def _run_group_discussion(
        self,
        group: TaskGroup,
        day: int,
        graph: KnowledgeGraph,
    ) -> DialogueLog:
        """运行任务组讨论"""
        dialogue = DialogueLog(
            group_id=group.group_id,
            day=day,
        )
        
        # 获取参与讨论的Agent
        agent_ids = group.assigned_agents or list(self.runner.agents.keys())[:3]
        dialogue.participants = agent_ids
        
        # 获取任务
        task_id = group.task_ids[0] if group.task_ids else None
        if not task_id:
            return dialogue
        
        task = graph.get_task(task_id)
        if not task:
            return dialogue
        
        # 运行讨论
        discussions = await self.runner.run_discussion(
            task=task,
            agent_ids=agent_ids,
            rounds=2,
        )
        
        for d in discussions:
            dialogue.add_message(d["agent_id"], d["response"])
        
        return dialogue
    
    async def _check_environment_events(
        self,
        day: int,
        daily_result: DailySimulationResult,
    ) -> List[Dict[str, Any]]:
        """检查环境事件"""
        context = {
            "current_day": day,
            "total_days": self.config.total_days,
            "completed_tasks": daily_result.completed_tasks,
            "in_progress_tasks": [],
        }
        
        result = await self.runner.environment_agent.act(context)
        
        if result.get("action") == "event":
            return [result["event"]]
        
        return []
    
    def pause(self):
        """暂停模拟"""
        if self.result:
            self.result.status = SimulationStatus.PAUSED
    
    def resume(self):
        """恢复模拟"""
        if self.result:
            self.result.status = SimulationStatus.RUNNING
    
    def get_status(self) -> Dict[str, Any]:
        """获取模拟状态"""
        if not self.result:
            return {"status": "not_started"}
        
        return {
            "status": self.result.status.value,
            "current_day": self.result.current_day,
            "total_days": self.config.total_days,
            "progress": self.result.current_day / self.config.total_days if self.config.total_days > 0 else 0,
        }