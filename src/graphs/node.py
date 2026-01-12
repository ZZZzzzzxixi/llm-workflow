import os
import re
import zipfile
import shutil
from typing import List, Dict, Any
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import (
    AnalyzeStructureInput,
    AnalyzeStructureOutput,
    ExtractFunctionsInput,
    ExtractFunctionsOutput,
    AnalyzeCallRelationInput,
    AnalyzeCallRelationOutput,
    GenerateFlowchartInput,
    GenerateFlowchartOutput,
    GenerateReadmeInput,
    GenerateReadmeOutput,
    UnzipInput,
    UnzipOutput,
    UploadLocalFileInput,
    UploadLocalFileOutput,
)
import json
from jinja2 import Template


def upload_local_file_node(state: UploadLocalFileInput, config: RunnableConfig, runtime: Runtime[Context]) -> UploadLocalFileOutput:
    """
    title: 上传本地文件
    desc: 如果是本地文件路径，上传到对象存储；如果是URL或目录，直接返回
    integrations: 对象存储
    """

    path = state.component_path.strip()  # 去除前后空格

    # 检测Windows路径格式（D:/ 或 C:\ 等）
    if re.match(r'^[A-Za-z]:[/\\]', path):
        error_msg = f"""
❌ 检测到Windows路径格式，无法在Linux环境中访问！
路径: {path}

解决方案：
1. 如果在WSL中，请使用Linux路径格式：
   Windows: D:/wsl-file-sharing/file.zip
   WSL路径: /mnt/d/wsl-file-sharing/file.zip

2. 如果文件在Windows上，请：
   - 复制文件到Linux可访问的目录
   - 或使用对象存储URL

3. 如果使用WSL，正确的路径应该是：
   /mnt/d/wsl-file-sharing/newbridge/robotics_svc_media.zip
        """
        raise Exception(error_msg.strip())

    # 如果是URL，直接返回
    if path.startswith('http://') or path.startswith('https://'):
        return UploadLocalFileOutput(zip_file_path=path)

    # 如果是目录，直接返回
    if os.path.isdir(path):
        return UploadLocalFileOutput(zip_file_path=path)

    # 如果是本地文件，上传到对象存储（仅在Coze环境中）
    if os.path.isfile(path):
        # 检查是否在Coze环境中（通过环境变量判断）
        in_coze_env = os.getenv('COZE_WORKSPACE_PATH') and (
            os.getenv('COZE_BUCKET_ENDPOINT_URL') or os.getenv('COZE_BUCKET_NAME')
        )

        if in_coze_env:
            try:
                from coze_coding_dev_sdk.s3 import S3SyncStorage
                import os as env_os

                # 初始化对象存储
                storage = S3SyncStorage(
                    endpoint_url=env_os.getenv("COZE_BUCKET_ENDPOINT_URL"),
                    access_key="",
                    secret_key="",
                    bucket_name=env_os.getenv("COZE_BUCKET_NAME"),
                    region="cn-beijing",
                )

                # 读取文件
                filename = os.path.basename(path)
                with open(path, 'rb') as f:
                    file_content = f.read()

                # 上传到对象存储
                file_key = storage.upload_file(
                    file_content=file_content,
                    file_name=filename,
                    content_type="application/zip" if filename.endswith('.zip') else "application/octet-stream",
                )

                # 生成下载URL
                download_url = storage.generate_presigned_url(key=file_key, expire_time=3600)

                print(f"✅ 文件已上传到对象存储: {file_key}")
                print(f"📥 下载URL: {download_url}")

                return UploadLocalFileOutput(zip_file_path=download_url)

            except Exception as e:
                print(f"⚠️ 上传对象存储失败，将使用本地路径: {str(e)}")
                # 如果上传失败，返回本地路径
                return UploadLocalFileOutput(zip_file_path=path)
        else:
            # 本地环境，直接使用本地路径
            print(f"📁 本地运行模式，使用本地文件路径: {path}")
            return UploadLocalFileOutput(zip_file_path=path)

    raise Exception(f"❌ 路径无效或文件不存在: {path}\n\n请检查：\n1. 路径是否正确\n2. 文件是否存在\n3. 是否使用了Windows路径格式（应使用Linux路径）")


