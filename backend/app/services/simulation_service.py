"""
模拟服务

处理任务模拟相关的业务逻辑。
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
import json
from pathlib import Path
from datetime import datetime
import asyncio
from ..models.project import Project
from ..models.task import Task
from ..models.agent import Agent
from ..models.simulation_log import SimulationLog
from ..config import settings
from twork.agent import SimulationEngine
from twork.generator import DocumentGenerator, CSVExporter, GraphBuilder
from twork.llm import OpenAIAdapter
from twork.utils.logger import get_logger

logger = get_logger("simulation_service")


class SimulationService:
    """模拟服务"""
    
    def __init__(self, db: Session):
        """初始化模拟服务"""
        self.db = db
        self.llm = self._init_llm()
    
    def _init_llm(self) -> OpenAIAdapter:
        """初始化LLM适配器"""
        return OpenAIAdapter(
            api_base_url=settings.llm_api_base_url,
            api_key=settings.llm_api_key,
            model_name=settings.llm_model_name,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            timeout=settings.llm_timeout,
        )
    
    def run_simulation(
        self, 
        project_id: int,
        enable_env_agent: bool = True,
        env_event_probability: float = 0.2
    ) -> Dict[str, Any]:
        """
        运行模拟
        
        Args:
            project_id: 项目ID
            
        Returns:
            模拟日志列表
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"项目不存在: {project_id}")
        
        # 获取任务和Agent
        tasks = self.db.query(Task).filter(Task.project_id == project_id).all()
        agents = self.db.query(Agent).filter(Agent.project_id == project_id).all()
        
        # 转换为字典格式
        task_dicts = [
            {
                "task_id": t.task_id,
                "task_name": t.task_name,
                "description": t.description,
                "duration_days": t.duration_days,
                "dependencies": t.dependencies or []
            }
            for t in tasks
        ]
        
        agent_dicts = [
            {
                "agent_id": a.agent_id,
                "role_name": a.role_name,
                "role_type": a.role_type,
                "capabilities": a.capabilities or [],
                "assigned_tasks": a.assigned_tasks or [],
                "personality": a.personality or "",
                "system_prompt": a.system_prompt or ""
            }
            for a in agents
        ]
        
        # 运行模拟
        project.status = "simulating"
        self.db.commit()
        
        engine = SimulationEngine(self.llm)
        simulation_result = engine.simulate(
            agents=agent_dicts,
            tasks=task_dicts,
            total_days=project.total_days or 30,
            enable_env_agent=enable_env_agent,
            env_event_probability=env_event_probability
        )
        
        # 获取结果
        simulation_logs = simulation_result.get("logs", [])
        detailed_logs = simulation_result.get("detailed_logs", [])
        daily_summaries = simulation_result.get("daily_summaries", [])
        env_events = simulation_result.get("env_events", [])
        env_summary = simulation_result.get("env_summary")
        
        # 保存模拟日志（使用详细日志格式）
        for log in detailed_logs:
            sim_log = SimulationLog(
                project_id=project_id,
                day_number=log.get("day"),
                agent_id=log.get("role_name", "unknown"),  # 使用role_name作为agent_id
                task_id=log.get("task_id"),
                start_time="",
                end_time="",
                output=log.get("content", ""),
                discussion="",
                notes="",
                # 新字段
                timestamp=datetime.utcnow(),
                event_type=log.get("event_type"),
                role_name=log.get("role_name"),
                task_name=log.get("task_name"),
                content=log.get("content"),
                participants=log.get("participants"),
                status=log.get("status"),
                progress_percentage=log.get("progress_percentage"),
                metadata=log.get("metadata")
            )
            self.db.add(sim_log)
        
        # 保存每日摘要
        from ..models.daily_summary import DailySummary
        for summary in daily_summaries:
            daily_summary = DailySummary(
                project_id=project_id,
                day_number=summary["day_number"],
                total_tasks_started=summary["total_tasks_started"],
                total_tasks_completed=summary["total_tasks_completed"],
                agent_summaries=summary["agent_summaries"],
                communications=summary["communications"],
                env_events=summary["env_events"],
                overall_progress=summary["overall_progress"]
            )
            self.db.add(daily_summary)
        
        # 保存Agent执行日志
        from ..models.agent_execution_log import AgentExecutionLog
        from datetime import time
        for log in detailed_logs:
            # 转换时间格式
            start_time_str = log.get("metadata", {}).get("start_time") if log.get("metadata") else None
            end_time_str = log.get("metadata", {}).get("end_time") if log.get("metadata") else None
            
            start_time = None
            end_time = None
            if start_time_str:
                try:
                    parts = start_time_str.split(":")
                    if len(parts) == 2:
                        start_time = time(int(parts[0]), int(parts[1]))
                except:
                    pass
            if end_time_str:
                try:
                    parts = end_time_str.split(":")
                    if len(parts) == 2:
                        end_time = time(int(parts[0]), int(parts[1]))
                except:
                    pass
            
            agent_log = AgentExecutionLog(
                project_id=project_id,
                day_number=log.get("day"),
                agent_id=log.get("role_name", "unknown"),
                role_name=log.get("role_name"),
                task_id=log.get("task_id"),
                task_name=log.get("task_name"),
                action_type=log.get("event_type", "unknown"),
                start_time=start_time,
                end_time=end_time,
                content=log.get("content"),
                output=log.get("metadata", {}).get("output") if log.get("metadata") else None,
                extra_metadata=log.get("metadata")
            )
            self.db.add(agent_log)
        
        project.status = "completed"
        self.db.commit()
        
        return {
            "logs": simulation_logs,
            "detailed_logs": detailed_logs,
            "daily_summaries": daily_summaries,
            "env_events": env_events,
            "env_summary": env_summary
        }
    
    def generate_outputs(self, project_id: int) -> Dict[str, str]:
        """
        生成输出文件
        
        Args:
            project_id: 项目ID
            
        Returns:
            输出文件路径字典
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"项目不存在: {project_id}")
        
        tasks = self.db.query(Task).filter(Task.project_id == project_id).all()
        agents = self.db.query(Agent).filter(Agent.project_id == project_id).all()
        sim_logs = self.db.query(SimulationLog).filter(SimulationLog.project_id == project_id).all()
        
        # 转换为字典
        requirements = json.loads(project.requirements) if project.requirements else {}
        task_dicts = [
            {
                "task_id": t.task_id,
                "task_name": t.task_name,
                "description": t.description,
                "required_skills": t.required_skills or [],
                "person_type": t.person_type,
                "tools_needed": t.tools_needed or [],
                "duration_days": t.duration_days,
                "priority": t.priority,
                "dependencies": t.dependencies or []
            }
            for t in tasks
        ]
        
        agent_dicts = [
            {
                "agent_id": a.agent_id,
                "role_name": a.role_name,
                "role_type": a.role_type,
                "capabilities": a.capabilities or [],
                "assigned_tasks": a.assigned_tasks or []
            }
            for a in agents
        ]
        
        log_dicts = [
            {
                "day_number": log.day_number,
                "agent_id": log.agent_id,
                "role_name": next((a.role_name for a in agents if a.agent_id == log.agent_id), "N/A"),
                "completed_tasks": [{
                    "task_id": log.task_id,
                    "start_time": log.start_time,
                    "end_time": log.end_time,
                    "output": log.output
                }] if log.task_id else [],
                "discussions": json.loads(log.discussion) if log.discussion else [],
                "notes": log.notes
            }
            for log in sim_logs
        ]
        
        # 创建输出目录
        output_dir = Path(settings.output_dir) / f"project_{project_id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文档
        doc_gen = DocumentGenerator()
        md_path = doc_gen.generate_markdown(
            requirements=requirements,
            tasks=task_dicts,
            agents=agent_dicts,
            output_path=str(output_dir / "task_breakdown.md")
        )
        
        # 生成CSV
        csv_exp = CSVExporter()
        csv_path = csv_exp.export_schedule(
            simulation_logs=log_dicts,
            output_path=str(output_dir / "schedule.csv")
        )
        
        task_csv_path = csv_exp.export_tasks(
            tasks=task_dicts,
            output_path=str(output_dir / "tasks.csv")
        )
        
        # 生成图谱
        graph_builder = GraphBuilder()
        triplets = graph_builder.build_triplets(task_dicts, agent_dicts)
        triplet_path = graph_builder.export_triplets(
            triplets=triplets,
            output_path=str(output_dir / "graph_triplets.json")
        )
        
        mermaid_path = graph_builder.export_mermaid(
            tasks=task_dicts,
            agents=agent_dicts,
            output_path=str(output_dir / "graph.md")
        )
        
        return {
            "markdown": md_path,
            "schedule_csv": csv_path,
            "tasks_csv": task_csv_path,
            "triplets": triplet_path,
            "mermaid": mermaid_path
        }
    
    def get_detailed_logs(self, project_id: int) -> List[Dict[str, Any]]:
        """
        获取详细日志
        
        Args:
            project_id: 项目ID
            
        Returns:
            详细日志列表
        """
        sim_logs = self.db.query(SimulationLog).filter(
            SimulationLog.project_id == project_id
        ).order_by(SimulationLog.day_number, SimulationLog.timestamp).all()
        
        detailed_logs = []
        for log in sim_logs:
            detailed_logs.append({
                "timestamp": f"{log.day_number}d {log.start_time}" if log.start_time else f"{log.day_number}d",
                "day": log.day_number,
                "event_type": log.event_type or "unknown",
                "role_name": log.role_name or log.agent_id,
                "task_id": log.task_id,
                "task_name": log.task_name,
                "content": log.content or log.output,
                "status": log.status,
                "progress_percentage": log.progress_percentage,
                "participants": log.participants,
                "extra_metadata": log.extra_metadata
            })
        
        return detailed_logs
    
    async def run_simulation_stream(
        self,
        project_id: int,
        enable_env_agent: bool = True,
        env_event_probability: float = 0.2
    ):
        """
        流式运行模拟（生成器）
        
        Args:
            project_id: 项目ID
            enable_env_agent: 是否启用环境Agent
            env_event_probability: 环境事件概率
            
        Yields:
            每天的模拟结果
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"项目不存在: {project_id}")
        
        # 获取任务和Agent
        tasks = self.db.query(Task).filter(Task.project_id == project_id).all()
        agents = self.db.query(Agent).filter(Agent.project_id == project_id).all()
        
        if not tasks:
            raise ValueError("没有任务数据，请先执行任务拆解")
        if not agents:
            raise ValueError("没有Agent数据，请先生成Agent")
        
        # 转换为字典格式
        task_dicts = [
            {
                "task_id": t.task_id,
                "task_name": t.task_name,
                "description": t.description,
                "duration_days": t.duration_days,
                "dependencies": t.dependencies or []
            }
            for t in tasks
        ]
        
        agent_dicts = [
            {
                "agent_id": a.agent_id,
                "role_name": a.role_name,
                "role_type": a.role_type,
                "capabilities": a.capabilities or [],
                "assigned_tasks": a.assigned_tasks or [],
                "personality": a.personality or "",
                "system_prompt": a.system_prompt or ""
            }
            for a in agents
        ]
        
        # 更新项目状态
        project.status = "simulating"
        self.db.commit()
        
        logger.info(f"开始流式模拟: project_id={project_id}, total_days={project.total_days}")
        
        # 创建模拟引擎
        engine = SimulationEngine(self.llm)
        
        # 清理旧日志
        self.db.query(SimulationLog).filter(SimulationLog.project_id == project_id).delete()
        from ..models.daily_summary import DailySummary
        from ..models.agent_execution_log import AgentExecutionLog
        self.db.query(DailySummary).filter(DailySummary.project_id == project_id).delete()
        self.db.query(AgentExecutionLog).filter(AgentExecutionLog.project_id == project_id).delete()
        self.db.commit()
        
        # 流式模拟
        for chunk in engine.simulate_stream(
            agents=agent_dicts,
            tasks=task_dicts,
            total_days=project.total_days or 30,
            enable_env_agent=enable_env_agent,
            env_event_probability=env_event_probability
        ):
            # 保存日志到数据库
            if chunk["type"] == "agent_work":
                from datetime import time
                for log in chunk.get("logs", []):
                    sim_log = SimulationLog(
                        project_id=project_id,
                        day_number=log.get("day"),
                        agent_id=log.get("role_name", "unknown"),
                        task_id=log.get("task_id"),
                        start_time="",
                        end_time="",
                        output=log.get("content", ""),
                        discussion="",
                        notes="",
                        timestamp=datetime.utcnow(),
                        event_type=log.get("event_type"),
                        role_name=log.get("role_name"),
                        task_name=log.get("task_name"),
                        content=log.get("content"),
                        participants=log.get("participants"),
                        status=log.get("status"),
                        progress_percentage=log.get("progress_percentage"),
                        metadata=log.get("metadata")
                    )
                    self.db.add(sim_log)
                    
                    # 保存Agent执行日志
                    start_time_str = log.get("metadata", {}).get("start_time") if log.get("metadata") else None
                    end_time_str = log.get("metadata", {}).get("end_time") if log.get("metadata") else None
                    
                    start_time = None
                    end_time = None
                    if start_time_str:
                        try:
                            parts = start_time_str.split(":")
                            if len(parts) == 2:
                                start_time = time(int(parts[0]), int(parts[1]))
                        except:
                            pass
                    if end_time_str:
                        try:
                            parts = end_time_str.split(":")
                            if len(parts) == 2:
                                end_time = time(int(parts[0]), int(parts[1]))
                        except:
                            pass
                    
                    agent_log = AgentExecutionLog(
                        project_id=project_id,
                        day_number=log.get("day"),
                        agent_id=log.get("role_name", "unknown"),
                        role_name=log.get("role_name"),
                        task_id=log.get("task_id"),
                        task_name=log.get("task_name"),
                        action_type=log.get("event_type", "unknown"),
                        start_time=start_time,
                        end_time=end_time,
                        content=log.get("content"),
                        output=log.get("metadata", {}).get("output") if log.get("metadata") else None,
                        extra_metadata=log.get("metadata")
                    )
                    self.db.add(agent_log)
                
                try:
                    self.db.commit()
                except Exception as e:
                    logger.error(f"保存日志失败: {str(e)}")
                    self.db.rollback()
            
            elif chunk["type"] == "day_summary":
                # 保存每日摘要
                daily_summary_data = chunk.get("summary", {}).get("daily_summary")
                if daily_summary_data:
                    daily_summary = DailySummary(
                        project_id=project_id,
                        day_number=daily_summary_data["day_number"],
                        total_tasks_started=daily_summary_data["total_tasks_started"],
                        total_tasks_completed=daily_summary_data["total_tasks_completed"],
                        agent_summaries=daily_summary_data["agent_summaries"],
                        communications=daily_summary_data["communications"],
                        env_events=daily_summary_data["env_events"],
                        overall_progress=daily_summary_data["overall_progress"]
                    )
                    self.db.add(daily_summary)
                    try:
                        self.db.commit()
                    except Exception as e:
                        logger.error(f"保存每日摘要失败: {str(e)}")
                        self.db.rollback()
            
            elif chunk["type"] == "complete":
                # 保存最终结果
                project.status = "completed"
                self.db.commit()
                logger.info("模拟完成")
            
            # 推送给前端
            yield chunk
            
            # 小延迟，避免过快
            await asyncio.sleep(0.05)
    
    def get_daily_summaries(self, project_id: int) -> List[Dict[str, Any]]:
        """
        获取每日摘要
        
        Args:
            project_id: 项目ID
            
        Returns:
            每日摘要列表
        """
        from ..models.daily_summary import DailySummary
        
        summaries = self.db.query(DailySummary).filter(
            DailySummary.project_id == project_id
        ).order_by(DailySummary.day_number).all()
        
        return [s.to_dict() for s in summaries]
    
    def get_agent_execution_logs(
        self,
        project_id: int,
        agent_id: str = None,
        day_number: int = None
    ) -> List[Dict[str, Any]]:
        """
        获取Agent执行日志
        
        Args:
            project_id: 项目ID
            agent_id: Agent ID（可选）
            day_number: 天数（可选）
            
        Returns:
            日志列表
        """
        from ..models.agent_execution_log import AgentExecutionLog
        
        query = self.db.query(AgentExecutionLog).filter(
            AgentExecutionLog.project_id == project_id
        )
        
        if agent_id:
            query = query.filter(AgentExecutionLog.agent_id == agent_id)
        
        if day_number is not None:
            query = query.filter(AgentExecutionLog.day_number == day_number)
        
        logs = query.order_by(
            AgentExecutionLog.day_number,
            AgentExecutionLog.start_time
        ).all()
        
        return [log.to_dict() for log in logs]
    
    def export_agent_logs_markdown(self, logs: List[Dict[str, Any]]) -> str:
        """
        将Agent日志导出为Markdown格式
        
        Args:
            logs: 日志列表
            
        Returns:
            Markdown文本
        """
        md_lines = []
        md_lines.append("# Agent执行日志\n")
        
        # 按天数分组
        days = {}
        for log in logs:
            day = log.get("day_number")
            if day not in days:
                days[day] = []
            days[day].append(log)
        
        # 按天数排序输出
        for day in sorted(days.keys()):
            md_lines.append(f"## 第{day}天\n")
            
            day_logs = days[day]
            for log in day_logs:
                md_lines.append(f"### {log.get('role_name', 'N/A')} - {log.get('action_type', 'N/A')}\n")
                md_lines.append(f"- **任务**: {log.get('task_name', 'N/A')}")
                md_lines.append(f"- **时间**: {log.get('start_time', '')} - {log.get('end_time', '')}")
                md_lines.append(f"- **内容**: {log.get('content', '')}")
                if log.get('output'):
                    md_lines.append(f"- **产出**: {log.get('output')}")
                md_lines.append("")
        
        return "\n".join(md_lines)
