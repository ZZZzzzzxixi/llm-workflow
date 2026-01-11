# Coze API Key 和 Space ID 说明

## 重要提示

**你不需要手动配置这两个环境变量！**

## 原因说明

### 1. 自动注入机制
在 Coze 平台部署时，这些环境变量会**自动注入**到运行环境中：

```python
# 代码中自动获取（无需手动配置）
from coze_coding_dev_sdk import LLMClient
from coze_workload_identity import Client

# SDK 内部会自动处理 API Key 和认证
client = LLMClient(ctx=ctx)

# 对象存储 SDK 也会自动获取端点
storage = S3SyncStorage(
    endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),  # 自动注入
    access_key="",
    secret_key="",
    bucket_name=os.getenv("COZE_BUCKET_NAME"),  # 自动注入
    region="cn-beijing",
)
```

### 2. 本地运行模式
本地运行时：
- ❌ 不需要 `COZE_API_KEY`
- ❌ 不需要 `COZE_SPACE_ID`
- ❌ 不需要 `COZE_BUCKET_ENDPOINT_URL`
- ✅ 直接运行即可：`bash run_local.sh "/path/to/file.zip"`

### 3. Coze 部署模式
部署到 Coze 平台时：
- ✅ 平台自动注入所有必需的环境变量
- ✅ SDK 会自动读取并使用这些变量
- ✅ 无需手动配置

---

## 如果确实需要查看（仅限调试）

⚠️ **注意**：通常不需要手动配置这些值。如果确实需要查看，可以通过以下方式：

### 方法一：在 Coze 控制台查看

1. 访问 [Coze 工作台](https://www.coze.cn/workspace)
2. 选择你的项目/工作空间
3. 进入项目设置 → 环境变量
4. 查看或添加自定义环境变量

### 方法二：使用 Coze CLI（如果可用）

```bash
# 列出项目环境变量
coze env list

# 查看特定变量
coze env get COZE_API_KEY
coze env get COZE_SPACE_ID
```

### 方法三：运行时打印（调试用）

在代码中添加调试输出：

```python
import os

# 调试：打印所有 Coze 相关环境变量
coze_vars = {k: v for k, v in os.environ.items() if 'COZE' in k}
for key, value in coze_vars.items():
    print(f"{key}={value[:10]}..." if len(value) > 10 else f"{key}={value}")
```

---

## 常见 Coze 环境变量

| 环境变量 | 说明 | 是否必需 | 来源 |
|---------|------|---------|------|
| `COZE_API_KEY` | API 认证密钥 | 自动注入 | Coze 平台 |
| `COZE_SPACE_ID` | 工作空间 ID | 自动注入 | Coze 平台 |
| `COZE_WORKSPACE_PATH` | 工作空间路径 | 自动注入 | Coze 平台 |
| `COZE_BUCKET_ENDPOINT_URL` | 对象存储端点 | 自动注入 | Coze 平台 |
| `COZE_BUCKET_NAME` | 存储桶名称 | 自动注入 | Coze 平台 |

---

## 使用 SDK 的正确方式

### ✅ 正确：使用 SDK 自动处理

```python
from coze_coding_dev_sdk import LLMClient
from coze_workload_identity import Client

# SDK 内部会自动获取 API Key
client = LLMClient(ctx=ctx)

response = client.invoke(messages=messages)
```

### ❌ 错误：手动设置环境变量

```python
# 不需要这样做！SDK 会自动处理
import os
os.environ['COZE_API_KEY'] = '手动设置的key'  # ❌ 错误
```

---

## 总结

1. **本地运行**：不需要任何环境变量，直接运行
2. **Coze 部署**：平台自动注入所有必需变量
3. **SDK 使用**：通过 `coze_workload_identity.Client` 自动获取
4. **无需手动配置**：代码已做好自动处理

---

## 相关文档

- [Coze 官方文档](https://www.coze.cn/docs)
- [LLM 集成文档](../integration_docs/llm_integration.md)
- [对象存储集成文档](../integration_docs/s3_integration.md)
