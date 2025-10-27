"""
领域模板定义（增强版）

重构后的领域模板系统，支持图谱构建所需的实体和关系提取。
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class DomainTemplateV2:
    """领域模板V2（增强版）"""
    
    domain_type: str
    template_id: str
    
    # 角色模板
    default_roles: List[Dict[str, Any]] = field(default_factory=list)
    
    # 工具模板
    common_tools: List[Dict[str, Any]] = field(default_factory=list)
    
    # 技能模板
    common_skills: List[Dict[str, Any]] = field(default_factory=list)
    
    # 任务类型模板
    task_types: List[str] = field(default_factory=list)
    
    # 提取模式（正则表达式）
    extraction_patterns: Dict[str, str] = field(default_factory=dict)
    
    # LLM提示词增强（领域上下文）
    domain_context: str = ""
    
    # 关注点
    focus_points: List[str] = field(default_factory=list)
    
    # 默认配置
    default_config: Dict[str, Any] = field(default_factory=dict)


# 软件开发领域模板
SOFTWARE_DEV_TEMPLATE = DomainTemplateV2(
    domain_type="软件开发",
    template_id="software_dev_v2",
    default_roles=[
        {
            "name": "产品经理",
            "responsibilities": ["需求分析", "产品规划", "需求评审", "用户研究"],
            "skills_required": ["需求分析", "原型设计", "产品规划", "用户研究"]
        },
        {
            "name": "架构师",
            "responsibilities": ["架构设计", "技术选型", "技术评审", "性能优化"],
            "skills_required": ["系统架构", "技术选型", "性能优化", "高可用设计"]
        },
        {
            "name": "前端工程师",
            "responsibilities": ["前端开发", "UI实现", "前端优化", "组件开发"],
            "skills_required": ["前端开发", "JavaScript", "CSS", "响应式设计"]
        },
        {
            "name": "后端工程师",
            "responsibilities": ["后端开发", "API开发", "数据库设计", "业务逻辑实现"],
            "skills_required": ["后端开发", "数据库设计", "API设计", "并发处理"]
        },
        {
            "name": "测试工程师",
            "responsibilities": ["测试设计", "测试执行", "缺陷管理", "自动化测试"],
            "skills_required": ["测试设计", "自动化测试", "性能测试", "缺陷跟踪"]
        },
        {
            "name": "DevOps工程师",
            "responsibilities": ["CI/CD配置", "部署管理", "监控告警", "基础设施管理"],
            "skills_required": ["Docker", "Kubernetes", "CI/CD", "Linux运维"]
        },
        {
            "name": "UI设计师",
            "responsibilities": ["界面设计", "交互设计", "视觉设计", "设计规范"],
            "skills_required": ["UI设计", "交互设计", "Figma", "原型设计"]
        }
    ],
    common_tools=[
        {"name": "Git", "category": "版本控制", "purpose": "代码版本管理"},
        {"name": "Docker", "category": "容器化", "purpose": "应用容器化部署"},
        {"name": "React", "category": "前端框架", "purpose": "构建用户界面"},
        {"name": "Vue", "category": "前端框架", "purpose": "构建用户界面"},
        {"name": "FastAPI", "category": "后端框架", "purpose": "构建高性能API"},
        {"name": "Django", "category": "后端框架", "purpose": "Web应用开发"},
        {"name": "PostgreSQL", "category": "数据库", "purpose": "关系型数据存储"},
        {"name": "Redis", "category": "缓存", "purpose": "数据缓存和会话存储"},
        {"name": "Nginx", "category": "Web服务器", "purpose": "反向代理和负载均衡"},
        {"name": "Kubernetes", "category": "容器编排", "purpose": "容器集群管理"},
        {"name": "Jenkins", "category": "CI/CD", "purpose": "持续集成和部署"},
        {"name": "Figma", "category": "设计工具", "purpose": "UI/UX设计"},
        {"name": "Jira", "category": "项目管理", "purpose": "需求和缺陷管理"},
        {"name": "Postman", "category": "API测试", "purpose": "API接口测试"}
    ],
    common_skills=[
        {"name": "前端开发", "level": "中级", "related_tools": ["React", "Vue", "TypeScript"]},
        {"name": "后端开发", "level": "中级", "related_tools": ["FastAPI", "Django", "Flask"]},
        {"name": "数据库设计", "level": "中级", "related_tools": ["PostgreSQL", "MySQL", "MongoDB"]},
        {"name": "系统架构", "level": "高级", "related_tools": ["微服务", "分布式系统"]},
        {"name": "DevOps", "level": "中级", "related_tools": ["Docker", "Kubernetes", "Jenkins"]},
        {"name": "测试", "level": "中级", "related_tools": ["Pytest", "Jest", "Selenium"]},
        {"name": "UI设计", "level": "中级", "related_tools": ["Figma", "Sketch", "Adobe XD"]},
        {"name": "需求分析", "level": "中级", "related_tools": ["Axure", "Figma", "Confluence"]},
        {"name": "API设计", "level": "中级", "related_tools": ["Swagger", "Postman"]},
        {"name": "性能优化", "level": "高级", "related_tools": ["性能监控", "代码优化"]}
    ],
    task_types=[
        "需求分析", "架构设计", "前端开发", "后端开发",
        "数据库设计", "API开发", "测试", "部署", "UI设计", "文档编写"
    ],
    extraction_patterns={
        "tech_stack": r"(React|Vue|Angular|Django|Flask|FastAPI|Spring|Express)",
        "tool_mention": r"使用(\w+)|采用(\w+)|基于(\w+)",
        "role_mention": r"(产品经理|架构师|开发工程师|测试工程师|设计师)",
        "api_endpoint": r"API[:：](.+)|接口[:：](.+)",
        "database": r"(PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch)"
    },
    focus_points=[
        "用户故事", "功能模块", "技术栈", "API设计",
        "数据库设计", "测试策略", "部署方案", "性能优化"
    ],
    domain_context="""
