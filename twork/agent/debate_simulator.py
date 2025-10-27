"""
讨论模拟器
模拟Agent之间的技术讨论和决策过程
"""

from typing import Dict, List, Any, Optional
import json
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DebateSimulator:
    """讨论模拟器"""
    
    def __init__(self, llm_adapter, max_rounds: int = 3):
        """
        初始化模拟器
        
        Args:
            llm_adapter: LLM适配器
            max_rounds: 最大讨论轮数
        """
        self.llm = llm_adapter
        self.max_rounds = max_rounds
    
    def simulate_debate(
        self,
        conflict: Dict[str, Any],
        agents_info: Dict[str, Dict],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        模拟讨论过程
        
        Args:
            conflict: 冲突信息
            agents_info: Agent信息字典（role -> info）
            context: 上下文信息
        
        Returns:
            讨论结果
        """
        conflict_type = conflict.get("type")
        participants = conflict.get("participants", [])
        
        if len(participants) < 2:
            logger.warning("讨论参与者不足2人，跳过")
            return {
                "consensus_reached": True,
                "final_decision": "无需讨论",
                "rounds": []
            }
        
        # 获取参与者信息
        role1_name = participants[0]
        role2_name = participants[1]
        role1_info = agents_info.get(role1_name, {})
        role2_info = agents_info.get(role2_name, {})
        
        # 模拟多轮讨论
        rounds = []
        consensus_reached = False
        final_decision = None
        
        for round_num in range(1, self.max_rounds + 1):
            logger.info(f"开始第 {round_num} 轮讨论")
            
            # 构建讨论提示
            prompt = self._build_debate_prompt(
                conflict_type=conflict_type,
                role1_name=role1_name,
                role1_personality=role1_info.get("personality", "中立"),
                role2_name=role2_name,
                role2_personality=role2_info.get("personality", "中立"),
                round_num=round_num,
                max_rounds=self.max_rounds,
                previous_rounds=rounds,
                context=context
            )
            
            # 调用LLM生成讨论内容
            try:
                response = self.llm.chat(
                    system_prompt="你是一个专业的项目协调员，负责模拟团队成员之间的技术讨论。",
                    user_prompt=prompt,
                    temperature=0.8
                )
                
                # 解析响应
                round_result = json.loads(response)
                rounds.append(round_result)
                
                # 检查是否达成共识
                if round_result.get("consensus_reached"):
                    consensus_reached = True
                    final_decision = round_result.get("final_decision")
                    break
            
            except Exception as e:
                logger.error(f"讨论模拟失败: {e}")
                break
        
        # 如果未达成共识，使用默认决策
        if not consensus_reached:
            final_decision = self._generate_default_decision(conflict_type)
        
        # 识别风险
        risks = self._identify_risks(rounds, conflict)
        
        return {
            "consensus_reached": consensus_reached,
            "final_decision": final_decision,
            "rounds": rounds,
            "total_rounds": len(rounds),
            "risks_identified": risks
        }
    
    def _build_debate_prompt(
        self,
        conflict_type: str,
        role1_name: str,
        role1_personality: str,
        role2_name: str,
        role2_personality: str,
        round_num: int,
        max_rounds: int,
        previous_rounds: List[Dict],
        context: Optional[str]
    ) -> str:
        """构建讨论提示"""
        
        prompt = f"""模拟两个角色之间的技术讨论。

角色1: {role1_name} - 性格: {role1_personality}
角色2: {role2_name} - 性格: {role2_personality}

讨论主题: {conflict_type}
当前轮次: {round_num}/{max_rounds}
"""
        
        if context:
            prompt += f"\n上下文:\n{context}\n"
        
        if previous_rounds:
            prompt += "\n之前的讨论:\n"
            for i, prev_round in enumerate(previous_rounds, 1):
                prompt += f"第{i}轮:\n"
                prompt += f"- {role1_name}: {prev_round.get('role1_response', '')}\n"
                prompt += f"- {role2_name}: {prev_round.get('role2_response', '')}\n"
        
        prompt += f"""
请生成本轮讨论内容，输出JSON格式：
{{
    "role1_response": "{role1_name}的发言",
    "role2_response": "{role2_name}的回应",
    "consensus_reached": true/false,
    "final_decision": "最终决策(如果达成共识)",
    "risk_identified": ["识别到的风险"]
}}

要求：
1. 根据角色性格生成符合特点的发言
2. 讨论应该围绕{conflict_type}展开
3. 如果是第{max_rounds}轮，必须达成共识
4. 识别讨论中暴露的潜在风险
"""
        
        return prompt
    
    def _generate_default_decision(self, conflict_type: str) -> str:
        """生成默认决策"""
        default_decisions = {
            "技术方案争议": "采用风险较低的稳健方案，后续可优化",
            "时间预估分歧": "采用保守估算，增加缓冲时间",
            "资源分配冲突": "优先保障关键路径任务",
            "质量标准争议": "遵循行业标准，确保基本质量要求"
        }
        
        return default_decisions.get(conflict_type, "按团队既定标准执行")
    
    def _identify_risks(
        self,
        rounds: List[Dict],
        conflict: Dict[str, Any]
    ) -> List[str]:
        """从讨论中识别风险"""
        risks = []
        
        # 收集所有轮次中识别的风险
        for round_data in rounds:
            round_risks = round_data.get("risk_identified", [])
            risks.extend(round_risks)
        
        # 去重
        risks = list(set(risks))
        
        return risks
