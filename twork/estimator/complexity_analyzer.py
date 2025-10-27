"""
复杂度分析器
根据任务描述、技能需求等因素计算任务复杂度
"""

from typing import Dict, List, Any
import re


class ComplexityAnalyzer:
    """任务复杂度分析器"""
    
    # 技术关键词权重
    TECH_KEYWORDS_WEIGHT = {
        "高复杂度": ["算法", "架构", "优化", "性能", "安全", "分布式", "并发", "机器学习", "AI"],
        "中复杂度": ["数据库", "API", "集成", "测试", "部署", "配置", "接口"],
        "低复杂度": ["页面", "样式", "文档", "配置", "简单"]
    }
    
    def __init__(self):
        """初始化分析器"""
        self.keyword_weight = 1.0
        self.dependency_weight = 0.5
        self.skill_weight = 0.3
    
    def analyze(self, task: Dict[str, Any]) -> float:
        """
        分析任务复杂度
        
        Args:
            task: 任务字典，包含task_name, description, required_skills, dependencies等
        
        Returns:
            复杂度评分(1-10)
        """
        score = 5.0  # 基础分数
        
        # 基于描述的关键词分析
        description = task.get("description", "") + " " + task.get("task_name", "")
        keyword_score = self._analyze_keywords(description)
        
        # 基于依赖数量
        dependencies = task.get("dependencies", [])
        dependency_score = len(dependencies) * self.dependency_weight
        
        # 基于技能需求
        skills = task.get("required_skills", [])
        skill_score = len(skills) * self.skill_weight
        
        # 综合评分
        total_score = score + keyword_score + dependency_score + skill_score
        
        # 限制在1-10范围内
        final_score = max(1.0, min(10.0, total_score))
        
        return round(final_score, 1)
    
    def _analyze_keywords(self, text: str) -> float:
        """分析关键词得分"""
        score = 0.0
        
        # 高复杂度关键词 +2分
        for keyword in self.TECH_KEYWORDS_WEIGHT["高复杂度"]:
            if re.search(keyword, text, re.IGNORECASE):
                score += 2.0
        
        # 中复杂度关键词 +1分
        for keyword in self.TECH_KEYWORDS_WEIGHT["中复杂度"]:
            if re.search(keyword, text, re.IGNORECASE):
                score += 1.0
        
        # 低复杂度关键词 -0.5分
        for keyword in self.TECH_KEYWORDS_WEIGHT["低复杂度"]:
            if re.search(keyword, text, re.IGNORECASE):
                score -= 0.5
        
        return score
    
    def batch_analyze(self, tasks: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        批量分析任务复杂度
        
        Args:
            tasks: 任务列表
        
        Returns:
            任务ID到复杂度的映射
        """
        results = {}
        for task in tasks:
            task_id = task.get("task_id")
            if task_id:
                results[task_id] = self.analyze(task)
        
        return results
