# NeoGodot 常见问题 (FAQ)

本页面收集了 NeoGodot 用户最常问的问题和解答。

---

## 目录

1. [入门相关](#入门相关)
2. [插件使用](#插件使用)
3. [Runtime Gateway](#runtime-gateway)
4. [AI 生成](#ai-生成)
5. [开发与贡献](#开发与贡献)
6. [其他问题](#其他问题)

---

## 入门相关

### Q: NeoGodot 是什么？

**A**: NeoGodot 是在 Godot Engine 基础上进行增强和优化的游戏引擎版本，集成了强大的 AI 辅助开发功能，让游戏开发更加高效和智能。它保留了 Godot 所有原生功能，同时添加了 AI 助手集成、智能代码生成、场景和资源生成等特性。

### Q: NeoGodot 和 Godot 有什么区别？

**A**: 
- NeoGodot 完整保留了 Godot Engine 的所有功能和特性
- 添加了 AI 助手面板，可直接在编辑器中使用 AI 功能
- 支持通过自然语言生成 GDScript 代码、场景和资源
- 提供独立的 Runtime Gateway 服务，支持多 AI 提供商
- 所有 AI 生成操作都支持完整的撤销/重做

### Q: 需要付费使用吗？

**A**: NeoGodot 本身是免费开源的，基于 MIT 许可证。但是：
- 使用 AI 功能需要相应的 AI 提供商 API Key（可能产生费用）
- 你可以使用免费额度或选择适合的付费计划

### Q: 支持哪些 Godot 版本？

**A**: NeoGodot 目前支持 Godot 4.x 版本。建议使用最新的稳定版 Godot 4.x 以获得最佳体验。

---

## 插件使用

### Q: 如何安装 NeoGodot 插件？

**A**: 
1. 将 `addons/neo_godot/` 目录复制到你的 Godot 项目中
2. 在 Godot 编辑器中打开「项目 → 项目设置 → 插件」
3. 找到「NeoGodot AI Assistant」并点击「启用」

详细步骤请参考 [QuickStart.md](QuickStart.md)。

### Q: 插件启用后没有反应怎么办？

**A**: 请检查：
1. 确认使用的是 Godot 4.x
2. 查看编辑器控制台是否有错误信息
3. 确认插件目录结构完整
4. 尝试重新加载项目

更多帮助请查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)。

### Q: 可以在多个项目中使用同一个插件吗？

**A**: 可以。你需要在每个 Godot 项目中都复制 `addons/neo_godot/` 目录并单独启用插件。

### Q: 如何卸载插件？

**A**: 
1. 在项目设置中禁用插件
2. 删除项目中的 `addons/neo_godot/` 目录
3. 重新加载项目

---

## Runtime Gateway

### Q: 什么是 Runtime Gateway？

**A**: Runtime Gateway 是 NeoGodot 的独立 AI 服务网关，负责：
- 提供 RESTful API 和 WebSocket 接口
- 集成多个 AI 提供商（Anthropic、OpenAI 等）
- 处理 Godot 插件的 AI 请求
- 提供健康检查和监控功能

### Q: Runtime Gateway 必须一直在运行吗？

**A**: 
- **开发阶段**：是的，需要运行 Runtime Gateway 才能使用 AI 功能
- **游戏运行时**：不需要，Runtime Gateway 仅用于开发阶段

### Q: 可以在远程服务器上部署 Runtime Gateway 吗？

**A**: 可以。你可以将 Runtime Gateway 部署在远程服务器上，然后在 Godot 插件配置中修改 URL 为远程地址。记得配置适当的安全措施（如认证、HTTPS 等）。

### Q: 如何更改 Runtime Gateway 的端口？

**A**: 编辑 `runtime/.env` 文件，修改 `PORT` 变量的值，然后重启服务。

### Q: 多个用户可以共享同一个 Runtime Gateway 吗？

**A**: 可以。只要网络可达，多个 Godot 编辑器可以连接到同一个 Runtime Gateway 实例。

---

## AI 生成

### Q: 支持哪些 AI 提供商？

**A**: 目前支持：
- Anthropic (Claude)
- OpenAI (GPT)

可以通过扩展 Runtime Gateway 来添加更多 AI 提供商。

### Q: AI 生成的内容版权归谁？

**A**: 
- NeoGodot 本身不主张对生成内容的版权
- 具体版权归属取决于所使用的 AI 提供商的服务条款
- 建议查看 AI 提供商的相关政策

### Q: 生成的代码可以直接用于商业项目吗？

**A**: 
- 可以，但建议进行充分测试
- AI 生成的代码可能存在 bug 或安全问题
- 建议进行代码审查和测试

### Q: 如何提高 AI 生成内容的质量？

**A**: 
- 提供更详细、更具体的需求描述
- 在提示词中包含相关上下文
- 明确指定技术栈和风格要求
- 多次尝试，然后选择最好的结果
- 将 AI 生成作为起点，进行手动优化

### Q: AI 生成很慢怎么办？

**A**: 
- 检查网络连接
- 尝试使用更简单的提示词
- 查看 Runtime Gateway 日志确认没有错误
- 考虑使用更快的 AI 模型

---

## 开发与贡献

### Q: 如何为 NeoGodot 做贡献？

**A**: 欢迎贡献！你可以：
- 提交 Bug 报告
- 提出功能建议
- 贡献代码
- 改进文档
- 帮助其他用户

### Q: 可以扩展 AI 提供商吗？

**A**: 可以。Runtime Gateway 设计为可扩展的，你可以添加新的 AI 提供商支持。

### Q: 如何报告 Bug？

**A**: 请在 GitHub 上提交 Issue，包含：
- 详细的问题描述
- 复现步骤
- 错误日志或截图
- 系统环境信息

### Q: 有路线图吗？

**A**: 项目的发展方向会根据社区反馈不断调整。建议关注 GitHub 仓库的更新。

---

## 其他问题

### Q: 导出游戏时需要包含 Runtime Gateway 吗？

**A**: 不需要。Runtime Gateway 仅在开发阶段使用，导出的游戏不依赖它。

### Q: 可以在没有网络连接的情况下使用吗？

**A**: 
- Godot 编辑器的原生功能可以离线使用
- AI 生成功能需要网络连接到 AI 提供商
- 可以实现离线 AI 模型集成（需要额外开发）

### Q: NeoGodot 会收集我的数据吗？

**A**: 
- NeoGodot 本身不会收集用户数据
- AI 请求会发送到所配置的 AI 提供商
- 请查看 AI 提供商的隐私政策

### Q: 有官方 Discord/Slack 社区吗？

**A**: 请关注项目 GitHub 仓库获取最新的社区信息。

### Q: 如何获取更多帮助？

**A**: 
1. 阅读文档：[README.md](README.md)、[QuickStart.md](QuickStart.md)、[TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. 搜索 GitHub Issues
3. 提交新的 Issue

---

**没有找到你的问题？** 欢迎在 GitHub 上提交 Issue 提问！
