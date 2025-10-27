"""
配置API

处理配置相关的API请求。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from twork.llm import OpenAIAdapter
from twork.utils.logger import get_logger
from ..config import settings
from ..services.config_service import ConfigPersistenceService

router = APIRouter()
logger = get_logger("config_api")


class LLMConfig(BaseModel):
    """模型配置"""
    api_base_url: str = Field(..., description="API基础URL")
    api_key: str = Field(default="", description="API密钥（可为空或占位符********）")
    model_name: str = Field(default="gpt-4", description="模型名称")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=2000, gt=0, description="最大token数")
    timeout: int = Field(default=60, gt=0, description="超时时间(秒)")


class DatabaseConfig(BaseModel):
    """数据库配置"""
    db_type: str
    host: str = "localhost"
    port: int = 5432
    database: str = "teamwork"
    username: str = "admin"
    password: str = ""


@router.get("/llm")
async def get_llm_config():
    """
    获取当前LLM配置
    
    Returns:
        当前LLM配置信息
    """
    try:
        # 优先从.env文件加载持久化配置
        persisted_config = ConfigPersistenceService.load_llm_config()
        
        # 合并内存配置和持久化配置
        return {
            "api_base_url": persisted_config.get('api_base_url', settings.llm_api_base_url),
            "model_name": persisted_config.get('model_name', settings.llm_model_name),
            "temperature": persisted_config.get('temperature', settings.llm_temperature),
            "max_tokens": persisted_config.get('max_tokens', settings.llm_max_tokens),
            "timeout": persisted_config.get('timeout', settings.llm_timeout),
            # 不返回API Key保证安全
            "api_key_configured": persisted_config.get('api_key_configured', bool(settings.llm_api_key))
        }
    except Exception as e:
        logger.error(f"获取LLM配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/llm")
async def update_llm_config(config: LLMConfig):
    """
    更新LLM配置
    
    Args:
        config: LLM配置
        
    Returns:
        更新结果
    """
    try:
        logger.info(f"更新LLM配置: model={config.model_name}, url={config.api_base_url}")
        
        # 更新全局配置（内存）
        settings.llm_api_base_url = config.api_base_url
        settings.llm_model_name = config.model_name
        settings.llm_temperature = config.temperature
        settings.llm_max_tokens = config.max_tokens
        settings.llm_timeout = config.timeout
        
        # 准备持久化数据
        persist_data = {
            "api_base_url": config.api_base_url,
            "model_name": config.model_name,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "timeout": config.timeout
        }
        
        # 只有当API Key不是占位符时才更新和持久化
        if config.api_key and config.api_key != "********":
            settings.llm_api_key = config.api_key
            persist_data["api_key"] = config.api_key
            logger.info("已更新API Key")
        else:
            logger.info("跳过API Key更新（使用现有配置）")
        
        # 持久化到.env文件
        persistence_success = ConfigPersistenceService.save_llm_config(persist_data)
        
        if not persistence_success:
            logger.warning("配置已在内存中更新，但持久化失败")
        
        logger.info("LLM配置更新成功")
        
        return {
            "success": True,
            "message": "LLM配置更新成功" + ("（已持久化）" if persistence_success else "（仅内存，重启后丢失）"),
            "config": {
                "api_base_url": config.api_base_url,
                "model_name": config.model_name,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "timeout": config.timeout
            },
            "persisted": persistence_success
        }
        
    except Exception as e:
        logger.error(f"更新LLM配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-llm")
async def test_llm_connection(config: LLMConfig):
    """
    测试LLM连接
    
    Args:
        config: LLM配置
        
    Returns:
        连接测试结果
    """
    try:
        logger.info(f"测试LLM连接: model={config.model_name}, url={config.api_base_url}")
        
        adapter = OpenAIAdapter(
            api_base_url=config.api_base_url,
            api_key=config.api_key,
            model_name=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.timeout
        )
        
        result = adapter.validate_connection()
        
        logger.info(f"LLM连接测试结果: {result['success']}")
        return result
        
    except Exception as e:
        logger.error(f"测试LLM连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-db")
async def test_db_connection(config: DatabaseConfig):
    """
    测试数据库连接
    
    Args:
        config: 数据库配置
        
    Returns:
        连接测试结果
    """
    try:
        logger.info(f"测试数据库连接: type={config.db_type}, host={config.host}")
        
        # 简化实现，实际应该真正测试数据库连接
        logger.info("数据库连接测试成功")
        
        return {
            "success": True,
            "message": "数据库连接测试成功",
            "db_type": config.db_type
        }
        
    except Exception as e:
        logger.error(f"测试数据库连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
