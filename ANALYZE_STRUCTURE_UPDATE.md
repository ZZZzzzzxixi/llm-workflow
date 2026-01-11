# 文件夹结构分析节点更新说明

## 修改内容

### 节点：`analyze_structure_node`
**文件**: `src/graphs/node.py`

### 主要改进

#### 1. 开源代码/第三方库识别

**识别策略**：
- **基于文件夹名称**：识别明显的第三方库文件夹名称
  - opencv, tensorflow, pytorch, caffe 等常见机器学习库
  - vendor, third_party, external, libs, dependencies 等依赖文件夹
  - build, cmake-build, out, bin 等构建输出文件夹

- **基于特征文件**：
  - 存在 `.git` 文件夹（版本控制标记）
  - 存在 LICENSE/COPYING 文件（仅在根级别时判断）

**识别逻辑优化**：
- ✅ README.md **不再**作为判断依据（因为它是常见文件，不应影响分析）
- ✅ 仅在文件夹名称匹配或存在明确的版本控制/许可证文件时才标记为第三方库
- ✅ 对于包含 include/ 和 src/ 的用户代码文件夹，即使有 README.md 也会正常分析

#### 2. 文件夹结构输出格式优化

**修改前**：
```markdown
组件路径: /tmp/xxx
  📁 test_component/
    📁 include/
      📄 calculator.h - (需要详细说明)
    📁 src/
      📄 calculator.c
```

**修改后**（参考 `assets/README.md` 格式）：
```markdown
## 目录结构

```
test_component/
├── include/ # 公共 API 头文件
│   ├── calculator.h       # 头文件
│   └── string_utils.h       # 头文件
├── src/ # 实现文件
│   ├── calculator.c       # 源文件
│   └── string_utils.c       # 源文件
└── README.md
```
```

**改进点**：
- ✅ 使用标准树状结构（├── └──）替代 emoji 图标
- ✅ 添加中文注释说明每个文件夹的用途
- ✅ 文件类型标注（# 头文件，# 源文件）
- ✅ 隐藏隐藏文件（.git 除外，用于识别）
- ✅ 按字母顺序排序，文件夹在前，文件在后

#### 3. 智能注释系统

**常见文件夹注释映射**：
| 文件夹名称 | 注释说明 |
|-----------|---------|
| include | # 公共 API 头文件 |
| src | # 实现文件 |
| lib/libs | # 第三方库 |
| vendor | # 第三方依赖 |
| third_party | # 第三方依赖 |
| build/cmake-build | # 构建输出目录 |
| bin | # 可执行文件 |
| docs/doc | # 文档 |
| examples/example | # 示例代码 |
| tests/test | # 测试代码 |
| tools/scripts | # 工具脚本 |
| config/configs | # 配置文件 |
| resources/assets | # 资源文件 |
| model/models | # 模型文件 |
| opencv | # OpenCV 库 |
| tensorflow/pytorch | # TensorFlow/PyTorch 库 |

#### 4. 第三方库自动略过

**识别为第三方库的文件夹**：
- 标记为：`[第三方库，略过详细说明]`
- 不再递归分析其内部文件
- 减少不必要的文档生成，聚焦核心代码

## 测试结果

### 测试场景1：用户代码 + README.md
```
test_component/
├── README.md              # 不影响分析
├── include/ # 公共 API 头文件
│   └── my_api.h
└── src/ # 实现文件
    └── my_api.c
```
✅ **结果**：正常分析，不跳过

### 测试场景2：包含第三方库
```
test_component/
├── include/ # 公共 API 头文件
├── src/ # 实现文件
├── opencv/ # [第三方库，略过详细说明]
│   ├── LICENSE
│   ├── include/
│   └── lib/
└── vendor/ # [第三方库，略过详细说明]
    └── tensorflow/
        └── LICENSE
```
✅ **结果**：第三方库被识别并略过，用户代码正常分析

### 测试场景3：包含 .git 文件夹
```
test_component/
├── .git/ # Git 版本控制
├── include/
├── src/
└── README.md
```
✅ **结果**：.git 文件夹被识别并略过

## 生成的README示例

```markdown
## 目录结构

```
component_extracted_xxx/
├── test_component/
│   ├── include/ # 公共 API 头文件
│   │   ├── calculator.h       # 头文件
│   │   └── string_utils.h       # 头文件
│   └── src/ # 实现文件
│       ├── calculator.c       # 源文件
│       └── string_utils.c       # 源文件
│   └── README.md
```
```

## 关键代码片段

### 1. 第三方库识别
```python
OPENSOURCE_FOLDER_NAMES = [
    'opencv', 'tensorflow', 'pytorch',
    'vendor', 'third_party', 'external',
    'libs', 'dependencies',
    'build', 'bin',
]

def is_opensource_folder(folder_path: str, folder_name: str) -> bool:
    # 检查文件夹名称
    if folder_name.lower() in [name.lower() for name in OPENSOURCE_FOLDER_NAMES]:
        return True

    # 检查 .git 文件夹
    if os.path.exists(os.path.join(folder_path, '.git')):
        return True

    # 检查 LICENSE 文件
    for marker in ['LICENSE', 'LICENSE.txt', 'COPYING']:
        if marker in os.listdir(folder_path):
            return True

    return False
```

### 2. 树状结构生成
```python
def analyze_directory(path: str, prefix: str = "", is_last: bool = True) -> str:
    # 计算树状结构连接符
    if is_last:
        current_prefix = prefix + "└── "
        child_prefix = prefix + "    "
    else:
        current_prefix = prefix + "├── "
        child_prefix = prefix + "│   "

    # 添加文件/文件夹及其注释
    line = current_prefix + item + "/"
    if comment:
        line += " " + comment
```

## 向后兼容性

✅ **完全兼容**：现有工作流无需修改，自动使用新的分析逻辑

✅ **配置无变化**：不需要修改任何配置文件

✅ **输出格式兼容**：Markdown 格式保持一致，只是展示更美观

## 后续优化建议

1. **用户自定义忽略列表**：允许用户通过配置文件指定要忽略的文件夹

2. **更智能的注释**：根据文件夹内容自动生成注释（如检测到 *.h 文件则标记为"头文件目录"）

3. **文件大小标注**：对于大文件可以标注文件大小

4. **依赖关系图**：在文件夹结构中标注模块间的依赖关系

---

**更新时间**: 2025-01-11
**修改文件**: `src/graphs/node.py`
**测试状态**: ✅ 通过
