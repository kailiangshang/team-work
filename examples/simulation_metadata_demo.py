#!/usr/bin/env python3
"""
模拟元信息使用示例

演示如何使用模拟元信息实现可编辑性设计:
- 用户删除 Agent 后重新分配任务
- 用户修改 Agent 技能
- 用户手动指定任务分配
- 用户标记任务为已完成
"""

import json
import sys
from pathlib import Path

# 添加 twork 到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from twork.agent import (
    RoleGenerator,
    SimulationEngine,
    SimulationMetadata,
    SimulationConfig
)
from twork.parser import WBSDecomposer
from twork.llm import OpenAIAdapter
from twork.utils.logger import get_logger

logger = get_logger("metadata_demo")


def demo_metadata_workflow():
    """演示完整的元信息工作流"""
    
    print("=" * 80)
    print("模拟元信息使用示例")
    print("=" * 80)
    
    # ===== 步骤 1: 准备测试数据 =====
    print("\n📌 步骤 1: 准备测试数据")
    
    # 模拟任务树(简化版)
    task_tree = [
        {
            "task_id": "T001",
            "task_name": "需求分析",
            "level": 1,
            "parent_task_id": None,
            "estimated_complexity": 5,
            "dependencies": [],
            "children": [
                {
                    "task_id": "T001-1",
                    "task_name": "用户访谈",
                    "level": 2,
                    "parent_task_id": "T001",
                    "estimated_complexity": 3,
                    "dependencies": [],
                    "children": []
                },
                {
                    "task_id": "T001-2",
                    "task_name": "需求文档",
                    "level": 2,
                    "parent_task_id": "T001",
                    "estimated_complexity": 4,
                    "dependencies": ["T001-1"],
                    "children": []
                }
            ]
        },
        {
            "task_id": "T002",
            "task_name": "系统设计",
            "level": 1,
            "parent_task_id": None,
            "estimated_complexity": 6,
            "dependencies": ["T001"],
            "children": []
        }
    ]
    
    # 模拟 Agent 列表
    agents = [
        {
            "agent_id": "A001",
            "role_name": "产品经理",
            "role_type": "产品",
            "capabilities": [
                {"skill_name": "需求分析", "proficiency_level": 5},
                {"skill_name": "用户研究", "proficiency_level": 4}
            ],
            "assigned_tasks": ["T001", "T001-1"],
            "available_hours_per_day": 8.0,
            "org_level": 2
        },
        {
            "agent_id": "A002",
            "role_name": "架构师",
            "role_type": "技术",
            "capabilities": [
                {"skill_name": "系统设计", "proficiency_level": 5},
                {"skill_name": "架构设计", "proficiency_level": 5}
            ],
            "assigned_tasks": ["T002"],
            "available_hours_per_day": 8.0,
            "org_level": 3
        },
        {
            "agent_id": "A003",
            "role_name": "文档工程师",
            "role_type": "文档",
            "capabilities": [
                {"skill_name": "文档编写", "proficiency_level": 4},
                {"skill_name": "技术写作", "proficiency_level": 4}
            ],
            "assigned_tasks": ["T001-2"],
            "available_hours_per_day": 8.0,
            "org_level": 3
        }
    ]
    
    print(f"✅ 初始数据准备完成:")
    print(f"   - Agent 数量: {len(agents)}")
    print(f"   - 任务数量: 3")
    
    # ===== 步骤 2: 创建模拟元信息 =====
    print("\n📌 步骤 2: 创建模拟元信息")
    
    metadata = SimulationMetadata(
        project_id=1,
        base_version_id="v1.0",
        simulation_config=SimulationConfig(
            total_days=10,
            enable_env_agent=True,
            env_event_probability=0.1
        )
    )
    
    print(f"✅ 元信息创建完成: project_id={metadata.project_id}")
    
    # ===== 步骤 3: 用户删除 Agent =====
    print("\n📌 步骤 3: 用户删除 Agent (A003 - 文档工程师)")
    
    # 记录删除的 Agent
    metadata.add_removed_agent("A003")
    
    # 获取被删除 Agent 的任务
    removed_agent = next((a for a in agents if a["agent_id"] == "A003"), None)
    orphan_tasks = removed_agent["assigned_tasks"] if removed_agent else []
    
    print(f"✅ Agent A003 已删除")
    print(f"   - 孤儿任务: {orphan_tasks}")
    
    # ===== 步骤 4: 手动重新分配任务 =====
    print("\n📌 步骤 4: 手动重新分配孤儿任务")
    
    # 将 T001-2 分配给 A001 (产品经理)
    for task_id in orphan_tasks:
        metadata.set_manual_assignment(task_id, "A001")
    
    print(f"✅ 任务已重新分配:")
    print(f"   - T001-2 → A001 (产品经理)")
    
    # ===== 步骤 5: 修改 Agent 技能 =====
    print("\n📌 步骤 5: 修改 Agent 技能")
    
    # 给产品经理添加文档编写技能
    metadata.modify_agent("A001", {
        "capabilities": [
            {"skill_name": "需求分析", "proficiency_level": 5},
            {"skill_name": "用户研究", "proficiency_level": 4},
            {"skill_name": "文档编写", "proficiency_level": 3}  # 新增技能
        ]
    })
    
    print(f"✅ Agent A001 技能已更新:")
    print(f"   - 新增: 文档编写 (等级 3)")
    
    # ===== 步骤 6: 标记任务为已完成 =====
    print("\n📌 步骤 6: 标记任务为已完成")
    
    metadata.mark_task_completed("T001-1")
    
    print(f"✅ 任务 T001-1 已标记为完成")
    
    # ===== 步骤 7: 查看元信息摘要 =====
    print("\n📌 步骤 7: 元信息摘要")
    
    metadata_dict = metadata.to_dict()
    
    print(f"✅ 元信息内容:")
    print(f"   - 删除的 Agent: {metadata_dict['removed_agents']}")
    print(f"   - 删除的任务: {metadata_dict['removed_tasks']}")
    print(f"   - 修改的 Agent: {len(metadata_dict['modified_agents'])} 个")
    print(f"   - 手动分配: {len(metadata_dict['manual_assignments'])} 个")
    print(f"   - 已完成任务: {metadata_dict['completed_tasks']}")
    
    # ===== 步骤 8: 应用元信息 =====
    print("\n📌 步骤 8: 应用元信息到数据")
    
    from twork.agent import (
        apply_metadata_to_agents,
        apply_metadata_to_tasks,
        apply_manual_assignments
    )
    
    # 应用到 Agent
    updated_agents = apply_metadata_to_agents(agents.copy(), metadata)
    print(f"✅ Agent 应用后数量: {len(agents)} → {len(updated_agents)}")
    
    # 应用手动分配
    updated_agents = apply_manual_assignments(updated_agents, metadata)
    
    # 显示更新后的 Agent
    for agent in updated_agents:
        print(f"   - {agent['agent_id']} ({agent['role_name']}): 分配任务 {agent['assigned_tasks']}")
    
    # ===== 步骤 9: 保存和加载元信息 =====
    print("\n📌 步骤 9: 保存和加载元信息")
    
    # 保存到 JSON
    metadata_json = json.dumps(metadata_dict, ensure_ascii=False, indent=2)
    
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    metadata_file = output_dir / "simulation_metadata.json"
    metadata_file.write_text(metadata_json, encoding="utf-8")
    
    print(f"✅ 元信息已保存: {metadata_file}")
    
    # 从 JSON 加载
    loaded_metadata = SimulationMetadata.from_dict(json.loads(metadata_json))
    print(f"✅ 元信息已加载: project_id={loaded_metadata.project_id}")
    
    # ===== 步骤 10: 使用元信息进行模拟 (模拟调用) =====
    print("\n📌 步骤 10: 使用元信息进行模拟")
    
    print("✅ 使用元信息模拟:")
    print("   注意: 实际模拟需要 LLM API,这里仅演示接口")
    print("""
    # 实际使用示例:
    llm = OpenAIAdapter(api_key="your-key")
    engine = SimulationEngine(llm_adapter=llm)
    
    # 使用元信息模拟
    result = engine.simulate_with_metadata(
        agents=agents,
        tasks=flat_tasks,
        metadata=metadata
    )
    
    # 或使用流式模拟
    for event in engine.simulate_stream_with_metadata(agents, flat_tasks, metadata):
        print(event)
    """)
    
    # ===== 完成 =====
    print("\n" + "=" * 80)
    print("🎉 元信息工作流演示完成!")
    print("=" * 80)
    print("\n关键要点:")
    print("1. 元信息记录所有用户修改,支持可编辑性设计")
    print("2. 可以删除/修改 Agent 和任务,系统自动处理")
    print("3. 支持手动任务分配覆盖自动分配")
    print("4. 元信息可序列化为 JSON,方便存储和传输")
    print("5. 模拟引擎自动应用元信息,无需手动处理")
    print("\n输出文件:")
    print(f"- {metadata_file}")


if __name__ == "__main__":
    try:
        demo_metadata_workflow()
    except Exception as e:
        logger.error(f"示例运行失败: {str(e)}", exc_info=True)
        sys.exit(1)
