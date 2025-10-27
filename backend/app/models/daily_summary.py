"""
每日摘要模型
"""

from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class DailySummary(Base):
    """每日摘要表 - 记录每天所有Agent的汇总信息"""
    
    __tablename__ = "daily_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    day_number = Column(Integer, nullable=False, index=True)
    
    # 任务统计
    total_tasks_started = Column(Integer, default=0, nullable=False)
    total_tasks_completed = Column(Integer, default=0, nullable=False)
    
    # Agent摘要 - JSON格式存储每个Agent的执行摘要
    # 结构: [{"agent_id": "A001", "role_name": "后端工程师", "tasks_executed": [...], "communications": [...], "work_hours": 8.5, "efficiency": 95}]
    agent_summaries = Column(JSON)
    
    # 沟通记录 - JSON格式存储Agent间的沟通
    # 结构: [{"time": "10:30", "from": "A001", "to": "A002", "topic": "API接口", "content": "..."}]
    communications = Column(JSON)
    
    # 环境事件 - JSON格式存储环境触发的事件
    # 结构: [{"time": "14:00", "event_type": "resource_shortage", "description": "...", "affected_agents": ["A001"]}]
    env_events = Column(JSON)
    
    # 整体进度
    overall_progress = Column(Float, default=0.0)  # 0-100的百分比
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    project = relationship("Project", back_populates="daily_summaries")
    
    def __repr__(self):
        return f"<DailySummary(id={self.id}, day={self.day_number}, progress={self.overall_progress}%)>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "day_number": self.day_number,
            "total_tasks_started": self.total_tasks_started,
            "total_tasks_completed": self.total_tasks_completed,
            "agent_summaries": self.agent_summaries or [],
            "communications": self.communications or [],
            "env_events": self.env_events or [],
            "overall_progress": self.overall_progress,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