软件开发项目通常包括需求分析、设计、开发、测试、部署等阶段。

关注点：
- 技术栈选型：前端框架、后端框架、数据库、部署工具
- API设计：RESTful/GraphQL规范、版本控制、文档生成
- 数据库设计：ER模型、索引优化、数据迁移策略
- 测试策略：单元测试、集成测试、E2E测试、覆盖率要求
- CI/CD流程：代码审查、自动化测试、部署流水线

典型角色及职责：
- 产品经理：需求分析、优先级排序、验收标准制定
- 架构师：技术选型、架构设计、性能优化、技术评审
- 前端工程师：UI实现、组件开发、前端优化、浏览器兼容
- 后端工程师：API开发、业务逻辑、数据库设计、性能优化
- 测试工程师：测试设计、自动化测试、缺陷跟踪、质量把控
- DevOps工程师：CI/CD配置、容器化、监控告警、基础设施
- UI设计师：界面设计、交互设计、设计规范、原型制作

技术栈示例：
- 前端：React/Vue + TypeScript + Tailwind CSS + Vite
- 后端：FastAPI/Django + SQLAlchemy + Celery
- 数据库：PostgreSQL + Redis + Elasticsearch
- 部署：Docker + Kubernetes + Jenkins/GitLab CI

关键交付物：
- 需求文档（PRD、用户故事）
- 设计文档（架构设计、数据库设计、API文档）
- 代码（前端代码、后端代码、配置文件）
- 测试（测试用例、测试报告、覆盖率报告）
- 部署（Dockerfile、K8s配置、部署文档）

常见风险：
- 需求变更频繁
- 技术选型不当
- 第三方依赖不稳定
- 性能瓶颈
- 安全漏洞

