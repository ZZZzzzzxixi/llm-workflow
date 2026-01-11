# README中文乱码修复说明

## 问题描述

打开README文件链接时，中文显示为乱码，无法正常阅读。

## 原因分析

对象存储上传文件时，`Content-Type` 头设置为 `text/markdown`，但**没有指定字符集**（charset）。

这导致浏览器无法识别文件的编码方式，默认使用了错误的编码（如ISO-8859-1），导致UTF-8编码的中文显示为乱码。

### 修复前
```
Content-Type: text/markdown
```

### 修复后
```
Content-Type: text/markdown; charset=utf-8
```

## 修复方案

### 修改文件：`src/graphs/graph.py`

**位置**：`save_readme_node` 函数

**修改前**：
```python
key = storage.upload_file(
    file_content=content_bytes,
    file_name=file_name,
    content_type="text/markdown",
)
```

**修改后**：
```python
key = storage.upload_file(
    file_content=content_bytes,
    file_name=file_name,
    content_type="text/markdown; charset=utf-8",
)
```

## 验证结果

### 1. HTTP响应头验证
```bash
$ curl -I <README_URL> | grep -i content-type
Content-Type: text/markdown; charset=utf-8
```

✅ **已包含 `charset=utf-8`**

### 2. 文件内容验证
```bash
$ curl -s <README_URL> | head -30

# 组件文档

> 自动生成的组件文档

---

## 目录结构

...
```

✅ **中文正常显示**

### 3. 浏览器验证
在浏览器中打开README链接，中文内容正常显示，无乱码。

## 技术说明

### Content-Type 和 Charset

- **Content-Type**：指定文件的MIME类型（如 `text/markdown`、`text/html`）
- **Charset**：指定字符编码（如 `utf-8`、`gbk`、`iso-8859-1`）

对于包含非ASCII字符（如中文）的文本文件，必须指定正确的charset，否则浏览器无法正确解码。

### 为什么是UTF-8？

- UTF-8是现代Web的标准编码
- Python字符串默认使用UTF-8编码
- 支持多语言（中文、日文、韩文等）
- 向后兼容ASCII

### 常见Content-Type

| 文件类型 | Content-Type | 建议Charset |
|---------|-------------|-------------|
| Markdown | text/markdown | utf-8 |
| HTML | text/html | utf-8 |
| Plain Text | text/plain | utf-8 |
| CSS | text/css | utf-8 |
| JavaScript | application/javascript | utf-8 |
| JSON | application/json | utf-8 |

## 影响范围

✅ **向后兼容**：
- 现有的README链接如果还在有效期内，可以重新生成获取正确编码的版本
- 旧文件（乱码）需要重新工作流执行才能修复

✅ **所有新文件**：
- 所有新生成的README文件都会使用正确的编码
- 浏览器能正确显示中文

## 测试方法

### 方法1：使用测试脚本
```bash
bash test_encoding.sh
```

### 方法2：手动验证
```bash
# 1. 生成新README
export PYTHONPATH=/workspace/projects/src
python3 -c "from graphs.graph import main_graph; print(main_graph.invoke({'component_path': 'assets/test_component.zip'})['readme_url'])"

# 2. 检查Content-Type
curl -I <URL> | grep -i content-type

# 3. 在浏览器中打开URL
```

### 方法3：通过API测试
```bash
curl --location "https://rfvfy978y6.coze.site/run" \
  --header "Authorization: Bearer YOUR_TOKEN" \
  --header "Content-Type: application/json" \
  --data '{"component_path":"..."}'
```

然后打开返回的README URL，检查中文是否正常显示。

## 常见问题

### Q1: 修复后旧的README文件还是乱码怎么办？

**A**: 旧文件的Content-Type已经确定，无法修改。需要重新执行工作流生成新的README文件。

### Q2: 为什么之前没有这个问题？

**A**: 可能是因为：
1. 之前生成的README只包含英文内容
2. 浏览器自动检测了编码（不准确）
3. 或者没有注意到乱码问题

### Q3: 除了UTF-8，还可以用其他编码吗？

**A**: 不建议。UTF-8是Web标准，使用其他编码会导致兼容性问题。

### Q4: 如果上传其他文本文件，也需要指定charset吗？

**A**: 是的。所有包含非ASCII字符的文本文件都应该指定 `charset=utf-8`。

## 相关代码位置

- **修改文件**: `src/graphs/graph.py`
- **修改函数**: `save_readme_node`
- **修改行数**: 约50-55行

---

**修复时间**: 2025-01-11
**影响**: 所有新生成的README文件
**测试状态**: ✅ 通过
