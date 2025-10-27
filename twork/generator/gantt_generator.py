"""
甘特图生成器
使用matplotlib和plotly生成交互式甘特图
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json


class GanttGenerator:
    """甘特图生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.chart_data = None
    
    def generate(
        self,
        tasks: List[Dict[str, Any]],
        start_date: Optional[datetime] = None,
        critical_path: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        生成甘特图数据
        
        Args:
            tasks: 任务列表（包含duration_days）
            start_date: 项目开始日期
            critical_path: 关键路径任务ID列表
        
        Returns:
            甘特图数据字典
        """
        if not start_date:
            start_date = datetime.now()
        
        critical_path = critical_path or []
        
        # 计算每个任务的开始和结束日期
        task_schedule = self._calculate_schedule(tasks, start_date)
        
        # 构建甘特图数据
        chart_data = {
            "tasks": [],
            "project_start": start_date.isoformat(),
            "project_end": None,
            "critical_path": critical_path
        }
        
        max_end_date = start_date
        
        for task in task_schedule:
            task_id = task["task_id"]
            is_critical = task_id in critical_path
            
            chart_data["tasks"].append({
                "task_id": task_id,
                "task_name": task["task_name"],
                "start_date": task["start_date"].isoformat(),
                "end_date": task["end_date"].isoformat(),
                "duration_days": task["duration_days"],
                "assigned_to": task.get("assigned_to", "未分配"),
                "is_critical": is_critical,
                "dependencies": task.get("dependencies", [])
            })
            
            if task["end_date"] > max_end_date:
                max_end_date = task["end_date"]
        
        chart_data["project_end"] = max_end_date.isoformat()
        
        self.chart_data = chart_data
        return chart_data
    
    def _calculate_schedule(
        self,
        tasks: List[Dict[str, Any]],
        start_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        计算任务调度（考虑依赖关系）
        
        Args:
            tasks: 任务列表
            start_date: 开始日期
        
        Returns:
            带有日期的任务列表
        """
        # 任务ID到开始日期的映射
        task_start_dates = {}
        scheduled_tasks = []
        
        for task in tasks:
            task_id = task.get("task_id")
            dependencies = task.get("dependencies", [])
            duration = task.get("duration_days", 1)
            
            # 计算最早开始时间
            earliest_start = start_date
            
            # 考虑依赖任务
            for dep_id in dependencies:
                if dep_id in task_start_dates:
                    dep_end = task_start_dates[dep_id]["end_date"]
                    if dep_end > earliest_start:
                        earliest_start = dep_end
            
            # 计算结束日期
            end_date = earliest_start + timedelta(days=duration)
            
            task_start_dates[task_id] = {
                "start_date": earliest_start,
                "end_date": end_date
            }
            
            scheduled_tasks.append({
                **task,
                "start_date": earliest_start,
                "end_date": end_date
            })
        
        return scheduled_tasks
    
    def export_to_json(self, output_path: str) -> bool:
        """
        导出为JSON文件
        
        Args:
            output_path: 输出路径
        
        Returns:
            是否成功
        """
        if not self.chart_data:
            return False
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.chart_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def get_html_representation(self) -> str:
        """
        获取HTML表示（简化版）
        
        Returns:
            HTML字符串
        """
        if not self.chart_data:
            return "<p>无甘特图数据</p>"
        
        html = "<div class='gantt-chart'>"
        html += f"<h3>项目甘特图</h3>"
        html += f"<p>项目周期: {self.chart_data['project_start']} 至 {self.chart_data['project_end']}</p>"
        html += "<table border='1'>"
        html += "<tr><th>任务ID</th><th>任务名称</th><th>开始日期</th><th>结束日期</th><th>工期</th><th>负责人</th></tr>"
        
        for task in self.chart_data["tasks"]:
            critical_class = "critical" if task["is_critical"] else ""
            html += f"<tr class='{critical_class}'>"
            html += f"<td>{task['task_id']}</td>"
            html += f"<td>{task['task_name']}</td>"
            html += f"<td>{task['start_date']}</td>"
            html += f"<td>{task['end_date']}</td>"
            html += f"<td>{task['duration_days']}天</td>"
            html += f"<td>{task['assigned_to']}</td>"
            html += "</tr>"
        
        html += "</table></div>"
        
        return html
