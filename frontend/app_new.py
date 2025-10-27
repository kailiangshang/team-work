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
        with open(file.name, "rb") as f:
            files = {"file": (Path(file.name).name, f, "application/octet-stream")}
            response = requests.post(
                f"{BACKEND_URL}/api/upload/document",
                files=files,
                timeout=120
            )
            
            if response.status_code != 200:
                error_detail = response.json().get("detail", "未知错误") if response.headers.get("content-type") == "application/json" else response.text
                return f"❌ 上传失败 ({response.status_code}): {error_detail}", None, None
            
            result = response.json()
            current_project_id = result["project_id"]
            requirements = result["requirements"]
            files_info = result.get("files", {})
            
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
        return "❌ 请求超时，请检查网络连接或后端服务是否正常", None, None
    except requests.exceptions.ConnectionError:
        return f"❌ 无法连接到后端服务: {BACKEND_URL}，请检查后端是否启动", None, None
    except Exception as e:
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
            return temp_path
        else:
            return None
            
    except Exception as e:
        print(f"下载失败: {str(e)}")
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
        return "请先上传文档并拆解任务", None
    
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
        
        return agent_info, agents
        
    except Exception as e:
        return f"❌ Agent生成失败: {str(e)}", None


def run_simulation(project_id, enable_env_agent, env_probability):
    """运行模拟"""
    if not project_id:
        return "请先完成前面的步骤", None, None, None
    
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
        detailed_logs = result.get("detailed_logs", [])
        env_events = result.get("env_events", [])
        env_summary = result.get("env_summary", {})
        
        # 转换为DataFrame格式
        if detailed_logs:
            df_data = []
            for log in detailed_logs:
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
        
        # 格式化环境事件摘要
        summary_info = f"## 模拟执行完成！\n\n"
        summary_info += f"**总日志数**: {len(detailed_logs)}\n\n"
        
        if enable_env_agent and env_summary:
            summary_info += f"### 环境干扰统计\n\n"
            summary_info += f"- **总事件数**: {env_summary.get('total_events', 0)}\n"
            summary_info += f"- **总延期**: {env_summary.get('total_delay', 0)} 天\n"
            summary_info += f"- **平均延期**: {env_summary.get('average_delay', 0)} 天\n\n"
            
            if env_summary.get('by_category'):
                summary_info += "#### 按类别统计\n\n"
                for cat, stats in env_summary['by_category'].items():
                    summary_info += f"- **{cat}**: {stats['count']}次, 延期{stats['total_delay']}天\n"
        
        return summary_info, df, detailed_logs
        
    except Exception as e:
        return f"❌ 模拟执行失败: {str(e)}", None, None


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


def load_mermaid_graph(project_id):
    """加载Mermaid图谱"""
    if not project_id:
        return ""
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/download/graph_md/{project_id}",
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.text
            # 提取mermaid代码块
            if "```mermaid" in content:
                start = content.find("```mermaid") + 10
                end = content.find("```", start)
                mermaid_code = content[start:end].strip()
            else:
                mermaid_code = content
            
            # 嵌入HTML渲染
            html = f"""
            <div class="mermaid">
            {mermaid_code}
            </div>
            <script type="module">
                import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                mermaid.initialize({{ startOnLoad: true }});
            </script>
            """
            return html
        else:
            return "<p>图谱文件不存在，请先完成任务拆解和模拟执行</p>"
            
    except Exception as e:
        return f"<p>加载图谱失败: {str(e)}</p>"


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
        graph_display = gr.HTML(label="图谱可视化")
        
        gr.Markdown("""
        ### 图例说明
        - 🔷 蓝色节点: 任务
        - 🔶 橙色节点: Agent角色
        - ➡️ 箭头: 依赖关系或负责关系
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
        agent_md, agents = generate_agents(proj_id)
        return agent_md
    
    agent_btn.click(
        handle_generate_agents,
        inputs=[project_id_state],
        outputs=[agents_output]
    )
    
    # 运行模拟
    def handle_simulation(proj_id, enable_env, env_prob):
        summary, df, logs = run_simulation(proj_id, enable_env, env_prob)
        return summary, df
    
    simulate_btn.click(
        handle_simulation,
        inputs=[project_id_state, enable_env_agent, env_probability],
        outputs=[simulation_summary, agent_chat_logs]
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
        return load_mermaid_graph(proj_id)
    
    refresh_graph_btn.click(
        handle_refresh_graph,
        inputs=[project_id_state],
        outputs=[graph_display]
    )


if __name__ == "__main__":
    print(f"🚀 TeamWork前端启动中...")
    print(f"📡 后端API地址: {BACKEND_URL}")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
