
@echo off
chcp 65001 &gt;nul
echo ========================================
echo NeoGodot Runtime Gateway 启动脚本
echo ========================================
echo.

cd /d "%~dp0"

if not exist ".env" (
    echo [INFO] .env 文件不存在，正在从 .env.example 创建...
    copy ".env.example" ".env" &gt;nul
    echo [INFO] 已创建 .env 文件，请配置必要的参数后重新运行此脚本。
    echo.
    pause
    exit /b 1
)

echo [INFO] 检查 Python 环境...
python --version &gt;nul 2&gt;&amp;1
if errorlevel 1 (
    echo [ERROR] 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

echo [INFO] 检查依赖...
python -c "import fastapi" &gt;nul 2&gt;&amp;1
if errorlevel 1 (
    echo [INFO] 正在安装依赖...
    pip install -r requirements.txt
)

echo.
echo [INFO] 启动 NeoGodot Runtime Gateway...
echo.

python main.py

pause

