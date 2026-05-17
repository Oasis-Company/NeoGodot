
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

print("=" * 50)
print("NeoGodot Runtime Gateway - 启动测试")
print("=" * 50)
print()

try:
    print("[1/4] 测试导入 FastAPI...")
    from fastapi import FastAPI
    print("      ✓ FastAPI 导入成功")
except ImportError as e:
    print(f"      ✗ FastAPI 导入失败: {e}")
    print("      请运行: pip install -r requirements.txt")
    sys.exit(1)

try:
    print("[2/4] 测试导入 main 模块...")
    import main
    print("      ✓ main 模块导入成功")
except Exception as e:
    print(f"      ✗ main 模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("[3/4] 测试配置加载...")
    from config import get_config
    config = get_config()
    print(f"      ✓ 配置加载成功")
    print(f"        - Host: {config.host}")
    print(f"        - Port: {config.port}")
    print(f"        - Debug: {config.debug}")
    print(f"        - Version: {config.version}")
except Exception as e:
    print(f"      ✗ 配置加载失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("[4/4] 测试 HealthResponse 模型...")
    from models.responses import HealthResponse
    from datetime import datetime
    health_check = HealthResponse(
        status="healthy",
        version=config.version,
    )
    print(f"      ✓ HealthResponse 模型创建成功")
    print(f"        - Status: {health_check.status}")
    print(f"        - Version: {health_check.version}")
    print(f"        - Timestamp: {health_check.timestamp.isoformat()}")
except Exception as e:
    print(f"      ✗ HealthResponse 模型测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 50)
print("所有测试通过！✓")
print("=" * 50)
print()
print("你现在可以使用以下方式启动服务:")
print("  1. python main.py")
print("  2. start.bat (Windows)")
print("  3. ./start.sh (Linux/Mac)")
print()
print("启动后访问:")
print("  - 健康检查: http://localhost:8000/v1/health")
print("  - API 文档: http://localhost:8000/docs")
print()

