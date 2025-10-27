"""
CSV导出器

导出任务编排CSV文件。
"""

import csv
from typing import Dict, Any, List
from pathlib import Path
from ..utils.logger import get_logger
from ..utils.file_handler import FilePermissionHandler

logger = get_logger("csv_exporter")


class CSVExporter:
    """CSV导出器"""
    
    def __init__(self):
        """初始化CSV导出器"""
        logger.info("CSV导出器初始化完成")
    
    def export_schedule(
        self,
        simulation_logs: List[Dict[str, Any]],
        output_path: str,
        use_detailed_logs: bool = False
    ) -> str:
        """
        导出任务排期CSV
        
        Args:
            simulation_logs: 模拟日志列表（可以是原始日志或详细日志）
            output_path: 输出路径
            use_detailed_logs: 是否使用详细日志格式
            
        Returns:
            生成的文件路径
        """
        logger.info(f"开始导出CSV文件: {output_path}, 使用详细日志={use_detailed_logs}")
        
        # 数据验证
        if not simulation_logs:
            logger.warning("模拟日志为空，生成空 CSV 模板")
            simulation_logs = [{
                "day_number": 0,
                "role_name": "无数据",
                "completed_tasks": [],
                "discussions": [],
                "notes": "请先运行模拟"
            }]
        
        rows = []
        headers = [
            "日期", "时间", "角色", "任务ID", "任务名称", 
            "事件类型", "内容", "状态", "进度(%)", "备注"
        ]
        
        # 根据日志格式选择处理方式
        if use_detailed_logs:
            # 处理详细日志格式（新格式）
            for log in simulation_logs:
                day = log.get("day", log.get("day_number", 0))
                timestamp = log.get("timestamp", "N/A")
                role_name = log.get("role_name", "N/A")
                task_id = log.get("task_id", "")
                task_name = log.get("task_name", "")
                event_type = log.get("event_type", "unknown")
                content = log.get("content", "")
                status = log.get("status", "")
                progress = log.get("progress_percentage", "")
                
                # 事件类型中文映射
                event_type_map = {
                    "task_start": "任务开始",
                    "task_complete": "任务完成",
                    "task_progress": "任务进展",
                    "discussion": "讨论交流",
                    "env_event": "环境事件",
                    "conflict": "冲突解决"
                }
                event_type_cn = event_type_map.get(event_type, event_type)
                
                row = [
                    f"第{day}天",
                    timestamp.split()[-1] if "d" in timestamp else timestamp,
                    role_name,
                    task_id or "",
                    task_name or "",
                    event_type_cn,
                    content,
                    status or "",
                    progress if progress != "" else "",
                    ""
                ]
                rows.append(row)
        else:
            # 处理原始日志格式（兼容旧版本）
            for log in simulation_logs:
                day_number = log.get("day_number", 0)
                role_name = log.get("role_name", "N/A")
                
                # 处理完成的任务
                for task in log.get("completed_tasks", []):
                    row = [
                        f"第{day_number}天",
                        task.get("start_time", "N/A"),
                        role_name,
                        task.get("task_id", "N/A"),
                        task.get("task_name", "N/A"),
                        "任务执行",
                        task.get("output", "N/A"),
                        task.get("status", "N/A"),
                        task.get("progress_percentage", 0),
                        log.get("notes", "")
                    ]
                    rows.append(row)
                
                # 处理讨论记录
                for discussion in log.get("discussions", []):
                    row = [
                        f"第{day_number}天",
                        discussion.get("time", "N/A"),
                        role_name,
                        "",
                        discussion.get("topic", "N/A"),
                        "讨论交流",
                        f"与{discussion.get('with_role', 'N/A')}讨论: {discussion.get('content', '')}",
                        "",
                        "",
                        ""
                    ]
                    rows.append(row)
        
        # 如果没有数据行，添加一个默认行
        if not rows:
            rows.append(["第0天", "00:00", "无数据", "", "", "", "请先运行模拟", "", "", ""])
        
        # 构建CSV内容
        output_file = Path(output_path)
        csv_content = []
        import io
        
        # 使用StringIO构建CSV内容
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(headers)
        writer.writerows(rows)
        csv_content = csv_buffer.getvalue()
        csv_buffer.close()
        
        # 使用安全写入
        # 注意: 对于CSV文件，需要使用UTF-8-BOM编码
        csv_content_with_bom = '\ufeff' + csv_content  # 添加BOM
        
        success = FilePermissionHandler.safe_write_file(
            file_path=str(output_file),
            content=csv_content_with_bom,
            mode='w',
            file_permission=0o644
        )
        
        if not success:
            raise IOError(f"无法写入文件: {output_path}")
        
        logger.info(f"CSV文件导出完成: {output_file}, 共{len(rows)}行数据")
        
        return str(output_file)
    
    def export_tasks(
        self,
        tasks: List[Dict[str, Any]],
        output_path: str
    ) -> str:
        """
        导出任务列表CSV
        
        Args:
            tasks: 任务列表
            output_path: 输出路径
            
        Returns:
            生成的文件路径
        """
        logger.info(f"开始导出任务列表CSV: {output_path}")
        
        headers = [
            "任务ID",
            "任务名称",
            "描述",
            "所需能力",
            "人员类型",
            "所需工具",
            "工期(天)",
            "优先级",
            "依赖任务"
        ]
        
        rows = []
        for task in tasks:
            row = [
                task.get("task_id", ""),
                task.get("task_name", ""),
                task.get("description", ""),
                ", ".join(task.get("required_skills", [])),
                task.get("person_type", ""),
                ", ".join(task.get("tools_needed", [])),
                task.get("duration_days", 0),
                task.get("priority", "Medium"),
                ", ".join(task.get("dependencies", []))
            ]
            rows.append(row)
        
        # 构建CSV内容
        import io
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(headers)
        writer.writerows(rows)
        csv_content = csv_buffer.getvalue()
        csv_buffer.close()
        
        # 使用安全写入
        csv_content_with_bom = '\ufeff' + csv_content  # 添加BOM
        output_file = Path(output_path)
        
        success = FilePermissionHandler.safe_write_file(
            file_path=str(output_file),
            content=csv_content_with_bom,
            mode='w',
            file_permission=0o644
        )
        
        if not success:
            raise IOError(f"无法写入文件: {output_path}")
        
        logger.info(f"任务列表CSV导出完成: {output_file}, 共{len(rows)}个任务")
        
        return str(output_file)
