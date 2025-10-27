"""
项目模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Project(Base):
    """项目表"""
    
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    document_path = Column(String(500))
    status = Column(String(50), default="parsing")  # parsing, decomposing, simulating, completed, error
    total_days = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 需求信息（JSON字符串）
    requirements = Column(Text)
    
    # 关系
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="project", cascade="all, delete-orphan")
    simulation_logs = relationship("SimulationLog", back_populates="project", cascade="all, delete-orphan")
    agent_execution_logs = relationship("AgentExecutionLog", back_populates="project", cascade="all, delete-orphan")
    daily_summaries = relationship("DailySummary", back_populates="project", cascade="all, delete-orphan")
    domain_config = relationship("DomainConfig", back_populates="project", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"
