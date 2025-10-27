"""
StructureUnderstandFactory - 结构化信息生产工厂（增强版）

用于解析文档、提取需求、生成WBS任务树、提取图谱实体和关系。
简化版本：专注于单次解析处理，移除了存储和快照功能。
增强版本：集成实体和关系提取器，为下游图谱构建提供数据。
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from .tools.base_tool import BaseTool
from .tools.doc_parse_tool import DocParseTool
from .tools.requirement_analyzer_tool import RequirementAndDomainAnalyzerTool
from .tools.wbs_parse_tool import WbsParseTool
from .extractors.entity_extractor import EntityExtractor
from .extractors.relation_extractor import RelationExtractor
from ..llm.base import LLMAdapter
from ..utils.logger import get_logger

logger = get_logger(__name__)


class StructureUnderstandFactory:
    """结构化信息生产工厂"""
    
    def __init__(
        self,
        project_id: str,
        original_file_path: str,
        cache_dir: str = "./cache"
    ):
        """
        初始化工厂
        
        Args:
            project_id: 项目ID
            original_file_path: 原始文档路径
            cache_dir: 缓存目录
        """
        self.project_id = project_id
        self.original_file_path = original_file_path
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化工具
        self.tools: Dict[str, BaseTool] = {
            "doc_parse": DocParseTool(),
            "analyzer": RequirementAndDomainAnalyzerTool(),
            "wbs": WbsParseTool()
        }
        
        # 初始化提取器
        self.extractors = {
            "entity": EntityExtractor(),
            "relation": RelationExtractor()
        }
        
        # 缓存的解析结果
        self._parsed_text: Optional[Dict[str, Any]] = None
        
        logger.info(f"StructureUnderstandFactory初始化完成: project_id={project_id}")
    
    def use_tool(self, name: str, instance: BaseTool):
        """
        替换某个工具
        
        Args:
            name: 工具名称（"doc_parse", "analyzer", "wbs"）
            instance: 工具实例
        """
        if name not in self.tools:
            raise ValueError(f"未知的工具名称: {name}，支持的工具: {list(self.tools.keys())}")
        
        self.tools[name] = instance
        logger.info(f"工具已替换: {name} -> {instance.__class__.__name__}")
    
    def run(self, extract_graph: bool = True) -> Dict[str, Any]:
        """
        执行完整流程（增强版）
        
        Args:
            extract_graph: 是否提取图谱实体和关系（默认True）
        
        Returns:
            {
                "requirements_and_domain": Dict,
                "wbs": Dict,
                "graph": Dict (optional, 包含nodes和edges)
            }
        """
        logger.info("开始执行完整流程")
        
        # 1. 解析文档（使用缓存）
        parsed_text = self._get_or_parse_document()
        
        # 2. 分析需求与领域
        analyzer = self.tools["analyzer"]
        requirements_and_domain = analyzer.execute(parsed_text)
        
        # 3. 生成WBS
        wbs_tool = self.tools["wbs"]
        wbs_result = wbs_tool.execute(requirements_and_domain)
        
        result = {
            "requirements_and_domain": requirements_and_domain,
            "wbs": wbs_result
        }
        
        # 4. 提取图谱实体和关系（可选）
        if extract_graph:
            graph_data = self._extract_graph(requirements_and_domain, wbs_result)
            result["graph"] = graph_data
            logger.info(f"图谱提取完成: nodes={len(graph_data.get('nodes', []))}, "
                       f"edges={len(graph_data.get('edges', []))}")
        
        logger.info("完整流程执行完成")
        
        return result
    
    def _get_or_parse_document(self) -> Dict[str, Any]:
        """获取或解析文档（使用缓存）"""
        cache_file = self.cache_dir / self.project_id / "parsed_text.json"
        
        # 检查缓存
        if cache_file.exists() and self._parsed_text is None:
            logger.info("从缓存加载解析结果")
            with open(cache_file, "r", encoding="utf-8") as f:
                self._parsed_text = json.load(f)
                return self._parsed_text
        
        # 如果已缓存在内存中
        if self._parsed_text:
            return self._parsed_text
        
        # 解析文档
        logger.info("解析文档（首次）")
        doc_parser = self.tools["doc_parse"]
        result = doc_parser.execute({"file_path": self.original_file_path})
        
        # 保存缓存
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        self._parsed_text = result
        
        return result
    
    def _extract_graph(self, requirements_and_domain: Dict[str, Any], wbs: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取图谱实体和关系
        
        Args:
            requirements_and_domain: 需求分析结果
            wbs: WBS拆解结果
            
        Returns:
            {
                "nodes": List[Dict],
                "edges": List[Dict]
            }
        """
        logger.info("开始提取图谱实体和关系")
        
        # 提取实体
        entity_extractor = self.extractors["entity"]
        entity_result = entity_extractor.extract({
            "requirements_and_domain": requirements_and_domain,
            "wbs": wbs
        })
        
        # 提取关系
        relation_extractor = self.extractors["relation"]
        relation_result = relation_extractor.extract({
            "requirements_and_domain": requirements_and_domain,
            "wbs": wbs,
            "entities": entity_result.get("nodes", [])
        })
        
        return {
            "nodes": entity_result.get("nodes", []),
            "edges": relation_result.get("edges", [])
        }