质量标准：
- 代码覆盖率 ≥ 80%
- 代码审查通过率 100%
- 性能指标：API响应时间 < 200ms，并发1000+
- 安全：通过OWASP Top 10检查
""",
    default_config={
        "max_task_level": 4,
        "default_sprint_days": 14,
        "work_hours_per_day": 8,
        "enable_code_review": True,
        "enable_testing": True
    }
)


# 户外施工领域模板
OUTDOOR_CONSTRUCTION_TEMPLATE = DomainTemplateV2(
    domain_type="户外施工",
    template_id="outdoor_construction_v2",
    default_roles=[
        {
            "name": "项目经理",
            "responsibilities": ["项目规划", "进度管理", "资源协调", "风险管控"],
            "skills_required": ["项目管理", "资源调度", "风险评估", "成本控制"]
        },
        {
            "name": "设计师",
            "responsibilities": ["方案设计", "图纸绘制", "技术交底", "变更设计"],
            "skills_required": ["CAD设计", "施工图设计", "结构设计", "材料选型"]
        },
        {
            "name": "施工队长",
            "responsibilities": ["现场指挥", "人员调度", "质量把控", "进度跟踪"],
            "skills_required": ["施工管理", "人员管理", "质量控制", "安全管理"]
        },
        {
            "name": "安全员",
            "responsibilities": ["安全检查", "隐患排查", "安全培训", "应急处理"],
            "skills_required": ["安全管理", "应急处理", "安全培训", "风险识别"]
        },
        {
            "name": "质检员",
            "responsibilities": ["质量检查", "材料验收", "工序验收", "质量记录"],
            "skills_required": ["质量检验", "材料鉴定", "标准规范", "检测技术"]
        },
        {
            "name": "材料员",
            "responsibilities": ["材料采购", "材料验收", "材料保管", "材料发放"],
            "skills_required": ["材料管理", "成本核算", "仓库管理", "供应商管理"]
        }
    ],
    common_tools=[
        {"name": "挖掘机", "category": "施工机械", "purpose": "土方开挖"},
        {"name": "吊车", "category": "施工机械", "purpose": "重物吊装"},
        {"name": "混凝土搅拌机", "category": "施工机械", "purpose": "混凝土制备"},
        {"name": "全站仪", "category": "测量仪器", "purpose": "施工测量"},
        {"name": "水准仪", "category": "测量仪器", "purpose": "高程测量"},
        {"name": "CAD软件", "category": "设计软件", "purpose": "图纸绘制"},
        {"name": "项目管理软件", "category": "管理工具", "purpose": "进度管理"}
    ],
    common_skills=[
        {"name": "施工管理", "level": "高级", "related_tools": ["项目管理软件"]},
        {"name": "CAD设计", "level": "中级", "related_tools": ["CAD软件"]},
        {"name": "安全管理", "level": "高级", "related_tools": ["安全检测工具"]},
        {"name": "质量控制", "level": "中级", "related_tools": ["检测仪器"]},
        {"name": "测量技术", "level": "中级", "related_tools": ["全站仪", "水准仪"]}
    ],
    task_types=[
        "现场勘察", "方案设计", "施工准备", "材料采购",
        "设备调配", "现场作业", "安全检查", "质量验收", "竣工清理"
    ],
    extraction_patterns={
        "location": r"地点[:：](.+)|位置[:：](.+)|现场[:：](.+)",
        "safety_level": r"安全等级[:：](.+)",
        "equipment": r"设备[:：](.+)|机械[:：](.+)",
        "material": r"材料[:：](.+)",
        "weather": r"天气[:：](.+)|气候[:：](.+)"
    },
    focus_points=[
        "地理环境", "天气依赖", "安全等级", "设备需求",
        "材料采购", "人员配置", "质量标准", "进度计划"
    ],
    domain_context="""
