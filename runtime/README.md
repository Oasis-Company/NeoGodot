
# NeoGodot Runtime Gateway

NeoGodot Runtime Gateway 是一个为 Godot 游戏引擎提供 AI 能力的 FastAPI 服务。

## 功能特性

- **REST API** - 标准的 HTTP API 接口
- **WebSocket** - 实时流式通信支持
- **多 AI 提供商** - 支持 Anthropic、OpenAI 等
- **健康检查** - `/v1/health` 端点
- **API 文档** - 自动生成的 Swagger UI 和 ReDoc
- **完善的错误处理** - 清晰的错误提示和配置验证
- **测试支持** - 内置测试脚本确保服务可靠性

## 环境要求

- Python 3.9+
- pip

## 快速开始

### 1. 安装依赖

```bash
cd runtime
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的参数：

```env
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
VERSION=1.0.0
ALLOWED_ORIGINS=*

ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 启动服务

#### 方式一：直接运行

```bash
python main.py
```

#### 方式二：使用 uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 方式三：使用启动脚本

Windows:
```bash
start.bat
```

Linux/Mac:
```bash
chmod +x start.sh
./start.sh
```

## 访问服务

启动成功后，可以访问以下地址：

- **API 服务**: http://localhost:8000
- **Swagger UI 文档**: http://localhost:8000/docs
- **ReDoc 文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/v1/health

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| HOST | 服务监听地址 | 0.0.0.0 |
| PORT | 服务监听端口 (1-65535) | 8000 |
| DEBUG | 调试模式 | false |
| LOG_LEVEL | 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL) | INFO |
| VERSION | 服务版本 | 1.0.0 |
| ALLOWED_ORIGINS | CORS 允许的源 | * |
| ANTHROPIC_API_KEY | Anthropic API 密钥 | - |
| OPENAI_API_KEY | OpenAI API 密钥 | - |

## 测试

运行测试以验证服务是否正常工作：

```bash
cd runtime
python test_gateway.py
```

或使用 pytest：

```bash
cd runtime
pytest test_gateway.py -v
```

测试覆盖范围：
- 健康检查端点
- 响应头验证
- 自定义 Trace ID
- 配置验证
- 错误处理

## API 端点

### 健康检查

```http
GET /v1/health
```

响应示例：
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### WebSocket 流式通信

```
WS /ws/stream
```

## 开发指南

### 调试模式

设置 `DEBUG=true` 启用调试模式，此时：
- 代码变更会自动重载
- 日志级别会自动降低
- 会输出更详细的调试信息

### 日志级别

支持的日志级别：
- DEBUG
- INFO
- WARNING
- ERROR
- CRITICAL

## 项目结构

```
runtime/
├── main.py              # 主入口文件
├── config.py            # 配置管理
├── logger.py            # 日志模块
├── test_gateway.py     # 测试脚本
├── requirements.txt     # Python 依赖
├── .env.example         # 环境变量模板
├── models/              # 数据模型
├── routes/              # API 路由
├── services/            # 业务逻辑
├── providers/           # AI 提供商
└── websocket/          # WebSocket 相关
```

## 故障排查

### 端口被占用

修改 `.env` 文件中的 `PORT` 变量，或停止占用端口的进程。

### 环境变量未加载

确保 `.env` 文件在 `runtime/` 目录下，且文件名正确。

### 配置错误

如果启动时遇到配置错误，错误消息会明确说明具体问题（如无效的端口号或日志级别）。检查 `.env` 文件中的配置是否正确。

### API 密钥问题

检查 `.env` 文件中的 API 密钥是否正确设置。

## License

参见项目根目录的 LICENSE 文件。

