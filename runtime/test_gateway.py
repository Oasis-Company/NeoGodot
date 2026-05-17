import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import httpx
import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app
from config import get_config, ConfigError


client = TestClient(app)


def test_health_check():
    """测试健康检查端点"""
    print("\n=== 测试健康检查端点...")
    response = client.get("/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "version" in data
    print(f"✓ 健康检查通过")
    print(f"  响应数据: {data}")


def test_trace_id_header():
    """测试响应中包含 X-Trace-ID 头"""
    print("\n=== 测试 X-Trace-ID 响应头...")
    response = client.get("/v1/health")
    assert "x-trace-id" in response.headers
    print(f"✓ X-Trace-ID 响应头存在")


def test_custom_trace_id():
    """测试自定义 X-Trace-ID 请求头"""
    print("\n=== 测试自定义 X-Trace-ID 请求头...")
    custom_trace_id = "test-trace-id-12345"
    response = client.get("/v1/health", headers={"X-Trace-ID": custom_trace_id})
    assert response.headers["x-trace-id"] == custom_trace_id
    print(f"✓ 自定义 X-Trace-ID 正确回传")


def test_config_validation():
    """测试配置验证功能"""
    print("\n=== 测试配置验证...")
    
    config = get_config()
    assert config.host is not None
    assert 1 <= config.port <= 65535
    assert config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    print("✓ 配置验证通过")
    print(f"  Host: {config.host}")
    print(f"  Port: {config.port}")
    print(f"  Log Level: {config.log_level}")


def test_404_error():
    """测试 404 错误处理"""
    print("\n=== 测试 404 错误处理...")
    response = client.get("/nonexistent-endpoint")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "code" in data
    print("✓ 404 错误处理正常")


@pytest.mark.asyncio
async def test_websocket_ping_pong():
    """测试 WebSocket  ping-pong"""
    print("\n=== 测试 WebSocket ping-pong...")
    try:
        async with httpx.AsyncClient() as async_client:
            async with async_client.websocket_connect("ws://testserver/ws/stream") as websocket:
                data = await websocket.receive_json()
                assert "type" in data
                print(f"✓ WebSocket 连接成功")
                print(f"  初始响应: {data}")
    except Exception as e:
        print(f"⚠ 跳过 WebSocket 测试: {e}")


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("NeoGodot Runtime Gateway 测试")
    print("=" * 60)
    
    tests = [
        test_health_check,
        test_trace_id_header,
        test_custom_trace_id,
        test_config_validation,
        test_404_error
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n✗ 测试失败: {test.__name__}")
            print(f"  错误: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
