"""
Gradio前端应用 - 优化版

提供用户交互界面，支持文档解析、任务拆解、Agent对话日志和图谱可视化。
"""

import gradio as gr
import requests
import os
import json
import pandas as pd
from pathlib import Path
from twork.utils.logger import setup_logger, get_logger

# 初始化日志
setup_logger(
    log_file="/app/logs/frontend.log",
    log_level=os.getenv("LOG_LEVEL", "INFO")
)

logger = get_logger("frontend")

# 后端API地址
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# 全局变量存储当前项目ID
current_project_id = None


def upload_document(file):
    """上传文档"""
    global current_project_id
    
    if file is None:
        return "⚠️ 请选择要上传的文件", None, None
    
    try:
        logger.info(f"接收上传文件: {file.name}")
        with open(file.name, "rb") as f:
            files = {"file": (Path(file.name).name, f, "application/octet-stream")}
            response = requests.post(
                f"{BACKEND_URL}/api/upload/document",
                files=files,
                timeout=120
            )
            
            if response.status_code != 200:
                error_detail = response.json().get("detail", "未知错误") if response.headers.get("content-type") == "application/json" else response.text
                logger.error(f"上传失败: {error_detail}")
                return f"❌ 上传失败 ({response.status_code}): {error_detail}", None, None
            
            result = response.json()
            current_project_id = result["project_id"]
            requirements = result["requirements"]
            files_info = result.get("files", {})
            
            logger.info(f"文档上传成功: project_id={current_project_id}")
            
            # 格式化需求信息
            info = f"""## ✅ 项目需求解析成功！

**项目名称**: {requirements.get('project_name', 'N/A')}

**项目描述**: {requirements.get('project_description', 'N/A')}

**主要目标**:
{chr(10).join(['- ' + obj for obj in requirements.get('main_objectives', [])])}

**关键需求**:
{chr(10).join(['- ' + req for req in requirements.get('key_requirements', [])])}

**项目ID**: {current_project_id}
"""
            
            return info, files_info.get("requirements_md"), current_project_id
            
    except requests.exceptions.Timeout:
        logger.error("请求超时")
        return "❌ 请求超时，请检查网络连接或后端服务是否正常", None, None
    except requests.exceptions.ConnectionError:
        logger.error(f"无法连接到后端服务: {BACKEND_URL}")
        return f"❌ 无法连接到后端服务: {BACKEND_URL}，请检查后端是否启动", None, None
    except Exception as e:
        logger.error(f"上传失败: {str(e)}", exc_info=True)
        return f"❌ 上传失败: {str(e)}", None, None


def download_file(file_type, project_id):
    """下载文件"""
    if not project_id:
        return None
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/download/{file_type}/{project_id}",
            timeout=30
        )
        
        if response.status_code == 200:
            # 保存临时文件
            temp_path = f"/tmp/{file_type}_{project_id}.file"
            with open(temp_path, "wb") as f:
                f.write(response.content)
            logger.info(f"文件下载成功: {temp_path}")
            return temp_path
        else:
            logger.warning(f"文件下载失败: status={response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"下载失败: {str(e)}", exc_info=True)
        return None


def decompose_tasks(project_id):
    """拆解任务"""
    if not project_id:
        return "请先上传文档", None, None, None, None
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/task/decompose",
            json={"project_id": project_id}
        )
        response.raise_for_status()
        
        result = response.json()
        tasks = result["tasks"]
        task_tree = result.get("task_tree", {})
        files_info = result.get("files", {})
        
        # 格式化任务信息
        task_info = f"## ✅ 任务拆解完成！\n\n共生成 {len(tasks)} 个任务:\n\n"
        for i, task in enumerate(tasks, 1):
            task_info += f"### {i}. {task['task_name']}\n"
            task_info += f"- **任务ID**: {task['task_id']}\n"
            task_info += f"- **工期**: {task['duration_days']} 天\n"
            task_info += f"- **描述**: {task['description']}\n"
            if task.get('dependencies'):
                task_info += f"- **依赖**: {', '.join(task['dependencies'])}\n"
            task_info += "\n"
        
        # 准备下载按钮
        return task_info, tasks, files_info.get("breakdown_md"), files_info.get("tasks_json"), files_info.get("tree_json")
        
    except Exception as e:
        return f"❌ 任务拆解失败: {str(e)}", None, None, None, None


