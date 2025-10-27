#!/bin/bash
# 数据库迁移脚本 - 应用SimulationLog模型的字段扩展

set -e

echo "📦 TeamWork 数据库迁移脚本"
echo "================================"
echo ""

# 检查是否在项目根目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

echo "🔍 检查数据库连接..."

# 使用Docker执行迁移（如果使用Docker部署）
if command -v docker-compose &> /dev/null; then
    echo "✅ 检测到Docker Compose环境"
    echo ""
    echo "📝 创建迁移脚本..."
    
    # 生成Alembic迁移
    docker-compose exec backend alembic revision --autogenerate -m "extend_simulation_log_fields"
    
    echo ""
    echo "🚀 应用数据库迁移..."
    docker-compose exec backend alembic upgrade head
    
    echo ""
    echo "✅ 数据库迁移完成！"
else
    echo "⚠️  未检测到Docker环境，尝试本地迁移..."
    
    # 激活虚拟环境（如果存在）
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    cd backend
    
    # 生成迁移
    alembic revision --autogenerate -m "extend_simulation_log_fields"
    
    # 应用迁移
    alembic upgrade head
    
    cd ..
    
    echo ""
    echo "✅ 数据库迁移完成！"
fi

echo ""
echo "📊 新增字段列表:"
echo "  - timestamp (DateTime): 事件时间戳"
echo "  - event_type (String): 事件类型"
echo "  - role_name (String): 角色名称"
echo "  - task_name (String): 任务名称"
echo "  - content (Text): 对话内容"
echo "  - participants (JSON): 参与者列表"
echo "  - status (String): 状态"
echo "  - progress_percentage (Integer): 进度百分比"
echo "  - metadata (JSON): 扩展元数据"
echo ""
echo "🎉 迁移完成！可以开始使用新功能了。"
