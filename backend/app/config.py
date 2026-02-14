"""配置管理"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用
    APP_NAME: str = "TWork API"
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # FalkorDB
    FALKORDB_HOST: str = "localhost"
    FALKORDB_PORT: int = 6379
    
    # LLM
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4"
    
    # 模拟
    DEFAULT_SIMULATION_DAYS: int = 30
    MAX_SIMULATION_DAYS: int = 365
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()