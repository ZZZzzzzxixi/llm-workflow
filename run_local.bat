@echo off
REM 快速本地运行脚本（Windows）

setlocal enabledelayedexpansion

if "%1"=="" (
    echo 用法: %~nx0 ^<zip文件路径^>
    echo.
    echo 示例:
    echo   %~nx0 "D:\wsl-file-sharing\newbridge\robotics_svc_media.zip"
    echo   %~nx0 ".\test_component.zip"
    exit /b 1
)

set "COMPONENT_PATH=%~1"

echo ==========================================
echo 组件文档生成工作流 - 本地运行
echo ==========================================
echo 输入路径: %COMPONENT_PATH%
echo.

REM 运行工作流
python src\main.py -m flow -i "{\"component_path\": \"%COMPONENT_PATH%\"}"

if !errorlevel! equ 0 (
    echo.
    echo ==========================================
    echo ✅ 工作流执行成功！
    echo ==========================================
    echo 生成的README.md位置: %%TEMP%%\README.md
) else (
    echo.
    echo ==========================================
    echo ❌ 工作流执行失败
    echo ==========================================
    exit /b 1
)
