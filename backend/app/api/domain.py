"""
领域识别API
提供文档领域识别和模板管理接口

注意：此文件可能已废弃，新架构请使用 twork.parser.StructureUnderstandFactory
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel

from ..database import get_db
from ..models.project import Project
from ..models.domain_config import DomainConfig

# TODO: 以下模块已重构，需要更新导入
# from twork.parser.domain_classifier import DomainClassifier
# from twork.parser.context_template_manager import ContextTemplateManager

# 临时禁用，等待更新到新架构
RAISE_NOT_IMPLEMENTED = True


router = APIRouter(prefix="/api/domain", tags=["domain"])

# 初始化工具（已禁用，等待重构）
# domain_classifier = DomainClassifier()
# template_manager = ContextTemplateManager()


# Pydantic模型
class DomainClassifyRequest(BaseModel):
    """领域分类请求"""
    project_id: int
    user_selected_domain: Optional[str] = None


class DomainClassifyResponse(BaseModel):
    """领域分类响应"""
    domain_type: str
    confidence: float
    keywords: List[str]
    template_id: str
    all_scores: dict


class TemplateInfoResponse(BaseModel):
    """模板信息响应"""
    domain_type: str
    template_id: str
    focus_points: List[str]
    task_types: List[str]
    role_types: List[str]
    default_config: dict


@router.post("/classify", response_model=DomainClassifyResponse)
def classify_domain(
    request: DomainClassifyRequest,
    db: Session = Depends(get_db)
):
    """
    对项目文档进行领域分类
    
    注意：此API已废弃，请使用新架构的 StructureUnderstandFactory
    
    Args:
        request: 分类请求（包含project_id和可选的用户选择）
        db: 数据库会话
    
    Returns:
        领域分类结果
    """
    if RAISE_NOT_IMPLEMENTED:
        raise HTTPException(
            status_code=501,
            detail="此API已废弃，请使用新架构的 twork.parser.StructureUnderstandFactory"
        )
    # 查询项目
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 读取文档内容
    if not project.document_path:
        raise HTTPException(status_code=400, detail="项目未上传文档")
    
    try:
        with open(project.document_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文档失败: {str(e)}")
    
    # 执行领域分类
    result = domain_classifier.classify(
        content=content,
        user_selected_domain=request.user_selected_domain
    )
    
    # 获取模板信息
    template_info = template_manager.get_template_info(result["template_id"])
    
    # 提取上下文信息
    extracted_context = template_manager.extract_context(
        content=content,
        template_id=result["template_id"]
    )
    
    # 保存或更新领域配置
    domain_config = db.query(DomainConfig).filter(
        DomainConfig.project_id == request.project_id
    ).first()
    
    if domain_config:
        # 更新现有配置
        domain_config.domain_type = result["domain_type"]
        domain_config.confidence = result["confidence"]
        domain_config.keywords = result["keywords"]
        domain_config.template_id = result["template_id"]
        domain_config.template_config = template_info
        domain_config.user_selected_domain = request.user_selected_domain
        domain_config.extracted_context = extracted_context
    else:
        # 创建新配置
        domain_config = DomainConfig(
            project_id=request.project_id,
            domain_type=result["domain_type"],
            confidence=result["confidence"],
            keywords=result["keywords"],
            template_id=result["template_id"],
            template_config=template_info,
            user_selected_domain=request.user_selected_domain,
            extracted_context=extracted_context
        )
        db.add(domain_config)
    
    db.commit()
    db.refresh(domain_config)
    
    return DomainClassifyResponse(**result)


@router.get("/templates", response_model=List[TemplateInfoResponse])
def get_all_templates():
    """
    获取所有可用的领域模板
    
    Returns:
        模板列表
    """
    templates = template_manager.get_all_templates()
    
    result = []
    for template in templates:
        result.append(TemplateInfoResponse(
            domain_type=template.domain_type,
            template_id=template.template_id,
            focus_points=template.focus_points,
            task_types=template.task_types,
            role_types=template.role_types,
            default_config=template.default_config
        ))
    
    return result


@router.get("/templates/{template_id}", response_model=TemplateInfoResponse)
def get_template(template_id: str):
    """
    获取指定模板的详细信息
    
    Args:
        template_id: 模板ID
    
    Returns:
        模板详细信息
    """
    template_info = template_manager.get_template_info(template_id)
    
    if not template_info:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    return TemplateInfoResponse(**template_info)


@router.get("/supported-domains", response_model=List[str])
def get_supported_domains():
    """
    获取支持的领域类型列表
    
    Returns:
        领域类型列表
    """
    return domain_classifier.get_supported_domains()


@router.get("/config/{project_id}")
def get_domain_config(project_id: int, db: Session = Depends(get_db)):
    """
    获取项目的领域配置
    
    Args:
        project_id: 项目ID
        db: 数据库会话
    
    Returns:
        领域配置信息
    """
    domain_config = db.query(DomainConfig).filter(
        DomainConfig.project_id == project_id
    ).first()
    
    if not domain_config:
        raise HTTPException(status_code=404, detail="该项目尚未进行领域识别")
    
    return domain_config.to_dict()