户外施工项目通常包括现场勘察、方案设计、施工准备、现场作业、质量验收等阶段。
关注点：地理环境、天气条件、安全等级、设备需求、材料采购、人员配置。
典型角色：项目经理、设计师、施工队长、安全员、质检员、材料员。
关键设备：挖掘机、吊车、混凝土搅拌机、测量仪器等。
关键交付物：施工方案、施工图纸、质量记录、竣工报告。
安全要求：必须进行安全检查，恶劣天气需停工。
""",
    default_config={
        "max_task_level": 3,
        "weather_check_required": True,
        "safety_priority": "high",
        "work_hours_per_day": 8,
        "rest_on_bad_weather": True
    }
)


# 营销活动领域模板
MARKETING_CAMPAIGN_TEMPLATE = DomainTemplateV2(
    domain_type="营销活动",
    template_id="marketing_campaign_v2",
    default_roles=[
        {
            "name": "营销经理",
            "responsibilities": ["营销策略", "预算管理", "团队协调", "效果评估"],
            "skills_required": ["营销策划", "数据分析", "预算管理", "团队管理"]
        },
        {
            "name": "策划专员",
            "responsibilities": ["活动策划", "方案撰写", "资源协调", "执行跟进"],
            "skills_required": ["活动策划", "创意策划", "项目管理", "沟通协调"]
        },
        {
            "name": "文案策划",
            "responsibilities": ["文案撰写", "内容创作", "文案优化", "创意提案"],
            "skills_required": ["文案写作", "创意思维", "市场洞察", "品牌理解"]
        },
        {
            "name": "设计师",
            "responsibilities": ["视觉设计", "物料制作", "品牌设计", "创意设计"],
            "skills_required": ["平面设计", "VI设计", "创意设计", "设计软件"]
        },
        {
            "name": "媒介专员",
            "responsibilities": ["渠道投放", "媒介采购", "投放优化", "效果跟踪"],
            "skills_required": ["媒介投放", "数据分析", "渠道管理", "预算控制"]
        },
        {
            "name": "数据分析师",
            "responsibilities": ["数据监测", "效果分析", "报告撰写", "优化建议"],
            "skills_required": ["数据分析", "数据可视化", "统计分析", "报告撰写"]
        }
    ],
    common_tools=[
        {"name": "Google Analytics", "category": "数据分析", "purpose": "网站流量分析"},
        {"name": "微信公众平台", "category": "社交媒体", "purpose": "内容发布和用户互动"},
        {"name": "Adobe Creative Suite", "category": "设计工具", "purpose": "视觉设计"},
        {"name": "Tableau", "category": "数据可视化", "purpose": "数据展示"},
        {"name": "SEMrush", "category": "营销工具", "purpose": "SEO和竞品分析"},
        {"name": "Mailchimp", "category": "邮件营销", "purpose": "邮件营销自动化"}
    ],
    common_skills=[
        {"name": "营销策划", "level": "高级", "related_tools": ["营销自动化平台"]},
        {"name": "数据分析", "level": "中级", "related_tools": ["Google Analytics", "Tableau"]},
        {"name": "文案写作", "level": "中级", "related_tools": []},
        {"name": "平面设计", "level": "中级", "related_tools": ["Adobe Creative Suite"]},
        {"name": "社交媒体运营", "level": "中级", "related_tools": ["微信公众平台", "微博"]}
    ],
    task_types=[
        "市场调研", "策略规划", "创意设计", "文案撰写",
        "物料制作", "渠道投放", "数据监测", "效果评估", "优化调整"
    ],
    extraction_patterns={
        "target_audience": r"目标用户[:：](.+)|受众[:：](.+)|用户画像[:：](.+)",
        "channel": r"渠道[:：](.+)|平台[:：](.+)",
        "budget": r"预算[:：](.+)|费用[:：](.+)",
        "kpi": r"KPI[:：](.+)|指标[:：](.+)|目标[:：](.+)"
    },
    focus_points=[
        "目标受众", "营销渠道", "内容策略", "预算分配",
        "效果指标", "创意设计", "执行计划", "数据监测"
    ],
    domain_context="""
营销活动通常包括市场调研、策略规划、创意设计、执行投放、效果评估等阶段。
关注点：目标受众、营销渠道、内容策略、预算分配、效果指标。
典型角色：营销经理、策划专员、文案策划、设计师、媒介专员、数据分析师。
常用工具：Google Analytics、微信公众平台、设计软件、数据分析工具。
关键交付物：营销方案、创意文案、设计物料、投放计划、效果报告。
""",
    default_config={
        "max_task_level": 3,
        "default_campaign_days": 30,
        "work_hours_per_day": 8,
        "enable_ab_testing": True,
        "daily_report_required": True
    }
)


# 研究项目领域模板
RESEARCH_PROJECT_TEMPLATE = DomainTemplateV2(
    domain_type="研究项目",
    template_id="research_project_v2",
    default_roles=[
        {
            "name": "项目负责人",
            "responsibilities": ["项目规划", "团队管理", "资源协调", "成果把控"],
            "skills_required": ["项目管理", "学术研究", "团队领导", "资源管理"]
        },
        {
            "name": "研究员",
            "responsibilities": ["文献调研", "实验设计", "数据采集", "论文撰写"],
            "skills_required": ["文献检索", "实验设计", "数据分析", "学术写作"]
        },
        {
            "name": "实验员",
            "responsibilities": ["实验执行", "样本采集", "数据记录", "设备维护"],
            "skills_required": ["实验操作", "数据记录", "设备使用", "安全规范"]
        },
        {
            "name": "数据分析师",
            "responsibilities": ["数据清洗", "统计分析", "结果验证", "可视化展示"],
            "skills_required": ["统计分析", "数据处理", "编程能力", "数据可视化"]
        }
    ],
    common_tools=[
        {"name": "SPSS", "category": "统计软件", "purpose": "统计分析"},
        {"name": "Python", "category": "编程语言", "purpose": "数据处理和分析"},
        {"name": "R", "category": "统计语言", "purpose": "统计计算和可视化"},
        {"name": "Matlab", "category": "数值计算", "purpose": "科学计算"},
        {"name": "EndNote", "category": "文献管理", "purpose": "文献管理和引用"},
        {"name": "LaTeX", "category": "排版系统", "purpose": "学术论文排版"}
    ],
    common_skills=[
        {"name": "学术研究", "level": "高级", "related_tools": ["文献数据库"]},
        {"name": "数据分析", "level": "高级", "related_tools": ["SPSS", "Python", "R"]},
        {"name": "实验设计", "level": "中级", "related_tools": []},
        {"name": "学术写作", "level": "中级", "related_tools": ["LaTeX", "EndNote"]},
        {"name": "统计分析", "level": "高级", "related_tools": ["SPSS", "R"]}
    ],
    task_types=[
        "文献调研", "假设提出", "实验设计", "样本采集",
        "数据分析", "结果验证", "论文撰写", "成果发表", "项目总结"
    ],
    extraction_patterns={
        "hypothesis": r"假设[:：](.+)|研究假设[:：](.+)",
        "method": r"方法[:：](.+)|实验方法[:：](.+)|研究方法[:：](.+)",
        "sample": r"样本[:：](.+)|样本量[:：](.+)",
        "tool": r"工具[:：](.+)|软件[:：](.+)|设备[:：](.+)"
    },
    focus_points=[
        "研究假设", "实验方法", "数据采集", "样本选择",
        "分析工具", "文献综述", "成果输出", "伦理审查"
    ],
    domain_context="""
