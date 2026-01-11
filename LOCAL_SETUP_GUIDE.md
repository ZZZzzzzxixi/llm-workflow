# 本地运行环境配置指南

## 快速开始

### 方式一：使用配置助手（推荐）

```bash
# 运行配置脚本
./setup_local_env.sh
```

脚本会引导你完成以下步骤：
1. 输入你的 API Key
2. 自动创建 `.env` 配置文件
3. 测试配置是否正确

### 方式二：手动配置

1. 复制配置模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填写你的 API Key：
```bash
nano .env  # 或使用其他编辑器
```

3. 填写以下内容：
```env
COZE_INTEGRATION_MODEL_API_KEY=your_actual_api_key_here
```

---

## 获取 API Key

### 步骤

1. **访问 Coze 平台**
   - 打开浏览器访问：https://www.coze.cn
   - 使用你的账号登录

2. **进入工作空间**
   - 选择你的工作空间
   - 进入 "设置" 或 "API 密钥管理"

3. **获取 API Key**
   - 点击 "创建 API Key"
   - 复制生成的密钥（格式通常为：`sat_xxxxxxxxxxxxxx`）

4. **配置到环境**
   - 将 API Key 填写到 `.env` 文件中的 `COZE_INTEGRATION_MODEL_API_KEY` 字段

---

## 验证配置

运行以下命令测试配置是否正确：

```bash
# 方法一：运行工作流
./run_local.sh assets/test_component.zip

# 方法二：测试环境变量
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('COZE_INTEGRATION_MODEL_API_KEY')[:20] + '...')"
```

如果看到输出正常，说明配置成功。

---

## 常见问题

### Q1: 提示 "缺少 API Key 配置"

**原因**：`.env` 文件不存在或未设置 `COZE_INTEGRATION_MODEL_API_KEY`

**解决**：
```bash
# 运行配置助手
./setup_local_env.sh

# 或手动检查
cat .env | grep COZE_INTEGRATION_MODEL_API_KEY
```

### Q2: API Key 格式不正确

**错误信息**：`AuthenticationError: the API key or AK/SK in request is missing or invalid`

**原因**：API Key 填写错误或格式不正确

**解决**：
- 确认 API Key 以 `sat_` 开头
- 确保没有多余的空格或引号
- 重新从 Coze 平台获取新的 API Key

### Q3: 配置文件不被识别

**原因**：`.env` 文件位置不正确

**解决**：
```bash
# 确认 .env 文件在项目根目录
ls -la .env

# 应该看到：
# -rw-r--r-- 1 user user ... .env
```

### Q4: 本地运行但使用的是云端配置

**原因**：`.env` 文件被提交到 Git 了

**解决**：
```bash
# 从 Git 移除 .env 文件（保留本地副本）
git rm --cached .env

# 确认 .gitignore 包含 /.env 和 .env
cat .gitignore | grep .env
```

---

## 环境变量说明

| 环境变量 | 说明 | 是否必需 | 默认值 |
|---------|------|---------|--------|
| `COZE_INTEGRATION_MODEL_API_KEY` | 大语言模型 API 密钥 | ✅ 必需 | 无 |
| `COZE_INTEGRATION_MODEL_BASE_URL` | 大语言模型 API 端点 | ❌ 可选 | `https://integration.coze.cn/api/v3` |
| `COZE_WORKSPACE_PATH` | 工作空间路径 | ❌ 可选 | 自动设置 |
| `COZE_BUCKET_ENDPOINT_URL` | 对象存储端点 | ❌ 可选 | `https://integration.coze.cn/coze-coding-s3proxy/v1` |
| `COZE_BUCKET_NAME` | 存储桶名称 | ❌ 可选 | `bucket_1767939698208` |

---

## 安全提示

⚠️ **重要**：

1. **不要提交 API Key 到 Git**
   - `.env` 文件已在 `.gitignore` 中配置
   - 确保不要手动添加到 Git

2. **定期更换 API Key**
   - 建议每 3-6 个月更换一次
   - 如果发现异常使用，立即更换

3. **妥善保管 API Key**
   - 不要分享给他人
   - 不要在不信任的环境中使用

4. **使用不同环境的不同 Key**
   - 开发环境和生产环境使用不同的 API Key
   - 便于追踪和管理

---

## 相关文档

- [Coze 平台文档](https://www.coze.cn/docs)
- [工作流使用指南](./README.md)
- [Coze 环境变量说明](./COZE_ENV_GUIDE.md)
- [GitHub 推送指南](./PUSH_GUIDE.md)

---

## 技术支持

如果遇到问题：

1. 检查 [常见问题](#常见问题)
2. 查看 [Coze 官方文档](https://www.coze.cn/docs)
3. 在项目 GitHub 提交 Issue
