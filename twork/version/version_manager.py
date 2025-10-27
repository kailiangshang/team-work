"""
版本管理器
管理项目的版本快照
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import copy


class VersionManager:
    """版本管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.versions = {}  # project_id -> [versions]
    
    def create_snapshot(
        self,
        project_id: int,
        description: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建版本快照
        
        Args:
            project_id: 项目ID
            description: 版本说明
            data: 完整快照数据
        
        Returns:
            版本信息
        """
        if project_id not in self.versions:
            self.versions[project_id] = []
        
        version_number = len(self.versions[project_id]) + 1
        
        snapshot = {
            "version_number": version_number,
            "description": description,
            "snapshot_data": copy.deepcopy(data),
            "created_at": datetime.now().isoformat()
        }
        
        self.versions[project_id].append(snapshot)
        
        return {
            "project_id": project_id,
            "version_number": version_number,
            "description": description,
            "created_at": snapshot["created_at"]
        }
    
    def get_version(
        self,
        project_id: int,
        version_number: int
    ) -> Optional[Dict[str, Any]]:
        """
        获取指定版本
        
        Args:
            project_id: 项目ID
            version_number: 版本号
        
        Returns:
            版本快照数据
        """
        if project_id not in self.versions:
            return None
        
        for version in self.versions[project_id]:
            if version["version_number"] == version_number:
                return version
        
        return None
    
    def list_versions(self, project_id: int) -> List[Dict[str, Any]]:
        """
        列出项目的所有版本
        
        Args:
            project_id: 项目ID
        
        Returns:
            版本列表（不包含完整快照数据）
        """
        if project_id not in self.versions:
            return []
        
        return [
            {
                "version_number": v["version_number"],
                "description": v["description"],
                "created_at": v["created_at"]
            }
            for v in self.versions[project_id]
        ]
    
    def restore_version(
        self,
        project_id: int,
        version_number: int
    ) -> Optional[Dict[str, Any]]:
        """
        恢复到指定版本
        
        Args:
            project_id: 项目ID
            version_number: 版本号
        
        Returns:
            恢复的数据
        """
        version = self.get_version(project_id, version_number)
        if not version:
            return None
        
        return copy.deepcopy(version["snapshot_data"])
    
    def delete_version(
        self,
        project_id: int,
        version_number: int
    ) -> bool:
        """
        删除指定版本
        
        Args:
            project_id: 项目ID
            version_number: 版本号
        
        Returns:
            是否成功
        """
        if project_id not in self.versions:
            return False
        
        original_count = len(self.versions[project_id])
        self.versions[project_id] = [
            v for v in self.versions[project_id]
            if v["version_number"] != version_number
        ]
        
        return len(self.versions[project_id]) < original_count
