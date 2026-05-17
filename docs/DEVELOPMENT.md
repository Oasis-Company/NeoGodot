# 开发指南

本文档为想要为 NeoGodot 贡献代码的开发者提供指导。

## 开发环境设置

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/neogodot.git
cd neogodot
```

### 2. 分支工作流

我们使用 Git Flow：

```bash
git checkout -b feature/my-feature
```

## 项目结构概览

```
neogodot/
├── addons/neo_godot/  # Godot 插件
│   ├── plugin.gd      # 插件入口
│   ├── ui/            # UI 组件
│   ├── autoload/      # 自动加载单例
│   └── ...
├── runtime/           # Python 服务
│   ├── main.py        # FastAPI 入口
│   └── ...
└── docs/              # 文档
```

## Godot 插件开发

### 扩展插件

- 插件使用 GDScript 4.x
- 遵循 Godot 代码风格
- 在 `ui/` 中添加新 UI 组件

### 添加新命令

在 `commands/` 中创建新命令类，继承 `NeuralCommand`。

## Runtime Gateway 开发

### 运行开发服务

```bash
cd runtime
pip install -r requirements.txt
python main.py
```

### 添加新端点

1. 在 `routes/` 中创建新路由文件
2. 在 `main.py` 中注册
3. 添加 API 文档到 `docs/API_REFERENCE.md`

## 测试

### Godot 插件测试

在 Godot 编辑器中进行手动测试。

### Runtime 测试

```bash
python -m unittest discover
```

## 提交规范

### Pull Request 流程

1. 从 `main` 创建分支
2. 开发并测试
3. 创建 Pull Request
4. 等待代码审查
5. 合并

### 提交信息

使用清晰的提交信息：

- `feat: 添加了新功能`
- `fix: 修复了某个 bug`
- `docs: 更新了文档`
- `refactor: 重构了代码`

## 获取帮助

有问题？查看 [CONTRIBUTING.md](../CONTRIBUTING.md) 或创建 Issue。
