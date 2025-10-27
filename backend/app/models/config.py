"""
配置模型
"""

from sqlalchemy import Column, Integer, String, Text, Boolean
from ..database import Base


class Config(Base):
    """配置表"""
    
    __tablename__ = "configs"
    
    id = Column(Integer, primary_key=True, index=True)
    config_type = Column(String(50), nullable=False, index=True)  # llm, database
    config_key = Column(String(100), nullable=False, unique=True, index=True)
    config_value = Column(Text)
    is_encrypted = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Config(type='{self.config_type}', key='{self.config_key}')>"
