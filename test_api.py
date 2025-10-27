#!/usr/bin/env python3
"""
API测试脚本

用于测试后端API的功能
"""

import requests
import json
from pathlib import Path


BACKEND_URL = "http://localhost:8000"


def test_health():
    """测试健康检查"""
    print("=" * 60)
    print("测试健康检查...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False


def test_get_llm_config():
    """测试获取LLM配置"""
    print("=" * 60)
    print("测试获取LLM配置...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/config/llm", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"配置: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False


def test_update_llm_config():
    """测试更新LLM配置"""
    print("=" * 60)
    print("测试更新LLM配置...")
    
    config = {
        "api_base_url": "https://api.openai.com/v1",
        "api_key": "test_key_12345",
        "model_name": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2000,
        "timeout": 60
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/config/llm",
            json=config,
            timeout=5
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False


def test_upload_document():
    """测试文档上传"""
    print("=" * 60)
    print("测试文档上传...")
    
    # 创建测试文件
    test_file = Path("test_requirement.txt")
    test_file.write_text("""
# 项目需求文档

## 项目名称
测试项目

## 项目描述
这是一个用于测试API的示例项目

## 主要目标
- 完成基本功能开发
- 进行充分测试
- 按时交付

## 关键需求
- 需求1: 实现用户登录功能
- 需求2: 实现数据管理功能
- 需求3: 实现报表生成功能
""", encoding="utf-8")
    
    try:
        with open(test_file, "rb") as f:
            files = {"file": (test_file.name, f, "text/plain")}
            response = requests.post(
                f"{BACKEND_URL}/api/upload/document",
                files=files,
                timeout=30
            )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"项目ID: {result.get('project_id')}")
            print(f"状态: {result.get('status')}")
            print(f"需求: {json.dumps(result.get('requirements'), indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("TeamWork API 测试")
    print("=" * 60 + "\n")
    
    results = {
        "健康检查": test_health(),
        "获取LLM配置": test_get_llm_config(),
        "更新LLM配置": test_update_llm_config(),
        # "文档上传": test_upload_document(),  # 需要LLM配置才能工作
    }
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\n总计: {passed}/{total} 通过")


if __name__ == "__main__":
    main()