def generate_agents(project_id):
    """生成Agent"""
    if not project_id:
        return "请先上传文档并拆解任务", None, None
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/task/generate-agents",
            json={"project_id": project_id}
        )
        response.raise_for_status()
        
        result = response.json()
        agents = result["agents"]
        
        # 格式化Agent信息
        agent_info = f"## ✅ Agent生成完成！\n\n共生成 {len(agents)} 个角色:\n\n"
        for i, agent in enumerate(agents, 1):
            agent_info += f"### {i}. {agent['role_name']}\n"
            agent_info += f"- **角色类型**: {agent.get('role_type', 'N/A')}\n"
            agent_info += f"- **核心能力**: {', '.join(agent.get('capabilities', []))}\n"
            agent_info += f"- **负责任务**: {', '.join(agent.get('assigned_tasks', []))}\n\n"
        
        # 准备可编辑表格数据
        agent_table_data = []
        for agent in agents:
            agent_table_data.append([
                True,  # 启用
                agent.get("agent_id", ""),
                agent.get("role_name", ""),
                agent.get("role_type", ""),
                ", ".join(agent.get("capabilities", [])),
                ", ".join(agent.get("assigned_tasks", []))
            ])
        
        return agent_info, agent_table_data, agents
        
    except Exception as e:
        return f"❌ Agent生成失败: {str(e)}", None, None


def save_agent_edits(project_id, agent_table, total_days):
    """保存Agent编辑"""
    if not project_id:
        return "⚠️ 请先上传文档并生成Agent"
    
    # 检查agent_table是否为空（DataFrame需要用.empty判断）
    if agent_table is None or (isinstance(agent_table, pd.DataFrame) and agent_table.empty):
        return "⚠️ 请先生成Agent"
    
    # 如果是普通列表，也检查是否为空
    if isinstance(agent_table, list) and len(agent_table) == 0:
        return "⚠️ 请先生成Agent"
    
    try:
        # 解析表格数据（处理DataFrame或列表两种情况）
        agents = []
        
        # 将DataFrame转换为列表
        if isinstance(agent_table, pd.DataFrame):
            table_rows = agent_table.values.tolist()
        else:
            table_rows = agent_table
        
        for row in table_rows:
            enabled, agent_id, role_name, role_type, capabilities_str, assigned_tasks_str = row
            
            agents.append({
                "agent_id": agent_id,
                "role_name": role_name,
                "role_type": role_type,
                "capabilities": [c.strip() for c in capabilities_str.split(",")] if capabilities_str else [],
                "assigned_tasks": [t.strip() for t in assigned_tasks_str.split(",")] if assigned_tasks_str else [],
                "enabled": enabled
            })
        
        # 发送更新请求
        response = requests.put(
            f"{BACKEND_URL}/api/agent/batch-update",
            json={
                "project_id": project_id,
                "agents": agents,
                "total_days": int(total_days) if total_days else None
            }
        )
        response.raise_for_status()
        
        result = response.json()
        
        # 格式化详细反馈
        feedback = f"""## ✅ 配置保存成功！

**更新统计**:
- 启用的Agent: {result.get('enabled_count', 0)}个
- 禁用的Agent: {result.get('disabled_count', 0)}个
- 项目总工期: {result.get('total_days', 'N/A')}天

**启用的Agents**:
"""
        
        enabled_agents = result.get('enabled_agents', [])
        if enabled_agents:
            feedback += "\n".join([f"- {name}" for name in enabled_agents])
        else:
            feedback += "- 无"
        
        feedback += "\n\n"
        
        disabled_agents = result.get('disabled_agents', [])
        if disabled_agents:
            feedback += f"**已禁用的Agents**:\n"
            feedback += "\n".join([f"- {name}" for name in disabled_agents])
            feedback += "\n"
        
        return feedback
        
    except Exception as e:
        return f"❌ 保存失败: {str(e)}"


