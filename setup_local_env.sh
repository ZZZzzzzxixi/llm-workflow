#!/bin/bash

# API Key 配置助手
# 帮助用户配置本地运行所需的 API Key

echo "=========================================="
echo "  本地运行环境配置助手"
echo "=========================================="
echo ""

# 检查是否存在 .env 文件
if [ -f ".env" ]; then
    echo "⚠️  检测到已存在 .env 文件"
    read -p "是否要重新配置？(y/n): " choice
    if [[ ! $choice =~ ^[Yy]$ ]]; then
        echo "取消配置，使用现有配置"
        exit 0
    fi
    echo ""
fi

echo "📝 开始配置本地运行环境..."
echo ""

# 提示用户输入 API Key
echo "=========================================="
echo "  步骤 1: 获取 API Key"
echo "=========================================="
echo ""
echo "请按以下步骤获取 API Key："
echo ""
echo "1. 访问 Coze 平台：https://www.coze.cn"
echo "2. 登录并进入你的工作空间"
echo "3. 进入 'API 密钥管理' 或 'Access Key' 页面"
echo "4. 创建新的 API Key 或复制现有的"
echo ""
read -p "🔑 请输入你的 API Key: " api_key

if [ -z "$api_key" ]; then
    echo "❌ API Key 不能为空"
    exit 1
fi

# 创建 .env 文件
echo ""
echo "=========================================="
echo "  步骤 2: 创建配置文件"
echo "=========================================="
echo ""

cat > .env << EOF
# 本地运行环境变量配置
# 生成时间: $(date)

# 大语言模型配置
COZE_INTEGRATION_MODEL_API_KEY=$api_key
COZE_INTEGRATION_MODEL_BASE_URL=https://integration.coze.cn/api/v3

# 对象存储配置（可选）
COZE_BUCKET_ENDPOINT_URL=https://integration.coze.cn/coze-coding-s3proxy/v1
COZE_BUCKET_NAME=bucket_1767939698208

# 工作目录（自动设置）
COZE_WORKSPACE_PATH=$(pwd)

EOF

echo "✅ 配置文件已创建: .env"
echo ""

# 测试配置
echo "=========================================="
echo "  步骤 3: 测试配置"
echo "=========================================="
echo ""

# 测试 Python 能否加载环境变量
if python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅ 环境变量加载成功'); api_key = os.getenv('COZE_INTEGRATION_MODEL_API_KEY'); print(f'API Key: {api_key[:20]}...' if api_key else '❌ API Key 未设置')" 2>/dev/null; then
    echo ""
    echo "✅ 配置测试通过！"
else
    echo ""
    echo "⚠️  警告：python-dotenv 未安装"
    echo "正在安装 python-dotenv..."
    pip3 install python-dotenv
fi

echo ""
echo "=========================================="
echo "  配置完成！"
echo "=========================================="
echo ""
echo "✅ 配置文件已创建：.env"
echo ""
echo "下一步："
echo "1. 运行工作流：./run_local.sh <zip文件路径>"
echo "2. 或使用：python3 src/main.py -m flow -i '{\"component_path\": \"<路径>\"}'"
echo ""
echo "⚠️  注意："
echo "- .env 文件包含敏感信息，不要提交到 Git"
echo "- 已在 .gitignore 中配置，不会被提交"
echo ""
