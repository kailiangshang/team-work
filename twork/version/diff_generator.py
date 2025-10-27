"""
Diff生成器
生成两个版本之间的差异对比
"""

from typing import Dict, List, Any, Optional


class DiffGenerator:
    """版本差异生成器"""
    
    def __init__(self):
        """初始化生成器"""
        pass
    
    def generate_diff(
        self,
        version1: Dict[str, Any],
        version2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成两个版本的差异
        
        Args:
            version1: 版本1数据
            version2: 版本2数据
        
        Returns:
            差异报告
        """
        diff_report = {
            "tasks_diff": self._diff_tasks(
                version1.get("tasks", []),
                version2.get("tasks", [])
            ),
            "agents_diff": self._diff_agents(
                version1.get("agents", []),
                version2.get("agents", [])
            ),
            "config_diff": self._diff_config(
                version1.get("config", {}),
                version2.get("config", {})
            ),
            "summary": {}
        }
        
        # 生成摘要
        diff_report["summary"] = self._generate_summary(diff_report)
        
        return diff_report
    
    def _diff_tasks(
        self,
        tasks1: List[Dict],
        tasks2: List[Dict]
    ) -> Dict[str, List]:
        """对比任务差异"""
        task1_ids = {t["task_id"]: t for t in tasks1}
        task2_ids = {t["task_id"]: t for t in tasks2}
        
        added = []
        removed = []
        modified = []
        
        # 找出新增的任务
        for task_id in task2_ids:
            if task_id not in task1_ids:
                added.append({
                    "task_id": task_id,
                    "task_name": task2_ids[task_id].get("task_name")
                })
        
        # 找出删除的任务
        for task_id in task1_ids:
            if task_id not in task2_ids:
                removed.append({
                    "task_id": task_id,
                    "task_name": task1_ids[task_id].get("task_name")
                })
        
        # 找出修改的任务
        for task_id in task1_ids:
            if task_id in task2_ids:
                changes = self._compare_task(
                    task1_ids[task_id],
                    task2_ids[task_id]
                )
                if changes:
                    modified.append({
                        "task_id": task_id,
                        "changes": changes
                    })
        
        return {
            "added": added,
            "removed": removed,
            "modified": modified
        }
    
    def _compare_task(
        self,
        task1: Dict,
        task2: Dict
    ) -> List[str]:
        """比较单个任务的变化"""
        changes = []
        
        # 检查关键字段
        if task1.get("task_name") != task2.get("task_name"):
            changes.append(f"名称: '{task1.get('task_name')}' → '{task2.get('task_name')}'")
        
        if task1.get("duration_days") != task2.get("duration_days"):
            changes.append(
                f"工期: {task1.get('duration_days')}天 → {task2.get('duration_days')}天"
            )
        
        if task1.get("dependencies") != task2.get("dependencies"):
            changes.append("依赖关系发生变化")
        
        return changes
    
    def _diff_agents(
        self,
        agents1: List[Dict],
        agents2: List[Dict]
    ) -> Dict[str, List]:
        """对比Agent差异"""
        agent1_names = {a["name"]: a for a in agents1}
        agent2_names = {a["name"]: a for a in agents2}
        
        added = [name for name in agent2_names if name not in agent1_names]
        removed = [name for name in agent1_names if name not in agent2_names]
        
        return {
            "added": added,
            "removed": removed
        }
    
    def _diff_config(
        self,
        config1: Dict,
        config2: Dict
    ) -> List[str]:
        """对比配置差异"""
        changes = []
        
        for key in set(config1.keys()) | set(config2.keys()):
            val1 = config1.get(key)
            val2 = config2.get(key)
            
            if val1 != val2:
                changes.append(f"{key}: {val1} → {val2}")
        
        return changes
    
    def _generate_summary(self, diff_report: Dict) -> Dict[str, Any]:
        """生成差异摘要"""
        tasks_diff = diff_report["tasks_diff"]
        agents_diff = diff_report["agents_diff"]
        
        return {
            "total_task_changes": (
                len(tasks_diff["added"]) +
                len(tasks_diff["removed"]) +
                len(tasks_diff["modified"])
            ),
            "tasks_added": len(tasks_diff["added"]),
            "tasks_removed": len(tasks_diff["removed"]),
            "tasks_modified": len(tasks_diff["modified"]),
            "agents_added": len(agents_diff["added"]),
            "agents_removed": len(agents_diff["removed"]),
            "config_changes": len(diff_report["config_diff"])
        }
    
    def format_diff_text(self, diff_report: Dict) -> str:
        """格式化差异为文本"""
        text = "版本差异报告\n"
        text += "=" * 60 + "\n\n"
        
        # 摘要
        summary = diff_report["summary"]
        text += f"总变更数: {summary['total_task_changes']}\n"
        text += f"- 新增任务: {summary['tasks_added']}\n"
        text += f"- 删除任务: {summary['tasks_removed']}\n"
        text += f"- 修改任务: {summary['tasks_modified']}\n\n"
        
        # 详细变更
        tasks_diff = diff_report["tasks_diff"]
        
        if tasks_diff["added"]:
            text += "【新增任务】\n"
            for task in tasks_diff["added"]:
                text += f"+ {task['task_id']}: {task['task_name']}\n"
            text += "\n"
        
        if tasks_diff["removed"]:
            text += "【删除任务】\n"
            for task in tasks_diff["removed"]:
                text += f"- {task['task_id']}: {task['task_name']}\n"
            text += "\n"
        
        if tasks_diff["modified"]:
            text += "【修改任务】\n"
            for task in tasks_diff["modified"]:
                text += f"~ {task['task_id']}:\n"
                for change in task["changes"]:
                    text += f"  {change}\n"
            text += "\n"
        
        return text
