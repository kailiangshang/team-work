"""实体提取器 - 使用LLM从文档中提取结构化信息"""
import json
import re
from typing import List, Dict, Any
import logging

from ..schemas.document import ParsedDocument, ExtractedEntity, ExtractedRelation
from ..llm.base import BaseLLM, ChatMessage
from ..llm.prompts import PromptTemplates

logger = logging.getLogger(__name__)


class EntityExtractor:
    """实体提取器
    
    使用 LLM 从文档内容中提取结构化信息：
    - 任务
    - 角色
    - 技能
    - 工具
    - 约束条件
    - 交付物
    """
    
    def __init__(self, llm: BaseLLM):
        self.llm = llm
    
    def extract(
        self, 
        document_id: str, 
        project_id: str, 
        content: str
    ) -> ParsedDocument:
        """从文档内容中提取实体
        
        Args:
            document_id: 文档ID
            project_id: 项目ID
            content: 文档内容
        
        Returns:
            解析后的文档
        """
        parsed_doc = ParsedDocument(
            document_id=document_id,
            project_id=project_id,
            raw_content=content,
        )
        
        # 使用 LLM 提取结构化信息
        messages = [
            ChatMessage(role="system", content=PromptTemplates.DOCUMENT_PARSER_SYSTEM),
            ChatMessage(role="user", content=PromptTemplates.DOCUMENT_PARSER_TEMPLATE.format(
                document_content=content
            )),
        ]
        
        try:
            response = self.llm.chat(messages)
            result = self._parse_llm_response(response.content)
            
            if result:
                parsed_doc.project_name = result.get("project_name", "")
                parsed_doc.project_description = result.get("project_description", "")
                
                # 解析任务
                for task_data in result.get("tasks", []):
                    entity = ExtractedEntity(
                        name=task_data.get("name", ""),
                        entity_type="task",
                        description=task_data.get("description", ""),
                        properties={
                            "level": task_data.get("level", 1),
                            "duration_days": task_data.get("duration_days", 1),
                            "complexity": task_data.get("complexity", 3),
                            "priority": task_data.get("priority", 3),
                            "dependencies": task_data.get("dependencies", []),
                            "required_skills": task_data.get("required_skills", []),
                            "subtasks": task_data.get("subtasks", []),
                        },
                    )
                    parsed_doc.tasks.append(entity)
                
                # 解析角色
                for role_data in result.get("roles", []):
                    entity = ExtractedEntity(
                        name=role_data.get("name", ""),
                        entity_type="role",
                        description=role_data.get("description", ""),
                        properties={
                            "role_type": role_data.get("role_type", ""),
                            "skills": role_data.get("skills", []),
                            "capabilities": role_data.get("capabilities", []),
                        },
                    )
                    parsed_doc.roles.append(entity)
                
                # 解析技能
                for skill_name in result.get("skills", []):
                    entity = ExtractedEntity(
                        name=skill_name,
                        entity_type="skill",
                    )
                    parsed_doc.skills.append(entity)
                
                # 解析工具
                for tool_name in result.get("tools", []):
                    entity = ExtractedEntity(
                        name=tool_name,
                        entity_type="tool",
                    )
                    parsed_doc.tools.append(entity)
                
                # 解析约束
                for constraint_data in result.get("constraints", []):
                    entity = ExtractedEntity(
                        name=constraint_data.get("type", "unknown"),
                        entity_type="constraint",
                        description=constraint_data.get("description", ""),
                    )
                    parsed_doc.constraints.append(entity)
                
                # 解析交付物
                for deliverable_name in result.get("deliverables", []):
                    entity = ExtractedEntity(
                        name=deliverable_name,
                        entity_type="deliverable",
                    )
                    parsed_doc.deliverables.append(entity)
        
        except Exception as e:
            logger.error(f"Failed to extract entities: {e}")
        
        return parsed_doc
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """解析LLM响应中的JSON"""
        # 尝试提取JSON块
        json_patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'\{.*\}',
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1) if '```' in pattern else match.group(0)
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue
        
        logger.warning("Failed to parse JSON from LLM response")
        return {}
    
    def extract_dependencies(
        self, 
        tasks: List[ExtractedEntity]
    ) -> List[ExtractedRelation]:
        """提取任务依赖关系"""
        relations = []
        
        for task in tasks:
            deps = task.properties.get("dependencies", [])
            for dep in deps:
                relation = ExtractedRelation(
                    source=task.name,
                    target=dep,
                    relation_type="depends_on",
                )
                relations.append(relation)
        
        return relations
    
    def extract_skill_requirements(
        self, 
        tasks: List[ExtractedEntity]
    ) -> List[ExtractedRelation]:
        """提取任务技能需求"""
        relations = []
        
        for task in tasks:
            skills = task.properties.get("required_skills", [])
            for skill in skills:
                relation = ExtractedRelation(
                    source=task.name,
                    target=skill,
                    relation_type="requires",
                )
                relations.append(relation)
        
        return relations