"""
图谱可视化服务

使用Plotly生成交互式任务依赖关系图谱。
"""

from typing import List, Dict, Any
import plotly.graph_objects as go
import networkx as nx
from sqlalchemy.orm import Session
from ..models.project import Project
from ..models.task import Task
from ..models.agent import Agent
from twork.utils.logger import get_logger

logger = get_logger("graph_service")


class GraphVisualizationService:
    """图谱可视化服务"""
    
    def __init__(self, db: Session):
        """初始化服务"""
        self.db = db
    
    def build_plotly_graph(self, project_id: int) -> Dict[str, Any]:
        """
        构建Plotly交互式图谱
        
        Args:
            project_id: 项目ID
            
        Returns:
            Plotly Figure的JSON表示
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"项目不存在: {project_id}")
        
        # 获取任务和Agent
        tasks = self.db.query(Task).filter(Task.project_id == project_id).all()
        agents = self.db.query(Agent).filter(Agent.project_id == project_id).all()
        
        if not tasks:
            logger.warning(f"项目{project_id}没有任务数据")
            return self._empty_graph()
        
        # 创建NetworkX图用于布局计算
        G = nx.DiGraph()
        
        # 添加任务节点
        for task in tasks:
            G.add_node(
                task.task_id,
                node_type='task',
                label=task.task_name or task.task_id,
                duration=task.duration_days,
                priority=task.priority
            )
        
        # 添加Agent节点
        for agent in agents:
            G.add_node(
                agent.agent_id,
                node_type='agent',
                label=agent.role_name,
                role_type=agent.role_type
            )
        
        # 添加任务依赖边
        for task in tasks:
            if task.dependencies:
                for dep_id in task.dependencies:
                    if G.has_node(dep_id):
                        G.add_edge(dep_id, task.task_id, edge_type='dependency')
        
        # 添加Agent-任务分配边
        for agent in agents:
            if agent.assigned_tasks:
                for task_id in agent.assigned_tasks:
                    if G.has_node(task_id):
                        G.add_edge(agent.agent_id, task_id, edge_type='assignment')
        
        # 使用Spring布局计算节点位置
        try:
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        except:
            # 如果图为空或有问题，使用随机布局
            pos = nx.random_layout(G, seed=42)
        
        # 构建Plotly traces
        edge_traces = self._build_edge_traces(G, pos)
        node_trace = self._build_node_trace(G, pos)
        
        # 创建Figure
        fig = go.Figure(
            data=edge_traces + [node_trace],
            layout=go.Layout(
                title=dict(
                    text=f'项目任务依赖关系图谱 - {project.name}',
                    x=0.5,
                    xanchor='center'
                ),
                showlegend=True,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='rgba(240, 240, 240, 0.5)',
                height=700,
                width=1200
            )
        )
        
        logger.info(f"生成图谱成功: project_id={project_id}, nodes={len(G.nodes)}, edges={len(G.edges)}")
        
        return fig.to_dict()
    
    def _build_edge_traces(self, G: nx.DiGraph, pos: dict) -> List[go.Scatter]:
        """构建边的traces"""
        traces = []
        
        # 依赖关系边（蓝色实线）
        dep_edge_x, dep_edge_y = [], []
        for edge in G.edges(data=True):
            if edge[2].get('edge_type') == 'dependency':
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                dep_edge_x.extend([x0, x1, None])
                dep_edge_y.extend([y0, y1, None])
        
        if dep_edge_x:
            traces.append(go.Scatter(
                x=dep_edge_x, y=dep_edge_y,
                mode='lines',
                line=dict(width=2, color='#1f77b4'),
                hoverinfo='none',
                name='任务依赖',
                showlegend=True
            ))
        
        # 分配关系边（橙色虚线）
        assign_edge_x, assign_edge_y = [], []
        for edge in G.edges(data=True):
            if edge[2].get('edge_type') == 'assignment':
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                assign_edge_x.extend([x0, x1, None])
                assign_edge_y.extend([y0, y1, None])
        
        if assign_edge_x:
            traces.append(go.Scatter(
                x=assign_edge_x, y=assign_edge_y,
                mode='lines',
                line=dict(width=1.5, color='#ff7f0e', dash='dash'),
                hoverinfo='none',
                name='Agent分配',
                showlegend=True
            ))
        
        return traces
    
    def _build_node_trace(self, G: nx.DiGraph, pos: dict) -> go.Scatter:
        """构建节点trace"""
        node_x, node_y, node_text, node_color, node_size = [], [], [], [], []
        hover_text = []
        
        for node in G.nodes(data=True):
            node_id = node[0]
            node_data = node[1]
            x, y = pos[node_id]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node_data['label'])
            
            # 设置颜色和大小
            if node_data['node_type'] == 'agent':
                node_color.append('#ff7f0e')  # 橙色
                node_size.append(25)
                hover_text.append(
                    f"<b>Agent</b><br>"
                    f"角色: {node_data['label']}<br>"
                    f"类型: {node_data.get('role_type', 'N/A')}"
                )
            else:  # task
                node_color.append('#1f77b4')  # 蓝色
                node_size.append(20)
                hover_text.append(
                    f"<b>任务</b><br>"
                    f"名称: {node_data['label']}<br>"
                    f"工期: {node_data.get('duration', 'N/A')}天<br>"
                    f"优先级: {node_data.get('priority', 'N/A')}"
                )
        
        return go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white')
            ),
            text=node_text,
            textposition="top center",
            textfont=dict(size=10),
            hovertext=hover_text,
            hoverinfo='text',
            name='节点'
        )
    
    def _empty_graph(self) -> Dict[str, Any]:
        """返回空图谱"""
        fig = go.Figure(
            layout=go.Layout(
                title='暂无图谱数据',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=700
            )
        )
        return fig.to_dict()