研究项目通常包括文献调研、假设提出、实验设计、数据采集、数据分析、论文撰写等阶段。
关注点：研究假设、实验方法、数据采集、样本选择、分析工具、成果输出。
典型角色：项目负责人、研究员、实验员、数据分析师。
常用工具：SPSS、Python、R、Matlab、EndNote、LaTeX。
关键交付物：研究方案、实验记录、数据分析报告、学术论文。
特殊要求：可能需要伦理审查、同行评审。
""",
    default_config={
        "max_task_level": 4,
        "default_project_months": 6,
        "work_hours_per_day": 8,
        "peer_review_required": True,
        "ethics_approval_required": True
    }
)


# 默认模板
DEFAULT_TEMPLATE = DomainTemplateV2(
    domain_type="其他",
    template_id="default_v2",
    default_roles=[
        {
            "name": "项目经理",
            "responsibilities": ["项目规划", "进度管理", "资源协调"],
            "skills_required": ["项目管理", "沟通协调"]
        },
        {
            "name": "执行人员",
            "responsibilities": ["任务执行", "成果交付"],
            "skills_required": ["专业技能"]
        }
    ],
    common_tools=[
        {"name": "项目管理工具", "category": "管理工具", "purpose": "项目管理"}
    ],
    common_skills=[
        {"name": "项目管理", "level": "中级", "related_tools": ["项目管理工具"]}
    ],
    task_types=[
        "需求分析", "方案设计", "任务执行", "质量检查", "成果交付"
    ],
    extraction_patterns={
        "goal": r"目标[:：](.+)",
        "deliverable": r"交付物[:：](.+)|成果[:：](.+)"
    },
    focus_points=[
        "项目目标", "交付成果", "时间节点", "资源需求"
    ],
    domain_context="""
通用项目通常包括需求分析、方案设计、任务执行、质量检查、成果交付等阶段。
关注点：项目目标、交付成果、时间节点、资源需求。
""",
    default_config={
        "max_task_level": 3,
        "work_hours_per_day": 8
    }
)


# 模板注册表
DOMAIN_TEMPLATES = {
    "software_dev_v2": SOFTWARE_DEV_TEMPLATE,
    "outdoor_construction_v2": OUTDOOR_CONSTRUCTION_TEMPLATE,
    "marketing_campaign_v2": MARKETING_CAMPAIGN_TEMPLATE,
    "research_project_v2": RESEARCH_PROJECT_TEMPLATE,
    "default_v2": DEFAULT_TEMPLATE
}


def get_template_by_domain(domain_type: str) -> DomainTemplateV2:
    """
    根据领域类型获取模板
    
    Args:
        domain_type: 领域类型
        
    Returns:
        领域模板对象
    """
    domain_map = {
        "软件开发": "software_dev_v2",
        "户外施工": "outdoor_construction_v2",
        "营销活动": "marketing_campaign_v2",
        "研究项目": "research_project_v2",
        "其他": "default_v2"
    }
    
    template_id = domain_map.get(domain_type, "default_v2")
    return DOMAIN_TEMPLATES[template_id]


def get_template_by_id(template_id: str) -> DomainTemplateV2:
    """
    根据模板ID获取模板
    
    Args:
        template_id: 模板ID
        
    Returns:
        领域模板对象
    """
    return DOMAIN_TEMPLATES.get(template_id, DEFAULT_TEMPLATE)
