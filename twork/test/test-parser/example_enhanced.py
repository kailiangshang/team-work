"""
StructureUnderstandFactory 增强版示例脚本

演示如何使用增强版的结构化信息生产工厂，包括图谱提取功能。
"""

import sys
from pathlib import Path
import json

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from twork.parser.structure_factory import StructureUnderstandFactory
from twork.parser.tools.doc_parse_tool import DocParseTool
from twork.parser.tools.requirement_analyzer_tool import RequirementAndDomainAnalyzerTool
from twork.parser.tools.wbs_parse_tool import WbsParseTool
from twork.llm.openai_adapter import OpenAIAdapter
from twork.llm.config import LLMConfig


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_subsection(title: str):
    """打印子分节标题"""
    print(f"\n[{title}]")
    print("-" * 40)


def main():
    """主函数"""
    
    print_section("StructureUnderstandFactory 增强版示例")
    
    # 配置LLM
    print_subsection("1. 配置LLM适配器")
    llm_config = LLMConfig(
        api_base_url="https://api.openai.com/v1",  # 修改为你的API地址
        api_key="your-api-key-here",  # 修改为你的API密钥
        model_name="gpt-4",
        temperature=0.7,
        max_tokens=2000,
        enable_cache=True,
        cache_dir="./llm_cache"
    )
    
    llm = OpenAIAdapter(llm_config)
    print("✓ LLM适配器配置完成")
    
    # 创建工厂
    print_subsection("2. 创建StructureUnderstandFactory")
    
    # 创建示例文档
    example_doc = Path("./example_software_project.md")
    if not example_doc.exists():
        print("创建示例文档...")
        create_example_document(example_doc)
        print(f"✓ 示例文档已创建: {example_doc}")
    
    factory = StructureUnderstandFactory(
        project_id="P-SOFTWARE-DEV-001",
        original_file_path=str(example_doc),
        cache_dir="./cache"
    )
    print("✓ 工厂创建完成")
    
    # 配置工具的LLM适配器
    print_subsection("3. 配置工具")
    for tool_name in ["analyzer", "wbs"]:
        factory.tools[tool_name].setup({
            "llm_adapter": llm,
            "temperature": 0.5
        })
    print("✓ 工具配置完成")
    
    # 运行工厂（启用图谱提取）
    print_subsection("4. 执行完整流程（包括图谱提取）")
    try:
        result = factory.run(extract_graph=True)
        
        # 显示需求分析结果
        print("\n需求与领域分析结果:")
        req_and_domain = result['requirements_and_domain']
        print(f"  领域: {req_and_domain.get('domain', 'N/A')}")
        print(f"  领域置信度: {req_and_domain.get('domain_confidence', 0):.2f}")
        print(f"  功能需求数量: {len(req_and_domain.get('functional_requirements', []))}")
        print(f"  非功能需求数量: {len(req_and_domain.get('non_functional_requirements', []))}")
        
        # 显示实体信息
        entities = req_and_domain.get('entities', {})
        print(f"\n  提取的实体:")
        print(f"    - 角色: {len(entities.get('roles', []))} 个")
        print(f"    - 工具: {len(entities.get('tools', []))} 个")
        print(f"    - 技能: {len(entities.get('skills', []))} 个")
        
        # 显示技术栈
        tech_stack = req_and_domain.get('tech_stack', {})
        if tech_stack:
            print(f"\n  技术栈:")
            for category, techs in tech_stack.items():
                if techs:
                    print(f"    - {category}: {', '.join(techs)}")
        
        # 显示WBS结果
        print("\nWBS任务树结果:")
        wbs = result['wbs']
        print(f"  阶段: {wbs.get('phase', 'N/A')}")
        print(f"  任务数量: {len(wbs.get('tasks', []))}")
        print(f"  总工时: {wbs.get('total_estimated_hours', 0)} 小时")
        
        # 显示资源汇总
        resource_summary = wbs.get('resource_summary', {})
        if resource_summary:
            print(f"\n  资源汇总:")
            total_roles = resource_summary.get('total_roles', [])
            print(f"    - 涉及角色: {len(total_roles)} 个")
            for role_stat in total_roles[:5]:  # 显示前5个
                print(f"      * {role_stat.get('role')}: {role_stat.get('total_hours')} 小时 ({role_stat.get('task_count')} 个任务)")
            
            total_tools = resource_summary.get('total_tools', [])
            if total_tools:
                print(f"    - 涉及工具: {', '.join(total_tools[:10])}")
        
        # 显示图谱提取结果
        print("\n图谱提取结果:")
        graph = result.get('graph', {})
        nodes = graph.get('nodes', [])
        edges = graph.get('edges', [])
        
        print(f"  节点数量: {len(nodes)}")
        print(f"  边数量: {len(edges)}")
        
        # 统计节点类型
        node_type_stats = {}
        for node in nodes:
            node_type = node.get('type', 'UNKNOWN')
            node_type_stats[node_type] = node_type_stats.get(node_type, 0) + 1
        
        print(f"\n  节点类型统计:")
        for node_type, count in node_type_stats.items():
            print(f"    - {node_type}: {count} 个")
        
        # 统计关系类型
        edge_type_stats = {}
        for edge in edges:
            edge_type = edge.get('relation', 'UNKNOWN')
            edge_type_stats[edge_type] = edge_type_stats.get(edge_type, 0) + 1
        
        print(f"\n  关系类型统计:")
        for edge_type, count in edge_type_stats.items():
            print(f"    - {edge_type}: {count} 条")
        
        # 保存结果到文件
        print_subsection("5. 保存结果到文件")
        output_dir = Path("./output")
        output_dir.mkdir(exist_ok=True)
        
        # 保存完整结果
        with open(output_dir / "full_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✓ 完整结果已保存: {output_dir / 'full_result.json'}")
        
        # 保存图谱数据
        with open(output_dir / "graph_data.json", "w", encoding="utf-8") as f:
            json.dump(graph, f, ensure_ascii=False, indent=2)
        print(f"✓ 图谱数据已保存: {output_dir / 'graph_data.json'}")
        
        print("\n✓ 流程执行成功!")
        
    except Exception as e:
        print(f"\n✗ 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    print_section("示例运行完成!")
    print("\n提示:")
    print("1. 请根据实际情况修改LLM配置（API地址、密钥等）")
    print("2. 结果文件保存在 ./output/ 目录下")
    print("3. 可以使用图谱数据构建知识图谱或进行可视化展示")


def create_example_document(file_path: Path):
    """创建示例文档"""
    content = """# 在线任务管理系统需求文档

## 1. 项目概述

本项目旨在开发一个基于Web的在线任务管理系统，帮助团队进行高效协作和任务跟踪。

## 2. 功能需求

### 2.1 用户管理模块
- **用户注册**：支持邮箱和手机号注册，发送验证码
- **用户登录**：支持邮箱/手机号登录，支持第三方登录（微信、GitHub）
- **权限管理**：支持角色权限配置（管理员、项目经理、普通成员）
- **个人信息管理**：支持头像上传、昵称修改、密码重置

### 2.2 任务管理模块
- **任务创建**：创建任务，设置标题、描述、截止时间、优先级、标签
- **任务分配**：将任务分配给团队成员
- **任务状态**：待处理、进行中、已完成、已关闭
- **任务跟踪**：查看任务历史记录和变更日志
- **子任务**：支持创建子任务，形成任务层级结构

### 2.3 团队协作模块
- **团队创建**：创建团队，设置团队名称和描述
- **成员管理**：邀请成员、移除成员、设置成员权限
- **任务评论**：支持任务评论和@提醒
- **通知系统**：任务分配、状态变更、评论等实时通知

### 2.4 数据统计模块
- **任务统计**：按状态、优先级、成员统计任务数量
- **进度报告**：生成项目进度报告
- **可视化图表**：任务甘特图、燃尽图、统计图表

## 3. 非功能需求

### 3.1 性能要求
- 页面响应时间：小于2秒
- 并发用户数：支持10000+在线用户
- 数据库查询优化：复杂查询响应时间小于500ms

### 3.2 安全要求
- 数据传输加密：使用HTTPS协议
- 密码加密存储：使用bcrypt加密
- 防止XSS、CSRF攻击
- 定期数据备份

### 3.3 可用性要求
- 系统可用性：99.9%在线时间
- 故障恢复时间：小于30分钟
- 支持多终端访问：Web、移动端

### 3.4 可维护性要求
- 代码规范：遵循PEP8规范
- 文档齐全：API文档、用户手册、开发文档
- 单元测试覆盖率：大于80%

## 4. 技术栈

### 4.1 前端
- 框架：React 18.x
- 状态管理：Redux Toolkit
- UI组件库：Ant Design
- 构建工具：Vite
- 语言：TypeScript

### 4.2 后端
- 框架：FastAPI
- 语言：Python 3.8+
- 异步处理：asyncio、aiohttp
- 任务队列：Celery + Redis

### 4.3 数据库
- 主数据库：PostgreSQL 14+
- 缓存：Redis 6+
- 搜索引擎：Elasticsearch（可选）

### 4.4 部署
- 容器化：Docker
- 编排：Kubernetes
- CI/CD：GitHub Actions
- 监控：Prometheus + Grafana

## 5. 交付物

- 需求文档
- 架构设计文档
- API接口文档
- 前端源代码
- 后端源代码
- 数据库脚本
- 部署文档
- 用户手册
- 测试报告
"""
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    main()
