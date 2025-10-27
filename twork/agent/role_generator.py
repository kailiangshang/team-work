"""  
角色生成器

根据任务列表生成多角色Agent配置。
支持基于任务树生成Agent、技能映射、任务重新分配等功能。
"""

from typing import Dict, Any, List, Optional
import json
from ..llm.base import LLMAdapter
from ..utils.logger import get_logger

logger = get_logger("role_generator")


class RoleGenerator:
    """角色生成器"""
    
    ROLE_GENERATION_PROMPT = """你是一个专业的团队组建专家。请根据以下任务列表，生成参与项目的角色Agent配置。

任务列表:
{tasks}

请按照以下JSON格式输出角色配置:
{{
    "agents": [
        {{
            "agent_id": "agent_001",
            "role_name": "产品经理",
            "role_type": "product_manager",
            "capabilities": ["需求分析", "原型设计", "文档编写"],
            "assigned_tasks": ["T001", "T002"],
            "personality": "注重细节，善于沟通",
            "system_prompt": "你是一位经验丰富的产品经理...",
            "tools": ["Axure", "Jira"]
        }},
        ...
    ]
}}

要求:
1. 根据任务中的person_type字段提取角色类型，并去重
2. 为每个角色分配相应的任务
3. 根据角色类型设定合适的能力、性格和系统提示词
4. agent_id从agent_001开始递增
5. 只输出JSON格式，不要包含其他文字
"""
    
    def __init__(self, llm_adapter: LLMAdapter):
        """
        初始化角色生成器
        
        Args:
            llm_adapter: LLM适配器实例
        """
        self.llm = llm_adapter
        logger.info("角色生成器初始化完成")
    
    def generate(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        生成角色配置
        
        Args:
            tasks: 任务列表
            
        Returns:
            角色配置列表
        """
        logger.info(f"开始生成角色配置: 任务数={len(tasks)}")
        
        try:
            # 构造提示词
            tasks_text = json.dumps(tasks, ensure_ascii=False, indent=2)
            prompt = self.ROLE_GENERATION_PROMPT.format(tasks=tasks_text)
            
            # 调用LLM
            response = self.llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=3000,
            )
            
            # 解析响应
            content = response["choices"][0]["message"]["content"]
            
            # 尝试解析JSON
            try:
                # 清理可能的markdown代码块标记
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                result = json.loads(content)
                
                # 验证结果
                if "agents" not in result:
                    raise ValueError("返回结果中缺少agents字段")
                
                agents = result["agents"]
                
                # 验证每个Agent的必需字段
                required_fields = [
                    "agent_id",
                    "role_name",
                    "role_type",
                    "assigned_tasks",
                    "system_prompt",
                ]
                
                for i, agent in enumerate(agents):
                    for field in required_fields:
                        if field not in agent:
                            logger.warning(f"Agent{i}缺少必需字段: {field}")
                            if field in ["agent_id", "role_name", "role_type", "system_prompt"]:
                                agent[field] = f"unknown_{i}"
                            else:
                                agent[field] = []
                    
                    # 确保可选字段存在
                    agent.setdefault("capabilities", [])
                    agent.setdefault("personality", "专业负责")
                    agent.setdefault("tools", [])
                
                logger.info(f"角色生成完成: 共{len(agents)}个角色")
                
                return agents
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {str(e)}, content={content}")
                raise ValueError(f"LLM返回的内容无法解析为JSON: {str(e)}")
                
        except Exception as e:
            logger.error(f"角色生成失败: {str(e)}")
            raise
    
    def generate_roles(
        self,
        task_tree: List[Dict[str, Any]],
        domain_type: str = "软件开发",
        team_size_hint: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        基于任务树生成Agent配置（新方法符合设计文档）
        
        Args:
            task_tree: 任务树（嵌套结构）
            domain_type: 领域类型
            team_size_hint: 团队规模提示
            
        Returns:
            Agent配置列表
        """
        logger.info(f"基于任务树生成角色: domain={domain_type}, team_size_hint={team_size_hint}")
        
        # 将任务树展平
        flat_tasks = self._flatten_task_tree(task_tree)
        
        # 提取技能需求
        skill_requirements = self._extract_skill_requirements(flat_tasks)
        
        # 提取工具需求
        tool_requirements = self._extract_tool_requirements(flat_tasks, domain_type)
        
        # 构建提示词
        prompt = self._build_role_generation_prompt(
            tasks=flat_tasks,
            domain_type=domain_type,
            team_size_hint=team_size_hint,
            skill_requirements=skill_requirements,
            tool_requirements=tool_requirements
        )
        
        try:
            # 调用LLM
            response = self.llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=3000,
            )
            
            content = response["choices"][0]["message"]["content"]
            
            # 解析JSON
            content = self._clean_json_response(content)
            result = json.loads(content)
            
            if "agents" not in result:
                raise ValueError("返回结果中缺少agents字段")
            
            agents = result["agents"]
            
            # 验证和标准化Agent配置
            agents = self._validate_and_normalize_agents(agents, flat_tasks)
            
            logger.info(f"角色生成完成: 共{len(agents)}个角色")
            
            return agents
            
        except Exception as e:
            logger.error(f"基于任务树生成角色失败: {str(e)}")
            raise
    
    def reassign_tasks(
        self,
        agents: List[Dict[str, Any]],
        task_tree: List[Dict[str, Any]],
        orphan_tasks: List[str]
    ) -> List[Dict[str, Any]]:
        """
        重新分配孤儿任务（当Agent被删除时）
        
        Args:
            agents: Agent列表
            task_tree: 任务树
            orphan_tasks: 需要重新分配的任务ID列表
            
        Returns:
            更新后的Agent列表
        """
        logger.info(f"重新分配任务: 孤儿任务数={len(orphan_tasks)}")
        
        if not orphan_tasks:
            return agents
        
        # 展平任务树
        flat_tasks = self._flatten_task_tree(task_tree)
        task_map = {t["task_id"]: t for t in flat_tasks}
        
        # 获取推荐分配
        recommendations = self.recommend_assignments(
            agents=agents,
            task_tree=task_tree,
            strategy="skill_match"
        )
        
        # 应用推荐
        for task_id in orphan_tasks:
            if task_id in recommendations:
                agent_id = recommendations[task_id]
                # 找到对应的Agent
                for agent in agents:
                    if agent["agent_id"] == agent_id:
                        if "assigned_tasks" not in agent:
                            agent["assigned_tasks"] = []
                        if task_id not in agent["assigned_tasks"]:
                            agent["assigned_tasks"].append(task_id)
                        logger.info(f"任务 {task_id} 分配给 {agent['role_name']}")
                        break
        
        return agents
    
    def recommend_assignments(
        self,
        agents: List[Dict[str, Any]],
        task_tree: List[Dict[str, Any]],
        strategy: str = "skill_match"
    ) -> Dict[str, str]:
        """
        推荐任务分配
        
        Args:
            agents: Agent列表
            task_tree: 任务树
            strategy: 分配策略（"skill_match" 或 "workload_balance"）
            
        Returns:
            {task_id: agent_id} 映射
        """
        logger.info(f"生成任务分配推荐: strategy={strategy}")
        
        flat_tasks = self._flatten_task_tree(task_tree)
        recommendations = {}
        
        if strategy == "skill_match":
            # 基于技能匹配
            for task in flat_tasks:
                task_id = task["task_id"]
                required_skills = task.get("required_skills", [])
                
                # 计算每个Agent的匹配度
                best_agent = None
                best_score = 0
                
                for agent in agents:
                    agent_skills = agent.get("capabilities", [])
                    # 简单的技能匹配计分
                    match_count = 0
                    for req_skill in required_skills:
                        skill_name = req_skill if isinstance(req_skill, str) else req_skill.get("skill_name", "")
                        if skill_name in agent_skills or any(skill_name.lower() in str(s).lower() for s in agent_skills):
                            match_count += 1
                    
                    if match_count > best_score:
                        best_score = match_count
                        best_agent = agent["agent_id"]
                
                if best_agent:
                    recommendations[task_id] = best_agent
        
        elif strategy == "workload_balance":
            # 基于工作负载均衡
            agent_workload = {agent["agent_id"]: len(agent.get("assigned_tasks", [])) for agent in agents}
            
            for task in flat_tasks:
                task_id = task["task_id"]
                # 选择当前工作量最少的Agent
                min_agent = min(agent_workload, key=agent_workload.get)
                recommendations[task_id] = min_agent
                agent_workload[min_agent] += 1
        
        logger.info(f"推荐生成完成: {len(recommendations)}个任务")
        
        return recommendations
    
    def _flatten_task_tree(self, task_tree: List[Dict]) -> List[Dict]:
        """展平任务树"""
        flat_list = []
        
        def flatten_recursive(tasks: List[Dict]):
            for task in tasks:
                flat_task = {k: v for k, v in task.items() if k != "children"}
                flat_list.append(flat_task)
                if task.get("children"):
                    flatten_recursive(task["children"])
        
        flatten_recursive(task_tree)
        return flat_list
    
    def _extract_skill_requirements(self, tasks: List[Dict]) -> List[str]:
        """提取任务所需技能"""
        skills = set()
        for task in tasks:
            # 从 task 中提取 required_skills
            required_skills = task.get("required_skills", [])
            for skill in required_skills:
                if isinstance(skill, dict):
                    skills.add(skill.get("skill_name", ""))
                else:
                    skills.add(str(skill))
        
        return list(skills)
    
    def _extract_tool_requirements(self, tasks: List[Dict], domain_type: str) -> List[str]:
        """提取工具需求"""
        # 域特定工具库
        domain_tools = {
            "软件开发": ["VS Code", "Git", "Docker", "Postman", "JIRA"],
            "户外施工": ["挖掘机", "起重机", "水准仪", "安全帽"],
            "营销活动": ["社交媒体工具", "Adobe Creative Suite", "数据分析工具"],
            "研究项目": ["SPSS", "Python", "LaTeX", "文献管理工具"]
        }
        
        tools = set(domain_tools.get(domain_type, []))
        
        # 从任务中提取
        for task in tasks:
            tools_needed = task.get("tools_needed", [])
            tools.update(tools_needed)
        
        return list(tools)
    
    def _build_role_generation_prompt(
        self,
        tasks: List[Dict],
        domain_type: str,
        team_size_hint: Optional[int],
        skill_requirements: List[str],
        tool_requirements: List[str]
    ) -> str:
        """构建角色生成提示词"""
        tasks_summary = f"总任务数: {len(tasks)}"
        skills_str = ", ".join(skill_requirements[:10]) if skill_requirements else "无"
        tools_str = ", ".join(tool_requirements) if tool_requirements else "无"
        
        prompt = f"""**你是一个专业的团队组建专家。**请根据以下信息生成项目团队的Agent配置。

**项目信息:**
- 领域类型: {domain_type}
- {tasks_summary}
- 所需技能: {skills_str}
- 所需工具: {tools_str}
{f"- 团队规模提示: {team_size_hint}人" if team_size_hint else ""}

**输出格式:**
```json
{{
    "agents": [
        {{
            "agent_id": "A001",
            "role_name": "后端工程师",
            "role_type": "开发",
            "capabilities": [
                {{"skill_name": "Python", "proficiency_level": 5}},
                {{"skill_name": "FastAPI", "proficiency_level": 4}}
            ],
            "available_hours_per_day": 8.0,
            "fatigue_threshold": 8.0,
            "personality": "专业、注重细节",
            "assigned_tasks": [],
            "org_level": 3,
            "communication_style": "direct",
            "tools": ["VS Code", "Docker"]
        }}
    ]
}}
```

**要求:**
1. 根据项目需求生成合适的角色
2. agent_id从 A001 开始递增
3. capabilities 为技能列表，包含 skill_name 和 proficiency_level (1-5)
4. available_hours_per_day 默认 8.0
5. org_level: 1=EXECUTIVE, 2=MANAGER, 3=LEAD, 4=MEMBER
6. 只输出JSON，不要其他文字
"""
        
        return prompt
    
    def _validate_and_normalize_agents(
        self,
        agents: List[Dict],
        tasks: List[Dict]
    ) -> List[Dict]:
        """验证和标准化Agent配置"""
        required_fields = [
            "agent_id", "role_name", "role_type", "capabilities"
        ]
        
        for i, agent in enumerate(agents):
            # 验证必需字段
            for field in required_fields:
                if field not in agent:
                    if field == "agent_id":
                        agent[field] = f"A{i+1:03d}"
                    elif field in ["role_name", "role_type"]:
                        agent[field] = f"unknown_{i}"
                    else:
                        agent[field] = []
            
            # 设置默认值
            agent.setdefault("assigned_tasks", [])
            agent.setdefault("available_hours_per_day", 8.0)
            agent.setdefault("fatigue_threshold", 8.0)
            agent.setdefault("personality", "专业负责")
            agent.setdefault("org_level", 3)
            agent.setdefault("communication_style", "direct")
            agent.setdefault("tools", [])
            agent.setdefault("system_prompt", f"你是一位经验丰富的{agent.get('role_name', '角色')}。")
        
        return agents
    
    def _clean_json_response(self, content: str) -> str:
        """清理JSON响应"""
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()
