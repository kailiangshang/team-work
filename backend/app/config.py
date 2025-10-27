"""
配置管理

管理应用配置信息。
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置"""
    
    # LLM配置
    llm_api_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="LLM API基础URL"
    )
    llm_api_key: str = Field(
        default="",
        description="LLM API密钥"
    )
    llm_model_name: str = Field(
        default="gpt-4",
        description="LLM模型名称"
    )
    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="LLM温度参数"
    )
    llm_max_tokens: int = Field(
        default=2000,
        gt=0,
        description="LLM最大token数"
    )
    llm_timeout: int = Field(
        default=60,
        gt=0,
        description="LLM请求超时时间（秒）"
    )
    
    # 数据库配置
    database_type: str = Field(
        default="sqlite",
        description="数据库类型: sqlite, postgresql, mysql"
    )
    sqlite_path: str = Field(
        default="data/db/teamwork.db",
        description="SQLite数据库路径"
    )
    db_host: str = Field(
        default="localhost",
        description="数据库主机"
    )
    db_port: int = Field(
        default=5432,
        description="数据库端口"
    )
    db_name: str = Field(
        default="teamwork",
        description="数据库名称"
    )
    db_username: str = Field(
        default="admin",
        description="数据库用户名"
    )
    db_password: str = Field(
        default="",
        description="数据库密码"
    )
    db_pool_size: int = Field(
        default=10,
        gt=0,
        description="数据库连接池大小"
    )
    
    # 后端服务配置
    backend_host: str = Field(
        default="0.0.0.0",
        description="后端服务主机"
    )
    backend_port: int = Field(
        default=8000,
        gt=0,
        le=65535,
        description="后端服务端口"
    )
    debug: bool = Field(
        default=False,
        description="调试模式"
    )
    
    # 日志配置
    log_level: str = Field(
        default="INFO",
        description="日志级别"
    )
    log_file: str = Field(
        default="logs/teamwork.log",
        description="日志文件路径"
    )
    
    # 上传配置
    upload_dir: str = Field(
        default="data/uploads",
        description="上传文件目录"
    )
    max_upload_size_mb: int = Field(
        default=50,
        gt=0,
        description="最大上传文件大小（MB）"
    )
    
    # 输出配置
    output_dir: str = Field(
        default="data/outputs",
        description="输出文件目录"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def database_url(self) -> str:
        """获取数据库连接URL"""
        if self.database_type == "sqlite":
            return f"sqlite:///{self.sqlite_path}"
        elif self.database_type == "postgresql":
            return f"postgresql://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        elif self.database_type == "mysql":
            return f"mysql+pymysql://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        else:
            raise ValueError(f"不支持的数据库类型: {self.database_type}")


# 全局配置实例
settings = Settings()
