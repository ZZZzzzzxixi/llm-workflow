import os
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import (
    GlobalState,
    GraphInput,
    GraphOutput,
    SaveReadmeInput,
    SaveReadmeOutput,
    UnzipInput,
    UnzipOutput,
    UploadLocalFileInput,
    UploadLocalFileOutput
)
from graphs.node import (
    upload_local_file_node,
    unzip_node,
    analyze_structure_node,
    extract_functions_node,
    analyze_call_relation_node,
    generate_flowchart_node,
    generate_readme_node
)
from utils.file.file import File

def save_readme_node(state: SaveReadmeInput, config: RunnableConfig, runtime: Runtime[Context]) -> SaveReadmeOutput:
    """
    title: 保存README文件
    desc: 将生成的README内容保存到对象存储并返回可访问的URL
    integrations: 对象存储
    """
    import hashlib
    from coze_coding_dev_sdk.s3 import S3SyncStorage

    # 生成唯一的文件名：README_前两段MD5.html（生成HTML格式）
    content_bytes = state.readme_content.encode('utf-8')
    md5_hash = hashlib.md5(content_bytes).hexdigest()
    file_prefix = f"{md5_hash[:8]}_{md5_hash[8:16]}"
    file_name = f"README_{file_prefix}.html"

    # 上传到对象存储
    storage = S3SyncStorage(
        endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
        access_key="",
        secret_key="",
        bucket_name=os.getenv("COZE_BUCKET_NAME"),
        region="cn-beijing",
    )

    try:
        # 上传文件内容（HTML格式，指定UTF-8编码，解决中文乱码问题）
        key = storage.upload_file(
            file_content=content_bytes,
            file_name=file_name,
            content_type="text/html; charset=utf-8",
        )

        # 生成签名URL（有效期30分钟）
        readme_url = storage.generate_presigned_url(key=key, expire_time=1800)

        return SaveReadmeOutput(readme_url=readme_url)
    except Exception as e:
        # 如果对象存储不可用，回退到本地文件
        readme_path = f"/tmp/README_{file_prefix}.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(state.readme_content)
        return SaveReadmeOutput(readme_url=f"local:{readme_path}")

# 创建状态图，指定图的入参和出参
builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

# 添加节点
builder.add_node("upload_local_file", upload_local_file_node)
builder.add_node("unzip", unzip_node)
builder.add_node("analyze_structure", analyze_structure_node)
builder.add_node("extract_functions", extract_functions_node, metadata={"type": "agent", "llm_cfg": "config/function_extract_llm_cfg.json"})
builder.add_node("analyze_call_relation", analyze_call_relation_node, metadata={"type": "agent", "llm_cfg": "config/call_analysis_llm_cfg.json"})
builder.add_node("generate_flowchart", generate_flowchart_node, metadata={"type": "agent", "llm_cfg": "config/flowchart_llm_cfg.json"})
builder.add_node("generate_readme", generate_readme_node)
builder.add_node("save_readme", save_readme_node)

# 设置入口点
builder.set_entry_point("upload_local_file")

# 添加边（线性流程）
builder.add_edge("upload_local_file", "unzip")
builder.add_edge("unzip", "analyze_structure")
builder.add_edge("analyze_structure", "extract_functions")
builder.add_edge("extract_functions", "analyze_call_relation")
builder.add_edge("analyze_call_relation", "generate_flowchart")
builder.add_edge("generate_flowchart", "generate_readme")
builder.add_edge("generate_readme", "save_readme")
builder.add_edge("save_readme", END)

# 编译图
main_graph = builder.compile()