def unzip_node(state: UnzipInput, config: RunnableConfig, runtime: Runtime[Context]) -> UnzipOutput:
    """
    title: 解压缩文件
    desc: 如果输入是zip文件，则解压到临时目录；如果是文件夹，直接返回
    """

    path = state.zip_file_path

    # 判断是否是URL
    is_url = path.startswith('http://') or path.startswith('https://')

    # 判断是否是zip文件（对于URL，检查路径部分）
    if is_url or path.endswith('.zip') or path.endswith('.ZIP'):
        # 如果是URL，先下载到临时文件
        if is_url:
            from urllib.parse import urlparse
            import tempfile

            # 解析URL获取文件名
            parsed_url = urlparse(path)
            filename = os.path.basename(parsed_url.path)

            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            temp_file.close()

            try:
                import requests
                response = requests.get(path, timeout=120)
                response.raise_for_status()

                with open(temp_file.name, 'wb') as f:
                    f.write(response.content)

                print(f"已下载到: {temp_file.name}")
                path = temp_file.name
            except Exception as e:
                os.unlink(temp_file.name)
                raise Exception(f"下载失败: {str(e)}")

        # 创建临时解压目录
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix="component_extracted_")

        try:
            with zipfile.ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            print(f"已解压到: {temp_dir}")

            # 如果是下载的临时文件，删除它
            if is_url and 'temp_file' in locals():
                os.unlink(temp_file.name)

            # 提取组件名称（从解压后的第一个子文件夹）
            component_name = "Unknown"
            try:
                items = os.listdir(temp_dir)
                if items:
                    # 获取第一个文件夹作为组件名称
                    first_item = items[0]
                    if os.path.isdir(os.path.join(temp_dir, first_item)):
                        component_name = first_item
            except Exception:
                component_name = "Component"

            print(f"组件名称: {component_name}")

            # 返回解压后的路径和组件名称
            return UnzipOutput(extracted_path=temp_dir, component_name=component_name)
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise Exception(f"解压失败: {str(e)}")
    else:
        # 如果不是zip文件，直接返回原路径
        if os.path.isdir(path):
            # 提取组件名称
            component_name = os.path.basename(path.rstrip('/'))
            print(f"组件名称: {component_name}")
            return UnzipOutput(extracted_path=path, component_name=component_name)
        else:
            raise Exception(f"路径既不是zip文件也不是目录: {path}")


