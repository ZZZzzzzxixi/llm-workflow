#!/bin/bash

# 工作流API测试脚本

# API配置
API_URL="https://rfvfy978y6.coze.site/run"
TOKEN="eyJhbGciOiJSUzI1NiIsImtpZCI6IjI1NDgzMTMwLWQxYzAtNGZlNS05ZjJlLWRmNjU3OTFkMDJlNSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbImsxM09jVEVCT01FVnhmRTJKQzgyaFAyS1hhYzdEWkxxIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzY3OTQ0MzY5LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NTkzMjQzMTg1MTI0NDc0OTMwIiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NTkzMjYzMjQ5OTQ1MDAyMDI2In0.LZf4wiYUEX4di5dUNVyyGLUb_3B39ceqp3dlgH_qKp86t-eCzG5bQKpMH4AIt49ZFNzoMtaC5W9pvjY14TXIS9-KyJdZDCjhl85XQSNWP3M8SueitKf3c_D2o0f4z_UwNDyOJdTxLDWUeFAdLw4d3jhjii3TnkVQPlpt3lPG6F39iHbZsV51rrBZSvrKRXQeELO_4WsVMfWy6UtmBipPtRHRiKFwwQBb9o79c5ciUOLTmWBhVpKiIfIdVl-DOBVry_JGg_RsWzK7LaMEh09-onvcffusTrUKC8iAKIhz0ABdoZkRV-HItknm8arQnevk7ZpWt26bxV5UqICKne1hmA"

echo "=========================================="
echo "  工作流API测试"
echo "=========================================="
echo ""

# 方法1：测试本地文件（需要本地运行环境）
echo "【方法1】本地文件测试"
echo "注意：此方法需要工作流运行在本地环境，否则无法访问本地文件"
echo ""

# 检查本地文件
if [ -f "assets/test_component.zip" ]; then
    echo "✅ 找到测试文件：assets/test_component.zip"
    echo "文件大小：$(ls -lh assets/test_component.zip | awk '{print $5}')"
    echo ""
    echo "本地路径测试（仅适用于本地运行环境）："
    echo '{"component_path":"assets/test_component.zip"}' | \
    curl --location "${API_URL}" \
      --header "Authorization: Bearer ${TOKEN}" \
      --header "Content-Type: application/json" \
      --data @-
else
    echo "❌ 未找到测试文件：assets/test_component.zip"
fi

echo ""
echo ""
echo "【方法2】GitHub URL测试"
echo "注意：此方法需要先将文件推送到GitHub"
echo ""

# 检查是否需要推送文件
echo "检查Git状态..."
GIT_STATUS=$(git status --porcelain)

if [ -z "$GIT_STATUS" ]; then
    echo "✅ Git仓库状态正常"
    echo ""

    # 检查是否需要推送
    AHEAD_COUNT=$(git rev-list --count --left-right origin/main...HEAD | awk '{print $2}')
    if [ "$AHEAD_COUNT" -gt 0 ]; then
        echo "⚠️  本地有${AHEAD_COUNT}个提交未推送到GitHub"
        echo ""
        echo "为了测试API，需要先将文件推送到GitHub。请选择："
        echo "1. 手动推送（推荐）："
        echo "   git push origin main"
        echo ""
        echo "2. 使用GitHub Personal Access Token自动推送："
        echo "   请创建GitHub Personal Access Token，然后运行："
        echo "   git push https://YOUR_TOKEN@github.com/ZZZzzzzxixi/llm-workflow.git main"
        echo ""
        echo "3. 配置Git凭据后推送："
        echo "   ./setup_git_credentials.sh"
        echo "   git push origin main"
        echo ""
        echo "推送完成后，使用以下URL测试："
        echo 'https://raw.githubusercontent.com/ZZZzzzzxixi/llm-workflow/main/assets/test_component.zip'
    else
        echo "✅ 本地提交与GitHub同步"
        echo ""
        echo "使用GitHub URL测试API："
        GITHUB_URL="https://raw.githubusercontent.com/ZZZzzzzxixi/llm-workflow/main/assets/test_component.zip"
        echo "URL: ${GITHUB_URL}"
        echo ""

        echo "执行API调用..."
        curl --location "${API_URL}" \
          --header "Authorization: Bearer ${TOKEN}" \
          --header "Content-Type: application/json" \
          --data "{\"component_path\":\"${GITHUB_URL}\"}"
    fi
else
    echo "⚠️  Git仓库有未提交的更改"
    git status --short
    echo ""
    echo "请先提交更改："
    echo "git add ."
    echo "git commit -m 'Add test files'"
    echo "git push origin main"
fi

echo ""
echo ""
echo "=========================================="
echo "  推送文件到GitHub的快速方法"
echo "=========================================="
echo ""
echo "如果您有GitHub Personal Access Token，可以使用以下命令推送："
echo ""
echo "export GITHUB_TOKEN='your_token_here'"
echo "git push https://\${GITHUB_TOKEN}@github.com/ZZZzzzzxixi/llm-workflow.git main"
echo ""
echo "或者手动输入账号密码："
echo "git push origin main"
echo ""
