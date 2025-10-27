"""
任务模型
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..database import Base


class Task(Base):
    """任务表"""
    
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    task_id = Column(String(50), nullable=False, index=True)
    task_name = Column(String(200), nullable=False)
    description = Column(Text)
    required_skills = Column(JSON)  # 列表
    person_type = Column(String(100))
    tools_needed = Column(JSON)  # 列表
    duration_days = Column(Integer, default=1)
    priority = Column(String(20), default="Medium")  # High, Medium, Low
    dependencies = Column(JSON)  # 列表
    
    # WBS层级字段
    parent_task_id = Column(String(50), nullable=True, comment="父任务ID")
    level = Column(Integer, default=1, comment="层级(1-4)")
    sort_order = Column(Integer, default=0, comment="同级排序")
    task_type = Column(String(100), nullable=True, comment="任务类型")
    estimated_complexity = Column(Integer, default=5, comment="复杂度(1-10)")
    
    # 关系
    project = relationship("Project", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task(id={self.id}, task_id='{self.task_id}', name='{self.task_name}')>"
