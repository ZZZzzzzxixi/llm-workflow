#!/bin/bash

# README编码修复测试脚本

echo "=========================================="
echo "  README编码修复验证"
echo "=========================================="
echo ""

# 生成新的README
echo "步骤1: 生成新的README文件..."
export PYTHONPATH=/workspace/projects/src
RESULT=$(python3 -c "
from graphs.graph import main_graph
result = main_graph.invoke({'component_path': 'assets/test_component.zip'})
print(result.get('readme_url', ''))
" 2>&1 | grep -v WARNING)

if [ -z "$RESULT" ]; then
    echo "❌ 生成失败"
    exit 1
fi

echo "✅ 生成成功"
echo "URL: $RESULT"
echo ""

# 检查Content-Type
echo "步骤2: 检查Content-Type是否包含charset=utf-8..."
CONTENT_TYPE=$(curl -sI "$RESULT" | grep -i "content-type:" | head -1)

echo "Content-Type: $CONTENT_TYPE"

if echo "$CONTENT_TYPE" | grep -q "charset=utf-8"; then
    echo "✅ Content-Type 正确（包含 charset=utf-8）"
else
    echo "❌ Content-Type 不正确（缺少 charset=utf-8）"
    exit 1
fi

echo ""

# 下载并验证中文内容
echo "步骤3: 验证中文内容是否正常..."
echo ""

# 下载前50行
echo "README 内容（前50行）："
echo "----------------------------------------"
curl -s "$RESULT" | head -50
echo "----------------------------------------"
echo ""

# 检查关键中文关键词
echo "步骤4: 检查关键中文关键词..."
echo ""

CHINESE_KEYWORDS=("组件文档" "自动生成" "目录结构" "头文件函数" "函数调用关系" "处理流程图")

for keyword in "${CHINESE_KEYWORDS[@]}"; do
    if curl -s "$RESULT" | grep -q "$keyword"; then
        echo "✅ 找到关键词: $keyword"
    else
        echo "❌ 未找到关键词: $keyword"
    fi
done

echo ""
echo "=========================================="
echo "  测试完成"
echo "=========================================="
echo ""
echo "修复说明："
echo "- 修改了 save_readme_node 函数"
echo "- Content-Type 从 'text/markdown' 改为 'text/markdown; charset=utf-8'"
echo "- 这样浏览器就能正确识别UTF-8编码的中文"
echo ""
echo "现在可以在浏览器中打开以下链接查看README："
echo "$RESULT"
echo ""
