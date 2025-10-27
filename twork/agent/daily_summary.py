"""
每日摘要Agent

负责汇总每日所有Agent的执行情况，生成结构化摘要。
"""

from typing import List, Dict, Any
from datetime import datetime
from ..utils.logger import get_logger

logger = get_logger("daily_summary")


class DailySummaryAgent:
    """每日摘要Agent - 汇总每日执行情况"""
    
    def __init__(self):
        """初始化每日摘要Agent"""
        logger.info("每日摘要Agent初始化完成")
    
    def generate_daily_summary(
        self,
        day_number: int,
        agent_logs: List[Dict[str, Any]],
        detailed_logs: List[Dict[str, Any]],
        env_events: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成每日摘要
        
        Args:
            day_number: 日期编号
            agent_logs: 原有格式的Agent日志列表
            detailed_logs: 详细日志列表
            env_events: 环境事件列表
            
        Returns:
            每日摘要字典
        """
        logger.info(f"生成第{day_number}天的摘要")
        
        # 筛选当天的日志
        day_logs = [log for log in agent_logs if log.get("day_number") == day_number]
        day_detailed_logs = [log for log in detailed_logs if log.get("day") == day_number]
        day_env_events = [event for event in (env_events or []) if event.get("day") == day_number]
        
        # 统计任务数量
        total_tasks_started = 0
        total_tasks_completed = 0
        
        for log in day_detailed_logs:
            if log.get("event_type") == "task_start":
                total_tasks_started += 1
            elif log.get("event_type") == "task_complete" and log.get("status") == "completed":
                total_tasks_completed += 1
        
        # 生成每个Agent的摘要
        agent_summaries = self._generate_agent_summaries(day_logs, day_detailed_logs)
        
        # 提取沟通记录
        communications = self._extract_communications(day_logs, day_detailed_logs)
        
        # 格式化环境事件
        formatted_env_events = self._format_env_events(day_env_events)
        
        # 计算整体进度（基于完成任务数）
        overall_progress = 0.0
        if total_tasks_started > 0:
            overall_progress = (total_tasks_completed / total_tasks_started) * 100
        
        summary = {
            "day_number": day_number,
            "total_tasks_started": total_tasks_started,
            "total_tasks_completed": total_tasks_completed,
            "agent_summaries": agent_summaries,
            "communications": communications,
            "env_events": formatted_env_events,
            "overall_progress": round(overall_progress, 2)
        }
        
        logger.info(f"第{day_number}天摘要生成完成: 开始任务{total_tasks_started}个, 完成{total_tasks_completed}个, 进度{overall_progress:.2f}%")
        
        return summary
    
    def _generate_agent_summaries(
        self,
        agent_logs: List[Dict[str, Any]],
        detailed_logs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """生成每个Agent的执行摘要"""
        agent_summaries = []
        
        # 按agent_id分组
        agent_groups = {}
        for log in agent_logs:
            agent_id = log.get("agent_id")
            if agent_id not in agent_groups:
                agent_groups[agent_id] = {
                    "agent_id": agent_id,
                    "role_name": log.get("role_name", ""),
                    "logs": []
                }
            agent_groups[agent_id]["logs"].append(log)
        
        # 为每个Agent生成摘要
        for agent_id, group_data in agent_groups.items():
            logs = group_data["logs"]
            
            # 提取任务执行记录
            tasks_executed = []
            for log in logs:
                for completed_task in log.get("completed_tasks", []):
                    tasks_executed.append({
                        "task_id": completed_task.get("task_id"),
                        "task_name": completed_task.get("task_name", ""),
                        "status": completed_task.get("status", "in_progress"),
                        "progress": completed_task.get("progress_percentage", 0),
                        "output": completed_task.get("output", "")
                    })
            
            # 提取沟通记录
            communications = []
            for log in logs:
                for discussion in log.get("discussions", []):
                    communications.append({
                        "time": discussion.get("time"),
                        "with": discussion.get("with_role"),
                        "topic": discussion.get("topic"),
                        "content": discussion.get("content")
                    })
            
            # 计算工作时长（粗略估计）
            work_hours = len(tasks_executed) * 2  # 假设每个任务平均2小时
            
            # 计算效率（简化版本）
            efficiency = 85 + (len(tasks_executed) * 2)  # 基础效率85，每完成一个任务+2
            if efficiency > 100:
                efficiency = 100
            
            agent_summaries.append({
                "agent_id": agent_id,
                "role_name": group_data["role_name"],
                "tasks_executed": tasks_executed,
                "communications": communications,
                "work_hours": work_hours,
                "efficiency": efficiency
            })
        
        return agent_summaries
    
    def _extract_communications(
        self,
        agent_logs: List[Dict[str, Any]],
        detailed_logs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """提取Agent间的沟通记录"""
        communications = []
        
        for log in agent_logs:
            agent_id = log.get("agent_id")
            role_name = log.get("role_name", "")
            
            for discussion in log.get("discussions", []):
                communications.append({
                    "time": discussion.get("time"),
                    "from": role_name,
                    "from_id": agent_id,
                    "to": discussion.get("with_role"),
                    "topic": discussion.get("topic"),
                    "content": discussion.get("content")
                })
        
        # 按时间排序
        communications.sort(key=lambda x: x.get("time", "00:00"))
        
        return communications
    
    def _format_env_events(self, env_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """格式化环境事件"""
        formatted_events = []
        
        for event in env_events:
            formatted_events.append({
                "time": event.get("timestamp", ""),
                "event_type": event.get("event_type", "unknown"),
                "description": event.get("content", ""),
                "affected_agents": event.get("affected_agents", [])
            })
        
        return formatted_events
    
    def generate_markdown_summary(self, summary: Dict[str, Any]) -> str:
        """
        生成Markdown格式的每日摘要
        
        Args:
            summary: 每日摘要字典
            
        Returns:
            Markdown格式的摘要文本
        """
        md_lines = []
        
        md_lines.append(f"# 第{summary['day_number']}天执行摘要\n")
        md_lines.append(f"**任务完成情况**: {summary['total_tasks_completed']}/{summary['total_tasks_started']} 个")
        md_lines.append(f"**整体进度**: {summary['overall_progress']}%\n")
        
        # Agent执行摘要
        md_lines.append("## Agent执行情况\n")
        for agent_summary in summary['agent_summaries']:
            md_lines.append(f"### {agent_summary['role_name']} ({agent_summary['agent_id']})\n")
            md_lines.append(f"- **工作时长**: {agent_summary['work_hours']}小时")
            md_lines.append(f"- **效率**: {agent_summary['efficiency']}%")
            md_lines.append(f"- **完成任务**: {len(agent_summary['tasks_executed'])}个\n")
            
            if agent_summary['tasks_executed']:
                md_lines.append("**任务详情**:")
                for task in agent_summary['tasks_executed']:
                    md_lines.append(f"  - {task['task_name']} ({task['task_id']}): {task['status']} - {task['progress']}%")
                md_lines.append("")
        
        # 沟通记录
        if summary['communications']:
            md_lines.append("## 团队沟通记录\n")
            for comm in summary['communications']:
                md_lines.append(f"- **{comm['time']}**: {comm['from']} → {comm['to']} - {comm['topic']}")
            md_lines.append("")
        
        # 环境事件
        if summary['env_events']:
            md_lines.append("## 环境事件\n")
            for event in summary['env_events']:
                md_lines.append(f"- **{event['time']}**: {event['description']} ({event['event_type']})")
            md_lines.append("")
        
        return "\n".join(md_lines)
