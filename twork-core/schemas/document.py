"""文档相关数据结构"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime


class DocumentType(Enum):
    """文档类型"""
    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "markdown"
    TXT = "txt"
    PPTX = "pptx"
    UNKNOWN = "unknown"


@dataclass
class Document:
    """文档"""
    id: str
    filename: str
    file_type: DocumentType
    file_size: int = 0
    file_path: str = ""
    
    # 时间信息
    uploaded_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # 状态
    is_parsed: bool = False
    parse_error: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "filename": self.filename,
            "file_type": self.file_type.value,
            "file_size": self.file_size,
            "file_path": self.file_path,
            "uploaded_at": self.uploaded_at,
            "is_parsed": self.is_parsed,
            "parse_error": self.parse_error,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        return cls(
            id=data["id"],
            filename=data["filename"],
            file_type=DocumentType(data.get("file_type", "unknown")),
            file_size=data.get("file_size", 0),
            file_path=data.get("file_path", ""),
            uploaded_at=data.get("uploaded_at", datetime.now().isoformat()),
            is_parsed=data.get("is_parsed", False),
            parse_error=data.get("parse_error", ""),
        )


@dataclass
class ExtractedEntity:
    """提取的实体"""
    name: str
    entity_type: str                  # task/role/skill/tool/constraint
    description: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "entity_type": self.entity_type,
            "description": self.description,
            "properties": self.properties,
        }


@dataclass
class ExtractedRelation:
    """提取的关系"""
    source: str
    target: str
    relation_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "relation_type": self.relation_type,
            "properties": self.properties,
        }


@dataclass
class ParsedDocument:
    """解析后的文档"""
    document_id: str
    project_id: str
    
    # 原始内容
    raw_content: str = ""
    
    # 提取的信息
    project_name: str = ""
    project_description: str = ""
    
    # 提取的实体
    tasks: List[ExtractedEntity] = field(default_factory=list)
    roles: List[ExtractedEntity] = field(default_factory=list)
    skills: List[ExtractedEntity] = field(default_factory=list)
    tools: List[ExtractedEntity] = field(default_factory=list)
    constraints: List[ExtractedEntity] = field(default_factory=list)
    deliverables: List[ExtractedEntity] = field(default_factory=list)
    
    # 提取的关系
    relations: List[ExtractedRelation] = field(default_factory=list)
    
    # 元数据
    parsed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    parse_version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "project_id": self.project_id,
            "raw_content": self.raw_content,
            "project_name": self.project_name,
            "project_description": self.project_description,
            "tasks": [t.to_dict() for t in self.tasks],
            "roles": [r.to_dict() for r in self.roles],
            "skills": [s.to_dict() for s in self.skills],
            "tools": [t.to_dict() for t in self.tools],
            "constraints": [c.to_dict() for c in self.constraints],
            "deliverables": [d.to_dict() for d in self.deliverables],
            "relations": [r.to_dict() for r in self.relations],
            "parsed_at": self.parsed_at,
            "parse_version": self.parse_version,
        }