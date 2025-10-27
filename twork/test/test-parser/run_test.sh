#!/bin/bash

# StructureFactory 测试快速启动脚本

set -e

echo "======================================"
echo "StructureFactory 测试环境启动"
echo "======================================"
echo ""

# 检查当前目录
if [ ! -f "test.py" ]; then
    echo "错误：请在 test-parser 目录下运行此脚本"
    exit 1
fi

# 选择运行模式
echo "请选择运行模式："
echo "1) 使用 Docker (推荐)"
echo "2) 本地运行 (需要已安装依赖)"
echo ""
read -p "请输入选项 [1/2]: " choice

case $choice in
    1)
        echo ""
        echo "使用 Docker 运行测试..."
        echo ""
        
        # 检查 Docker
        if ! command -v docker &> /dev/null; then
            echo "错误：未安装 Docker"
            exit 1
        fi
        
        # 检查 docker-compose
        if ! command -v docker-compose &> /dev/null; then
            echo "错误：未安装 docker-compose"
            exit 1
        fi
        
        # 构建镜像
        echo "正在构建 Docker 镜像..."
        docker-compose build
        
        echo ""
        echo "是否配置 OpenAI API 进行完整测试? [y/N]"
        read -p "> " use_llm
        
        if [[ $use_llm =~ ^[Yy]$ ]]; then
            echo ""
            read -p "请输入 OPENAI_API_KEY: " api_key
            read -p "请输入 OPENAI_API_BASE (留空使用默认): " api_base
            
            export OPENAI_API_KEY="$api_key"
            if [ -n "$api_base" ]; then
                export OPENAI_API_BASE="$api_base"
            fi
        fi
        
        echo ""
        echo "正在运行测试..."
        docker-compose run --rm test-parser
        ;;
        
    2)
        echo ""
        echo "本地运行测试..."
        echo ""
        
        # 检查 Python
        if ! command -v python3 &> /dev/null; then
            echo "错误：未安装 Python 3"
            exit 1
        fi
        
        # 检查依赖
        echo "检查依赖..."
        if ! python3 -c "import PyPDF2" &> /dev/null; then
            echo "警告：缺少某些依赖，尝试安装..."
            pip3 install -r requirements.txt
        fi
        
        echo ""
        echo "是否配置 OpenAI API 进行完整测试? [y/N]"
        read -p "> " use_llm
        
        if [[ $use_llm =~ ^[Yy]$ ]]; then
            echo ""
            read -p "请输入 OPENAI_API_KEY: " api_key
            read -p "请输入 OPENAI_API_BASE (留空使用默认): " api_base
            
            export OPENAI_API_KEY="$api_key"
            if [ -n "$api_base" ]; then
                export OPENAI_API_BASE="$api_base"
            fi
        fi
        
        echo ""
        echo "正在运行测试..."
        
        # 设置 PYTHONPATH
        export PYTHONPATH="$(cd ../.. && pwd)"
        
        python3 test.py
        ;;
        
    *)
        echo "无效选项"
        exit 1
        ;;
esac

echo ""
echo "======================================"
echo "测试完成！"
echo "======================================"
echo ""
echo "查看结果："
echo "  - 测试输出已显示在上方"
echo "  - 完整结果保存在: output_result.json (如果运行了完整测试)"
echo "  - 缓存文件位于: cache/"
echo ""
