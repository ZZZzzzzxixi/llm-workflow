from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from utils.file.file import File

# 全局状态定义
class GlobalState(BaseModel):
    """全局状态定义"""
    component_path: str = Field(default="", description="组件文件夹路径或zip文件路径")
    component_name: str = Field(default="", description="组件名称（文件夹名称）")
    zip_file_path: str = Field(default="", description="zip文件路径（可能是URL或本地路径）")
    extracted_path: str = Field(default="", description="解压后的组件文件夹路径")
    folder_structure: str = Field(default="", description="文件夹结构分析结果")
    header_functions: str = Field(default="", description="头文件函数信息")
    call_relationship: str = Field(default="", description="函数调用关系分析结果")
    flow_diagrams: str = Field(default="", description="流程图数据")
    readme_content: str = Field(default="", description="生成的README内容")

# 工作流输入
class GraphInput(BaseModel):
    """工作流输入"""
    component_path: str = Field(..., description="组件文件夹路径或zip文件路径")

# 工作流输出
class GraphOutput(BaseModel):
    """工作流输出"""
    readme_url: str = Field(..., description="生成的README.html文件URL或路径")

# 文件夹结构分析节点输入输出
class AnalyzeStructureInput(BaseModel):
    """文件夹结构分析输入"""
    extracted_path: str = Field(..., description="解压后的组件文件夹路径")

class AnalyzeStructureOutput(BaseModel):
    """文件夹结构分析输出"""
    folder_structure: str = Field(..., description="文件夹结构分析结果")

# 头文件函数提取节点输入输出
class ExtractFunctionsInput(BaseModel):
    """头文件函数提取输入"""
    extracted_path: str = Field(..., description="解压后的组件文件夹路径")
    component_name: str = Field(default="", description="组件名称")

class ExtractFunctionsOutput(BaseModel):
    """头文件函数提取输出"""
    header_functions: str = Field(..., description="头文件函数信息")

# 函数调用关系分析节点输入输出
class AnalyzeCallRelationInput(BaseModel):
    """函数调用关系分析输入"""
    extracted_path: str = Field(..., description="解压后的组件文件夹路径")

class AnalyzeCallRelationOutput(BaseModel):
    """函数调用关系分析输出"""
    call_relationship: str = Field(..., description="函数调用关系分析结果")

# 流程图生成节点输入输出
class GenerateFlowchartInput(BaseModel):
    """流程图生成输入"""
    call_relationship: str = Field(..., description="函数调用关系")

class GenerateFlowchartOutput(BaseModel):
    """流程图生成输出"""
    flow_diagrams: str = Field(..., description="流程图数据")

# README生成节点输入输出
class GenerateReadmeInput(BaseModel):
    """README生成输入"""
    component_name: str = Field(default="", description="组件名称")
    folder_structure: str = Field(..., description="文件夹结构")
    header_functions: str = Field(..., description="头文件函数信息")
    call_relationship: str = Field(..., description="函数调用关系")
    flow_diagrams: str = Field(..., description="流程图数据")

class GenerateReadmeOutput(BaseModel):
    """README生成输出"""
    readme_content: str = Field(..., description="生成的README内容")

# README保存节点输入输出
class SaveReadmeInput(BaseModel):
    """README保存输入"""
    readme_content: str = Field(..., description="生成的README内容")

class SaveReadmeOutput(BaseModel):
    """README保存输出"""
    readme_url: str = Field(..., description="生成的README.md文件URL或路径")

# 解压缩节点输入输出
class UnzipInput(BaseModel):
    """解压缩输入"""
    zip_file_path: str = Field(..., description="zip文件路径（URL或本地路径）")

class UnzipOutput(BaseModel):
    """解压缩输出"""
    extracted_path: str = Field(..., description="解压后的组件文件夹路径")
    component_name: str = Field(..., description="组件名称（文件夹名称）")

# 本地文件上传节点输入输出
class UploadLocalFileInput(BaseModel):
    """本地文件上传输入"""
    component_path: str = Field(..., description="组件文件夹路径或本地文件路径")

class UploadLocalFileOutput(BaseModel):
    """本地文件上传输出"""
    zip_file_path: str = Field(..., description="zip文件路径（可能是上传后的URL或本地路径）")
