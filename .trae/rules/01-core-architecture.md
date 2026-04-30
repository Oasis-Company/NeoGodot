# NeoGodot 核心架构规则

## 插件优先原则
* 所有新增的 AI 功能必须通过 `EditorPlugin`、`GDExtension` 或自定义 `MainScreen` 实现[cite: 2]。
* 禁止直接修改 Godot 核心源码（如 `core/` 或 `servers/`），除非确认为解决热路径性能瓶颈[cite: 2]。

## 资产与文件系统
* AI 生成的所有资产（模型、脚本、图片）必须统一存放在 `res://ai_generated/` 目录下[cite: 2]。
* 资产操作必须触发 `EditorFileSystem` 的重导入流程，确保资源状态同步[cite: 2]。

## 解耦要求
* 禁止在插件代码中硬编码任何模型 API 密钥或供应商特定逻辑[cite: 2]。
* 所有推理请求必须转发至本地代理网关 `127.0.0.1:7777` 进行统一调度[cite: 2]。
