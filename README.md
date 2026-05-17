<p align="center">
  <img src="assets/neogodotlogo.png" width="400" alt="NeoGodot logo">
</p>

# NeoGodot

> 基于 Godot Engine 的 AI 增强游戏引擎，让游戏开发更智能。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Godot Version](https://img.shields.io/badge/Godot-4.x-blue)](https://godotengine.org/)
[![Python Version](https://img.shields.io/badge/Python-3.9+-green)](https://www.python.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Code of Conduct](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)

---

## ✨ 特性

### 🎮 Godot 原生功能
- 完整保留 Godot Engine 的所有强大能力
- 统一的 2D 和 3D 开发界面
- 跨平台导出支持
- GDScript、C#、C++ 多语言支持

### 🤖 AI 增强功能
- **AI 助手集成** - 内置 AI 助手面板
- **智能代码生成** - 通过自然语言生成 GDScript
- **场景和资源生成** - 自动创建游戏资源
- **撤销/重做支持** - 所有 AI 操作可撤销
- **配置管理** - 灵活的自定义配置

### 🔌 Runtime Gateway
- FastAPI 后端服务
- RESTful API 和 WebSocket 支持
- 多 AI 提供商集成
- 健康检查和监控

---

## 🚀 快速开始

### 前置要求

- Godot 4.x 编辑器
- Python 3.9+

### 安装

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/neogodot.git
cd neogodot

# 2. 安装并启动 Runtime Gateway
cd runtime
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 配置 API Key
python main.py
```

### 使用插件

1. 将 `addons/neo_godot/` 复制到 Godot 项目
2. 在 Godot 编辑器中启用插件
3. 点击 NeoGodot 配置按钮连接 Gateway
4. 开始使用 AI 助手！

详细指南请查看 [QuickStart](docs/QuickStart.md)。

---

## 📖 文档

- [📚 文档中心](docs/README.md)
- [🚀 快速开始](docs/QuickStart.md)
- [📦 安装指南](docs/INSTALLATION.md)
- [🏗️ 架构说明](docs/ARCHITECTURE.md)
- [📋 API 参考](docs/API_REFERENCE.md)
- [💡 常见问题](docs/FAQ.md)
- [🔧 故障排除](docs/TROUBLESHOOTING.md)

---

## 📂 项目结构

```
neogodot/
├── addons/neo_godot/        # Godot 插件
│   ├── plugin.gd            # 插件主脚本
│   ├── autoload/            # 自动加载
│   ├── ui/                  # UI 组件
│   ├── commands/            # 命令系统
│   └── ...
├── runtime/                 # Python 服务
│   ├── main.py              # 入口
│   └── ...
├── assets/                  # 资源文件
├── docs/                    # 文档
└── ai_generated/            # AI 生成资源
```

---

## 🤝 贡献

我们欢迎所有形式的贡献！请查看：

- [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献指南
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) - 行为准则

### 快速贡献流程：

1. Fork 这个仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交变更 (`git commit -m 'feat: 添加了一个新功能'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目基于 [MIT License](LICENSE.txt) 开源。

---

## 🙏 致谢

- 感谢 [Godot Engine](https://godotengine.org/) 社区
- 感谢所有贡献者

---

<p align="center">
  <b>Made with 💖 for game developers</b><br>
  NeoGodot - 让游戏开发更智能 🚀
</p>
