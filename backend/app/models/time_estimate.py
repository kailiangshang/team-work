"""
时间估算数据模型
存储任务的时间估算结果
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class TimeEstimate(Base):
    """时间估算表"""
    
    __tablename__ = "time_estimates"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    task_id = Column(String(50), ForeignKey("tasks.task_id"), nullable=False, index=True)
    
    # 复杂度评估
    complexity_score = Column(Float, nullable=False, comment="复杂度评分(1-10)")
    
    # 工期估算
    base_duration = Column(Float, nullable=False, comment="基础工期(天)")
    estimated_duration = Column(Float, nullable=False, comment="估算工期(天)")
    actual_duration = Column(Float, nullable=True, comment="实际工期(天,模拟后)")
    
    # 调整因素
    team_efficiency_factor = Column(Float, default=1.0, comment="团队效率因子")
    adjustment_reason = Column(Text, nullable=True, comment="调整原因")
    
    # 置信度
    confidence = Column(Float, default=0.8, comment="估算置信度(0-1)")
    
    # 是否在关键路径
    is_critical_path = Column(Integer, default=0, comment="是否关键路径(0/1)")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    project = relationship("Project")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "task_id": self.task_id,
            "complexity_score": self.complexity_score,
            "base_duration": self.base_duration,
            "estimated_duration": self.estimated_duration,
            "actual_duration": self.actual_duration,
            "team_efficiency_factor": self.team_efficiency_factor,
            "adjustment_reason": self.adjustment_reason,
            "confidence": self.confidence,
            "is_critical_path": bool(self.is_critical_path),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
