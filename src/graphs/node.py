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

    # 如果是本地文件，上传到对象存储
    if os.path.isfile(path):
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
            print(f"⚠️ 上传对象存储失败: {str(e)}")
            # 如果上传失败，返回本地路径
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

            # 返回解压后的路径
            return UnzipOutput(extracted_path=temp_dir)
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise Exception(f"解压失败: {str(e)}")
    else:
        # 如果不是zip文件，直接返回原路径
        if os.path.isdir(path):
            return UnzipOutput(extracted_path=path)
        else:
            raise Exception(f"路径既不是zip文件也不是目录: {path}")


def analyze_structure_node(state: AnalyzeStructureInput, config: RunnableConfig, runtime: Runtime[Context]) -> AnalyzeStructureOutput:
    """
    title: 文件夹结构分析
    desc: 分析组件文件夹的层级结构，输出每个子文件夹的概括说明，特别关注include和src文件夹下的文件
    """

    component_path = state.extracted_path
    result = []

    def analyze_directory(path: str, indent: int = 0) -> List[str]:
        """递归分析目录结构"""
        lines = []
        prefix = "  " * indent

        try:
            items = sorted(os.listdir(path))
            for item in items:
                full_path = os.path.join(path, item)

                # 跳过隐藏文件
                if item.startswith('.'):
                    continue

                if os.path.isdir(full_path):
                    lines.append(f"{prefix}📁 {item}/")
                    sub_content = analyze_directory(full_path, indent + 1)
                    lines.extend(sub_content)
                elif os.path.isfile(full_path):
                    # 特别关注 .h 和 .c 文件
                    if item.endswith('.h') or item.endswith('.c'):
                        lines.append(f"{prefix}  📄 {item} - (需要详细说明)")
                    else:
                        lines.append(f"{prefix}  📄 {item}")
        except Exception as e:
            lines.append(f"{prefix}❌ 无法访问: {str(e)}")

        return lines

    # 开始分析
    if os.path.exists(component_path):
        lines = [f"组件路径: {component_path}", ""]
        lines.extend(analyze_directory(component_path))

        # 生成概括说明
        result = "\n".join(lines)
    else:
        result = f"❌ 组件路径不存在: {component_path}"

    return AnalyzeStructureOutput(folder_structure=result)


def extract_functions_node(state: ExtractFunctionsInput, config: RunnableConfig, runtime: Runtime[Context]) -> ExtractFunctionsOutput:
    """
    title: 头文件函数提取
    desc: 提取include文件夹下.h内部的所有函数，详细说明函数名称、功能、输入参数、返回值、调用示例
    """

    component_path = state.extracted_path
    include_path = os.path.join(component_path, "include")

    if not os.path.exists(include_path):
        return ExtractFunctionsOutput(header_functions=f"❌ include 文件夹不存在于 {component_path}")

    result = ["## 头文件函数详细说明\n"]

    # 遍历所有 .h 文件
    for root, dirs, files in os.walk(include_path):
        for file in files:
            if file.endswith('.h'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, component_path)

                result.append(f"### {relative_path}\n")

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # 提取函数定义（简化版，实际需要更复杂的解析）
                    # 匹配函数声明模式：返回类型 函数名(参数)
                    function_pattern = r'(?:[\w\s\*]+\s+)(\w+)\s*\(([^)]*)\)\s*(?:;|$)'
                    functions = re.findall(function_pattern, content, re.MULTILINE)

                    if functions:
                        for func_name, params in functions:
                            result.append(f"#### 函数: `{func_name}`\n")
                            result.append(f"- **函数名称**: `{func_name}`\n")
                            result.append(f"- **输入参数**: `{params if params.strip() else 'void'}`\n")
                            result.append(f"- **返回值**: 根据代码上下文推断\n")
                            result.append(f"- **调用示例**: `TODO: 根据使用情况补充`\n")
                            result.append("")
                    else:
                        result.append("*未找到函数定义*\n")

                    result.append("---\n")

                except Exception as e:
                    result.append(f"❌ 读取文件失败: {str(e)}\n")

    header_functions = "\n".join(result)
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
                        code_content.append(f"\n// File: {relative_path}\n{content[:2000]}\n")  # 限制长度避免过长
                except Exception as e:
                    code_content.append(f"\n// Error reading {file_path}: {str(e)}\n")

    all_code = "\n".join(code_content)

    # 使用jinja2模板渲染提示词
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render({"code_content": all_code[:10000]})

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
    desc: 整合所有分析结果，生成美化的README.md文档，使用不同等级的标题
    """

    # 使用大模型整合和美化内容
    readme_content = f"""# 组件文档

> 自动生成的组件文档

---

## 目录结构

{state.folder_structure}

---

## 头文件函数说明

{state.header_functions}

---

## 函数调用关系

{state.call_relationship}

---

## 处理流程图

{state.flow_diagrams}

---

*文档自动生成*
"""

    return GenerateReadmeOutput(readme_content=readme_content)
