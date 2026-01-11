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
    desc: 将生成的README内容保存到本地文件
    """

    # 保存到本地临时目录
    readme_path = "/tmp/README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(state.readme_content)

    # TODO: 如果需要上传到对象存储，可以在这里实现
    # 返回文件路径（本地环境）或URL（部署环境）
    return SaveReadmeOutput(readme_url=readme_path)

# 创建状态图，指定图的入参和出参
builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

# 添加节点
builder.add_node("upload_local_file", upload_local_file_node)
builder.add_node("unzip", unzip_node)
builder.add_node("analyze_structure", analyze_structure_node)
builder.add_node("extract_functions", extract_functions_node)
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