def run_simulation_stream(project_id, enable_env_agent, env_probability, progress=gr.Progress()):
    """运行流式模拟（使用SSE）"""
    if not project_id:
        return "请先完成前面的步骤", "", None
    
    try:
        import sseclient
        
        logger.info(f"开始流式模拟: project_id={project_id}")
        
        url = f"{BACKEND_URL}/api/simulation/run-stream"
        data = {
            "project_id": project_id,
            "enable_env_agent": enable_env_agent,
            "env_event_probability": env_probability
        }
        
        # 使用SSE连接
        response = requests.post(url, json=data, stream=True, timeout=None)
        response.raise_for_status()
        
        client = sseclient.SSEClient(response)
        
        all_logs = []
        daily_summaries = []
        current_day = 0
        total_days = 0
        env_summary = None
        
        for event in client.events():
            if event.data:
                chunk = json.loads(event.data)
                chunk_type = chunk.get("type")
                
                if chunk_type == "day_start":
                    current_day = chunk.get("day")
                    progress((current_day - 1) / max(total_days, 30), desc=f"模拟第 {current_day} 天...")
                
                elif chunk_type == "env_event":
                    # 环境事件
                    logger.debug(f"环境事件: {chunk.get('event')}")
                
                elif chunk_type == "agent_work":
                    # 添加日志
                    logs = chunk.get("logs", [])
                    all_logs.extend(logs)
                
                elif chunk_type == "day_summary":
                    summary_data = chunk.get("summary", {})
                    daily_summary = summary_data.get("daily_summary")
                    if daily_summary:
                        daily_summaries.append(daily_summary)
                        logger.info(f"第{daily_summary.get('day_number')}天摘要: 完成{daily_summary.get('total_tasks_completed')}个任务")
                    total_days = summary_data.get("total_tasks", 30)
                
                elif chunk_type == "complete":
                    # 模拟完成
                    env_summary = chunk.get("env_summary")
                    progress(1.0, desc="模拟完成！")
                    logger.info("模拟执行完成")
                    break
                
                elif chunk_type == "error":
                    error_msg = chunk.get('message')
                    logger.error(f"模拟错误: {error_msg}")
                    return f"❌ 模拟错误: {error_msg}", "", None
        
        # 转换为DataFrame
        if all_logs:
            df_data = []
            for log in all_logs:
                df_data.append({
                    "时间": log.get("timestamp", ""),
                    "角色": log.get("role_name", ""),
                    "事件类型": log.get("event_type", ""),
                    "任务": log.get("task_name", "") or log.get("task_id", ""),
                    "内容": log.get("content", "")[:100] + "..." if len(log.get("content", "")) > 100 else log.get("content", ""),
                    "状态": log.get("status", ""),
                    "进度(%)": log.get("progress_percentage", "")
                })
            df = pd.DataFrame(df_data)
        else:
            df = pd.DataFrame(columns=["时间", "角色", "事件类型", "任务", "内容", "状态", "进度(%)"])
        
        # 格式化摘要
        summary_info = f"## 模拟执行完成！\n\n"
        summary_info += f"**总日志数**: {len(all_logs)}\n\n"
        
        if enable_env_agent and env_summary:
            summary_info += f"### 环境干扰统计\n\n"
            summary_info += f"- **总事件数**: {env_summary.get('total_events', 0)}\n"
            summary_info += f"- **总延期**: {env_summary.get('total_delay', 0)} 天\n"
        
        # 生成每日摘要显示
        daily_summary_md = format_daily_summaries(daily_summaries)
        
        return summary_info, daily_summary_md, df
        
    except ImportError:
        logger.warning("sseclient未安装，使用同步方式")
        # 如果没有sseclient，使用同步方式
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/simulation/run",
                json={
                    "project_id": project_id,
                    "enable_env_agent": enable_env_agent,
                    "env_event_probability": env_probability
                },
                timeout=300  # 5分钟超时
            )
            response.raise_for_status()
            
            result = response.json()
            logs = result.get("logs", [])
            
            # 转换为DataFrame
            if logs:
                df_data = []
                for log in logs:
                    df_data.append({
                        "时间": log.get("timestamp", ""),
                        "角色": log.get("role_name", ""),
                        "事件类型": log.get("event_type", ""),
                        "任务": log.get("task_name", "") or log.get("task_id", ""),
                        "内容": log.get("content", "")[:100] + "..." if len(log.get("content", "")) > 100 else log.get("content", ""),
                        "状态": log.get("status", ""),
                        "进度(%)": log.get("progress_percentage", "")
                    })
                df = pd.DataFrame(df_data)
            else:
                df = pd.DataFrame(columns=["时间", "角色", "事件类型", "任务", "内容", "状态", "进度(%)"])
            
            summary_info = f"## 模拟执行完成！\n\n"
            summary_info += f"**总日志数**: {len(logs)}\n\n"
            
            return summary_info, "", df
            
        except Exception as e:
            logger.error(f"模拟失败: {str(e)}", exc_info=True)
            return f"❌ 模拟失败: {str(e)}", "", None
    except Exception as e:
        logger.error(f"模拟失败: {str(e)}", exc_info=True)
        return f"❌ 模拟失败: {str(e)}", "", None