def analyze_structure_node(state: AnalyzeStructureInput, config: RunnableConfig, runtime: Runtime[Context]) -> AnalyzeStructureOutput:
    """
    title: 文件夹结构分析
    desc: 分析组件文件夹的层级结构，识别开源代码库，输出树状结构
    """

    component_path = state.extracted_path

    # 明确的第三方库/开源代码文件夹名称
    OPENSOURCE_FOLDER_NAMES = [
        'opencv', 'opencv_contrib', 'opencv_extra',
        'tensorflow', 'tensorflow_cc', 'tensorflow_lite',
        'pytorch', 'torch', 'caffe', 'mxnet',
        'vendor', 'vendors', 'third_party', '3rdparty', 'external',
        'libs', 'lib', 'dependencies', 'deps',
        'build', 'cmake-build', 'out', 'bin',
    ]

    # 可能表示第三方库的特征文件（仅在根级别时才认为是开源库）
    OPENSOURCE_MARKERS = [
        '.git',
    ]

    def is_opensource_folder(folder_path: str, folder_name: str) -> bool:
        """检查是否为开源代码库文件夹"""
        if not os.path.isdir(folder_path):
            return False

        # 检查文件夹名称是否匹配已知的第三方库名称
        if folder_name.lower() in [name.lower() for name in OPENSOURCE_FOLDER_NAMES]:
            return True

        # 检查是否存在.git文件夹（明确的版本控制标记）
        git_folder = os.path.join(folder_path, '.git')
        if os.path.exists(git_folder) and os.path.isdir(git_folder):
            return True

        # 检查是否存在 LICENSE 文件（仅当根目录有此文件时才认为是开源库）
        # 注意：README.md 很常见，不应该作为判断依据
        license_markers = ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'LICENSE.MIT',
                          'COPYING', 'COPYRIGHT']
        items = os.listdir(folder_path)
        for marker in license_markers:
            if marker in items:
                return True

        return False

    def get_folder_comment(folder_name: str, path: str) -> str:
        """根据文件夹名称生成注释说明"""
        folder_lower = folder_name.lower()

        # 常见文件夹的注释
        comments = {
            'include': '# 公共 API 头文件',
            'src': '# 实现文件',
            'lib': '# 第三方库',
            'libs': '# 第三方库',
            'vendor': '# 第三方依赖',
            'third_party': '# 第三方依赖',
            'build': '# 构建输出目录',
            'cmake-build': '# CMake 构建输出',
            'output': '# 输出目录',
            'bin': '# 可执行文件',
            'docs': '# 文档',
            'doc': '# 文档',
            'examples': '# 示例代码',
            'example': '# 示例代码',
            'tests': '# 测试代码',
            'test': '# 测试代码',
            'tools': '# 工具脚本',
            'scripts': '# 脚本文件',
            'config': '# 配置文件',
            'configs': '# 配置文件',
            'resources': '# 资源文件',
            'assets': '# 资源文件',
            'model': '# 模型文件',
            'models': '# 模型文件',
            'data': '# 数据文件',
            'input': '# 输入数据',
            'output': '# 输出数据',
            'opencv': '# OpenCV 库',
            'tensorflow': '# TensorFlow 库',
            'pytorch': '# PyTorch 库',
            'torch': '# PyTorch 库',
            '.git': '# Git 版本控制',
            'github': '# GitHub 相关文件',
        }

        return comments.get(folder_lower, '')

    def analyze_directory(path: str, prefix: str = "", is_last: bool = True) -> str:
        """递归分析目录结构，生成树状结构"""
        lines = []

        try:
            items = sorted(os.listdir(path))

            # 分离文件夹和文件
            dirs = []
            files = []
            for item in items:
                full_path = os.path.join(path, item)

                # 跳过隐藏文件（.git, .gitignore 等除外，用于识别开源代码）
                if item.startswith('.') and item not in ['.git', '.gitignore', '.gitmodules']:
                    continue

                if os.path.isdir(full_path):
                    dirs.append(item)
                else:
                    files.append(item)

            # 合并排序，文件夹在前
            all_items = dirs + files
            total = len(all_items)

            for idx, item in enumerate(all_items):
                full_path = os.path.join(path, item)
                is_last_item = (idx == total - 1)

                # 计算当前行的前缀和子项的前缀
                if is_last:
                    current_prefix = prefix + "└── "
                    child_prefix = prefix + "    "
                else:
                    current_prefix = prefix + "├── "
                    child_prefix = prefix + "│   "

                if os.path.isdir(full_path):
                    # 检查是否为开源代码库
                    if is_opensource_folder(full_path, item):
                        comment = "# [第三方库，略过详细说明]"
                    else:
                        comment = get_folder_comment(item, full_path)

                    base_text = current_prefix + item + "/"
                    if comment:
                        # 计算对齐空格数，目标对齐到第40列
                        current_length = len(base_text)
                        target_column = 40
                        spaces = max(target_column - current_length, 1)
                        line = base_text + " " * spaces + comment
                    else:
                        line = base_text
                    lines.append(line)

                    # 递归分析子文件夹（第三方库不再深入）
                    if not is_opensource_folder(full_path, item):
                        sub_content = analyze_directory(full_path, child_prefix, is_last_item)
                        if sub_content:
                            lines.append(sub_content)
                else:
                    # 文件处理
                    # 特别关注 .h 和 .c/.cpp 文件
                    if item.endswith('.h') or item.endswith('.hpp'):
                        base_text = current_prefix + item
                        comment = "# 头文件"
                    elif item.endswith('.c') or item.endswith('.cpp') or item.endswith('.cc'):
                        base_text = current_prefix + item
                        comment = "# 源文件"
                    else:
                        base_text = current_prefix + item
                        comment = ""

                    # 计算对齐空格数，目标对齐到第40列
                    if comment:
                        current_length = len(base_text)
                        target_column = 40
                        spaces = max(target_column - current_length, 1)
                        line = base_text + " " * spaces + comment
                    else:
                        line = base_text
                    lines.append(line)

        except Exception as e:
            lines.append(f"{prefix}❌ 无法访问: {str(e)}")

        return "\n".join(lines)

    # 开始分析
    if os.path.exists(component_path):
        # 获取根目录名称
        root_name = os.path.basename(component_path.rstrip('/'))

        result_lines = []
        result_lines.append("## 目录结构")
        result_lines.append("")
        result_lines.append("```")
        result_lines.append(f"{root_name}/")
        result_lines.append(analyze_directory(component_path, "", False))
        result_lines.append("```")
        result_lines.append("")

        folder_structure = "\n".join(result_lines)
    else:
        folder_structure = f"❌ 组件路径不存在: {component_path}"

    return AnalyzeStructureOutput(folder_structure=folder_structure)


