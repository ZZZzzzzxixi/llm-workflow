def generate_readme_node(state, config, runtime):
    """
    title: README生成
    desc: 整合所有分析结果，生成美化的HTML文档，使用HTML样式和组件名称
    """

    # 获取组件名称
    component_name = state.component_name if hasattr(state, 'component_name') and state.component_name else "组件"

    # 使用HTML样式美化，添加Mermaid.js支持
    readme_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{component_name}说明文档</title>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({{ startOnLoad: true }});
</script>
<style>
    body {{
        font-family: "Microsoft YaHei", "PingFang SC", "Hiragino Sans GB", Arial, sans-serif;
        line-height: 1.8;
        color: #333;
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f9f9f9;
    }}

    h1 {{
        text-align: center;
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 15px;
        margin-bottom: 30px;
        font-size: 2.5em;
    }}

    h2 {{
        color: #34495e;
        border-left: 5px solid #3498db;
        padding-left: 15px;
        margin-top: 40px;
        margin-bottom: 20px;
        background-color: white;
        padding: 10px 15px;
        border-radius: 5px;
        font-size: 1.8em;
    }}

    h3 {{
        color: #2980b9;
        margin-top: 30px;
        margin-bottom: 15px;
        font-size: 1.5em;
    }}

    h4 {{
        color: #1abc9c;
        margin-top: 20px;
        margin-bottom: 10px;
        font-size: 1.3em;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}

    th, td {{
        padding: 12px 15px;
        text-align: left;
        border: 1px solid #ddd;
    }}

    th {{
        background-color: #3498db;
        color: white;
        font-weight: bold;
        width: 30%;
    }}

    tr:nth-child(even) {{
        background-color: #f2f2f2;
    }}

    code {{
        background-color: #f4f4f4;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: "Courier New", monospace;
        font-size: 14px;
        color: #e74c3c;
    }}

    pre {{
        background-color: #282c34;
        color: #abb2bf;
        padding: 20px;
        border-radius: 8px;
        overflow-x: auto;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        font-size: 14px;
    }}

    pre code {{
        background-color: transparent;
        color: inherit;
        padding: 0;
    }}

    blockquote {{
        border-left:4px solid #3498db;
        padding-left: 20px;
        margin: 20px 0;
        color: #666;
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 5px;
    }}

    .info-box {{
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
        font-size: 16px;
    }}

    .mermaid {{
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }}

    hr {{
        border: none;
        border-top: 2px solid #3498db;
        margin: 40px 0;
    }}
</style>
</head>
<body>

<h1>{component_name} 说明文档</h1>

<div class="info-box">
    <strong>📄 说明：</strong>本文档由代码分析工具自动生成，包含组件的目录结构、函数接口、调用关系和流程图。
</div>

<hr>

<h2>📁 目录结构</h2>

{state.folder_structure}

<hr>

<h2>📋 头文件函数说明</h2>

{state.header_functions}

<hr>

<h2>🔗 函数调用关系</h2>

{state.call_relationship}

<hr>

<h2>📊 处理流程图</h2>

<div class="mermaid">
{state.flow_diagrams}
</div>

<hr>

<div style="text-align: center; color: #7f8c8d; margin-top: 50px; font-size: 14px;">
    <p>📅 文档生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>🤖 由AI代码分析工具自动生成</p>
</div>

</body>
</html>
"""

    return readme_content
