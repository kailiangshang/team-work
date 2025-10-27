"""
配置持久化服务
"""
import os
from pathlib import Path
from typing import Dict, Any
from twork.utils.logger import get_logger

logger = get_logger("config_service")


class ConfigPersistenceService:
    """配置持久化服务 - 支持.env文件持久化"""
    
    ENV_FILE_PATH = Path(".env")
    
    @classmethod
    def save_llm_config(cls, config: Dict[str, Any]) -> bool:
        """
        持久化LLM配置到.env文件
        
        Args:
            config: 配置字典
            
        Returns:
            是否成功
        """
        try:
            # 读取现有.env内容
            env_vars = {}
            if cls.ENV_FILE_PATH.exists():
                with open(cls.ENV_FILE_PATH, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip()
            
            # 更新LLM相关配置
            if 'api_base_url' in config:
                env_vars['LLM_API_BASE_URL'] = config['api_base_url']
            if 'api_key' in config and config['api_key'] != "********":
                env_vars['LLM_API_KEY'] = config['api_key']
            if 'model_name' in config:
                env_vars['LLM_MODEL_NAME'] = config['model_name']
            if 'temperature' in config:
                env_vars['LLM_TEMPERATURE'] = str(config['temperature'])
            if 'max_tokens' in config:
                env_vars['LLM_MAX_TOKENS'] = str(config['max_tokens'])
            if 'timeout' in config:
                env_vars['LLM_TIMEOUT'] = str(config['timeout'])
            
            # 写回.env文件
            with open(cls.ENV_FILE_PATH, 'w', encoding='utf-8') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            
            logger.info("LLM配置已持久化到.env文件")
            return True
            
        except Exception as e:
            logger.error(f"持久化配置失败: {str(e)}", exc_info=True)
            return False
    
    @classmethod
    def load_llm_config(cls) -> Dict[str, Any]:
        """
        从.env文件加载LLM配置
        
        Returns:
            配置字典
        """
        try:
            env_vars = {}
            if cls.ENV_FILE_PATH.exists():
                with open(cls.ENV_FILE_PATH, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip()
            
            # 提取LLM配置
            config = {}
            if 'LLM_API_BASE_URL' in env_vars:
                config['api_base_url'] = env_vars['LLM_API_BASE_URL']
            if 'LLM_API_KEY' in env_vars:
                config['api_key'] = env_vars['LLM_API_KEY']
                config['api_key_configured'] = True
            if 'LLM_MODEL_NAME' in env_vars:
                config['model_name'] = env_vars['LLM_MODEL_NAME']
            if 'LLM_TEMPERATURE' in env_vars:
                config['temperature'] = float(env_vars['LLM_TEMPERATURE'])
            if 'LLM_MAX_TOKENS' in env_vars:
                config['max_tokens'] = int(env_vars['LLM_MAX_TOKENS'])
            if 'LLM_TIMEOUT' in env_vars:
                config['timeout'] = int(env_vars['LLM_TIMEOUT'])
            
            return config
            
        except Exception as e:
            logger.error(f"加载配置失败: {str(e)}", exc_info=True)
            return {}