def extract_functions_node(state: ExtractFunctionsInput, config: RunnableConfig, runtime: Runtime[Context]) -> ExtractFunctionsOutput:
    """
    title: 头文件函数提取
    desc: 提取include文件夹下.h内部的所有函数，结合头文件注释和大模型分析，详细说明函数功能、输入参数、返回值、调用示例
    integrations: 大语言模型
    """

    component_path = state.extracted_path
    component_name = state.component_name
    ctx = runtime.context

    # 查找 include 文件夹（支持多层嵌套）
    include_path = None
    for root, dirs, files in os.walk(component_path):
        if 'include' in dirs:
            include_path = os.path.join(root, 'include')
            break

    if not include_path or not os.path.exists(include_path):
        return ExtractFunctionsOutput(header_functions=f"❌ 未找到 include 文件夹于 {component_path}")

    # 收集所有头文件和源文件内容
    header_content = []
    source_content = []

    include_parent = os.path.dirname(include_path)
    for root, dirs, files in os.walk(component_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, component_path)

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                if file.endswith('.h'):
                    header_content.append(f"\n// File: {relative_path}\n{content}\n")
                elif file.endswith('.c') or file.endswith('.cpp'):
                    source_content.append(f"\n// File: {relative_path}\n{content}\n")
            except Exception as e:
                pass

    # 使用大模型分析函数
    all_code = "\n".join(header_content + source_content)

    # 读取配置文件
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r') as fd:
        _cfg = json.load(fd)

    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")

    # 构建系统提示词
    system_prompt = """你是C语言代码分析专家，负责分析头文件中的函数定义。

请按照以下格式输出函数说明，使用Markdown格式：

```markdown
### 配置相关

#### `config_function_name()`
获取或设置配置参数。

**参数：**
- `param1`: 参数1说明
- `param2`: 参数2说明（可选）

**返回值：** 返回值说明

**示例：**
```c
// 示例代码
config_type config = config_function_name();
```

### 初始化与清理

#### `init_function_name()`
初始化组件。

**参数：**
- `param1`: 参数1说明

**返回值：** 0 成功，负数表示失败

**示例：**
```c
if (init_function_name(param) != 0) {
    printf("Init failed\\n");
}
```

### 核心功能

#### `process_function_name()`
执行核心处理逻辑。

**参数：**
- `input`: 输入数据
- `output`: 输出缓冲区

**返回值：** 处理结果状态码

**示例：**
```c
result = process_function_name(input, output);
```
```

注意事项：
1. **优先从include文件夹下的公共API头文件中提取函数声明和注释说明**
2. 结合头文件中的已有注释和大模型分析，生成完整的函数说明
3. 如果头文件中已有详细的注释说明，尽量保留原文含义
4. 将函数按照功能分类（如：配置相关、初始化与清理、核心功能、辅助功能等）
5. 每个分类使用三级标题（###）
6. 每个函数使用四级标题（#### `function_name()`）
7. 功能描述简洁明了，一句话说明
8. 参数使用列表格式（**参数名称**: 说明）
9. 返回值清晰说明（成功/失败及具体含义）
10. 示例代码必须真实，从源代码中提取实际调用
11. 只分析include文件夹下的头文件及其对应的实现
"""

    user_prompt = f"""请分析以下C代码的函数定义，并生成详细的函数说明文档：

{all_code[:15000]}
"""

    # 调用大模型
    from coze_coding_dev_sdk import LLMClient
    from langchain_core.messages import SystemMessage, HumanMessage

    client = LLMClient(ctx=ctx)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    response = client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-1-6-251015"),
        temperature=llm_config.get("temperature", 0.3),
        top_p=llm_config.get("top_p", 0.7),
        max_tokens=llm_config.get("max_tokens", 3000),
        frequency_penalty=llm_config.get("frequency_penalty", 0)
    )

    header_functions = response.content
    return ExtractFunctionsOutput(header_functions=header_functions)


