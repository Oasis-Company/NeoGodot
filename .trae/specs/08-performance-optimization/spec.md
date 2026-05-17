# NeoGodot 性能优化计划 - 产品需求文档

## Overview

- **Summary**: 对 NeoGodot Runtime Gateway 和 Godot 插件进行全面性能优化，提升响应速度、资源使用效率和用户体验
- **Purpose**: 解决当前系统存在的性能瓶颈，提供更流畅的 AI 辅助开发体验
- **Target Users**: NeoGodot 开发者和用户

## Goals

1. 提升 API 响应速度，健康检查端点 < 100ms，生成端点首字响应 < 500ms
2. 降低内存使用，Runtime Gateway 启动内存 < 200MB，稳定运行内存 < 500MB
3. 实现响应缓存，相同请求响应速度提升 80%
4. 添加性能监控和分析功能
5. 优化 Godot 插件 UI 渲染，减少加载和切换卡顿

## Non-Goals (Out of Scope)

- 不改变现有 API 接口设计
- 不进行大规模架构重构
- 不优化 Godot 引擎本身
- 不进行核心算法重写

## Background & Context

当前 NeoGodot 系统：
- Runtime Gateway 使用 FastAPI，响应速度尚可，但缺少缓存和压缩
- Godot 插件在历史记录加载和渲染时存在卡顿
- 没有性能监控系统，难以发现瓶颈
- API 请求完全依赖外部 AI 提供商，没有本地缓存或限流机制
- 日志系统可能在高负载时产生性能影响

## Functional Requirements

### FR-1: 响应缓存系统
- 添加基于 LRU (Least Recently Used) 策略的内存缓存
- 支持按请求类型和内容配置缓存有效期
- 提供缓存统计和管理接口
- 缓存键基于请求内容哈希生成

### FR-2: HTTP 响应压缩
- 添加 Gzip/Brotli 响应压缩中间件
- 按内容类型配置压缩策略
- 支持动态选择压缩级别

### FR-3: 请求限流
- 实现基于 IP 的请求限流
- 支持按 API 端点配置不同限流策略
- 提供限流状态响应头
- 令牌桶算法实现

### FR-4: 性能监控系统
- 添加请求延迟和吞吐量统计
- 记录内存和 CPU 使用情况
- 提供 /v1/metrics 端点供 Prometheus 抓取
- 定期性能快照记录

### FR-5: 连接池优化
- 配置 HTTP 连接池
- 优化 AI 提供商连接复用
- 添加连接健康检查和回收

### FR-6: Godot 插件 UI 优化
- 实现消息项虚拟滚动
- 延迟加载历史记录
- 优化历史文件读取和写入
- 预加载常用 UI 组件

### FR-7: 预热机制
- 启动时预初始化常用组件
- 预热 AI 提供商连接
- 预加载系统提示词

## Non-Functional Requirements

### NFR-1: 性能指标
- 健康检查端点 P95 < 100ms
- 文本生成首字响应 P95 < 500ms (不包含 AI 处理时间)
- 缓存命中响应 P95 < 50ms
- 系统启动时间 < 10s

### NFR-2: 资源使用
- Runtime Gateway 稳定运行内存 < 500MB
- Godot 插件额外内存占用 < 100MB
- CPU 使用率在空闲时 < 1%

### NFR-3: 可扩展性
- 支持同时处理至少 100 个并发请求
- 缓存可配置容量范围 100-10000 条目
- 日志系统性能影响 < 5%

## Constraints

### Technical
- 使用 Python 3.9+，保持与现有依赖兼容
- 不添加超过 3 个新的生产依赖
- 优化必须向后兼容，不破坏现有功能
- Godot 插件必须兼容 Godot 4.0+

### Business
- 优化在 1 天内完成
- 保持代码质量，添加必要的注释
- 包含完整的测试

## Assumptions

1. 大多数生成请求有重复模式，缓存能发挥作用
2. 用户更看重响应速度而非极致精度（可配置）
3. 网络传输是主要瓶颈之一，压缩能有效改善
4. 监控数据对后续优化有重要价值

## Acceptance Criteria

### AC-1: 缓存系统功能正常
- **Given**: 系统运行并启用缓存
- **When**: 发送两个完全相同的文本生成请求
- **Then**: 第二个请求响应来自缓存且延迟 < 100ms
- **Verification**: programmatic

### AC-2: 响应压缩生效
- **Given**: 系统启用压缩
- **When**: 请求 API 端点，Accept-Encoding 包含 gzip
- **Then**: 响应包含 Content-Encoding: gzip 且大小 < 未压缩的 70%
- **Verification**: programmatic

### AC-3: 请求限流工作
- **Given**: 系统启用限流 (10 requests/second)
- **When**: 短时间内发送 20 个请求
- **Then**: 至少 10 个请求返回 429 状态码
- **Verification**: programmatic

### AC-4: 性能监控可用
- **Given**: 系统运行一段时间
- **When**: 访问 /v1/metrics 端点
- **Then**: 返回包含请求计数、延迟统计、资源使用的有效格式数据
- **Verification**: programmatic

### AC-5: Godot 插件 UI 性能改善
- **Given**: 有 100 条历史记录
- **When**: 打开 AI 助手面板
- **Then**: 面板在 200ms 内完全显示，滚动流畅
- **Verification**: human-judgment

### AC-6: 内存使用在限制内
- **Given**: 系统运行 1 小时，处理 100 个请求
- **When**: 监控内存使用
- **Then**: 内存使用 < 500MB
- **Verification**: programmatic

## Open Questions

1. 是否需要在插件端实现本地缓存？ (默认：先不做)
2. 缓存是否需要持久化到磁盘？ (默认：内存缓存即可)
3. 性能数据是否需要可视化面板？ (默认：先提供 API)
