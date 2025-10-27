"""
风险分析器
分析项目中的潜在风险并生成风险报告
"""

from typing import List, Dict, Any, Optional
from datetime import datetime


class RiskAnalyzer:
    """风险分析器"""
    
    def __init__(self):
        """初始化分析器"""
        pass
    
    def analyze(
        self,
        tasks: List[Dict[str, Any]],
        critical_path: List[str],
        resource_conflicts: List[Dict],
        debate_logs: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        综合风险分析
        
        Args:
            tasks: 任务列表
            critical_path: 关键路径
            resource_conflicts: 资源冲突列表
            debate_logs: 讨论日志
        
        Returns:
            风险报告
        """
        report = {
            "critical_risks": [],
            "resource_conflicts": [],
            "debate_insights": [],
            "recommendations": [],
            "risk_score": 0.0,
            "analyzed_at": datetime.now().isoformat()
        }
        
        # 分析关键路径风险
        critical_risks = self._analyze_critical_path_risks(tasks, critical_path)
        report["critical_risks"] = critical_risks
        
        # 分析资源冲突
        report["resource_conflicts"] = self._format_resource_conflicts(resource_conflicts)
        
        # 分析讨论中的风险
        if debate_logs:
            debate_insights = self._analyze_debate_risks(debate_logs)
            report["debate_insights"] = debate_insights
        
        # 生成建议
        report["recommendations"] = self._generate_recommendations(report)
        
        # 计算风险评分
        report["risk_score"] = self._calculate_risk_score(report)
        
        return report
    
    def _analyze_critical_path_risks(
        self,
        tasks: List[Dict[str, Any]],
        critical_path: List[str]
    ) -> List[Dict[str, Any]]:
        """分析关键路径风险"""
        risks = []
        
        for task in tasks:
            task_id = task.get("task_id")
            if task_id in critical_path:
                # 关键路径上的任务延误会影响整体
                duration = task.get("duration_days", 1)
                complexity = task.get("estimated_complexity", 5)
                
                risk_level = "高" if complexity > 7 else "中"
                
                risks.append({
                    "type": "关键路径延误风险",
                    "task_id": task_id,
                    "task_name": task.get("task_name"),
                    "description": f"该任务在关键路径上，复杂度{complexity}，工期{duration}天，延误将直接影响项目交付",
                    "impact": risk_level,
                    "mitigation": "增加资源投入或提前启动，设置检查点"
                })
        
        return risks
    
    def _format_resource_conflicts(
        self,
        conflicts: List[Dict]
    ) -> List[Dict[str, Any]]:
        """格式化资源冲突"""
        formatted = []
        
        for conflict in conflicts:
            formatted.append({
                "day": conflict.get("day"),
                "agent": conflict.get("agent"),
                "tasks": conflict.get("tasks", []),
                "description": f"第{conflict.get('day')}天，{conflict.get('agent')}被分配了{len(conflict.get('tasks', []))}个任务",
                "suggestion": "调整任务优先级或分配给其他成员"
            })
        
        return formatted
    
    def _analyze_debate_risks(
        self,
        debate_logs: List[Dict]
    ) -> List[Dict[str, Any]]:
        """分析讨论中暴露的风险"""
        insights = []
        
        for log in debate_logs:
            if log.get("risks_identified"):
                insights.append({
                    "day": log.get("day"),
                    "topic": log.get("topic"),
                    "risks": log.get("risks_identified"),
                    "action": "需要关注并采取预防措施"
                })
        
        return insights
    
    def _generate_recommendations(
        self,
        report: Dict[str, Any]
    ) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于关键风险
        if report["critical_risks"]:
            recommendations.append("建议对关键路径任务进行重点监控，设置里程碑检查点")
        
        # 基于资源冲突
        if report["resource_conflicts"]:
            recommendations.append("存在资源冲突，建议优化任务分配或增加团队成员")
        
        # 基于讨论风险
        if report["debate_insights"]:
            recommendations.append("团队讨论中识别出潜在风险，建议制定应对预案")
        
        if not recommendations:
            recommendations.append("当前项目风险在可控范围内")
        
        return recommendations
    
    def _calculate_risk_score(self, report: Dict[str, Any]) -> float:
        """
        计算综合风险评分 (0-100)
        
        Args:
            report: 风险报告
        
        Returns:
            风险评分，越高风险越大
        """
        score = 0.0
        
        # 关键风险 +20分/项
        score += len(report["critical_risks"]) * 20
        
        # 资源冲突 +10分/项
        score += len(report["resource_conflicts"]) * 10
        
        # 讨论风险 +5分/项
        score += len(report["debate_insights"]) * 5
        
        # 限制在0-100
        return min(100.0, score)
    
    def export_to_text(self, report: Dict[str, Any]) -> str:
        """
        导出为文本格式
        
        Args:
            report: 风险报告
        
        Returns:
            文本格式的报告
        """
        text = "=" * 60 + "\n"
        text += "项目风险分析报告\n"
        text += "=" * 60 + "\n\n"
        
        text += f"分析时间: {report['analyzed_at']}\n"
        text += f"综合风险评分: {report['risk_score']}/100\n\n"
        
        # 关键风险
        if report["critical_risks"]:
            text += "【关键风险】\n"
            for i, risk in enumerate(report["critical_risks"], 1):
                text += f"{i}. {risk['description']}\n"
                text += f"   缓解措施: {risk['mitigation']}\n\n"
        
        # 资源冲突
        if report["resource_conflicts"]:
            text += "【资源冲突】\n"
            for i, conflict in enumerate(report["resource_conflicts"], 1):
                text += f"{i}. {conflict['description']}\n"
                text += f"   建议: {conflict['suggestion']}\n\n"
        
        # 建议
        text += "【总体建议】\n"
        for i, rec in enumerate(report["recommendations"], 1):
            text += f"{i}. {rec}\n"
        
        return text
