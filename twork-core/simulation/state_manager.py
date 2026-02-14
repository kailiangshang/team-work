"""状态管理器 - 管理模拟状态"""
from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime

from ..schemas.simulation import (
    SimulationState, SimulationStatus, SimulationLog,
    SimulationResult, DailySimulationResult
)

logger = logging.getLogger(__name__)


class StateManager:
    """状态管理器
    
    管理模拟过程中的状态：
    - 状态持久化
    - 状态恢复
    - 状态查询
    """
    
    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path
        self.states: Dict[str, SimulationState] = {}
        self.results: Dict[str, SimulationResult] = {}
    
    def create_state(self, project_id: str, total_days: int = 30) -> SimulationState:
        """创建模拟状态"""
        state = SimulationState(
            project_id=project_id,
            total_days=total_days,
        )
        self.states[project_id] = state
        return state
    
    def get_state(self, project_id: str) -> Optional[SimulationState]:
        """获取模拟状态"""
        return self.states.get(project_id)
    
    def update_state(self, project_id: str, **kwargs):
        """更新模拟状态"""
        state = self.get_state(project_id)
        if state:
            for key, value in kwargs.items():
                if hasattr(state, key):
                    setattr(state, key, value)
    
    def add_log(
        self,
        project_id: str,
        agent_id: str,
        action: str,
        content: str,
        metadata: Dict = None,
    ):
        """添加日志"""
        state = self.get_state(project_id)
        if state:
            log = SimulationLog(
                agent_id=agent_id,
                action=action,
                content=content,
                metadata=metadata or {},
            )
            state.logs.append(log)
    
    def save_result(self, project_id: str, result: SimulationResult):
        """保存模拟结果"""
        self.results[project_id] = result
        
        if self.storage_path:
            try:
                file_path = f"{self.storage_path}/{project_id}_result.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"Failed to save result: {e}")
    
    def get_result(self, project_id: str) -> Optional[SimulationResult]:
        """获取模拟结果"""
        return self.results.get(project_id)
    
    def load_result(self, project_id: str) -> Optional[SimulationResult]:
        """从文件加载模拟结果"""
        if not self.storage_path:
            return None
        
        try:
            file_path = f"{self.storage_path}/{project_id}_result.json"
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 重建结果对象
            result = self._dict_to_result(data)
            self.results[project_id] = result
            return result
        except Exception as e:
            logger.error(f"Failed to load result: {e}")
            return None
    
    def _dict_to_result(self, data: Dict[str, Any]) -> SimulationResult:
        """将字典转换为 SimulationResult"""
        # 简化实现
        return SimulationResult(
            project_id=data.get("project_id", ""),
            status=SimulationStatus(data.get("status", "idle")),
            current_day=data.get("current_day", 0),
            started_at=data.get("started_at", ""),
            completed_at=data.get("completed_at", ""),
            error_message=data.get("error_message", ""),
        )
    
    def get_progress(self, project_id: str) -> Dict[str, Any]:
        """获取模拟进度"""
        state = self.get_state(project_id)
        if not state:
            return {"error": "Project not found"}
        
        return {
            "project_id": project_id,
            "status": state.status.value,
            "current_day": state.current_day,
            "total_days": state.total_days,
            "progress": state.current_day / state.total_days if state.total_days > 0 else 0,
            "completed_tasks": len(state.completed_tasks),
            "in_progress_tasks": len(state.in_progress_tasks),
            "pending_tasks": len(state.pending_tasks),
        }
    
    def list_simulations(self) -> List[Dict[str, Any]]:
        """列出所有模拟"""
        return [
            {
                "project_id": pid,
                "status": state.status.value,
                "current_day": state.current_day,
                "total_days": state.total_days,
            }
            for pid, state in self.states.items()
        ]
    
    def delete_simulation(self, project_id: str) -> bool:
        """删除模拟"""
        if project_id in self.states:
            del self.states[project_id]
        if project_id in self.results:
            del self.results[project_id]
        return True