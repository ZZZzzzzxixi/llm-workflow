# Git凭据自动配置说明

## 快速使用

执行配置脚本：

```bash
./setup_git_credentials.sh
```

## 配置选项说明

### 1. 缓存模式（1小时）
- 凭据保存在内存中
- 重启电脑后需要重新输入
- 适合临时使用或多人共用电脑

### 2. 永久存储模式（推荐个人使用）
- macOS：凭据保存在钥匙串
- Windows：凭据保存在凭据管理器
- Linux：凭据保存在 `~/.git-credentials` 文件中
- 首次输入密码后永久保存

### 3. SSH密钥模式（最安全）
- 使用SSH公钥认证
- 无需输入密码
- 最安全，适合长期使用

## 手动配置方法

### 缓存模式（1小时）
```bash
git config --global credential.helper cache
git config --global credential.helper 'cache --timeout=3600'
```

### 永久存储模式
```bash
git config --global credential.helper store
```
首次操作时输入一次密码后自动保存。

### SSH密钥模式

**1. 生成SSH密钥**
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

**2. 查看公钥**
```bash
cat ~/.ssh/id_ed25519.pub
```

**3. 添加到Git平台**
- GitHub：Settings → SSH and GPG keys → New SSH key
- GitLab：Settings → SSH Keys → Add new key
- Gitee：设置 → SSH公钥 → 添加公钥

**4. 将HTTPS仓库改为SSH**
```bash
# 查看当前远程仓库
git remote -v

# 改为SSH协议
git remote set-url origin git@github.com:username/repo.git
```

## 验证配置

### 验证HTTPS凭据
执行任意Git操作（如 `git pull`），确认无需重复输入密码。

### 验证SSH连接
```bash
ssh -T git@github.com
```

成功会显示：
```
Hi username! You've successfully authenticated...
```

## 常见问题

### Q: 还是需要输入密码？
**A:** 检查以下几点：
1. 确认配置是否生效：`git config --global credential.helper`
2. 如果使用SSH模式，确认已切换远程URL为SSH协议
3. 某些平台需要使用Personal Access Token代替密码

### Q: 如何清除已保存的凭据？
**A:**
```bash
# 清除Git凭据
git config --global --unset credential.helper

# Linux删除凭据文件
rm -f ~/.git-credentials

# macOS删除钥匙串凭据
# 打开"钥匙串访问"应用，搜索"git"并删除

# Windows删除凭据管理器中的Git凭据
# 控制面板 → 用户账户 → 凭据管理器 → Windows凭据 → 删除git相关条目
```

### Q: 公司GitLab自建服务器如何配置？
**A:** 
```bash
# 配置特定域名的凭据
git config --global credential.https://gitlab.company.com.helper store
```

## 安全建议

1. **个人电脑**：推荐使用永久存储或SSH模式
2. **公司电脑**：推荐使用缓存模式或SSH模式
3. **多人共用电脑**：使用缓存模式，退出前清除缓存：`git credential-cache exit`
4. 敏感仓库：始终使用SSH密钥认证

## 推荐方案总结

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| 个人开发电脑 | SSH密钥模式 | 最安全，最方便 |
| 公司开发电脑 | 缓存模式(1小时) | 安全和便利的平衡 |
| CI/CD环境 | SSH密钥模式 | 自动化最佳实践 |
| 临时测试 | 缓存模式 | 无需永久保存 |