def analyze_call_relation_node(state: AnalyzeCallRelationInput, config: RunnableConfig, runtime: Runtime[Context]) -> AnalyzeCallRelationOutput:
    """
    title: 函数调用关系分析
    desc: 分析代码中函数调用的层级关系，输出组件的处理流程
    integrations: 大语言模型
    """

    from coze_coding_dev_sdk import LLMClient
    from langchain_core.messages import SystemMessage, HumanMessage

    component_path = state.extracted_path
    ctx = runtime.context

    # 读取配置文件
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r') as fd:
        _cfg = json.load(fd)

    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")

    # 收集所有代码文件内容
    code_content = []
    for root, dirs, files in os.walk(component_path):
        for file in files:
            if file.endswith('.c') or file.endswith('.h'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        relative_path = os.path.relpath(file_path, component_path)
                        # 增加代码长度限制，以便更全面地分析线程函数内容
                        code_content.append(f"\n// File: {relative_path}\n{content[:5000]}\n")
                except Exception as e:
                    code_content.append(f"\n// Error reading {file_path}: {str(e)}\n")

    all_code = "\n".join(code_content)

    # 使用jinja2模板渲染提示词
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render({"code_content": all_code[:30000]})

    # 调用大模型分析函数调用关系
    from coze_coding_dev_sdk import LLMClient
    from langchain_core.messages import SystemMessage, HumanMessage

    client = LLMClient(ctx=ctx)
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt_content)
    ]

    response = client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-1-6-251015"),
        temperature=llm_config.get("temperature", 0.3),
        top_p=llm_config.get("top_p", 0.7),
        max_tokens=llm_config.get("max_tokens", 2000),
        frequency_penalty=llm_config.get("frequency_penalty", 0)
    )

    call_relationship = response.content

    return AnalyzeCallRelationOutput(call_relationship=call_relationship)


def generate_flowchart_node(state: GenerateFlowchartInput, config: RunnableConfig, runtime: Runtime[Context]) -> GenerateFlowchartOutput:
    """
    title: 流程图生成
    desc: 根据函数调用关系生成清晰的流程图（Mermaid格式），可拆分为多个小流程图
    integrations: 大语言模型
    """

    from coze_coding_dev_sdk import LLMClient
    from langchain_core.messages import SystemMessage, HumanMessage

    ctx = runtime.context

    # 读取配置文件
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r') as fd:
        _cfg = json.load(fd)

    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")

    # 使用jinja2模板渲染提示词
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render({"call_relationship": state.call_relationship})

    # 调用大模型生成流程图
    client = LLMClient(ctx=ctx)
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt_content)
    ]

    response = client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-1-6-251015"),
        temperature=llm_config.get("temperature", 0.3),
        top_p=llm_config.get("top_p", 0.7),
        max_tokens=llm_config.get("max_tokens", 2000),
        frequency_penalty=llm_config.get("frequency_penalty", 0)
    )

    flow_diagrams = response.content

    return GenerateFlowchartOutput(flow_diagrams=flow_diagrams)


