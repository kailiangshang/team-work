"""
项目服务

处理项目相关的业务逻辑。
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import json
from pathlib import Path
from ..models.project import Project
from ..models.task import Task
from ..models.agent import Agent
from ..models.simulation_log import SimulationLog
from ..config import settings
from twork.parser import DocumentLoader, RequirementExtractor, TaskDecomposer
from twork.agent import RoleGenerator, SimulationEngine
from twork.generator import DocumentGenerator, CSVExporter, GraphBuilder
from twork.llm import OpenAIAdapter


class ProjectService:
    """项目服务"""
    
    def __init__(self, db: Session):
        """初始化项目服务"""
        self.db = db
        self.llm = self._init_llm()
    
    def _init_llm(self) -> OpenAIAdapter:
        """初始化LLM适配器"""
        return OpenAIAdapter(
            api_base_url=settings.llm_api_base_url,
            api_key=settings.llm_api_key,
            model_name=settings.llm_model_name,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            timeout=settings.llm_timeout,
        )
    
    def create_project(self, name: str, document_path: str) -> Project:
        """
        创建项目
        
        Args:
            name: 项目名称
            document_path: 文档路径
            
        Returns:
            项目对象
        """
        project = Project(
            name=name,
            document_path=document_path,
            status="parsing"
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def parse_document(self, project_id: int) -> Dict[str, Any]:
        """
        解析文档
        
        Args:
            project_id: 项目ID
            
        Returns:
            解析结果
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"项目不存在: {project_id}")
        
        # 加载文档
        loader = DocumentLoader()
        doc_data = loader.load(project.document_path)
        
        # 提取需求
        extractor = RequirementExtractor(self.llm)
        requirements = extractor.extract(doc_data["content"])
        
        # 保存需求到数据库
        project.requirements = json.dumps(requirements, ensure_ascii=False)
        project.name = requirements.get("project_name", project.name)
        project.status = "decomposing"
        self.db.commit()
        
        return requirements
    
    def decompose_tasks(self, project_id: int) -> List[Dict[str, Any]]:
        """
        拆解任务（修复版）
        
        Args:
            project_id: 项目ID
            
        Returns:
            任务列表（字典格式）
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"项目不存在: {project_id}")
        
        # 获取需求
        requirements = json.loads(project.requirements)
        
        # 拆解任务
        decomposer = TaskDecomposer(self.llm)
        task_data = decomposer.decompose(requirements)
        
        # 删除旧任务（如果重新拆解）
        self.db.query(Task).filter(Task.project_id == project_id).delete()
        
        # 保存任务到数据库
        tasks = task_data.get("tasks", [])
        saved_tasks = []
        
        for task_dict in tasks:
            task = Task(
                project_id=project_id,
                task_id=task_dict["task_id"],
                task_name=task_dict["task_name"],
                description=task_dict.get("description", ""),
                required_skills=task_dict.get("required_skills", []),
                person_type=task_dict.get("person_type", ""),
                tools_needed=task_dict.get("tools_needed", []),
                duration_days=int(task_dict.get("duration_days", 1)),  # 确保类型转换
                priority=task_dict.get("priority", "Medium"),
                dependencies=task_dict.get("dependencies", [])
            )
            self.db.add(task)
            saved_tasks.append(task_dict)  # 使用原始字典返回
        
        project.total_days = int(task_data.get("total_estimated_days", 0))
        project.status = "ready_for_simulation"
        
        # 提交事务
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"保存任务失败: {str(e)}")
        
        return saved_tasks  # 返回字典列表而非ORM对象
    
    def generate_agents(self, project_id: int) -> List[Dict[str, Any]]:
        """
        生成Agent
        
        Args:
            project_id: 项目ID
            
        Returns:
            Agent列表
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"项目不存在: {project_id}")
        
        # 获取任务列表
        tasks = self.db.query(Task).filter(Task.project_id == project_id).all()
        task_dicts = [
            {
                "task_id": t.task_id,
                "task_name": t.task_name,
                "person_type": t.person_type,
                "required_skills": t.required_skills,
            }
            for t in tasks
        ]
        
        # 生成角色
        generator = RoleGenerator(self.llm)
        agents_list = generator.generate(task_dicts)
        
        # 保存到数据库
        for agent_dict in agents_list:
            agent = Agent(
                project_id=project_id,
                agent_id=agent_dict["agent_id"],
                role_name=agent_dict["role_name"],
                role_type=agent_dict.get("role_type", ""),
                capabilities=agent_dict.get("capabilities", []),
                assigned_tasks=agent_dict.get("assigned_tasks", []),
                personality=agent_dict.get("personality", ""),
                system_prompt=agent_dict.get("system_prompt", ""),
                tools=agent_dict.get("tools", [])
            )
            self.db.add(agent)
        
        self.db.commit()
        
        return agents_list
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """获取项目"""
        return self.db.query(Project).filter(Project.id == project_id).first()
    
    def list_projects(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """列出项目"""
        return self.db.query(Project).offset(skip).limit(limit).all()
    
    def build_task_tree(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        构建任务树结构
        
        Args:
            tasks: 任务列表
            
        Returns:
            任务树字典
        """
        task_dict = {task["task_id"]: task for task in tasks}
        tree = {}
        
        for task in tasks:
            task_id = task["task_id"]
            tree[task_id] = {
                "task_id": task_id,
                "task_name": task["task_name"],
                "description": task.get("description", ""),
                "duration_days": task.get("duration_days", 0),
                "dependencies": task.get("dependencies", []),
                "children": [],
                "metadata": {
                    "required_skills": task.get("required_skills", []),
                    "priority": task.get("priority", "Medium")
                }
            }
        
        # 构建父子关系（基于依赖关系）
        for task_id, node in tree.items():
            for dep_id in node["dependencies"]:
                if dep_id in tree:
                    tree[dep_id]["children"].append(task_id)
        
        return tree
