"""
日志管理模块

提供统一的日志配置和管理功能。
"""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger


def setup_logger(
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    rotation: str = "10 MB",
    retention: str = "7 days",
) -> None:
    """
    配置日志系统
    
    Args:
        log_file: 日志文件路径
        log_level: 日志级别
        rotation: 日志轮转大小
        retention: 日志保留时间
    """
    # 移除默认handler
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )
    
    # 添加文件输出
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression="zip",
        )


def get_logger(name: str):
    """
    获取logger实例
    
    Args:
        name: logger名称
        
    Returns:
        logger实例
    """
    return logger.bind(name=name)
