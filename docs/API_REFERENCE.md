# Runtime Gateway API 参考

## 基础信息

**API 基础 URL**: `http://localhost:8000/v1`

**认证**: 暂时不需要（本地开发）

## 通用响应

所有响应包含 `trace_id` 用于追踪。

---

## 端点

### 健康检查

```http
GET /v1/health
```

#### 响应示例

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

### 文本生成

```http
POST /v1/generate
Content-Type: application/json
```

#### 请求体

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `prompt` | string | 是 | 用户提示词 |
| `model` | string | 否 | 要使用的模型 |
| `max_tokens` | int | 否 | 最大 token 数 |
| `temperature` | float | 否 | 温度，0-1 |

#### 响应示例

```json
{
  "content": "生成的内容...",
  "trace_id": "abc-123",
  "model": "gpt-4",
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 200
  }
}
```

---

### 图像生成

```http
POST /v1/generate/image
Content-Type: application/json
```

#### 请求体

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `prompt` | string | 是 | 图像描述 |
| `size` | string | 否 | 图像尺寸 |
| `quality` | string | 否 | 质量设置 |

---

## WebSocket

### 连接

```
ws://localhost:8000/ws/stream
```

### 消息类型

| 类型 | 说明 |
| --- | --- |
| `ping` | 心跳检查 |
| `pong` | 心跳响应 |
| `generate` | 生成请求 |
| `generation_complete` | 生成完成 |
| `error` | 错误信息 |

### 错误处理

所有错误响应格式一致：

```json
{
  "error": "描述信息",
  "code": "错误代码",
  "trace_id": "追踪 ID"
}
```
