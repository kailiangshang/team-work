"""
Gradio前端应用

提供用户交互界面。
"""

import gradio as gr
import requests
import os
from pathlib import Path

# 后端API地址
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# 全局变量存储当前项目ID
current_project_id = None


def upload_document(file):
    """上传文档"""
    global current_project_id
    
    if file is None:
        return "⚠️ 请选择要上传的文件", gr.update(visible=False), gr.update(visible=False)
    
    try:
        with open(file.name, "rb") as f:
            files = {"file": (Path(file.name).name, f, "application/octet-stream")}
            response = requests.post(
                f"{BACKEND_URL}/api/upload/document",
                files=files,
                timeout=120  # 增加超时时间
            )
            
            # 检查响应状态
            if response.status_code != 200:
                error_detail = response.json().get("detail", "未知错误") if response.headers.get("content-type") == "application/json" else response.text
                return f"❌ 上传失败 ({response.status_code}): {error_detail}", gr.update(visible=False), gr.update(visible=False)
            
            result = response.json()
            current_project_id = result["project_id"]
            requirements = result["requirements"]
            
            # 格式化需求信息
            info = f"""## 项目需求解析成功！

**项目名称**: {requirements.get('project_name', 'N/A')}

**项目描述**: {requirements.get('project_description', 'N/A')}

**主要目标**:
{chr(10).join(['- ' + obj for obj in requirements.get('main_objectives', [])])}

**关键需求**:
{chr(10).join(['- ' + req for req in requirements.get('key_requirements', [])])}

**项目ID**: {current_project_id}
"""
            
            return info, gr.update(visible=True), gr.update(visible=False)
            
    except requests.exceptions.Timeout:
        return "❌ 请求超时，请检查网络连接或后端服务是否正常", gr.update(visible=False), gr.update(visible=False)
    except requests.exceptions.ConnectionError:
        return f"❌ 无法连接到后端服务: {BACKEND_URL}，请检查后端是否启动", gr.update(visible=False), gr.update(visible=False)
    except Exception as e:
        return f"❌ 上传失败: {str(e)}", gr.update(visible=False), gr.update(visible=False)


def decompose_tasks():
    """拆解任务"""
    global current_project_id
    
    if not current_project_id:
        return "请先上传文档", gr.update(visible=False)
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/task/decompose",
            json={"project_id": current_project_id}
        )
        response.raise_for_status()
        
        result = response.json()
        tasks = result["tasks"]
        
        # 格式化任务信息
        task_info = f"## 任务拆解完成！\n\n共生成 {len(tasks)} 个任务:\n\n"
        for i, task in enumerate(tasks, 1):
            task_info += f"### {i}. {task['task_name']}\n"
            task_info += f"- **任务ID**: {task['task_id']}\n"
            task_info += f"- **工期**: {task['duration_days']} 天\n"
            task_info += f"- **描述**: {task['description']}\n\n"
        
        return task_info, gr.update(visible=True)
        
    except Exception as e:
        return f"❌ 任务拆解失败: {str(e)}", gr.update(visible=False)


def generate_agents():
    """生成Agent"""
    global current_project_id
    
    if not current_project_id:
        return "请先上传文档并拆解任务"
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/task/generate-agents",
            json={"project_id": current_project_id}
        )
        response.raise_for_status()
        
        result = response.json()
        agents = result["agents"]
        
        # 格式化Agent信息
        agent_info = f"## Agent生成完成！\n\n共生成 {len(agents)} 个角色:\n\n"
        for i, agent in enumerate(agents, 1):
            agent_info += f"### {i}. {agent['role_name']}\n"
            agent_info += f"- **角色类型**: {agent.get('role_type', 'N/A')}\n"
            agent_info += f"- **核心能力**: {', '.join(agent.get('capabilities', []))}\n"
            agent_info += f"- **负责任务**: {', '.join(agent.get('assigned_tasks', []))}\n\n"
        
        return agent_info
        
    except Exception as e:
        return f"❌ Agent生成失败: {str(e)}"


