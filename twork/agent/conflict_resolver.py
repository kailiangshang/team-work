"""
冲突解决器
处理Agent之间的观点冲突和资源冲突
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import random


class ConflictType(Enum):
    """冲突类型"""
    TECHNICAL_APPROACH = "技术方案争议"
    TIME_ESTIMATION = "时间预估分歧"
    RESOURCE_ALLOCATION = "资源分配冲突"
    QUALITY_STANDARD = "质量标准争议"
    PRIORITY_DISPUTE = "优先级争议"


class ConflictResolver:
    """冲突解决器"""
    
    def __init__(self, llm_adapter):
        """初始化解决器"""
        self.llm = llm_adapter
        self.conflict_scenarios = self._init_conflict_scenarios()
    
    def _init_conflict_scenarios(self) -> Dict[str, Dict]:
        """初始化冲突场景配置"""
        return {
            ConflictType.TECHNICAL_APPROACH.value: {
                "participants": ["架构师", "开发工程师"],
                "trigger_keywords": ["技术选型", "架构设计", "框架", "方案"],
                "probability": 0.3
            },
            ConflictType.TIME_ESTIMATION.value: {
                "participants": ["项目经理", "开发人员"],
                "trigger_keywords": ["工期", "时间", "deadline", "延期"],
                "probability": 0.4
            },
            ConflictType.RESOURCE_ALLOCATION.value: {
                "participants": ["项目经理", "团队成员"],
                "trigger_keywords": ["资源", "人力", "分配", "负载"],
                "probability": 0.25
            },
            ConflictType.QUALITY_STANDARD.value: {
                "participants": ["测试工程师", "开发工程师"],
                "trigger_keywords": ["测试", "质量", "标准", "bug"],
                "probability": 0.2
            }
        }
    
    def detect_potential_conflicts(
        self,
        tasks: List[Dict[str, Any]],
        agents: List[Dict[str, Any]],
        daily_assignments: Dict[int, List[Dict]]
    ) -> List[Dict[str, Any]]:
        """
        检测潜在冲突
        
        Args:
            tasks: 任务列表
            agents: Agent列表
            daily_assignments: 每日任务分配
        
        Returns:
            潜在冲突列表
        """
        conflicts = []
        
        # 检测资源冲突
        resource_conflicts = self._detect_resource_conflicts(daily_assignments)
        conflicts.extend(resource_conflicts)
        
        # 检测技术冲突
        tech_conflicts = self._detect_technical_conflicts(tasks)
        conflicts.extend(tech_conflicts)
        
        return conflicts
    
    def _detect_resource_conflicts(
        self,
        daily_assignments: Dict[int, List[Dict]]
    ) -> List[Dict[str, Any]]:
        """检测资源冲突"""
        conflicts = []
        
        for day, assignments in daily_assignments.items():
            # 检查是否有Agent被分配多个任务
            agent_tasks = {}
            for assignment in assignments:
                agent = assignment.get("agent")
                if agent not in agent_tasks:
                    agent_tasks[agent] = []
                agent_tasks[agent].append(assignment.get("task_id"))
            
            # 如果同一Agent有多个任务，标记为冲突
            for agent, tasks in agent_tasks.items():
                if len(tasks) > 1:
                    conflicts.append({
                        "type": ConflictType.RESOURCE_ALLOCATION.value,
                        "day": day,
                        "agent": agent,
                        "tasks": tasks,
                        "severity": "medium"
                    })
        
        return conflicts
    
    def _detect_technical_conflicts(
        self,
        tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """检测技术决策冲突"""
        conflicts = []
        
        for task in tasks:
            task_name = task.get("task_name", "")
            description = task.get("description", "")
            text = f"{task_name} {description}"
            
            # 检查是否包含冲突触发关键词
            for conflict_type, config in self.conflict_scenarios.items():
                for keyword in config["trigger_keywords"]:
                    if keyword in text:
                        # 按概率触发
                        if random.random() < config["probability"]:
                            conflicts.append({
                                "type": conflict_type,
                                "task_id": task.get("task_id"),
                                "participants": config["participants"],
                                "severity": "low"
                            })
                            break
        
        return conflicts
    
    def should_trigger_debate(
        self,
        conflict: Dict[str, Any],
        debate_probability: float = 0.3
    ) -> bool:
        """
        判断是否应该触发讨论
        
        Args:
            conflict: 冲突信息
            debate_probability: 触发概率
        
        Returns:
            是否触发
        """
        # 高严重度冲突必然触发
        if conflict.get("severity") == "high":
            return True
        
        # 其他按概率触发
        return random.random() < debate_probability
