"""
领域配置数据模型
用于存储项目的领域识别结果和配置信息
"""

from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class DomainConfig(Base):
    """领域配置模型"""
    
    __tablename__ = "domain_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)
    
    # 领域识别结果
    domain_type = Column(String(50), nullable=False, comment="领域类型")
    confidence = Column(Float, nullable=False, comment="识别置信度")
    keywords = Column(JSON, nullable=True, comment="关键词列表")
    template_id = Column(String(50), nullable=False, comment="模板ID")
    
    # 模板配置
    template_config = Column(JSON, nullable=True, comment="模板配置详情")
    
    # 用户选择
    user_selected_domain = Column(String(50), nullable=True, comment="用户手动选择的领域")
    
    # 提取的上下文信息
    extracted_context = Column(JSON, nullable=True, comment="从文档提取的上下文信息")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    project = relationship("Project", back_populates="domain_config")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "domain_type": self.domain_type,
            "confidence": self.confidence,
            "keywords": self.keywords,
            "template_id": self.template_id,
            "template_config": self.template_config,
            "user_selected_domain": self.user_selected_domain,
            "extracted_context": self.extracted_context,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
