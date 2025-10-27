"""
模拟日志模型
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class SimulationLog(Base):
    """模拟日志表"""
    
    __tablename__ = "simulation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    
    # 原有字段
    day_number = Column(Integer, nullable=False)
    agent_id = Column(String(50), nullable=False)
    task_id = Column(String(50))
    start_time = Column(String(10))
    end_time = Column(String(10))
    output = Column(Text)
    discussion = Column(Text)  # JSON字符串
    notes = Column(Text)
    
    # 新增字段 - 增强日志记录
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=True)
    event_type = Column(String(50), nullable=True)  # discussion, task_start, task_complete, conflict, env_event
    role_name = Column(String(100), nullable=True)  # Agent角色名称
    task_name = Column(String(255), nullable=True)  # 任务名称
    content = Column(Text, nullable=True)  # 对话内容或事件描述
    participants = Column(JSON, nullable=True)  # 参与者列表
    status = Column(String(50), nullable=True)  # in_progress, completed, blocked
    progress_percentage = Column(Integer, default=0, nullable=True)  # 进度百分比
    extra_metadata = Column(JSON, nullable=True)  # 扩展元数据(重命名避免与SQLAlchemy保留字冲突)
    
    # 关系
    project = relationship("Project", back_populates="simulation_logs")
    
    def __repr__(self):
        return f"<SimulationLog(id={self.id}, day={self.day_number}, agent='{self.agent_id}')>"
