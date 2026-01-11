#!/usr/bin/env python3
"""
本地测试工作流脚本
"""
import os
import sys

# 设置环境变量
os.environ['PYTHONPATH'] = '/workspace/projects/src'
os.environ['COZE_WORKSPACE_PATH'] = '/workspace/projects'

sys.path.insert(0, '/workspace/projects/src')

from graphs.graph import main_graph

# 测试数据
test_input = {
    "component_path": "assets/test_component.zip"
}

print("=" * 60)
print("本地工作流测试")
print("=" * 60)
print()
print("输入:")
print(f"  component_path: {test_input['component_path']}")
print()
print("开始执行工作流...")
print()

try:
    result = main_graph.invoke(test_input)

    print()
    print("=" * 60)
    print("执行成功！")
    print("=" * 60)
    print()
    print("输出:")
    print(f"  readme_url: {result.get('readme_url', 'N/A')}")
    print()

    # 检查返回的URL类型
    readme_url = result.get('readme_url', '')
    if readme_url.startswith('http'):
        print("✅ 对象存储URL生成成功！")
        print(f"   直接访问: {readme_url}")
    elif readme_url.startswith('local:'):
        print("⚠️  使用本地文件模式（对象存储不可用）")
        print(f"   本地路径: {readme_url[6:]}")
    else:
        print("⚠️  未知的URL格式")

except Exception as e:
    print()
    print("=" * 60)
    print("执行失败！")
    print("=" * 60)
    print()
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
