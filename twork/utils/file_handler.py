"""
文件权限处理器 - twork模块版本

用于处理文件读写权限问题，特别是在容器化环境中。
"""

import os
from pathlib import Path
from typing import Optional
from .logger import get_logger

logger = get_logger("file_permission_handler")


class FilePermissionHandler:
    """文件权限处理器"""
    
    @staticmethod
    def safe_write_file(
        file_path: str,
        content: str | bytes,
        mode: str = 'w',
        file_permission: int = 0o644
    ) -> bool:
        """
        安全写入文件，确保权限正确
        
        Args:
            file_path: 文件路径
            content: 文件内容
            mode: 打开模式 ('w', 'wb', 'a')
            file_permission: 文件权限(默认644)
            
        Returns:
            是否成功
        """
        try:
            p = Path(file_path)
            p.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
            
            # 写入文件
            with open(p, mode, encoding='utf-8' if mode == 'w' else None) as f:
                f.write(content)
            
            # 设置权限
            os.chmod(str(p), file_permission)
            
            logger.info(f"文件写入成功: {file_path}, 权限={oct(file_permission)}")
            return True
            
        except Exception as e:
            logger.error(f"文件写入失败: {file_path}, error={str(e)}")
            return False
    
    @staticmethod
    def ensure_writable(path: str) -> bool:
        """
        确保路径可写
        
        Args:
            path: 文件路径
            
        Returns:
            是否可写
        """
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            
            # 尝试创建测试文件
            test_file = p.parent / ".write_test"
            test_file.touch()
            test_file.unlink()
            
            logger.debug(f"路径可写: {path}")
            return True
            
        except PermissionError as e:
            logger.error(f"路径无写权限: {path}, error={str(e)}")
            return False
        except Exception as e:
            logger.error(f"检查路径权限失败: {path}, error={str(e)}")
            return False
