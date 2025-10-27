"""
Agent模型
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..database import Base


class Agent(Base):
    """Agent表"""
    
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    agent_id = Column(String(50), nullable=False, index=True)
    role_name = Column(String(100), nullable=False)
    role_type = Column(String(50))
    capabilities = Column(JSON)  # 列表
    assigned_tasks = Column(JSON)  # 列表
    personality = Column(Text)
    system_prompt = Column(Text)
    tools = Column(JSON)  # 列表
    
    # 关系
    project = relationship("Project", back_populates="agents")
    
    def __repr__(self):
        return f"<Agent(id={self.id}, agent_id='{self.agent_id}', role='{self.role_name}')>"
