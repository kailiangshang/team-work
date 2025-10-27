"""
前端增强功能模块

提供每日摘要展示和Plotly图谱可视化功能。
"""

import requests
import pandas as pd
import plotly.graph_objects as go
from typing import Optional, Dict, Any


def get_daily_summaries(backend_url: str, project_id: int) -> tuple:
    """
    获取每日摘要
    
    Args:
        backend_url: 后端URL
        project_id: 项目ID
        
    Returns:
        (摘要Markdown文本, 原始数据)
    """
    if not project_id:
        return "⚠️ 请先选择项目", None
    
    try:
        response = requests.get(
            f"{backend_url}/api/simulation/daily-summaries/{project_id}",
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        summaries = result.get("summaries", [])
        
        if not summaries:
            return "📊 暂无每日摘要数据，请先运行模拟", None
        
        # 生成Markdown展示
        md_lines = ["# 📅 每日执行摘要\n"]
        
        for summary in summaries:
            day = summary.get("day_number")
            md_lines.append(f"## 第{day}天\n")
            md_lines.append(f"- **任务完成**: {summary.get('total_tasks_completed')}/{summary.get('total_tasks_started')} 个")
            md_lines.append(f"- **整体进度**: {summary.get('overall_progress', 0):.1f}%\n")
            
            # Agent执行情况
            agent_summaries = summary.get("agent_summaries", [])
            if agent_summaries:
                md_lines.append("### 👥 Agent执行情况\n")
                for agent_sum in agent_summaries:
                    md_lines.append(f"**{agent_sum.get('role_name')}**:")
                    md_lines.append(f"  - 工作时长: {agent_sum.get('work_hours', 0)}小时")
                    md_lines.append(f"  - 效率: {agent_sum.get('efficiency', 0)}%")
                    md_lines.append(f"  - 完成任务: {len(agent_sum.get('tasks_executed', []))}个\n")
            
            # 沟通记录
            communications = summary.get("communications", [])
            if communications:
                md_lines.append("### 💬 团队沟通\n")
                for comm in communications[:3]:  # 只显示前3条
                    md_lines.append(f"- **{comm.get('time')}**: {comm.get('from')} → {comm.get('to')} - {comm.get('topic')}")
                if len(communications) > 3:
                    md_lines.append(f"  ... 还有{len(communications) - 3}条沟通记录\n")
                else:
                    md_lines.append("")
            
            # 环境事件
            env_events = summary.get("env_events", [])
            if env_events:
                md_lines.append("### ⚠️ 环境事件\n")
                for event in env_events:
                    md_lines.append(f"- **{event.get('time')}**: {event.get('description')}")
                md_lines.append("")
            
            md_lines.append("---\n")
        
        return "\n".join(md_lines), summaries
        
    except requests.exceptions.RequestException as e:
        return f"❌ 获取每日摘要失败: {str(e)}", None
    except Exception as e:
        return f"❌ 处理数据失败: {str(e)}", None


def get_agent_execution_logs(backend_url: str, project_id: int, agent_id: Optional[str] = None) -> tuple:
    """
    获取Agent执行日志
    
    Args:
        backend_url: 后端URL
        project_id: 项目ID
        agent_id: Agent ID（可选）
        
    Returns:
        (DataFrame, 状态消息)
    """
    if not project_id:
        return None, "⚠️ 请先选择项目"
    
    try:
        params = {}
        if agent_id:
            params["agent_id"] = agent_id
        
        response = requests.get(
            f"{backend_url}/api/simulation/agent-logs/{project_id}",
            params=params,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        logs = result.get("logs", [])
        
        if not logs:
            return None, "📋 暂无日志数据"
        
        # 转换为DataFrame
        df_data = []
        for log in logs:
            df_data.append({
                "天数": log.get("day_number"),
                "Agent": log.get("role_name", "N/A"),
                "动作": log.get("action_type", "N/A"),
                "任务": log.get("task_name", "N/A"),
                "开始时间": log.get("start_time", "N/A"),
                "结束时间": log.get("end_time", "N/A"),
                "内容": log.get("content", "")[:50] + "..." if len(log.get("content", "")) > 50 else log.get("content", "")
            })
        
        df = pd.DataFrame(df_data)
        return df, f"✅ 加载了{len(logs)}条日志记录"
        
    except requests.exceptions.RequestException as e:
        return None, f"❌ 获取日志失败: {str(e)}"
    except Exception as e:
        return None, f"❌ 处理数据失败: {str(e)}"


def get_plotly_graph(backend_url: str, project_id: int) -> Optional[Dict[str, Any]]:
    """
    获取Plotly图谱
    
    Args:
        backend_url: 后端URL
        project_id: 项目ID
        
    Returns:
        Plotly Figure字典或None
    """
    if not project_id:
        return None
    
    try:
        response = requests.get(
            f"{backend_url}/api/graph/visualize/{project_id}",
            timeout=60
        )
        response.raise_for_status()
        
        result = response.json()
        graph_data = result.get("graph")
        
        return graph_data
        
    except requests.exceptions.RequestException as e:
        print(f"获取图谱失败: {str(e)}")
        return None
    except Exception as e:
        print(f"处理图谱数据失败: {str(e)}")
        return None


def export_agent_logs(backend_url: str, project_id: int, agent_id: Optional[str] = None, format: str = "json") -> tuple:
    """
    导出Agent日志
    
    Args:
        backend_url: 后端URL
        project_id: 项目ID
        agent_id: Agent ID（可选）
        format: 导出格式（json/csv/md）
        
    Returns:
        (文件路径, 状态消息)
    """
    if not project_id:
        return None, "⚠️ 请先选择项目"
    
    try:
        params = {"format": format}
        if agent_id:
            params["agent_id"] = agent_id
        
        response = requests.get(
            f"{backend_url}/api/simulation/export-agent-logs/{project_id}",
            params=params,
            timeout=30
        )
        
        if response.status_code != 200:
            return None, f"❌ 导出失败: {response.json().get('detail', '未知错误')}"
        
        # 保存临时文件
        temp_path = f"/tmp/agent_logs_{project_id}.{format}"
        with open(temp_path, "wb") as f:
            f.write(response.content)
        
        return temp_path, f"✅ 日志已导出为{format.upper()}格式"
        
    except requests.exceptions.RequestException as e:
        return None, f"❌ 导出失败: {str(e)}"
    except Exception as e:
        return None, f"❌ 处理失败: {str(e)}"
