"""
图谱可视化API

处理图谱可视化相关的API请求。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.graph_service import GraphVisualizationService
from twork.utils.logger import get_logger

router = APIRouter()
logger = get_logger("graph_api")


@router.get("/visualize/{project_id}")
async def get_graph_visualization(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    获取项目的图谱可视化数据
    
    Args:
        project_id: 项目ID
        db: 数据库会话
        
    Returns:
        Plotly图谱的JSON数据
    """
    try:
        service = GraphVisualizationService(db)
        graph_data = service.build_plotly_graph(project_id)
        
        return {
            "graph": graph_data,
            "status": "success"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"生成图谱失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成图谱失败: {str(e)}")
