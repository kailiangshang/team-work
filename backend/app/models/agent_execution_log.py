"""
Agent执行日志模型
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Time, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class AgentExecutionLog(Base):
    """Agent执行日志表 - 记录单个Agent的细粒度执行记录"""
    
    __tablename__ = "agent_execution_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    day_number = Column(Integer, nullable=False, index=True)
    
    # Agent信息
    agent_id = Column(String(50), nullable=False, index=True)
    role_name = Column(String(100))
    
    # 任务信息
    task_id = Column(String(50))
    task_name = Column(String(255))
    
    # 动作类型: task_start, task_complete, discussion, break, env_event
    action_type = Column(String(50), nullable=False)
    
    # 时间信息
    start_time = Column(Time)
    end_time = Column(Time)
    
    # 内容
    content = Column(Text)  # 执行内容描述
    output = Column(Text)  # 产出物
    
    # 扩展元数据
    extra_metadata = Column(JSON)  # 如: {"discussion_with": "A002", "topic": "API设计", "efficiency": 95}
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    project = relationship("Project", back_populates="agent_execution_logs")
    
    def __repr__(self):
        return f"<AgentExecutionLog(id={self.id}, day={self.day_number}, agent='{self.agent_id}', action='{self.action_type}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "day_number": self.day_number,
            "agent_id": self.agent_id,
            "role_name": self.role_name,
            "task_id": self.task_id,
            "task_name": self.task_name,
            "action_type": self.action_type,
            "start_time": str(self.start_time) if self.start_time else None,
            "end_time": str(self.end_time) if self.end_time else None,
            "content": self.content,
            "output": self.output,
            "extra_metadata": self.extra_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
