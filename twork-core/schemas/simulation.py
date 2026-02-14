"""模拟相关数据结构"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


class SimulationStatus(Enum):
    """模拟状态"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskGroup:
    """任务组 - 每天可执行的任务分组"""
    group_id: str
    task_ids: List[str]               # 任务ID列表
    assigned_agents: List[str] = field(default_factory=list)  # Agent ID列表
    required_skills: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "group_id": self.group_id,
            "task_ids": self.task_ids,
            "assigned_agents": self.assigned_agents,
            "required_skills": self.required_skills,
        }


@dataclass
class ChatMessage:
    """对话消息"""
    role: str                         # agent_id 或 "system"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
        }


@dataclass
class DialogueLog:
    """对话日志"""
    group_id: str
    day: int
    messages: List[ChatMessage] = field(default_factory=list)
    participants: List[str] = field(default_factory=list)
    summary: str = ""
    
    def add_message(self, role: str, content: str):
        """添加消息"""
        self.messages.append(ChatMessage(role=role, content=content))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "group_id": self.group_id,
            "day": self.day,
            "messages": [m.to_dict() for m in self.messages],
            "participants": self.participants,
            "summary": self.summary,
        }


@dataclass
class TaskAssignment:
    """任务分配"""
    task_id: str
    agent_id: str
    day: int
    start_time: str                   # HH:MM
    estimated_hours: float
    actual_hours: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "day": self.day,
            "start_time": self.start_time,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
        }


@dataclass
class TimeEstimate:
    """时间估算 (PERT三点估算)"""
    task_id: str
    optimistic: float                 # 乐观时间
    pessimistic: float                # 悲观时间
    most_likely: float                # 最可能时间
    
    @property
    def expected(self) -> float:
        """期望值 (PERT公式)"""
        return (self.optimistic + 4 * self.most_likely + self.pessimistic) / 6
    
    @property
    def variance(self) -> float:
        """方差"""
        return ((self.pessimistic - self.optimistic) / 6) ** 2
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "optimistic": self.optimistic,
            "pessimistic": self.pessimistic,
            "most_likely": self.most_likely,
            "expected": self.expected,
            "variance": self.variance,
        }


@dataclass
class TimeSlot:
    """时间段"""
    task_id: str
    start: str                        # HH:MM
    end: str                          # HH:MM
    duration: float                   # 小时
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "start": self.start,
            "end": self.end,
            "duration": self.duration,
        }


@dataclass
class DailySchedule:
    """每日排期"""
    day: int
    date: str = ""
    agent_schedules: Dict[str, List[TimeSlot]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "day": self.day,
            "date": self.date,
            "agent_schedules": {
                k: [s.to_dict() for s in v] 
                for k, v in self.agent_schedules.items()
            },
        }


@dataclass
class DailySimulationResult:
    """每日模拟结果"""
    day: int
    task_groups: List[TaskGroup] = field(default_factory=list)
    dialogue_logs: List[DialogueLog] = field(default_factory=list)
    assignments: Dict[str, TaskAssignment] = field(default_factory=dict)
    estimates: Dict[str, TimeEstimate] = field(default_factory=dict)
    schedule: DailySchedule = field(default_factory=lambda: DailySchedule(day=1))
    completed_tasks: List[str] = field(default_factory=list)
    env_events: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "day": self.day,
            "task_groups": [g.to_dict() for g in self.task_groups],
            "dialogue_logs": [l.to_dict() for l in self.dialogue_logs],
            "assignments": {k: v.to_dict() for k, v in self.assignments.items()},
            "estimates": {k: v.to_dict() for k, v in self.estimates.items()},
            "schedule": self.schedule.to_dict(),
            "completed_tasks": self.completed_tasks,
            "env_events": self.env_events,
        }


@dataclass
class SimulationConfig:
    """模拟配置"""
    total_days: int = 30
    enable_env_agent: bool = True
    env_event_probability: float = 0.1
    working_hours_per_day: float = 8.0
    start_hour: int = 9
    end_hour: int = 18
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_days": self.total_days,
            "enable_env_agent": self.enable_env_agent,
            "env_event_probability": self.env_event_probability,
            "working_hours_per_day": self.working_hours_per_day,
            "start_hour": self.start_hour,
            "end_hour": self.end_hour,
        }


@dataclass
class SimulationLog:
    """模拟日志"""
    agent_id: str
    action: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "action": self.action,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class SimulationState:
    """模拟状态"""
    project_id: str
    status: SimulationStatus = SimulationStatus.IDLE
    current_day: int = 0
    total_days: int = 30
    completed_tasks: List[str] = field(default_factory=list)
    in_progress_tasks: List[str] = field(default_factory=list)
    pending_tasks: List[str] = field(default_factory=list)
    logs: List[SimulationLog] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "status": self.status.value,
            "current_day": self.current_day,
            "total_days": self.total_days,
            "completed_tasks": self.completed_tasks,
            "in_progress_tasks": self.in_progress_tasks,
            "pending_tasks": self.pending_tasks,
        }


@dataclass
class SimulationResult:
    """完整模拟结果"""
    project_id: str
    config: SimulationConfig
    status: SimulationStatus = SimulationStatus.IDLE
    current_day: int = 0
    daily_results: List[DailySimulationResult] = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""
    error_message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "config": self.config.to_dict(),
            "status": self.status.value,
            "current_day": self.current_day,
            "daily_results": [r.to_dict() for r in self.daily_results],
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message,
        }