def format_daily_summaries(summaries):
    """格式化每日摘要为Markdown"""
    if not summaries:
        return "⚠️ 暂无每日摘要数据"
    
    md_lines = []
    md_lines.append("# 📅 每日执行摘要\n")
    
    for summary in summaries:
        day_number = summary.get('day_number', 0)
        md_lines.append(f"## 第{day_number}天\n")
        
        # 任务情况
        started = summary.get('total_tasks_started', 0)
        completed = summary.get('total_tasks_completed', 0)
        progress = summary.get('overall_progress', 0)
        
        md_lines.append(f"✅ **任务完成**: {completed}/{started} 个  ")
        md_lines.append(f"📊 **整体进度**: {progress}%\n")
        
        # Agent执行情况
        agent_summaries = summary.get('agent_summaries', [])
        if agent_summaries:
            md_lines.append("### 👥 Agent执行情况\n")
            for agent_sum in agent_summaries:
                role_name = agent_sum.get('role_name', 'N/A')
                tasks = agent_sum.get('tasks_executed', [])
                efficiency = agent_sum.get('efficiency', 0)
                
                md_lines.append(f"#### {role_name}\n")
                md_lines.append(f"- ⏱️ **工作时长**: {agent_sum.get('work_hours', 0)}小时")
                md_lines.append(f"- 🎯 **效率**: {efficiency}%")
                md_lines.append(f"- ✅ **完成任务**: {len(tasks)}个\n")
                
                if tasks:
                    md_lines.append("**任务详情**:")
                    for task in tasks[:3]:  # 最多显示3个
                        task_name = task.get('task_name', 'N/A')
                        status = task.get('status', '')
                        task_progress = task.get('progress', 0)
                        md_lines.append(f"  - {task_name}: {status} - {task_progress}%")
                    if len(tasks) > 3:
                        md_lines.append(f"  - ... 还有 {len(tasks) - 3} 个任务")
                    md_lines.append("")
        
        # 环境事件
        env_events = summary.get('env_events', [])
        if env_events:
            md_lines.append("### 🌪️ 环境事件\n")
            for event in env_events[:5]:  # 最多显示5个
                event_time = event.get('time', '')
                description = event.get('description', '')
                md_lines.append(f"- **{event_time}**: {description}")
            if len(env_events) > 5:
                md_lines.append(f"- ... 还有 {len(env_events) - 5} 个事件")
            md_lines.append("")
        
        md_lines.append("---\n")
    
    return "\n".join(md_lines)


def generate_outputs(project_id):
    """生成输出文件"""
    if not project_id:
        return "请先完成模拟", None, None, None
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/simulation/generate-outputs",
            json={"project_id": project_id}
        )
        response.raise_for_status()
        
        result = response.json()
        outputs = result["outputs"]
        
        return (
            "✅ 输出文件生成完成！",
            outputs.get("schedule_csv"),
            outputs.get("mermaid"),
            outputs.get("triplets")
        )
        
    except Exception as e:
        return f"❌ 生成失败: {str(e)}", None, None, None


