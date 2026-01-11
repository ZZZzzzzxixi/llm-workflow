# API测试指南

## 问题分析

当前遇到的错误：
```
404 Client Error: Not Found for url: https://raw.githubusercontent.com/ZZZzzzzxixi/llm-workflow/tmp/source/robotics_svc_media.zip
```

这说明GitHub仓库中没有这个文件，虽然本地存在，但未推送到GitHub。

## 解决方案

### 方法1：推送文件到GitHub（推荐）

#### 步骤1：检查本地文件

```bash
# 查看本地有哪些zip文件
ls -lh *.zip 2>/dev/null
ls -lh assets/*.zip 2>/dev/null
ls -lh tmp/source/*.zip 2>/dev/null
```

当前本地文件：
- `assets/test_component.zip` (1.5K) - 小型测试文件
- `tmp/source/robotics_svc_media.zip` (34M) - 大型测试文件

#### 步骤2：推送文件到GitHub

**选项A：使用Git凭据（交互式）**

```bash
# 配置Git凭据（只需一次）
./setup_git_credentials.sh

# 推送到GitHub
git push origin main
```

**选项B：使用Personal Access Token**

1. 在GitHub上创建Personal Access Token：
   - 访问：https://github.com/settings/tokens
   - 点击 "Generate new token" -> "Generate new token (classic)"
   - 勾选 `repo` 权限
   - 生成并复制token

2. 推送文件：

```bash
# 设置token环境变量（替换为你的token）
export GITHUB_TOKEN='ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# 推送到GitHub
git push https://${GITHUB_TOKEN}@github.com/ZZZzzzzxixi/llm-workflow.git main
```

**选项C：每次输入账号密码（简单但不推荐）**

```bash
git push origin main
# 会提示输入GitHub账号和密码（密码输入Personal Access Token）
```

#### 步骤3：验证文件是否可访问

推送完成后，在浏览器中访问以下URL，确认文件可以下载：

```bash
# 测试小型文件
https://raw.githubusercontent.com/ZZZzzzzxixi/llm-workflow/main/assets/test_component.zip

# 测试大型文件（如果已推送）
https://raw.githubusercontent.com/ZZZzzzzxixi/llm-workflow/main/tmp/source/robotics_svc_media.zip
```

#### 步骤4：调用工作流API

**使用小型文件（推荐，速度快）：**

```bash
curl --location "https://rfvfy978y6.coze.site/run" \
  --header "Authorization: Bearer YOUR_TOKEN" \
  --header "Content-Type: application/json" \
  --data "{\"component_path\":\"https://raw.githubusercontent.com/ZZZzzzzxixi/llm-workflow/main/assets/test_component.zip\"}"
```

**使用大型文件：**

```bash
curl --location "https://rfvfy978y6.coze.site/run" \
  --header "Authorization: Bearer YOUR_TOKEN" \
  --header "Content-Type: application/json" \
  --data "{\"component_path\":\"https://raw.githubusercontent.com/ZZZzzzzxixi/llm-workflow/main/tmp/source/robotics_svc_media.zip\"}"
```

### 方法2：使用本地文件（仅适用于本地运行环境）

如果工作流运行在本地环境（不是Coze远程服务），可以直接使用本地文件路径：

```bash
curl --location "http://localhost:8000/run" \
  --header "Content-Type: application/json" \
  --data "{\"component_path\":\"assets/test_component.zip\"}"
```

注意：远程API无法访问客户端本地文件系统。

### 方法3：使用其他可公开访问的URL

如果不想推送到GitHub，可以使用其他文件托管服务：

1. **GitHub Releases**：创建一个Release上传文件
2. **GitHub Gist**：上传文件（适合小文件）
3. **对象存储服务**：AWS S3、阿里云OSS等
4. **临时文件分享**：如 https://transfer.sh/ 等

## 快速测试脚本

我已创建了一个自动化测试脚本：

```bash
# 赋予执行权限
chmod +x test_workflow.sh

# 运行测试脚本
./test_workflow.sh
```

脚本会自动检测文件状态并给出测试建议。

## 常见问题

### Q: 为什么会出现404错误？

A: API返回404说明文件URL无法访问。原因可能是：
1. 文件未推送到GitHub
2. 分支名称不正确（main vs master）
3. 文件路径不正确

### Q: 如何确认文件已推送到GitHub？

A: 访问以下URL，如果文件能下载说明已推送成功：
```
https://raw.githubusercontent.com/ZZZzzzzxixi/llm-workflow/main/assets/test_component.zip
```

### Q: 推送时提示"Permission denied"怎么办？

A: 检查：
1. 是否是仓库的所有者或有推送权限
2. Personal Access Token是否有`repo`权限
3. GitHub URL是否正确

### Q: 文件太大推送失败怎么办？

A: GitHub单个文件限制为100MB。如果超过限制：
1. 使用Git LFS（Large File Storage）
2. 将文件拆分成多个小文件
3. 使用其他文件托管服务

## 预期结果

成功调用API后，应该返回类似以下内容：

```json
{
  "readme_url": "https://your-bucket.oss-endpoint.com/readme_xxxxx.md"
}
```

返回的URL是生成的README.md文件的下载地址。

## 下一步

测试成功后，可以：
1. 根据需要调整工作流配置
2. 测试不同的输入文件
3. 优化生成的README格式
4. 集成到自动化流程中
