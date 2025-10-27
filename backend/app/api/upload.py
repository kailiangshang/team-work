"""
上传API

处理文档上传相关的API请求。
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import traceback
from ..database import get_db
from ..services.project_service import ProjectService
from ..config import settings
from twork.utils.logger import get_logger

router = APIRouter()
logger = get_logger("upload_api")


@router.post("/document")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传需求文档
    
    Args:
        file: 上传的文件
        db: 数据库会话
        
    Returns:
        项目ID和解析结果
    """
    try:
        logger.info(f"开始上传文档: {file.filename}")
        
        # 验证文件类型
        allowed_extensions = [".pdf", ".md", ".txt", ".docx"]
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            logger.warning(f"不支持的文件类型: {file_ext}")
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file_ext}。支持的类型: {', '.join(allowed_extensions)}"
            )
        
        # 验证文件大小
        file.file.seek(0, 2)  # 移到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重置到开始
        
        max_size = settings.max_upload_size_mb * 1024 * 1024
        if file_size > max_size:
            logger.warning(f"文件过大: {file_size / 1024 / 1024:.2f}MB")
            raise HTTPException(
                status_code=400,
                detail=f"文件过大: {file_size / 1024 / 1024:.2f}MB，最大允许: {settings.max_upload_size_mb}MB"
            )
        
        # 保存文件
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        logger.info(f"保存文件到: {file_path}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"文件保存成功: {file_path}")
        
        # 创建项目
        service = ProjectService(db)
        project = service.create_project(
            name=file.filename,
            document_path=str(file_path)
        )
        
        logger.info(f"项目创建成功: project_id={project.id}")
        
        # 解析文档
        logger.info(f"开始解析文档: project_id={project.id}")
        requirements = service.parse_document(project.id)
        
        logger.info(f"文档解析成功: project_id={project.id}")
        
        # 生成解析结果文件
        output_dir = Path(settings.output_dir) / f"project_{project.id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存解析结果为Markdown文件
        requirements_md_path = output_dir / "requirements.md"
        with open(requirements_md_path, "w", encoding="utf-8") as f:
            f.write("# 需求解析结果\n\n")
            if isinstance(requirements, dict):
                for key, value in requirements.items():
                    f.write(f"## {key}\n\n")
                    if isinstance(value, list):
                        for item in value:
                            f.write(f"- {item}\n")
                    else:
                        f.write(f"{value}\n\n")
            else:
                f.write(str(requirements))
        
        logger.info(f"解析结果已保存: {requirements_md_path}")
        
        return {
            "project_id": project.id,
            "requirements": requirements,
            "files": {
                "requirements_md": str(requirements_md_path)
            },
            "status": "success"
        }
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"上传文档失败: {str(e)}")
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"上传失败: {str(e)}"
        )
