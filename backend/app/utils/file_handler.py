"""
文件权限处理器

用于处理文件读写权限问题，特别是在容器化环境中。
"""

import os
import stat
from pathlib import Path
from typing import Optional
from twork.utils.logger import get_logger

logger = get_logger("file_permission_handler")


class FilePermissionHandler:
    """文件权限处理器"""
    
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
    
    @staticmethod
    def ensure_readable(path: str) -> bool:
        """
        确保文件可读
        
        Args:
            path: 文件路径
            
        Returns:
            是否可读
        """
        try:
            p = Path(path)
            
            if not p.exists():
                logger.warning(f"文件不存在: {path}")
                return False
            
            # 检查读权限
            if not os.access(str(p), os.R_OK):
                logger.error(f"文件无读权限: {path}")
                return False
            
            logger.debug(f"文件可读: {path}")
            return True
            
        except Exception as e:
            logger.error(f"检查文件读权限失败: {path}, error={str(e)}")
            return False
    
    @staticmethod
    def get_writable_path(preferred_path: str, fallback_dir: str = "/tmp") -> str:
        """
        获取可写路径，失败则回退到临时目录
        
        Args:
            preferred_path: 首选路径
            fallback_dir: 回退目录
            
        Returns:
            可写路径
        """
        if FilePermissionHandler.ensure_writable(preferred_path):
            return preferred_path
        
        # 回退到临时目录
        fallback_path = Path(fallback_dir) / Path(preferred_path).name
        logger.warning(f"使用回退路径: {preferred_path} -> {fallback_path}")
        
        return str(fallback_path)
    
    @staticmethod
    def get_file_permissions(path: str) -> Optional[str]:
        """
        获取文件权限信息
        
        Args:
            path: 文件路径
            
        Returns:
            权限信息字符串（如 "rwxr-xr-x"）
        """
        try:
            p = Path(path)
            if not p.exists():
                return None
            
            st = p.stat()
            mode = st.st_mode
            
            # 转换为rwx格式
            permissions = stat.filemode(mode)
            
            logger.debug(f"文件权限: {path} -> {permissions}")
            return permissions
            
        except Exception as e:
            logger.error(f"获取文件权限失败: {path}, error={str(e)}")
            return None
    
    @staticmethod
    def fix_directory_permissions(directory: str, mode: int = 0o755) -> bool:
        """
        修复目录权限
        
        Args:
            directory: 目录路径
            mode: 权限模式（默认755）
            
        Returns:
            是否成功
        """
        try:
            p = Path(directory)
            
            if not p.exists():
                logger.warning(f"目录不存在: {directory}")
                return False
            
            # 尝试修改权限
            os.chmod(str(p), mode)
            
            logger.info(f"修复目录权限成功: {directory}, mode={oct(mode)}")
            return True
            
        except PermissionError as e:
            logger.error(f"无权限修改目录: {directory}, error={str(e)}")
            return False
        except Exception as e:
            logger.error(f"修复目录权限失败: {directory}, error={str(e)}")
            return False
    
    @staticmethod
    def check_path_ownership(path: str) -> dict:
        """
        检查路径所有者信息
        
        Args:
            path: 文件或目录路径
            
        Returns:
            所有者信息字典
        """
        try:
            p = Path(path)
            
            if not p.exists():
                return {"exists": False}
            
            st = p.stat()
            
            return {
                "exists": True,
                "uid": st.st_uid,
                "gid": st.st_gid,
                "mode": oct(st.st_mode),
                "size": st.st_size
            }
            
        except Exception as e:
            logger.error(f"检查路径所有者失败: {path}, error={str(e)}")
            return {"exists": False, "error": str(e)}
    
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
            file_permission: 文件权限（默认644）
            
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