def run_simulation():
    """运行模拟"""
    global current_project_id
    
    if not current_project_id:
        return "请先完成前面的步骤", gr.update(visible=False)
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/simulation/run",
            json={"project_id": current_project_id}
        )
        response.raise_for_status()
        
        result = response.json()
        logs = result["logs"]
        
        # 格式化模拟日志
        log_info = f"## 模拟执行完成！\n\n共模拟 {len(logs)} 个工作日:\n\n"
        for log in logs[:10]:  # 只显示前10条
            log_info += f"**第{log['day_number']}天 - {log['role_name']}**\n"
            log_info += f"- 备注: {log.get('notes', 'N/A')}\n\n"
        
        if len(logs) > 10:
            log_info += f"... (共{len(logs)}条日志)\n"
        
        return log_info, gr.update(visible=True)
        
    except Exception as e:
        return f"❌ 模拟执行失败: {str(e)}", gr.update(visible=False)


def generate_outputs():
    """生成输出文件"""
    global current_project_id
    
    if not current_project_id:
        return "请先完成模拟", "", "", ""
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/simulation/generate-outputs",
            json={"project_id": current_project_id}
        )
        response.raise_for_status()
        
        result = response.json()
        outputs = result["outputs"]
        
        return (
            "✅ 输出文件生成完成！",
            outputs.get("markdown", ""),
            outputs.get("schedule_csv", ""),
            outputs.get("mermaid", "")
        )
        
    except Exception as e:
        return f"❌ 生成失败: {str(e)}", "", "", ""


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
        if not api_url or not api_key:
            return "⚠️ 请填写API URL和API Key"
        
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


# 创建Gradio界面
with gr.Blocks(title="TeamWork - AI多角色任务协同模拟系统", theme=gr.themes.Soft()) as app:
    gr.Markdown("""
    # 🤝 TeamWork - AI多角色任务协同模拟系统
    
    将任意需求文档自动拆解为结构化任务，并通过多角色Agent模拟真实项目执行过程。
    """)
    
    with gr.Tab("📄 文档上传"):
        with gr.Row():
            with gr.Column():
                file_input = gr.File(label="上传需求文档（支持PDF、MD、TXT、DOCX）")
                upload_btn = gr.Button("上传并解析", variant="primary")
            
            with gr.Column():
                requirements_output = gr.Markdown(label="需求信息")
        
        decompose_btn = gr.Button("拆解任务", variant="primary", visible=False)
        tasks_output = gr.Markdown(label="任务列表")
        
        agent_btn = gr.Button("生成角色Agent", variant="primary", visible=False)
        agents_output = gr.Markdown(label="角色信息")
    
    with gr.Tab("🎮 模拟执行"):
        simulate_btn = gr.Button("开始模拟", variant="primary", size="lg")
        simulation_output = gr.Markdown(label="模拟日志")
        
        generate_btn = gr.Button("生成输出文件", variant="primary", visible=False)
        
        with gr.Row():
            output_status = gr.Markdown(label="状态")
        
        with gr.Row():
            md_file = gr.Textbox(label="任务文档路径", interactive=False)
            csv_file = gr.Textbox(label="排期CSV路径", interactive=False)
            graph_file = gr.Textbox(label="图谱文件路径", interactive=False)
    
    with gr.Tab("⚙️ 配置"):
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
        
        llm_result = gr.Markdown(label="结果")
    
    # 事件绑定
    upload_btn.click(
        upload_document,
        inputs=[file_input],
        outputs=[requirements_output, decompose_btn, tasks_output]
    )
    
    decompose_btn.click(
        decompose_tasks,
        outputs=[tasks_output, agent_btn]
    )
    
    agent_btn.click(
        generate_agents,
        outputs=[agents_output]
    )
    
    simulate_btn.click(
        run_simulation,
        outputs=[simulation_output, generate_btn]
    )
    
    generate_btn.click(
        generate_outputs,
        outputs=[output_status, md_file, csv_file, graph_file]
    )
    
    test_llm_btn.click(
        test_llm_connection,
        inputs=[api_url, api_key, model_name, temperature, max_tokens],
        outputs=[llm_result]
    )
    
    save_llm_btn.click(
        save_llm_config,
        inputs=[api_url, api_key, model_name, temperature, max_tokens, timeout_input],
        outputs=[llm_result]
    )


if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
