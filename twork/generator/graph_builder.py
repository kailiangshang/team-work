"""
图谱构建器

构建任务关系图谱并可视化。
"""

from typing import Dict, Any, List, Tuple
from pathlib import Path
import json
from ..utils.logger import get_logger
from ..utils.file_handler import FilePermissionHandler

logger = get_logger("graph_builder")


class GraphBuilder:
    """图谱构建器"""
    
    def __init__(self):
        """初始化图谱构建器"""
        logger.info("图谱构建器初始化完成")
    
    def build_triplets(
        self,
        tasks: List[Dict[str, Any]],
        agents: List[Dict[str, Any]]
    ) -> List[Tuple[str, str, str]]:
        """
        构建三元组
        
        Args:
            tasks: 任务列表
            agents: 角色列表
            
        Returns:
            三元组列表: [(主体, 关系, 客体), ...]
        """
        logger.info("开始构建三元组")
        
        triplets = []
        
        # 构建角色-任务关系
        for agent in agents:
            role_name = agent.get("role_name", "")
            assigned_tasks = agent.get("assigned_tasks", [])
            
            for task_id in assigned_tasks:
                triplets.append((role_name, "负责", task_id))
        
        # 构建任务-依赖关系
        for task in tasks:
            task_id = task.get("task_id", "")
            dependencies = task.get("dependencies", [])
            
            for dep_id in dependencies:
                triplets.append((task_id, "依赖于", dep_id))
        
        # 构建任务-优先级关系
        for task in tasks:
            task_id = task.get("task_id", "")
            priority = task.get("priority", "Medium")
            
            triplets.append((task_id, "优先级", priority))
        
        logger.info(f"三元组构建完成: 共{len(triplets)}个三元组")
        
        return triplets
    
    def export_triplets(
        self,
        triplets: List[Tuple[str, str, str]],
        output_path: str
    ) -> str:
        """
        导出三元组到JSON文件
        
        Args:
            triplets: 三元组列表
            output_path: 输出路径
            
        Returns:
            生成的文件路径
        """
        logger.info(f"开始导出三元组: {output_path}")
        
        # 转换为字典格式
        triplets_data = [
            {
                "subject": t[0],
                "relation": t[1],
                "object": t[2]
            }
            for t in triplets
        ]
        
        # 使用安全写入
        json_content = json.dumps(triplets_data, ensure_ascii=False, indent=2)
        
        success = FilePermissionHandler.safe_write_file(
            file_path=output_path,
            content=json_content,
            mode='w',
            file_permission=0o644
        )
        
        if not success:
            raise IOError(f"无法写入文件: {output_path}")
        
        logger.info(f"三元组导出完成: {output_path}")
        
        return output_path
    
    def generate_mermaid(
        self,
        tasks: List[Dict[str, Any]],
        agents: List[Dict[str, Any]]
    ) -> str:
        """
        生成Mermaid格式的图谱代码
        
        Args:
            tasks: 任务列表
            agents: 角色列表
            
        Returns:
            Mermaid代码字符串
        """
        logger.info("开始生成Mermaid图谱")
        
        lines = ["graph LR"]
        
        # 添加角色-任务关系
        for agent in agents:
            role_name = agent.get("role_name", "")
            # 使用中文ID需要用引号包裹
            role_id = f"A_{agent.get('agent_id', '')}"
            lines.append(f"    {role_id}[{role_name}]")
            
            assigned_tasks = agent.get("assigned_tasks", [])
            for task_id in assigned_tasks:
                lines.append(f"    {role_id} -->|负责| {task_id}")
        
        # 添加任务节点和依赖关系
        for task in tasks:
            task_id = task.get("task_id", "")
            task_name = task.get("task_name", "")
            priority = task.get("priority", "Medium")
            
            # 根据优先级设置样式
            if priority == "High":
                lines.append(f"    {task_id}[{task_name}]:::high")
            elif priority == "Low":
                lines.append(f"    {task_id}[{task_name}]:::low")
            else:
                lines.append(f"    {task_id}[{task_name}]")
            
            # 添加依赖关系
            dependencies = task.get("dependencies", [])
            for dep_id in dependencies:
                lines.append(f"    {dep_id} -.->|依赖| {task_id}")
        
        # 添加样式定义
        lines.append("")
        lines.append("    classDef high fill:#ff6b6b")
        lines.append("    classDef low fill:#90ee90")
        
        mermaid_code = "\n".join(lines)
        
        logger.info("Mermaid图谱生成完成")
        
        return mermaid_code
    
    def export_mermaid(
        self,
        tasks: List[Dict[str, Any]],
        agents: List[Dict[str, Any]],
        output_path: str
    ) -> str:
        """
        导出Mermaid图谱到文件
        
        Args:
            tasks: 任务列表
            agents: 角色列表
            output_path: 输出路径
            
        Returns:
            生成的文件路径
        """
        logger.info(f"开始导出Mermaid图谱: {output_path}")
        
        mermaid_code = self.generate_mermaid(tasks, agents)
        
        # 构建文件内容
        content = f"```mermaid\n{mermaid_code}\n```\n"
        
        # 使用安全写入
        success = FilePermissionHandler.safe_write_file(
            file_path=output_path,
            content=content,
            mode='w',
            file_permission=0o644
        )
        
        if not success:
            raise IOError(f"无法写入文件: {output_path}")
        
        logger.info(f"Mermaid图谱导出完成: {output_path}")
        
        return output_path
