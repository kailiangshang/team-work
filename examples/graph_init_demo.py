#!/usr/bin/env python3
"""
图谱初始化流程示例

演示如何使用 twork 核心库完成从文档到图谱的完整初始化流程。
"""

import json
import sys
from pathlib import Path

# 添加 twork 到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from twork.parser import (
    DocumentLoader,
    RequirementExtractor,
    DomainClassifier,
    WBSDecomposer
)
from twork.agent import RoleGenerator
from twork.generator import GraphBuilder
from twork.llm import OpenAIAdapter
from twork.utils.logger import get_logger

logger = get_logger("graph_init_demo")


def main():
    """主流程"""
    
    print("=" * 80)
    print("twork 图谱初始化流程示例")
    print("=" * 80)
    
    # ===== 步骤 0: 初始化 LLM =====
    print("\n📌 步骤 0: 初始化 LLM")
    llm = OpenAIAdapter(api_key="your-openai-api-key")  # 请替换为实际的 API Key
    print("✅ LLM 初始化完成")
    
    # ===== 步骤 1: 加载文档 =====
    print("\n📌 步骤 1: 加载项目文档")
    
    # 创建示例文档(实际使用时替换为真实文档路径)
    sample_doc_path = Path(__file__).parent / "sample_project.txt"
    
    if not sample_doc_path.exists():
        # 创建示例文档
        sample_content = """
项目名称: 智能客服系统

项目描述:
开发一个基于 AI 的智能客服系统,支持多渠道接入、智能问答、工单管理等功能。

主要目标:
1. 提升客户服务效率,减少人工客服工作量
2. 提供 7x24 小时在线服务
3. 支持多语言、多渠道(网页、微信、APP)

核心需求:
1. 用户管理:支持用户注册、登录、权限管理
2. 智能问答:基于 NLP 的智能问答引擎
3. 工单系统:问题工单创建、分配、跟踪
4. 知识库:支持知识库管理和智能检索
5. 数据分析:客服数据统计和分析报表
6. 系统对接:与现有 CRM 系统对接

约束条件:
- 需要兼容现有系统架构
- 数据安全合规
- 性能要求:支持 1000 并发用户

期望交付物:
- Web 管理后台
- 移动端 APP
- API 接口文档
- 用户使用手册
"""
        sample_doc_path.write_text(sample_content, encoding="utf-8")
        print(f"✅ 创建示例文档: {sample_doc_path}")
    
    loader = DocumentLoader()
    doc_result = loader.load(file_path=str(sample_doc_path))
    
    print(f"✅ 文档加载成功:")
    print(f"   - 文件名: {doc_result['file_name']}")
    print(f"   - 文件类型: {doc_result['file_type']}")
    print(f"   - 文件大小: {doc_result['file_size']} 字节")
    print(f"   - 内容长度: {len(doc_result['content'])} 字符")
    
    # ===== 步骤 2: 提取需求 =====
    print("\n📌 步骤 2: 智能提取需求信息")
    
    extractor = RequirementExtractor(llm_adapter=llm)
    requirements = extractor.extract(document_content=doc_result["content"])
    
    print(f"✅ 需求提取成功:")
    print(f"   - 项目名称: {requirements.get('project_name', 'N/A')}")
    print(f"   - 主要目标: {len(requirements.get('main_objectives', []))} 个")
    print(f"   - 核心需求: {len(requirements.get('key_requirements', []))} 个")
    print(f"   - 约束条件: {len(requirements.get('constraints', []))} 个")
    
    # ===== 步骤 3: 领域分类 =====
    print("\n📌 步骤 3: 项目领域分类")
    
    classifier = DomainClassifier()
    domain_result = classifier.classify(
        content=requirements["project_description"],
        user_selected_domain=None  # 可以手动指定领域,如 "软件开发"
    )
    
    print(f"✅ 领域分类完成:")
    print(f"   - 领域类型: {domain_result['domain_type']}")
    print(f"   - 置信度: {domain_result['confidence']}")
    print(f"   - 关键词: {', '.join(domain_result['keywords'][:5])}...")
    print(f"   - 模板ID: {domain_result['template_id']}")
    
    # 用户可在此处修改领域(可编辑点)
    # domain_result['domain_type'] = "软件开发"  # 手动修改
    
    # ===== 步骤 4: WBS 任务拆解 ⭐ 核心可编辑点 =====
    print("\n📌 步骤 4: WBS 任务拆解")
    
    decomposer = WBSDecomposer(llm_adapter=llm, max_level=4)
    wbs_result = decomposer.decompose(
        requirements=json.dumps(requirements, ensure_ascii=False),
        domain_type=domain_result["domain_type"],
        task_types=["需求分析", "设计", "开发", "测试", "部署"],
        template_config={},
        user_constraints={
            "total_days": 60,
            "team_size": 8
        }
    )
    
    task_tree = wbs_result["task_tree"]
    stats = wbs_result["statistics"]
    
    print(f"✅ WBS 拆解完成:")
    print(f"   - 总任务数: {stats['total_tasks']}")
    print(f"   - 最大层级: {stats['max_level_reached']}")
    print(f"   - 平均复杂度: {stats['avg_complexity']}")
    print(f"   - 各层级任务数: {stats['tasks_by_level']}")
    
    # 验证依赖关系(检测循环依赖)
    print("\n📌 步骤 4.1: 验证任务依赖关系")
    is_valid, errors = decomposer.validate_dependencies(task_tree)
    
    if is_valid:
        print("✅ 依赖关系验证通过,无循环依赖")
    else:
        print("❌ 依赖关系验证失败:")
        for error in errors:
            print(f"   - {error}")
    
    # 用户可在此处编辑任务树(可编辑点)
    # 示例:删除任务、修改任务属性、添加任务等
    # task_tree[0]["estimated_complexity"] = 8  # 修改复杂度
    # task_tree[0]["children"].pop()  # 删除子任务
    
    # ===== 步骤 5: 生成角色 Agent ⭐ 核心可编辑点 =====
    print("\n📌 步骤 5: 生成项目团队角色")
    
    generator = RoleGenerator(llm_adapter=llm)
    agents = generator.generate_roles(
        task_tree=task_tree,
        domain_type=domain_result["domain_type"],
        team_size_hint=8
    )
    
    print(f"✅ 角色生成完成: 共 {len(agents)} 个角色")
    for i, agent in enumerate(agents[:3], 1):  # 显示前3个角色
        print(f"   {i}. {agent['role_name']} ({agent['role_type']})")
        print(f"      - ID: {agent['agent_id']}")
        print(f"      - 技能: {len(agent.get('capabilities', []))} 项")
        print(f"      - 分配任务: {len(agent.get('assigned_tasks', []))} 个")
    
    if len(agents) > 3:
        print(f"   ... 还有 {len(agents) - 3} 个角色")
    
    # 用户可在此处编辑 Agent(可编辑点)
    # 示例:删除 Agent、修改技能、重新分配任务
    
    # 删除 Agent 示例
    # removed_agent = agents.pop(1)  # 删除第2个 Agent
    # orphan_tasks = removed_agent.get("assigned_tasks", [])
    # 
    # # 重新分配孤儿任务
    # agents = generator.reassign_tasks(
    #     agents=agents,
    #     task_tree=task_tree,
    #     orphan_tasks=orphan_tasks
    # )
    
    # 获取任务分配推荐
    print("\n📌 步骤 5.1: 生成任务分配推荐")
    recommendations = generator.recommend_assignments(
        agents=agents,
        task_tree=task_tree,
        strategy="skill_match"  # 或 "workload_balance"
    )
    
    print(f"✅ 推荐分配: {len(recommendations)} 个任务")
    print(f"   示例推荐: {list(recommendations.items())[:3]}")
    
    # ===== 步骤 6: 构建图谱 =====
    print("\n📌 步骤 6: 构建知识图谱")
    
    builder = GraphBuilder()
    
    # 展平任务树
    flat_tasks = decomposer.flatten_tree(task_tree)
    print(f"   - 展平任务数: {len(flat_tasks)}")
    
    # 构建三元组
    triplets = builder.build_triplets(tasks=flat_tasks, agents=agents)
    print(f"✅ 三元组构建完成: {len(triplets)} 个三元组")
    
    # 示例三元组
    print(f"   示例三元组:")
    for triplet in triplets[:5]:
        print(f"   - {triplet}")
    
    # ===== 步骤 7: 导出结果 =====
    print("\n📌 步骤 7: 导出结果文件")
    
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # 导出三元组
    triplets_file = output_dir / "graph_triplets.json"
    builder.export_triplets(triplets, str(triplets_file))
    print(f"✅ 三元组已导出: {triplets_file}")
    
    # 导出 Mermaid 图谱
    mermaid_file = output_dir / "graph.md"
    builder.export_mermaid(flat_tasks, agents, str(mermaid_file))
    print(f"✅ Mermaid 图谱已导出: {mermaid_file}")
    
    # 导出任务树
    task_tree_file = output_dir / "task_tree.json"
    task_tree_file.write_text(
        json.dumps(task_tree, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"✅ 任务树已导出: {task_tree_file}")
    
    # 导出 Agent 配置
    agents_file = output_dir / "agents.json"
    agents_file.write_text(
        json.dumps(agents, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"✅ Agent 配置已导出: {agents_file}")
    
    # ===== 完成 =====
    print("\n" + "=" * 80)
    print("🎉 图谱初始化流程完成!")
    print("=" * 80)
    print(f"\n输出文件目录: {output_dir}")
    print("\n可编辑点总结:")
    print("1. 步骤 3: 可手动修改领域分类")
    print("2. 步骤 4: 可编辑任务树(删除/修改/添加任务)")
    print("3. 步骤 5: 可编辑 Agent(删除/修改技能/重新分配任务)")
    print("\n下一步:")
    print("- 将数据导入外部系统(如 FastAPI 后端)")
    print("- 使用 Neo4j 存储图谱三元组")
    print("- 运行模拟引擎执行任务")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"示例运行失败: {str(e)}", exc_info=True)
        sys.exit(1)
