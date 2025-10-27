#!/usr/bin/env python3
"""
代码重复检测工具

检查项目中是否存在重复代码，帮助识别和消除重复。
"""

import os
import sys
from pathlib import Path
from collections import defaultdict
import hashlib


def get_file_hash(file_path):
    """计算文件内容的哈希值"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        return None


def find_duplicate_files(directory, extensions=None):
    """查找完全重复的文件"""
    if extensions is None:
        extensions = ['.py']
    
    hash_map = defaultdict(list)
    
    for root, dirs, files in os.walk(directory):
        # 跳过虚拟环境和缓存目录
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules']]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                file_hash = get_file_hash(file_path)
                
                if file_hash:
                    hash_map[file_hash].append(file_path)
    
    # 找出重复的文件
    duplicates = {h: files for h, files in hash_map.items() if len(files) > 1}
    return duplicates


def check_similar_function_names(directory):
    """检查相似的函数名（可能表示重复功能）"""
    import re
    
    function_pattern = re.compile(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')
    class_pattern = re.compile(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(:]')
    
    functions = defaultdict(list)
    classes = defaultdict(list)
    
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # 查找函数
                        for match in function_pattern.finditer(content):
                            func_name = match.group(1)
                            if not func_name.startswith('_'):  # 忽略私有函数
                                functions[func_name].append(file_path)
                        
                        # 查找类
                        for match in class_pattern.finditer(content):
                            class_name = match.group(1)
                            classes[class_name].append(file_path)
                
                except Exception as e:
                    continue
    
    # 找出在多个文件中出现的函数/类
    duplicate_functions = {name: files for name, files in functions.items() if len(files) > 1}
    duplicate_classes = {name: files for name, files in classes.items() if len(files) > 1}
    
    return duplicate_functions, duplicate_classes


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    twork_dir = project_root / 'twork'
    backend_dir = project_root / 'backend'
    
    print("=" * 80)
    print("TeamWork 代码重复检测")
    print("=" * 80)
    
    # 1. 检查完全重复的文件
    print("\n【检查1】查找完全重复的文件...")
    all_duplicates = {}
    
    for directory in [twork_dir, backend_dir]:
        if directory.exists():
            duplicates = find_duplicate_files(directory)
            all_duplicates.update(duplicates)
    
    if all_duplicates:
        print(f"⚠️  发现 {len(all_duplicates)} 组重复文件：")
        for hash_val, files in all_duplicates.items():
            print(f"\n  组 {hash_val[:8]}:")
            for file in files:
                print(f"    - {file}")
        has_issues = True
    else:
        print("✅ 未发现完全重复的文件")
        has_issues = False
    
    # 2. 检查重复的函数/类名
    print("\n【检查2】查找重复的函数和类名...")
    duplicate_functions, duplicate_classes = check_similar_function_names(twork_dir)
    
    # 过滤掉常见的函数名（如__init__）
    common_names = {'__init__', '__str__', '__repr__', 'main', 'test', 'setUp', 'tearDown'}
    duplicate_functions = {k: v for k, v in duplicate_functions.items() if k not in common_names}
    
    if duplicate_functions:
        print(f"\n⚠️  发现 {len(duplicate_functions)} 个重复的函数名（可能是重复功能）：")
        for func_name, files in list(duplicate_functions.items())[:10]:  # 只显示前10个
            print(f"\n  函数 '{func_name}' 出现在:")
            for file in files:
                print(f"    - {file}")
        if len(duplicate_functions) > 10:
            print(f"\n  ... 还有 {len(duplicate_functions) - 10} 个重复函数名")
        has_issues = True
    else:
        print("✅ 未发现重复的函数名")
    
    if duplicate_classes:
        print(f"\n⚠️  发现 {len(duplicate_classes)} 个重复的类名：")
        for class_name, files in duplicate_classes.items():
            print(f"\n  类 '{class_name}' 出现在:")
            for file in files:
                print(f"    - {file}")
        has_issues = True
    else:
        print("✅ 未发现重复的类名")
    
    # 3. 总结
    print("\n" + "=" * 80)
    if has_issues:
        print("❌ 发现潜在的代码重复问题，请检查上述结果")
        print("\n建议：")
        print("  1. 完全重复的文件应该删除其中一个")
        print("  2. 重复的函数/类名应该检查是否可以合并")
        print("  3. 如果是不同功能的同名函数，考虑重命名以提高代码可读性")
        return 1
    else:
        print("✅ 未发现明显的代码重复问题")
        return 0


if __name__ == '__main__':
    sys.exit(main())
