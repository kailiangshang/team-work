"""FalkorDB 客户端"""
from typing import Optional, Dict, Any, List
import redis
from redis.commands.graph import Graph
from redis.commands.graph.node import Node
from redis.commands.graph.edge import Edge
import logging

logger = logging.getLogger(__name__)


class FalkorDBClient:
    """FalkorDB 客户端
    
    FalkorDB 是基于 Redis 的图数据库，使用 RedisGraph 模块。
    支持类似 Cypher 的查询语言 (RedisGraph Query Language)。
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0,
        graph_name: str = "teamwork",
    ):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.graph_name = graph_name
        
        self._redis: Optional[redis.Redis] = None
        self._graph: Optional[Graph] = None
    
    def connect(self) -> bool:
        """连接到 FalkorDB"""
        try:
            self._redis = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                decode_responses=True,
            )
            # 测试连接
            self._redis.ping()
            
            # 获取图实例
            self._graph = self._redis.graph(self.graph_name)
            
            logger.info(f"Connected to FalkorDB at {self.host}:{self.port}")
            return True
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to FalkorDB: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self._redis:
            self._redis.close()
            self._redis = None
            self._graph = None
            logger.info("Disconnected from FalkorDB")
    
    @property
    def graph(self) -> Graph:
        """获取图实例"""
        if self._graph is None:
            raise RuntimeError("Not connected to FalkorDB. Call connect() first.")
        return self._graph
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """执行 Cypher 查询
        
        Args:
            query: Cypher 查询语句
            params: 查询参数
        
        Returns:
            查询结果
        """
        try:
            if params:
                result = self.graph.query(query, params)
            else:
                result = self.graph.query(query)
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}\nQuery: {query}")
            raise
    
    # ==================== 节点操作 ====================
    
    def create_node(
        self,
        label: str,
        properties: Dict[str, Any],
        node_id: str,
    ) -> bool:
        """创建节点
        
        Args:
            label: 节点标签 (Task, Agent, Skill, Tool)
            properties: 节点属性
            node_id: 节点ID
        
        Returns:
            是否成功
        """
        # 构建 Cypher 查询
        props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
        query = f"""
        MERGE (n:{label} {{id: $node_id}})
        SET n += {{{props_str}}}
        RETURN n
        """
        
        params = {"node_id": node_id, **properties}
        
        try:
            self.execute_query(query, params)
            return True
        except Exception as e:
            logger.error(f"Failed to create node {node_id}: {e}")
            return False
    
    def get_node(self, node_id: str, label: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取节点"""
        label_str = f":{label}" if label else ""
        query = f"""
        MATCH (n{label_str} {{id: $node_id}})
        RETURN n
        """
        
        result = self.execute_query(query, {"node_id": node_id})
        
        if result and result.result_set:
            node = result.result_set[0][0]
            return node.properties
        return None
    
    def update_node(self, node_id: str, properties: Dict[str, Any]) -> bool:
        """更新节点属性"""
        set_str = ", ".join([f"n.{k} = ${k}" for k in properties.keys()])
        query = f"""
        MATCH (n {{id: $node_id}})
        SET {set_str}
        RETURN n
        """
        
        params = {"node_id": node_id, **properties}
        
        try:
            self.execute_query(query, params)
            return True
        except Exception as e:
            logger.error(f"Failed to update node {node_id}: {e}")
            return False
    
    def delete_node(self, node_id: str) -> bool:
        """删除节点及其关系"""
        query = """
        MATCH (n {id: $node_id})
        DETACH DELETE n
        """
        
        try:
            self.execute_query(query, {"node_id": node_id})
            return True
        except Exception as e:
            logger.error(f"Failed to delete node {node_id}: {e}")
            return False
    
    def find_nodes(
        self,
        label: str,
        where: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """查找节点
        
        Args:
            label: 节点标签
            where: WHERE 条件
            limit: 返回数量限制
        
        Returns:
            节点属性列表
        """
        where_clause = f"WHERE {where}" if where else ""
        query = f"""
        MATCH (n:{label})
        {where_clause}
        RETURN n
        LIMIT {limit}
        """
        
        result = self.execute_query(query)
        
        nodes = []
        if result and result.result_set:
            for row in result.result_set:
                node = row[0]
                nodes.append(node.properties)
        
        return nodes
    
    # ==================== 关系操作 ====================
    
    def create_edge(
        self,
        source_id: str,
        target_id: str,
        relation: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """创建关系/边
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            relation: 关系类型
            properties: 关系属性
        
        Returns:
            是否成功
        """
        props_str = ""
        if properties:
            props_str = " {" + ", ".join([f"{k}: ${k}" for k in properties.keys()]) + "}"
        
        query = f"""
        MATCH (source {{id: $source_id}})
        MATCH (target {{id: $target_id}})
        MERGE (source)-[r:{relation}{props_str}]->(target)
        RETURN r
        """
        
        params = {"source_id": source_id, "target_id": target_id}
        if properties:
            params.update(properties)
        
        try:
            self.execute_query(query, params)
            return True
        except Exception as e:
            logger.error(f"Failed to create edge {source_id}-{relation}->{target_id}: {e}")
            return False
    
    def delete_edge(
        self,
        source_id: str,
        target_id: str,
        relation: Optional[str] = None,
    ) -> bool:
        """删除关系/边"""
        rel_str = f":{relation}" if relation else ""
        query = f"""
        MATCH (source {{id: $source_id}})-[r{rel_str}]->(target {{id: $target_id}})
        DELETE r
        """
        
        try:
            self.execute_query(query, {"source_id": source_id, "target_id": target_id})
            return True
        except Exception as e:
            logger.error(f"Failed to delete edge: {e}")
            return False
    
    # ==================== 图操作 ====================
    
    def get_neighbors(
        self,
        node_id: str,
        relation: Optional[str] = None,
        direction: str = "both",  # "in", "out", "both"
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """获取邻居节点"""
        rel_str = f":{relation}" if relation else ""
        
        if direction == "out":
            pattern = f"(n {{id: $node_id}})-[r{rel_str}]->(neighbor)"
        elif direction == "in":
            pattern = f"(neighbor)-[r{rel_str}]->(n {{id: $node_id}})"
        else:
            pattern = f"(n {{id: $node_id}})-[r{rel_str}]-(neighbor)"
        
        query = f"""
        MATCH {pattern}
        RETURN neighbor, r
        LIMIT {limit}
        """
        
        result = self.execute_query(query, {"node_id": node_id})
        
        neighbors = []
        if result and result.result_set:
            for row in result.result_set:
                neighbor = row[0]
                neighbors.append(neighbor.properties)
        
        return neighbors
    
    def find_path(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 10,
    ) -> List[List[str]]:
        """查找路径"""
        query = f"""
        MATCH path = shortestPath(
            (start {{id: $start_id}})-[*1..{max_depth}]-(end {{id: $end_id}})
        )
        RETURN [node in nodes(path) | node.id] as path_ids
        """
        
        result = self.execute_query(query, {"start_id": start_id, "end_id": end_id})
        
        paths = []
        if result and result.result_set:
            for row in result.result_set:
                paths.append(row[0])
        
        return paths
    
    def clear_graph(self) -> bool:
        """清空图（谨慎使用）"""
        query = "MATCH (n) DETACH DELETE n"
        
        try:
            self.execute_query(query)
            logger.warning(f"Graph '{self.graph_name}' cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear graph: {e}")
            return False
    
    def get_graph_stats(self) -> Dict[str, int]:
        """获取图统计信息"""
        node_count = self.execute_query("MATCH (n) RETURN count(n)").result_set[0][0]
        edge_count = self.execute_query("MATCH ()-[r]->() RETURN count(r)").result_set[0][0]
        
        return {
            "nodes": node_count,
            "edges": edge_count,
        }