def generate_readme_node(state: GenerateReadmeInput, config: RunnableConfig, runtime: Runtime[Context]) -> GenerateReadmeOutput:
    """
    title: README生成
    desc: 整合所有分析结果，生成美化的Markdown格式README.md文档
    """

    # 获取组件名称
    component_name = state.component_name if hasattr(state, 'component_name') and state.component_name else "组件"

    # 处理文件夹结构，替换临时目录名为组件名称
    folder_structure = state.folder_structure
    # 替换临时目录名（如component_extracted_xxxxxx）为组件名称
    import re
    temp_dir_pattern = r'component_extracted_[a-zA-Z0-9_]+'
    folder_structure = re.sub(temp_dir_pattern, component_name, folder_structure)

    # 从文件夹结构中提取主要模块
    def extract_main_modules(folder_structure):
        """从文件夹结构中提取主要模块"""
        modules = []
        # 查找常见的目录名称
        common_dirs = [
            r'(\w+)/\s*#\s*(公共|API|头文件)',
            r'(\w+)/\s*#\s*(实现|源文件)',
            r'(\w+)/\s*#\s*(第三方|vendor|依赖)',
            r'(\w+)/\s*#\s*(模型|model)',
            r'(\w+)/\s*#\s*(数据|data)',
            r'(\w+)/\s*#\s*(工具|tool)',
            r'(\w+)/\s*#\s*(文档|doc)',
            r'(\w+)/\s*#\s*(测试|test)',
        ]
        for pattern in common_dirs:
            matches = re.findall(pattern, folder_structure)
            for match in matches:
                if isinstance(match, tuple):
                    modules.append(match[0])
                else:
                    modules.append(match)
        # 去重并返回前5个
        return list(set(modules))[:5]

    main_modules = extract_main_modules(folder_structure)

    # 从函数调用关系中提取关键功能
    def extract_key_functions(call_relationship):
        """从函数调用关系中提取关键功能"""
        key_functions = []
        # 查找关键阶段
        patterns = [
            r'初始化.*?[:：](.*?)(?:\n|$)',
            r'视频.*?[:：](.*?)(?:\n|$)',
            r'音频.*?[:：](.*?)(?:\n|$)',
            r'采样线程.*?[:：](.*?)(?:\n|$)',
            r'检测线程.*?[:：](.*?)(?:\n|$)',
            r'object_detector.*?[:：](.*?)(?:\n|$)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, call_relationship, re.MULTILINE)
            for match in matches:
                if match and len(match) > 0:
                    clean_match = match.strip()[:50]  # 限制长度
                    if clean_match:
                        key_functions.append(clean_match)
        # 去重并返回前5个
        return list(set(key_functions))[:5]

    key_functions = extract_key_functions(state.call_relationship)

    # 从流程图中提取主要流程
    def extract_main_flow(flow_diagrams):
        """从流程图中提取主要流程"""
        flows = []
        # 查找主要节点
        patterns = [
            r'\[([^]]+初始化[^]]*)\]',
            r'\[([^]]+线程[^]]*)\]',
            r'\[([^]]+处理[^]]*)\]',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, flow_diagrams)
            for match in matches:
                if match:
                    flows.append(match[:30])  # 限制长度
        # 去重并返回前5个
        return list(set(flows))[:5]

    main_flows = extract_main_flow(state.flow_diagrams)

    # 生成简介
    introduction = f"""{component_name}模块是一个基于C语言开发的组件，本文档由代码分析工具自动生成。

### 功能概述
本组件提供了完整的C语言API接口，主要功能包括："""

    # 添加关键功能
    if key_functions:
        for func in key_functions:
            introduction += f"\n- {func}"
    else:
        introduction += "\n- 核心功能处理"
        introduction += "\n- 模块化接口设计"

    # 添加主要模块
    if main_modules:
        introduction += "\n\n### 主要模块\n本组件包含以下主要模块："
        for module in main_modules:
            introduction += f"\n- `{module}`"

    # 添加主要流程
    if main_flows:
        introduction += "\n\n### 核心流程\n组件的主要处理流程包括："
        for flow in main_flows:
            introduction += f"\n- {flow}"

    introduction += f"""

本文档详细介绍了组件的目录结构、API接口、函数调用关系和执行流程，帮助开发者快速理解和使用该组件。"""

    # 使用美化的Markdown格式，参考附件格式
    readme_content = f"""# {component_name} 模块

## 简介

{introduction}

## 目录结构

{folder_structure}

## API 参考

{state.header_functions}

## 函数调用关系

{state.call_relationship}

## 处理流程图

```mermaid
{state.flow_diagrams}
```

---

*文档生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return GenerateReadmeOutput(readme_content=readme_content)
