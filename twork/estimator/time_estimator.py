"""
时间估算器
基于任务复杂度、历史数据和团队能力估算任务工期
"""

from typing import Dict, List, Any, Optional
from .complexity_analyzer import ComplexityAnalyzer


class TimeEstimator:
    """时间估算器"""
    
    def __init__(self, complexity_analyzer: Optional[ComplexityAnalyzer] = None):
        """初始化估算器"""
        self.complexity_analyzer = complexity_analyzer or ComplexityAnalyzer()
        
        # 复杂度到天数的基础映射
        self.complexity_to_days_map = {
            1: 0.5, 2: 1.0, 3: 1.5, 4: 2.0, 5: 3.0,
            6: 4.0, 7: 5.0, 8: 7.0, 9: 10.0, 10: 15.0
        }
    
    def estimate(
        self,
        tasks: List[Dict[str, Any]],
        total_days: Optional[int] = None,
        team_size: int = 5,
        work_hours_per_day: int = 8
    ) -> Dict[str, Any]:
        """
        估算任务时间
        
        Args:
            tasks: 任务列表
            total_days: 总工期约束（可选）
            team_size: 团队规模
            work_hours_per_day: 每日工作时长
        
        Returns:
            包含估算结果的字典
        """
        # 分析复杂度
        complexity_map = self.complexity_analyzer.batch_analyze(tasks)
        
        # 计算基础工期
        task_estimates = []
        total_estimated_days = 0.0
        
        for task in tasks:
            task_id = task.get("task_id")
            complexity = complexity_map.get(task_id, 5.0)
            
            # 基础工期
            base_days = self._get_base_duration(complexity)
            
            # 调整后的工期
            adjusted_days = self._adjust_by_team(base_days, team_size)
            
            task_estimates.append({
                "task_id": task_id,
                "task_name": task.get("task_name"),
                "complexity_score": complexity,
                "base_duration": base_days,
                "estimated_duration": adjusted_days,
                "confidence": 0.8
            })
            
            total_estimated_days += adjusted_days
        
        # 如果有总工期约束，按比例调整
        if total_days and total_estimated_days > total_days:
            scale_factor = total_days / total_estimated_days
            for estimate in task_estimates:
                estimate["estimated_duration"] = round(
                    estimate["estimated_duration"] * scale_factor, 1
                )
            total_estimated_days = total_days
        
        # 关键路径分析（简化版）
        critical_path = self._find_critical_path(tasks, task_estimates)
        
        return {
            "total_estimated_days": round(total_estimated_days, 1),
            "task_estimates": task_estimates,
            "critical_path": critical_path,
            "team_size": team_size,
            "work_hours_per_day": work_hours_per_day
        }
    
    def _get_base_duration(self, complexity: float) -> float:
        """获取基础工期"""
        # 四舍五入到最近的整数复杂度
        rounded_complexity = round(complexity)
        return self.complexity_to_days_map.get(rounded_complexity, 3.0)
    
    def _adjust_by_team(self, base_days: float, team_size: int) -> float:
        """根据团队规模调整工期"""
        # 简化：团队越大，效率略微提升（但不是线性）
        efficiency_factor = 1.0 - (team_size - 1) * 0.05
        efficiency_factor = max(0.7, efficiency_factor)  # 最多提升30%
        
        return round(base_days * efficiency_factor, 1)
    
    def _find_critical_path(
        self,
        tasks: List[Dict[str, Any]],
        estimates: List[Dict[str, Any]]
    ) -> List[str]:
        """
        找出关键路径（简化版）
        
        Args:
            tasks: 任务列表
            estimates: 估算结果
        
        Returns:
            关键路径上的任务ID列表
        """
        # 简化实现：返回复杂度最高的任务链
        sorted_estimates = sorted(
            estimates,
            key=lambda x: x["complexity_score"],
            reverse=True
        )
        
        # 取前5个作为关键路径
        critical_tasks = [e["task_id"] for e in sorted_estimates[:5]]
        
        return critical_tasks
