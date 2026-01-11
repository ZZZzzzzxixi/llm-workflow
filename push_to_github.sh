#!/bin/bash

# GitHub 推送脚本
# 使用 Personal Access Token 推送代码到 GitHub

TOKEN="<GITHUB_PAT_PLACEHOLDER>"
REPO="github.com/ZZZzzzzxixi/llm-workflow.git"
BRANCH="main"

echo "=========================================="
echo "正在推送到 GitHub..."
echo "=========================================="
echo "仓库: https://${REPO}"
echo "分支: ${BRANCH}"
echo ""

# 先同步远程仓库
echo "📥 正在同步远程仓库..."
git fetch https://${TOKEN}@${REPO} ${BRANCH}

# 检查是否有冲突
LOCAL=$(git rev-parse ${BRANCH})
REMOTE=$(git rev-parse FETCH_HEAD)
BASE=$(git merge-base @ @{u})

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✅ 本地已是最新"
elif [ "$LOCAL" = "$BASE" ]; then
    echo "📥 需要拉取远程更改..."
    git pull --rebase https://${TOKEN}@${REPO} ${BRANCH}
    echo "✅ 远程更改已同步"
elif [ "$REMOTE" = "$BASE" ]; then
    echo "✅ 准备推送本地更改..."
else
    echo "⚠️  检测到分叉，正在变基..."
    git pull --rebase https://${TOKEN}@${REPO} ${BRANCH}
    echo "✅ 变基完成"
fi

echo ""
echo "📤 开始推送..."

# 推送代码
git push https://${TOKEN}@${REPO} ${BRANCH}

# 检查推送结果
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ 推送成功！"
    echo "=========================================="
    echo "访问你的仓库查看："
    echo "https://github.com/ZZZzzzzxixi/llm-workflow"
    echo ""
    echo "⚠️  安全提示：推送完成后请删除此脚本，避免 Token 泄露！"
    echo "   删除命令: rm push_to_github.sh"
else
    echo ""
    echo "=========================================="
    echo "❌ 推送失败"
    echo "=========================================="
    echo "请检查："
    echo "1. Token 是否正确"
    echo "2. 网络连接是否正常"
    echo "3. GitHub 仓库权限是否足够"
    exit 1
fi
