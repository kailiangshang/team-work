"""
文档生成器

生成PDF或Markdown格式的任务分解文档。
"""

from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime
from ..utils.logger import get_logger
from ..utils.file_handler import FilePermissionHandler

logger = get_logger("document_generator")


class DocumentGenerator:
    """文档生成器"""
    
    def __init__(self):
        """初始化文档生成器"""
        logger.info("文档生成器初始化完成")
    
    def generate_markdown(
        self,
        requirements: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        agents: List[Dict[str, Any]],
        output_path: str
    ) -> str:
        """
        生成Markdown文档
        
        Args:
            requirements: 需求信息
            tasks: 任务列表
            agents: 角色列表
            output_path: 输出路径
            
        Returns:
            生成的文件路径
        """
        logger.info(f"开始生成Markdown文档: {output_path}")
        
        # 构建文档内容
        content = self._build_markdown_content(requirements, tasks, agents)
        
        # 使用安全写入
        success = FilePermissionHandler.safe_write_file(
            file_path=output_path,
            content=content,
            mode='w',
            file_permission=0o644
        )
        
        if not success:
            raise IOError(f"无法写入文件: {output_path}")
        
        logger.info(f"Markdown文档生成完成: {output_path}")
        
        return output_path
    
    def _build_markdown_content(
        self,
        requirements: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        agents: List[Dict[str, Any]]
    ) -> str:
        """构建Markdown内容"""
        
        lines = []
        
        # 标题
        lines.append(f"# {requirements.get('project_name', '项目')}任务分解文档\n")
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append("---\n")
        
        # 项目概览
        lines.append("## 项目概览\n")
        lines.append(f"**项目名称**: {requirements.get('project_name', 'N/A')}\n")
        lines.append(f"**项目描述**: {requirements.get('project_description', 'N/A')}\n")
        
        # 主要目标
        objectives = requirements.get('main_objectives', [])
        if objectives:
            lines.append("\n**主要目标**:\n")
            for obj in objectives:
                lines.append(f"- {obj}\n")
        
        # 关键需求
        key_reqs = requirements.get('key_requirements', [])
        if key_reqs:
            lines.append("\n**关键需求**:\n")
            for req in key_reqs:
                lines.append(f"- {req}\n")
        
        # 约束条件
        constraints = requirements.get('constraints', [])
        if constraints:
            lines.append("\n**约束条件**:\n")
            for constraint in constraints:
                lines.append(f"- {constraint}\n")
        
        # 任务列表
        lines.append("\n---\n")
        lines.append("## 任务列表\n")
        
        total_days = sum(task.get("duration_days", 0) for task in tasks)
        lines.append(f"\n**预计总工期**: {total_days} 天\n")
        lines.append(f"**任务总数**: {len(tasks)}\n")
        
        for i, task in enumerate(tasks, 1):
            lines.append(f"\n### 任务{i}: {task.get('task_name', 'N/A')}\n")
            lines.append(f"- **任务ID**: {task.get('task_id', 'N/A')}\n")
            lines.append(f"- **描述**: {task.get('description', 'N/A')}\n")
            
            skills = task.get('required_skills', [])
            if skills:
                lines.append(f"- **所需能力**: {', '.join(skills)}\n")
            
            lines.append(f"- **人员类型**: {task.get('person_type', 'N/A')}\n")
            
            tools = task.get('tools_needed', [])
            if tools:
                lines.append(f"- **所需工具**: {', '.join(tools)}\n")
            
            lines.append(f"- **工期**: {task.get('duration_days', 0)} 天\n")
            lines.append(f"- **优先级**: {task.get('priority', 'Medium')}\n")
            
            deps = task.get('dependencies', [])
            if deps:
                lines.append(f"- **依赖任务**: {', '.join(deps)}\n")
        
        # 角色能力矩阵
        lines.append("\n---\n")
        lines.append("## 角色能力矩阵\n")
        
        lines.append("\n| 角色 | 核心能力 | 参与任务 |\n")
        lines.append("|------|---------|----------|\n")
        
        for agent in agents:
            role_name = agent.get('role_name', 'N/A')
            capabilities = ', '.join(agent.get('capabilities', []))
            assigned_tasks = ', '.join(agent.get('assigned_tasks', []))
            lines.append(f"| {role_name} | {capabilities} | {assigned_tasks} |\n")
        
        # 交付物
        lines.append("\n---\n")
        lines.append("## 预期交付物\n")
        
        deliverables = requirements.get('expected_deliverables', [])
        if deliverables:
            for deliverable in deliverables:
                lines.append(f"- {deliverable}\n")
        else:
            lines.append("- 待定\n")
        
        return "".join(lines)
