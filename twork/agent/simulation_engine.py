"""
模拟引擎

负责按日模拟任务执行过程。
支持模拟元信息应用,实现可编辑性设计。
"""

from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import json
from ..llm.base import LLMAdapter
from ..utils.logger import get_logger
from .environment_agent import EnvironmentAgent
from .daily_summary import DailySummaryAgent
from .simulation_metadata import (
    SimulationMetadata,
    apply_metadata_to_agents,
    apply_metadata_to_tasks,
    apply_manual_assignments
)

logger = get_logger("simulation_engine")


class SimulationEngine:
    """模拟引擎"""
    
    SIMULATION_PROMPT = """你正在模拟一个真实的项目执行过程。

当前日期: 第{day_number}天
当前角色: {role_name} ({role_type})
角色能力: {capabilities}
角色性格: {personality}

今日分配任务:
{today_tasks}

项目进度上下文:
{context}

请模拟这个角色在今天的工作情况，输出JSON格式:
{{
    "completed_tasks": [
        {{
            "task_id": "T001",
            "start_time": "09:00",
            "end_time": "12:00",
            "output": "产出物描述",
            "status": "completed/in_progress",
            "progress_percentage": 100
        }}
    ],
    "discussions": [
        {{
            "time": "10:30",
            "with_role": "开发工程师",
            "topic": "讨论主题",
            "content": "讨论内容"
        }}
    ],
    "notes": "今日工作总结"
}}

要求:
1. 工作时间通常是09:00-18:00
2. 根据任务工期合理分配时间
3. 模拟真实的角色间协作讨论
4. 只输出JSON格式
"""
    
    def __init__(self, llm_adapter: LLMAdapter):
        """
        初始化模拟引擎
        
        Args:
            llm_adapter: LLM适配器实例
        """
        self.llm = llm_adapter
        self.simulation_logs = []
        self.env_agent = EnvironmentAgent()  # 初始化环境Agent
        self.daily_summary_agent = DailySummaryAgent()  # 初始化每日摘要Agent
        logger.info("模拟引擎初始化完成")
    
    def simulate(
        self,
        agents: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]],
        total_days: int,
        enable_env_agent: bool = True,
        env_event_probability: float = 0.2
    ) -> Dict[str, Any]:
        """
        模拟项目执行
        
        Args:
            agents: 角色配置列表
            tasks: 任务列表
            total_days: 总工期
            enable_env_agent: 是否启用环境Agent
            env_event_probability: 环境事件发生概率
            
        Returns:
            包含模拟日志和环境事件的字典
        """
        logger.info(f"开始模拟项目执行: 角色数={len(agents)}, 任务数={len(tasks)}, 总工期={total_days}天, 环境Agent={'启用' if enable_env_agent else '禁用'}")
        
        self.simulation_logs = []
        detailed_logs = []  # 详细日志（包含每一条对话和事件）
        env_events = []  # 环境事件
        task_status = {task["task_id"]: {"status": "pending", "progress": 0} for task in tasks}
        
        # 按依赖关系排序任务
        sorted_tasks = self._topological_sort(tasks)
        
        for day in range(1, total_days + 1):
            logger.info(f"模拟第{day}天")
            
            # 获取当天可执行的任务
            available_tasks = self._get_available_tasks(sorted_tasks, task_status)
            
            if not available_tasks:
                logger.info(f"第{day}天没有可执行的任务")
                continue
            
            # 注入环境事件
            if enable_env_agent:
                day_env_events = self.env_agent.inject_events(
                    day=day,
                    tasks=available_tasks,
                    probability=env_event_probability
                )
                if day_env_events:
                    env_events.extend(day_env_events)
                    # 添加到详细日志
                    for event in day_env_events:
                        detailed_logs.append({
                            "timestamp": event["timestamp"],
                            "day": day,
                            "event_type": "env_event",
                            "role_name": "环境因素",
                            "task_id": None,
                            "task_name": None,
                            "content": event["content"],
                            "status": None,
                            "progress_percentage": None,
                            "metadata": event
                        })
                    logger.info(f"第{day}天发生{len(day_env_events)}个环境事件")
            
            # 为每个角色分配任务
            for agent in agents:
                agent_tasks = [
                    t for t in available_tasks 
                    if t["task_id"] in agent["assigned_tasks"]
                ]
                
                if not agent_tasks:
                    continue
                
                # 模拟角色工作
                day_log = self._simulate_agent_day(
                    day_number=day,
                    agent=agent,
                    tasks=agent_tasks,
                    context=self._build_context(day, agent, task_status)
                )
                
                self.simulation_logs.append(day_log)
                
                # 转换为详细日志格式
                agent_detailed_logs = self._convert_to_detailed_logs(day_log, agent_tasks)
                detailed_logs.extend(agent_detailed_logs)
                
                # 更新任务状态
                for completed_task in day_log.get("completed_tasks", []):
                    task_id = completed_task["task_id"]
                    task_status[task_id]["progress"] = completed_task.get("progress_percentage", 0)
                    if completed_task.get("status") == "completed":
                        task_status[task_id]["status"] = "completed"
        
        logger.info(f"模拟完成: 共{len(self.simulation_logs)}条日志, {len(detailed_logs)}条详细记录, {len(env_events)}个环境事件")
        
        # 生成每日摘要
        daily_summaries = []
        for day in range(1, total_days + 1):
            day_summary = self.daily_summary_agent.generate_daily_summary(
                day_number=day,
                agent_logs=self.simulation_logs,
                detailed_logs=detailed_logs,
                env_events=env_events
            )
            if day_summary['total_tasks_started'] > 0 or day_summary['total_tasks_completed'] > 0:
                daily_summaries.append(day_summary)
        
        return {
            "logs": self.simulation_logs,  # 原有格式的日志
            "detailed_logs": detailed_logs,  # 详细日志（用于前端展示）
            "daily_summaries": daily_summaries,  # 每日摘要
            "env_events": env_events,  # 环境事件
            "env_summary": self.env_agent.get_event_summary() if enable_env_agent else None
        }
    
    def _simulate_agent_day(
        self,
        day_number: int,
        agent: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        context: str
    ) -> Dict[str, Any]:
        """模拟角色一天的工作"""
        try:
            # 构造提示词
            tasks_text = json.dumps(tasks, ensure_ascii=False, indent=2)
            capabilities_text = ", ".join(agent.get("capabilities", []))
            
            prompt = self.SIMULATION_PROMPT.format(
                day_number=day_number,
                role_name=agent["role_name"],
                role_type=agent["role_type"],
                capabilities=capabilities_text,
                personality=agent.get("personality", "专业负责"),
                today_tasks=tasks_text,
                context=context
            )
            
            # 调用LLM
            response = self.llm.chat_completion(
                messages=[
                    {"role": "system", "content": agent.get("system_prompt", "")},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            
            # 解析响应
            content = response["choices"][0]["message"]["content"]
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            
            # 添加元数据
            result["day_number"] = day_number
            result["agent_id"] = agent["agent_id"]
            result["role_name"] = agent["role_name"]
            
            return result
            
        except Exception as e:
            logger.error(f"模拟失败: day={day_number}, agent={agent['role_name']}, error={str(e)}")
            # 返回默认结果
            return {
                "day_number": day_number,
                "agent_id": agent["agent_id"],
                "role_name": agent["role_name"],
                "completed_tasks": [],
                "discussions": [],
                "notes": "模拟失败"
            }
    
    def _topological_sort(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """拓扑排序任务"""
        # 简单实现：按依赖关系排序
        sorted_tasks = []
        task_dict = {t["task_id"]: t for t in tasks}
        visited = set()
        
        def visit(task_id):
            if task_id in visited:
                return
            task = task_dict.get(task_id)
            if not task:
                return
            
            # 先访问依赖
            for dep in task.get("dependencies", []):
                visit(dep)
            
            visited.add(task_id)
            sorted_tasks.append(task)
        
        for task in tasks:
            visit(task["task_id"])
        
        return sorted_tasks
    
    def _get_available_tasks(
        self,
        tasks: List[Dict[str, Any]],
        task_status: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """获取可执行的任务"""
        available = []
        
        for task in tasks:
            # 跳过已完成的任务
            if task_status[task["task_id"]]["status"] == "completed":
                continue
            
            # 检查依赖是否都已完成
            dependencies = task.get("dependencies", [])
            all_deps_completed = all(
                task_status.get(dep, {}).get("status") == "completed"
                for dep in dependencies
            )
            
            if all_deps_completed:
                available.append(task)
        
        return available
    
    def _build_context(
        self,
        day: int,
        agent: Dict[str, Any],
        task_status: Dict[str, Dict[str, Any]]
    ) -> str:
        """构建上下文信息"""
        completed_count = sum(
            1 for status in task_status.values()
            if status["status"] == "completed"
        )
        
        return f"已完成任务数: {completed_count}/{len(task_status)}"
    
    def simulate_stream(
        self,
        agents: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]],
        total_days: int,
        enable_env_agent: bool = True,
        env_event_probability: float = 0.2
    ):
        """
        流式模拟项目执行（生成器）
        
        Args:
            agents: 角色配置列表
            tasks: 任务列表
            total_days: 总工期
            enable_env_agent: 是否启用环境Agent
            env_event_probability: 环境事件概率
            
        Yields:
            每天的模拟结果
        """
        logger.info(f"开始流式模拟: 角色数={len(agents)}, 任务数={len(tasks)}, 总工期={total_days}天")
        
        task_status = {task["task_id"]: {"status": "pending", "progress": 0} for task in tasks}
        sorted_tasks = self._topological_sort(tasks)
        all_detailed_logs = []
        all_env_events = []
        
        for day in range(1, total_days + 1):
            logger.info(f"模拟第{day}天")
            
            available_tasks = self._get_available_tasks(sorted_tasks, task_status)
            
            # 发送当天开始信号
            day_result = {
                "type": "day_start",
                "day": day,
                "available_tasks": [t["task_id"] for t in available_tasks]
            }
            yield day_result
            
            # 环境事件
            day_env_events = []
            if enable_env_agent:
                day_env_events = self.env_agent.inject_events(day, available_tasks, env_event_probability)
                if day_env_events:
                    all_env_events.extend(day_env_events)
                    # 发送环境事件
                    yield {
                        "type": "env_event",
                        "day": day,
                        "events": day_env_events
                    }
                    
                    # 添加到详细日志
                    for event in day_env_events:
                        all_detailed_logs.append({
                            "timestamp": event["timestamp"],
                            "day": day,
                            "event_type": "env_event",
                            "role_name": "环境因素",
                            "task_id": None,
                            "task_name": None,
                            "content": event["content"],
                            "status": None,
                            "progress_percentage": None,
                            "metadata": event
                        })
            
            # Agent工作
            day_logs = []
            for agent in agents:
                agent_tasks = [
                    t for t in available_tasks 
                    if t["task_id"] in agent["assigned_tasks"]
                ]
                
                if not agent_tasks:
                    continue
                
                # 模拟角色工作
                day_log = self._simulate_agent_day(
                    day_number=day,
                    agent=agent,
                    tasks=agent_tasks,
                    context=self._build_context(day, agent, task_status)
                )
                
                agent_detailed_logs = self._convert_to_detailed_logs(day_log, agent_tasks)
                day_logs.extend(agent_detailed_logs)
                all_detailed_logs.extend(agent_detailed_logs)
                
                # 更新任务状态
                for completed_task in day_log.get("completed_tasks", []):
                    task_id = completed_task["task_id"]
                    task_status[task_id]["progress"] = completed_task.get("progress_percentage", 0)
                    if completed_task.get("status") == "completed":
                        task_status[task_id]["status"] = "completed"
            
            # 推送当天日志
            yield {
                "type": "agent_work",
                "day": day,
                "logs": day_logs
            }
            
            # 当天摘要
            completed_count = sum(1 for s in task_status.values() if s["status"] == "completed")
            
            # 生成当天的每日摘要
            day_summary_data = self.daily_summary_agent.generate_daily_summary(
                day_number=day,
                agent_logs=[log for log in self.simulation_logs if log.get("day_number") == day] if hasattr(self, 'simulation_logs') else [],
                detailed_logs=[log for log in all_detailed_logs if log.get("day") == day],
                env_events=[event for event in all_env_events if event.get("day") == day]
            )
            
            yield {
                "type": "day_summary",
                "day": day,
                "summary": {
                    "completed_tasks": completed_count,
                    "total_tasks": len(tasks),
                    "env_events_today": len(day_env_events),
                    "daily_summary": day_summary_data  # 添加详细摘要
                }
            }
        
        # 生成所有天数的每日摘要
        all_daily_summaries = []
        for day_num in range(1, total_days + 1):
            day_summary = self.daily_summary_agent.generate_daily_summary(
                day_number=day_num,
                agent_logs=[log for log in (self.simulation_logs if hasattr(self, 'simulation_logs') else []) if log.get("day_number") == day_num],
                detailed_logs=[log for log in all_detailed_logs if log.get("day") == day_num],
                env_events=[event for event in all_env_events if event.get("day") == day_num]
            )
            if day_summary['total_tasks_started'] > 0 or day_summary['total_tasks_completed'] > 0:
                all_daily_summaries.append(day_summary)
        
        # 最终结果
        yield {
            "type": "complete",
            "total_logs": len(all_detailed_logs),
            "detailed_logs": all_detailed_logs,
            "daily_summaries": all_daily_summaries,
            "env_events": all_env_events,
            "env_summary": self.env_agent.get_event_summary() if enable_env_agent else None
        }
    
    def _convert_to_detailed_logs(
        self,
        day_log: Dict[str, Any],
        tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        将日志转换为详细日志格式（用于前端展示）
        
        Args:
            day_log: 单天日志
            tasks: 任务列表
            
        Returns:
            详细日志列表
        """
        detailed = []
        day = day_log["day_number"]
        role_name = day_log["role_name"]
        
        # 添加任务开始日志
        for task_info in day_log.get("completed_tasks", []):
            task_id = task_info["task_id"]
            task = next((t for t in tasks if t["task_id"] == task_id), {})
            
            # 任务开始
            detailed.append({
                "timestamp": f"{day}d {task_info.get('start_time', '09:00')}",
                "day": day,
                "event_type": "task_start",
                "role_name": role_name,
                "task_id": task_id,
                "task_name": task.get("task_name", task_id),
                "content": f"开始执行任务: {task.get('task_name', task_id)}",
                "status": "in_progress",
                "progress_percentage": 0,
                "metadata": task_info
            })
            
            # 任务完成/进展
            detailed.append({
                "timestamp": f"{day}d {task_info.get('end_time', '18:00')}",
                "day": day,
                "event_type": "task_complete" if task_info.get("status") == "completed" else "task_progress",
                "role_name": role_name,
                "task_id": task_id,
                "task_name": task.get("task_name", task_id),
                "content": task_info.get("output", "任务完成"),
                "status": task_info.get("status", "in_progress"),
                "progress_percentage": task_info.get("progress_percentage", 100),
                "metadata": task_info
            })
        
        # 添加讨论日志
        for discussion in day_log.get("discussions", []):
            detailed.append({
                "timestamp": f"{day}d {discussion.get('time', '12:00')}",
                "day": day,
                "event_type": "discussion",
                "role_name": role_name,
                "task_id": None,
                "task_name": None,
                "content": f"[与 {discussion.get('with_role', '其他角色')} 讨论] {discussion.get('topic', '')}: {discussion.get('content', '')}",
                "status": None,
                "progress_percentage": None,
                "participants": [role_name, discussion.get("with_role")],
                "metadata": discussion
            })
        
        return detailed
    
    def simulate_with_metadata(
        self,
        agents: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]],
        metadata: SimulationMetadata,
    ) -> Dict[str, Any]:
        """
        使用元信息进行模拟（支持可编辑性）
        
        Args:
            agents: Agent列表
            tasks: 任务列表
            metadata: 模拟元信息
            
        Returns:
            包含模拟日志和环境事件的字典
        """
        logger.info(f"开始使用元信息模拟: project_id={metadata.project_id}")
        
        # 应用元信息到 Agent 和任务
        agents = apply_metadata_to_agents(agents, metadata)
        tasks = apply_metadata_to_tasks(tasks, metadata)
        
        logger.info(f"应用元信息后: agents={len(agents)}, tasks={len(tasks)}")
        logger.info(f"删除的Agent: {metadata.removed_agents}")
        logger.info(f"删除的任务: {metadata.removed_tasks}")
        
        # 应用手动任务分配
        if metadata.manual_assignments:
            agents = apply_manual_assignments(agents, metadata)
            logger.info(f"应用手动任务分配: {len(metadata.manual_assignments)}个")
        
        # 调用标准模拟方法
        simulation_result = self.simulate(
            agents=agents,
            tasks=tasks,
            total_days=metadata.simulation_config.total_days,
            enable_env_agent=metadata.simulation_config.enable_env_agent,
            env_event_probability=metadata.simulation_config.env_event_probability
        )
        
        # 添加元信息到返回结果
        simulation_result["metadata"] = metadata.to_dict()
        simulation_result["metadata_applied"] = True
        
        logger.info("元信息模拟完成")
        
        return simulation_result
    
    def simulate_stream_with_metadata(
        self,
        agents: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]],
        metadata: SimulationMetadata,
    ):
        """
        使用元信息进行流式模拟
        
        Args:
            agents: Agent列表
            tasks: 任务列表
            metadata: 模拟元信息
            
        Yields:
            每天的模拟结果
        """
        logger.info(f"开始流式模拟(元信息): project_id={metadata.project_id}")
        
        # 应用元信息
        agents = apply_metadata_to_agents(agents, metadata)
        tasks = apply_metadata_to_tasks(tasks, metadata)
        
        if metadata.manual_assignments:
            agents = apply_manual_assignments(agents, metadata)
        
        # 调用标准流式模拟
        for result in self.simulate_stream(
            agents=agents,
            tasks=tasks,
            total_days=metadata.simulation_config.total_days,
            enable_env_agent=metadata.simulation_config.enable_env_agent,
            env_event_probability=metadata.simulation_config.env_event_probability
        ):
            # 在最终结果中添加元信息
            if result.get("type") == "complete":
                result["metadata"] = metadata.to_dict()
                result["metadata_applied"] = True
            
            yield result
