#!/bin/bash

# 快速本地运行脚本

# 检查参数
if [ -z "$1" ]; then
    echo "用法: $0 <zip文件路径>"
    echo ""
    echo "示例:"
    echo "  $0 \"D:/wsl-file-sharing/newbridge/robotics_svc_media.zip\""
    echo "  $0 \"/mnt/d/wsl-file-sharing/newbridge/robotics_svc_media.zip\""
    echo "  $0 \"./test_component.zip\""
    exit 1
fi

COMPONENT_PATH="$1"

# 设置工作目录环境变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export COZE_WORKSPACE_PATH="${SCRIPT_DIR}"

# 设置大语言模型集成环境变量（本地运行必需）
export COZE_INTEGRATION_MODEL_BASE_URL="https://ark.cn-beijing.volces.com/api/v3"

echo "=========================================="
echo "组件文档生成工作流 - 本地运行"
echo "=========================================="
echo "输入路径: $COMPONENT_PATH"
echo "工作目录: ${COZE_WORKSPACE_PATH}"
echo ""

# 运行工作流
python3 src/main.py -m flow -i "{\"component_path\": \"$COMPONENT_PATH\"}"

# 检查执行结果
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ 工作流执行成功！"
    echo "=========================================="
    echo "生成的README.md位置: /tmp/README.md"
    echo ""
    echo "查看README内容："
    cat /tmp/README.md
else
    echo ""
    echo "=========================================="
    echo "❌ 工作流执行失败"
    echo "=========================================="
    exit 1
fi
