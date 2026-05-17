
#!/bin/bash

echo "========================================"
echo "NeoGodot Runtime Gateway 启动脚本"
echo "========================================"
echo ""

cd "$(dirname "$0")"

if [ ! -f ".env" ]; then
    echo "[INFO] .env 文件不存在，正在从 .env.example 创建..."
    cp ".env.example" ".env"
    echo "[INFO] 已创建 .env 文件，请配置必要的参数后重新运行此脚本。"
    echo ""
    exit 1
fi

echo "[INFO] 检查 Python 环境..."
if ! command -v python3 &amp;&gt; /dev/null; then
    if ! command -v python &amp;&gt; /dev/null; then
        echo "[ERROR] 未找到 Python，请先安装 Python 3.9+"
        exit 1
    else
        PYTHON_CMD=python
    fi
else
    PYTHON_CMD=python3
fi

$PYTHON_CMD --version

echo "[INFO] 检查依赖..."
if ! $PYTHON_CMD -c "import fastapi" 2&gt;/dev/null; then
    echo "[INFO] 正在安装依赖..."
    $PYTHON_CMD -m pip install -r requirements.txt
fi

echo ""
echo "[INFO] 启动 NeoGodot Runtime Gateway..."
echo ""

$PYTHON_CMD main.py

