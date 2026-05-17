# 安装指南

## 前置要求

在安装 NeoGodot 之前，请确保你的系统满足以下要求：

- **Godot 4.x** - 编辑器
- **Python 3.9+** - 用于 Runtime Gateway
- **pip** - Python 包管理器

## 1. 获取项目

有几种方式获取 NeoGodot：

### 方式 1: 克隆仓库

```bash
git clone https://github.com/yourusername/neogodot.git
cd neogodot
```

### 方式 2: 下载 ZIP

1. 访问项目主页
2. 点击 "Code" > "Download ZIP"
3. 解压到你想要的位置

## 2. 安装 Runtime Gateway

进入 runtime 目录并安装依赖：

```bash
cd runtime
pip install -r requirements.txt
```

### 配置

复制示例配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API Key：

```
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8000
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 测试启动

```bash
python main.py
```

访问 http://localhost:8000/v1/health 确认服务正常运行。

## 3. 使用插件

### 在现有项目中：

1. 复制 `addons/neo_godot/` 目录到你的 Godot 项目根目录
2. 在 Godot Editor 中打开项目
3. 进入 项目 > 项目设置 > 插件
4. 启用 "NeoGodot AI Assistant"

### 创建新项目：

1. 在 Godot 中创建新项目
2. 将 `addons/` 目录复制进去
3. 启用插件

## 4. 验证安装

1. 确保 Runtime Gateway 正在运行
2. 在 Godot 中启用插件
3. 点击 NeoGodot 配置按钮
4. 确认连接状态正常

## 下一步

完成安装后，查看[快速开始](QuickStart.md)开始使用！

遇到问题？查看[故障排除](../TROUBLESHOOTING.md)。
