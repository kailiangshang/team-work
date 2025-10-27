"""
环境Agent - 模拟影响项目进度的随机因素
"""

import random
from typing import List, Dict, Any, Tuple
from datetime import datetime


class EnvironmentAgent:
    """
    环境Agent - 模拟影响项目进度的随机因素
    
    模拟真实项目中会遇到的各种不可控因素，包括：
    - 技术问题：依赖冲突、API不稳定、性能瓶颈等
    - 资源问题：人员请假、突发需求、设备故障等
    - 沟通问题：需求变更、设计延期、协调困难等
    - 外部因素：节假日、停电维护、网络故障等
    """
    
    EVENT_TYPES = {
        "technical": {
            "name": "技术问题",
            "events": [
                "依赖库版本冲突需要解决",
                "第三方API接口不稳定",
                "发现严重性能瓶颈需要优化",
                "代码审查发现安全漏洞需要修复",
                "测试环境数据库异常",
                "编译构建失败需要排查",
                "内存泄漏问题需要处理",
                "跨浏览器兼容性问题"
            ],
            "severity_range": (0.5, 2.0)  # 延期0.5-2天
        },
        "resource": {
            "name": "资源问题",
            "events": [
                "核心开发人员突然请病假",
                "产品经理临时出差",
                "客户提出紧急需求需要插队",
                "服务器硬件故障",
                "测试环境不可用",
                "设计师工作负载过高延期交付",
                "运维团队进行系统升级",
                "关键设备需要维护"
            ],
            "severity_range": (1.0, 3.0)  # 延期1-3天
        },
        "communication": {
            "name": "沟通问题",
            "events": [
                "需求规格说明有歧义需要澄清",
                "设计稿延期交付",
                "跨部门协调困难",
                "客户反馈延迟",
                "需求变更需要重新评估",
                "会议时间冲突导致讨论延后",
                "关键决策人不在导致决策延迟",
                "文档更新不及时造成误解"
            ],
            "severity_range": (0.5, 1.5)
        },
        "external": {
            "name": "外部因素",
            "events": [
                "法定节假日",
                "停电维护",
                "网络故障",
                "办公楼电梯故障影响上班",
                "极端天气影响办公",
                "政策变化需要调整方案",
                "合作伙伴交付延期",
                "第三方服务商维护升级"
            ],
            "severity_range": (1.0, 5.0)  # 延期1-5天
        }
    }
    
    def __init__(self, seed: int = None):
        """
        初始化环境Agent
        
        Args:
            seed: 随机数种子，用于可复现的测试
        """
        if seed is not None:
            random.seed(seed)
        self.event_history = []
    
    def inject_events(
        self,
        day: int,
        tasks: List[Dict[str, Any]],
        probability: float = 0.2,
        enabled_event_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        注入随机干扰事件
        
        Args:
            day: 当前天数
            tasks: 当天执行的任务列表
            probability: 事件发生概率 (0.0-1.0)
            enabled_event_types: 启用的事件类型列表，None表示全部启用
            
        Returns:
            事件列表，每个事件包含时间戳、类型、描述、影响等信息
        """
        events = []
        
        # 如果没有任务在执行，不产生事件
        if not tasks:
            return events
        
        # 确定启用的事件类型
        if enabled_event_types is None:
            enabled_event_types = list(self.EVENT_TYPES.keys())
        else:
            # 验证事件类型
            enabled_event_types = [
                t for t in enabled_event_types 
                if t in self.EVENT_TYPES
            ]
        
        if not enabled_event_types:
            return events
        
        # 判断是否发生事件
        if random.random() < probability:
            # 随机选择事件类型
            event_type = random.choice(enabled_event_types)
            event_config = self.EVENT_TYPES[event_type]
            
            # 随机选择具体事件
            event_desc = random.choice(event_config["events"])
            
            # 计算事件影响
            impact = self._calculate_impact(event_type, event_config, tasks)
            
            # 生成事件时间戳
            event_hour = random.randint(9, 17)
            event_minute = random.choice([0, 15, 30, 45])
            timestamp_str = f"{day}d {event_hour:02d}:{event_minute:02d}"
            
            event = {
                "timestamp": timestamp_str,
                "day": day,
                "event_type": "env_event",
                "category": event_type,
                "category_name": event_config["name"],
                "role_name": "环境因素",
                "content": event_desc,
                "impact": impact,
                "affected_tasks": impact["affected_tasks"],
                "delay_days": impact["delay"],
                "severity": impact["severity"],
                "metadata": {
                    "event_id": f"ENV-{day}-{len(self.event_history) + 1}",
                    "probability_used": probability,
                    "random_seed": random.getstate()
                }
            }
            
            events.append(event)
            self.event_history.append(event)
        
        return events
    
    def _calculate_impact(
        self,
        event_type: str,
        event_config: Dict[str, Any],
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        计算事件影响
        
        Args:
            event_type: 事件类型
            event_config: 事件配置
            tasks: 任务列表
            
        Returns:
            影响信息字典
        """
        # 获取延期范围
        min_delay, max_delay = event_config["severity_range"]
        
        # 随机生成延期天数
        delay = round(random.uniform(min_delay, max_delay), 1)
        
        # 确定受影响的任务数量（1-3个任务，或全部任务如果任务数少于3）
        num_affected = min(len(tasks), random.randint(1, 3))
        
        # 随机选择受影响的任务
        affected_tasks = random.sample(tasks, k=num_affected)
        affected_task_ids = [t.get("task_id", t.get("id", "unknown")) for t in affected_tasks]
        
        # 确定严重程度
        if delay > 2.0:
            severity = "high"
        elif delay > 1.0:
            severity = "medium"
        else:
            severity = "low"
        
        return {
            "delay": delay,
            "affected_tasks": affected_task_ids,
            "affected_count": num_affected,
            "severity": severity,
            "description": f"预计延期 {delay} 天，影响 {num_affected} 个任务"
        }
    
    def get_event_summary(self) -> Dict[str, Any]:
        """
        获取所有事件的统计摘要
        
        Returns:
            统计信息字典
        """
        if not self.event_history:
            return {
                "total_events": 0,
                "total_delay": 0.0,
                "by_category": {},
                "by_severity": {}
            }
        
        total_delay = sum(e["delay_days"] for e in self.event_history)
        
        # 按类别统计
        by_category = {}
        for event in self.event_history:
            cat = event["category_name"]
            if cat not in by_category:
                by_category[cat] = {"count": 0, "total_delay": 0.0}
            by_category[cat]["count"] += 1
            by_category[cat]["total_delay"] += event["delay_days"]
        
        # 按严重程度统计
        by_severity = {}
        for event in self.event_history:
            sev = event["severity"]
            if sev not in by_severity:
                by_severity[sev] = {"count": 0, "total_delay": 0.0}
            by_severity[sev]["count"] += 1
            by_severity[sev]["total_delay"] += event["delay_days"]
        
        return {
            "total_events": len(self.event_history),
            "total_delay": round(total_delay, 1),
            "average_delay": round(total_delay / len(self.event_history), 1),
            "by_category": by_category,
            "by_severity": by_severity
        }
    
    def reset(self):
        """重置事件历史"""
        self.event_history = []