def test_llm_connection(api_url, api_key, model_name, temperature, max_tokens):
    """测试LLM连接"""
    try:
        if not api_url or not api_key:
            return "⚠️ 请填写API URL和API Key"
        
        response = requests.post(
            f"{BACKEND_URL}/api/config/test-llm",
            json={
                "api_base_url": api_url,
                "api_key": api_key,
                "model_name": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            timeout=30
        )
        
        if response.status_code != 200:
            error_detail = response.json().get("detail", "未知错误") if response.headers.get("content-type") == "application/json" else response.text
            return f"❌ 测试失败: {error_detail}"
        
        result = response.json()
        
        if result.get("success"):
            return f"""✅ 连接成功！

- **延迟**: {result.get('latency_ms', 0)}ms
- **模型**: {result.get('model_info', {}).get('model_name', 'N/A')}
- **API URL**: {result.get('model_info', {}).get('api_base_url', 'N/A')}
"""
        else:
            return f"❌ 连接失败: {result.get('message', '未知错误')}"
            
    except Exception as e:
        return f"❌ 测试失败: {str(e)}"


def save_llm_config(api_url, api_key, model_name, temperature, max_tokens, timeout):
    """保存LLM配置"""
    try:
        if not api_url:
            return "⚠️ 请填写API URL"
        
        # 如果API Key是占位符，说明用户没有修改，不需要重新提交
        if api_key == "********":
            return "ℹ️ API Key 未修改，其他配置已更新（如需修改 API Key，请直接输入新值）"
        
        if not api_key:
            return "⚠️ 请填写API Key"
        
        response = requests.post(
            f"{BACKEND_URL}/api/config/llm",
            json={
                "api_base_url": api_url,
                "api_key": api_key,
                "model_name": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timeout": timeout
            },
            timeout=10
        )
        
        if response.status_code != 200:
            error_detail = response.json().get("detail", "未知错误") if response.headers.get("content-type") == "application/json" else response.text
            return f"❌ 保存失败: {error_detail}"
        
        result = response.json()
        
        if result.get("success"):
            return f"✅ 配置保存成功！\n\n{result.get('message', '')}"
        else:
            return f"❌ 保存失败: {result.get('message', '未知错误')}"
            
    except Exception as e:
        return f"❌ 保存失败: {str(e)}"


def load_plotly_graph(project_id):
    """加载Plotly交互式图谱"""
    if not project_id:
        return None
    
    try:
        logger.info(f"加载图谱: project_id={project_id}")
        response = requests.get(
            f"{BACKEND_URL}/api/graph/visualize/{project_id}",
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info("图谱加载成功")
            return result["graph"]  # 返回Plotly Figure字典
        else:
            logger.warning(f"图谱加载失败: status={response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"加载图谱失败: {str(e)}", exc_info=True)
        return None


def load_llm_config():
    """从后端加载LLM配置"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/config/llm",
            timeout=10
        )
        
        if response.status_code == 200:
            config = response.json()
            # 返回配置值，用于填充表单
            # 注意：API Key 不会返回完整值，只返回是否已配置的标志
            return (
                config.get("api_base_url", "https://api.openai.com/v1"),
                "" if not config.get("api_key_configured") else "********",  # 已配置则显示占位符
                config.get("model_name", "gpt-4"),
                config.get("temperature", 0.7),
                config.get("max_tokens", 2000),
                config.get("timeout", 60),
                "ℹ️ 已加载保存的配置" if config.get("api_key_configured") else "⚠️ 请配置 LLM API"
            )
        else:
            # 返回默认值
            return (
                "https://api.openai.com/v1",
                "",
                "gpt-4",
                0.7,
                2000,
                60,
                "⚠️ 无法加载配置，请手动输入"
            )
            
    except Exception as e:
        # 返回默认值
        return (
            "https://api.openai.com/v1",
            "",
            "gpt-4",
            0.7,
            2000,
            60,
            f"⚠️ 加载配置失败: {str(e)}"
        )


# 创建Gradio界面
with gr.Blocks(title="TeamWork - AI多角色任务协同模拟系统", theme=gr.themes.Soft(), css="""
.scrollable-output {
    max-height: 400px;
    overflow-y: auto;
}
""") as app:
    
    gr.Markdown("""
    # 🤝 TeamWork - AI多角色任务协同模拟系统
    
    将任意需求文档自动拆解为结构化任务，并通过多角色Agent模拟真实项目执行过程。
    """)
    
    # 存储项目ID的隐藏组件
    project_id_state = gr.State(value=None)
    
    # Tab 1: 主工作台
    with gr.Tab("📊 主工作台"):
        gr.Markdown("## 1️⃣ 文档上传与解析")
        
        with gr.Row():
            with gr.Column(scale=1):
                file_input = gr.File(label="上传需求文档（支持PDF、MD、TXT、DOCX）")
                upload_btn = gr.Button("📤 上传并解析", variant="primary")
            
            with gr.Column(scale=2):
                requirements_output = gr.Markdown(label="需求信息", elem_classes=["scrollable-output"])
                with gr.Row():
                    download_req_btn = gr.DownloadButton("⬇️ 下载解析结果", visible=False)
        
        gr.Markdown("---")
        gr.Markdown("## 2️⃣ 任务拆解")
        
        decompose_btn = gr.Button("🔨 执行任务拆解", variant="primary")
        
        with gr.Row():
            with gr.Column(scale=2):
                tasks_output = gr.Markdown(label="任务列表", elem_classes=["scrollable-output"])
            with gr.Column(scale=1):
                gr.Markdown("### 下载选项")
                download_task_md_btn = gr.DownloadButton("⬇️ 下载任务说明(MD)")
                download_task_json_btn = gr.DownloadButton("⬇️ 下载任务数据(JSON)")
                download_tree_json_btn = gr.DownloadButton("⬇️ 下载任务树(JSON)")
        
        gr.Markdown("---")
        gr.Markdown("## 3️⃣ 模拟执行")
        
        with gr.Row():
            with gr.Column():
                agent_btn = gr.Button("👥 生成角色Agent", variant="secondary")
                agents_output = gr.Markdown(label="角色信息")
        
        gr.Markdown("### 编辑Agent和工期")
        with gr.Row():
            with gr.Column(scale=3):
                agent_edit_table = gr.Dataframe(
                    headers=["启用", "Agent ID", "角色名称", "角色类型", "能力", "分配任务"],
                    label="Agent编辑表（可直接修改）",
                    interactive=True,
                    wrap=True,
                    datatype=["bool", "str", "str", "str", "str", "str"]
                )
            with gr.Column(scale=1):
                total_days_input = gr.Number(
                    label="项目总工期（天）",
                    value=30,
                    precision=0
                )
                save_agent_btn = gr.Button("💾 保存修改", variant="primary")
                save_result = gr.Markdown()
        
        with gr.Accordion("⚙️ 模拟参数配置", open=False):
            enable_env_agent = gr.Checkbox(label="启用环境干扰Agent", value=True)
            env_probability = gr.Slider(
                label="环境事件发生概率",
                minimum=0.0,
                maximum=1.0,
                value=0.2,
                step=0.05
            )
        
        simulate_btn = gr.Button("▶️ 开始模拟", variant="primary", size="lg")
        
        simulation_summary = gr.Markdown(label="模拟摘要")
        
        gr.Markdown("### 📅 每日执行摘要（实时更新）")
        daily_summary_display = gr.Markdown(label="每日摘要", value="⚠️ 请先开始模拟")
        
        gr.Markdown("### Agent对话日志")
        agent_chat_logs = gr.Dataframe(
            headers=["时间", "角色", "事件类型", "任务", "内容", "状态", "进度(%)"],
            label="实时对话日志",
            interactive=False,
            wrap=True
        )
        
        gr.Markdown("---")
        gr.Markdown("## 4️⃣ 结果下载")
        
        generate_btn = gr.Button("📦 生成输出文件", variant="primary")
        output_status = gr.Markdown()
        
        with gr.Row():
            download_csv_btn = gr.DownloadButton("⬇️ 下载排期CSV")
            download_graph_btn = gr.DownloadButton("⬇️ 下载图谱文件")
            download_triplet_btn = gr.DownloadButton("⬇️ 下载图谱数据")
    
    # Tab 2: 可视化图谱
    with gr.Tab("📈 可视化图谱"):
        gr.Markdown("## 任务依赖关系图谱")
        gr.Markdown("_完成任务拆解后自动生成_")
        
        refresh_graph_btn = gr.Button("🔄 刷新图谱")
        graph_display = gr.Plot(label="图谱可视化", show_label=True)
        
        gr.Markdown("""
        ### 图例说明
        - 🔷 蓝色节点: 任务
        - 🔶 橙色节点: Agent角色
        - ➡️ 箭头: 依赖关系或负责关系
        
        **交互功能**:
        - 鼠标滚轮: 缩放图谱
        - 拖拽: 移动视角
        - 悬停: 查看节点详情
        - 点击图例: 隐藏/显示特定类型
        """)
    
    # Tab 3: 系统配置
    with gr.Tab("⚙️ 系统配置"):
        gr.Markdown("## LLM模型配置")
        
        with gr.Row():
            with gr.Column():
                api_url = gr.Textbox(
                    label="API Base URL",
                    value="https://api.openai.com/v1",
                    placeholder="例如: https://api.openai.com/v1"
                )
                api_key = gr.Textbox(
                    label="API Key",
                    type="password",
                    placeholder="输入你的API密钥"
                )
                
            with gr.Column():
                model_name = gr.Textbox(
                    label="模型名称",
                    value="gpt-4",
                    placeholder="例如: gpt-4, gpt-3.5-turbo"
                )
                timeout_input = gr.Slider(
                    label="超时时间(秒)",
                    minimum=10,
                    maximum=300,
                    value=60,
                    step=10
                )
        
        with gr.Row():
            with gr.Column():
                temperature = gr.Slider(
                    label="温度 (Temperature)",
                    minimum=0.0,
                    maximum=2.0,
                    value=0.7,
                    step=0.1,
                    info="控制输出的随机性，值越高输出越随机"
                )
            with gr.Column():
                max_tokens = gr.Slider(
                    label="最大Token数",
                    minimum=100,
                    maximum=8000,
                    value=2000,
                    step=100,
                    info="控制单次生成的最大长度"
                )
        
        with gr.Row():
            test_llm_btn = gr.Button("🔌 测试连接", variant="secondary")
            save_llm_btn = gr.Button("💾 保存配置", variant="primary")
            load_config_btn = gr.Button("🔄 加载配置", variant="secondary")
        
        llm_result = gr.Markdown(label="配置结果")
    
    # 事件绑定 - 文档上传
    def handle_upload(file):
        result_md, req_file_path, proj_id = upload_document(file)
        return result_md, req_file_path, proj_id
    
    upload_btn.click(
        handle_upload,
        inputs=[file_input],
        outputs=[requirements_output, download_req_btn, project_id_state]
    )
    
    # 任务拆解
    def handle_decompose(proj_id):
        task_md, tasks, breakdown_md, tasks_json, tree_json = decompose_tasks(proj_id)
        return task_md, breakdown_md, tasks_json, tree_json
    
    decompose_btn.click(
        handle_decompose,
        inputs=[project_id_state],
        outputs=[tasks_output, download_task_md_btn, download_task_json_btn, download_tree_json_btn]
    )
    
    # 生成Agent
    def handle_generate_agents(proj_id):
        agent_md, agent_table, agents = generate_agents(proj_id)
        return agent_md, agent_table
    
    agent_btn.click(
        handle_generate_agents,
        inputs=[project_id_state],
        outputs=[agents_output, agent_edit_table]
    )
    
    # 保存Agent编辑
    def handle_save_agents(proj_id, agent_table, total_days):
        result = save_agent_edits(proj_id, agent_table, total_days)
        return result
    
    save_agent_btn.click(
        handle_save_agents,
        inputs=[project_id_state, agent_edit_table, total_days_input],
        outputs=[save_result]
    )
    
    # 运行模拟（使用流式）
    def handle_simulation(proj_id, enable_env, env_prob):
        summary, daily_summary_md, df = run_simulation_stream(proj_id, enable_env, env_prob)
        return summary, daily_summary_md, df
    
    simulate_btn.click(
        handle_simulation,
        inputs=[project_id_state, enable_env_agent, env_probability],
        outputs=[simulation_summary, daily_summary_display, agent_chat_logs]
    )
    
    # 生成输出
    def handle_generate_outputs(proj_id):
        status, csv_path, graph_path, triplet_path = generate_outputs(proj_id)
        return status, csv_path, graph_path, triplet_path
    
    generate_btn.click(
        handle_generate_outputs,
        inputs=[project_id_state],
        outputs=[output_status, download_csv_btn, download_graph_btn, download_triplet_btn]
    )
    
    # 刷新图谱
    def handle_refresh_graph(proj_id):
        return load_plotly_graph(proj_id)
    
    refresh_graph_btn.click(
        handle_refresh_graph,
        inputs=[project_id_state],
        outputs=[graph_display]
    )
    
    # 配置LLM - 测试连接
    test_llm_btn.click(
        test_llm_connection,
        inputs=[api_url, api_key, model_name, temperature, max_tokens],
        outputs=[llm_result]
    )
    
    # 配置LLM - 保存配置
    save_llm_btn.click(
        save_llm_config,
        inputs=[api_url, api_key, model_name, temperature, max_tokens, timeout_input],
        outputs=[llm_result]
    )
    
    # 配置LLM - 加载配置
    load_config_btn.click(
        load_llm_config,
        inputs=[],
        outputs=[api_url, api_key, model_name, temperature, max_tokens, timeout_input, llm_result]
    )
    
    # 页面加载时自动加载配置
    app.load(
        load_llm_config,
        inputs=[],
        outputs=[api_url, api_key, model_name, temperature, max_tokens, timeout_input, llm_result]
    )


if __name__ == "__main__":
    logger.info("TeamWork前端启动中...")
    logger.info(f"后端API地址: {BACKEND_URL}")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
