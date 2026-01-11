#!/bin/bash

# Git凭据自动配置脚本
# 执行此脚本后，Git操作将缓存凭据，无需每次输入账号密码

echo "=========================================="
echo "  Git凭据自动配置工具"
echo "=========================================="
echo ""

# 检查Git是否安装
if ! command -v git &> /dev/null; then
    echo "❌ 错误：Git未安装，请先安装Git"
    exit 1
fi

echo "✅ Git已安装：$(git --version)"
echo ""

# 显示配置选项
echo "请选择凭据存储方式："
echo "1) 缓存模式（凭据在内存中保存1小时，重启电脑后需要重新输入）"
echo "2) 永久存储模式（凭据永久保存，适合个人电脑）"
echo "3) SSH密钥模式（推荐，最安全，需要配置SSH密钥）"
echo ""
read -p "请输入选项 (1/2/3，默认为2): " choice
choice=${choice:-2}

echo ""

case $choice in
    1)
        echo "📝 配置缓存模式（1小时）..."
        git config --global credential.helper cache
        git config --global credential.helper 'cache --timeout=3600'
        echo "✅ 配置完成！凭据将在内存中缓存1小时"
        echo "⚠️  重启电脑后需要重新输入一次密码"
        ;;
    2)
        echo "📝 配置永久存储模式..."
        
        # 检测操作系统
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            git config --global credential.helper osxkeychain
            echo "✅ 配置完成！凭据将保存在macOS钥匙串中"
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            git config --global credential.helper store
            echo "✅ 配置完成！"
            echo "⚠️  下次输入密码后，凭据将保存在 ~/.git-credentials 文件中（明文存储）"
            echo "💡 提示：首次拉取/推送时输入一次密码即可"
        elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            # Windows
            git config --global credential.helper wincred
            echo "✅ 配置完成！凭据将保存在Windows凭据管理器中"
        else
            git config --global credential.helper store
            echo "✅ 配置完成！"
            echo "💡 提示：首次拉取/推送时输入一次密码即可"
        fi
        ;;
    3)
        echo "📝 配置SSH密钥模式..."
        
        # 检查是否已有SSH密钥
        SSH_DIR="$HOME/.ssh"
        if [ -f "$SSH_DIR/id_ed25519.pub" ]; then
            echo "✅ 已检测到SSH密钥：$SSH_DIR/id_ed25519.pub"
            echo ""
            echo "公钥内容："
            cat "$SSH_DIR/id_ed25519.pub"
            echo ""
            echo "请将上述公钥添加到Git平台（GitHub/GitLab/Gitee）的SSH Keys设置中"
            echo ""
            read -p "是否需要测试SSH连接？(y/n): " test_ssh
            if [[ $test_ssh =~ ^[Yy]$ ]]; then
                echo "正在测试GitHub SSH连接..."
                ssh -T git@github.com 2>&1 | grep -q "successfully authenticated" && echo "✅ SSH连接成功！" || echo "❌ SSH连接失败，请检查密钥配置"
            fi
        else
            echo "未检测到SSH密钥，开始生成..."
            
            read -p "请输入您的邮箱（用于生成密钥注释）: " email
            email=${email:-"user@example.com"}
            
            echo "正在生成SSH密钥（ED25519算法）..."
            ssh-keygen -t ed25519 -C "$email" -f "$SSH_DIR/id_ed25519" -N ""
            
            if [ $? -eq 0 ]; then
                echo "✅ SSH密钥生成成功！"
                echo ""
                echo "私钥：$SSH_DIR/id_ed25519"
                echo "公钥：$SSH_DIR/id_ed25519.pub"
                echo ""
                echo "公钥内容："
                cat "$SSH_DIR/id_ed25519.pub"
                echo ""
                echo "=========================================="
                echo "  下一步操作："
                echo "=========================================="
                echo "1. 复制上述公钥内容"
                echo "2. 登录您的Git平台（GitHub/GitLab/Gitee）"
                echo "3. 进入 SSH Keys / SSH公钥 设置页面"
                echo "4. 粘贴公钥并保存"
                echo "5. 如果仓库是HTTPS协议，需要改为SSH协议："
                echo "   git remote set-url origin git@github.com:username/repo.git"
                echo ""
            else
                echo "❌ SSH密钥生成失败"
                exit 1
            fi
        fi
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "  配置总结"
echo "=========================================="
echo "当前凭据配置："
git config --global --get credential.helper
echo ""
echo "当前仓库URL："
if [ -d ".git" ]; then
    git remote -v
else
    echo "当前目录不是Git仓库"
fi
echo ""
echo "✅ 配置完成！现在执行Git操作时，只需输入一次账号密码即可"
