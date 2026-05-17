# NeoGodot 快速开始指南

欢迎使用 NeoGodot！本指南将帮助你快速上手并开始使用这款 AI 增强的游戏引擎。

---

## 目录

1. [系统要求](#系统要求)
2. [安装说明](#安装说明)
3. [NeoGodot 插件配置](#neogodot-插件配置)
4. [Runtime Gateway 配置](#runtime-gateway-配置)
5. [使用步骤](#使用步骤)
6. [常见问题](#常见问题)

---

## 系统要求

### 最低要求
- **操作系统**：Windows 10 或更高版本，macOS 10.14 或更高版本，Linux（Ubuntu 18.04+ 推荐）
- **处理器**：双核 2.0 GHz
- **内存**：4 GB RAM
- **显卡**：支持 OpenGL 3.3 或 Vulkan 1.0 的显卡
- **存储空间**：2 GB 可用空间
- **Godot 版本**：Godot 4.x
- **Python 版本**：Python 3.9+（用于 Runtime Gateway）

### 推荐配置
- **操作系统**：Windows 11，macOS 12+，最新版 Linux 发行版
- **处理器**：四核 3.0 GHz 或更高
- **内存**：16 GB RAM
- **显卡**：NVIDIA GTX 1060 / AMD RX 580 或更高
- **存储空间**：10 GB 可用 SSD

---

## 安装说明

### 方式一：从源码编译（Godot 引擎）

如果你需要编译自定义版本的 Godot 引擎：

1. **克隆仓库**
   ```bash
   git clone https://github.com/yourusername/neogodot.git
   cd neogodot
   ```

2. **安装编译工具**
   - **Windows**：安装 Visual Studio 2022（包含 C++ 桌面开发工作负载）
   - **macOS**：安装 Xcode 命令行工具
   - **Linux**：安装必需的依赖
     ```bash
     sudo apt-get install build-essential scons pkg-config libx11-dev libxcursor-dev libxinerama-dev libgl1-mesa-dev libglu-dev libasound2-dev libpulse-dev libudev-dev libxi-dev libxrandr-dev
     ```

3. **编译引擎**
   ```bash
   scons platform=windows  # Windows
   scons platform=macos    # macOS
   scons platform=linuxbsd # Linux
   ```

4. **启动编辑器**
   编译完成后，在 `bin/` 目录下找到可执行文件并运行。

### 方式二：使用现有 Godot 编辑器（推荐）

你可以直接使用官方的 Godot 4.x 编辑器，只需安装 NeoGodot 插件即可：

1. 从 [Godot 官网](https://godotengine.org/download) 下载并安装 Godot 4.x
2. 将 `addons/neo_godot/` 目录复制到你的 Godot 项目中
3. 按照下面的「插件配置」说明进行配置

---

## NeoGodot 插件配置

### 1. 启用插件

1. 打开或创建一个 Godot 项目
2. 将 `addons/neo_godot/` 目录复制到项目根目录
3. 在编辑器中点击「项目 → 项目设置」
4. 切换到「插件」标签页
5. 找到「NeoGodot AI Assistant」并点击「启用」

### 2. 验证插件安装

插件启用后，你应该看到：
- 编辑器右侧出现「NeoGodot AI 助手」Dock 面板
- 工具栏出现「NeoGodot 配置」按钮
- 编辑器控制台输出插件初始化信息

### 3. 插件配置

1. 点击工具栏的「NeoGodot 配置」按钮
2. 在弹出的配置面板中设置：
   - **Runtime Gateway URL**：Runtime Gateway 服务地址（默认 `http://localhost:8000`）
   - **API Key**：你的 AI 提供商 API Key（可选，也可以在 Runtime Gateway 中配置）
   - **默认 AI 提供商**：选择 Anthropic 或 OpenAI
3. 点击「保存配置」

---

## Runtime Gateway 配置

### 1. 安装依赖

```bash
cd runtime
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的配置
# 主要配置项：
# - HOST: 服务监听地址（默认 0.0.0.0）
# - PORT: 服务端口（默认 8000）
# - ANTHROPIC_API_KEY: Anthropic API Key
# - OPENAI_API_KEY: OpenAI API Key
```

### 3. 启动服务

#### Windows
```bash
start.bat
```

#### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

#### 或直接运行
```bash
python main.py
```

### 4. 验证服务

启动成功后，访问以下地址验证：
- 健康检查：http://localhost:8000/v1/health
- API 文档：http://localhost:8000/docs

---

## 使用步骤

### 第一步：创建新项目（或使用现有项目）

1. 启动 Godot 编辑器
2. 点击「新建项目」或打开现有项目
3. 确保已安装并启用 NeoGodot 插件

### 第二步：启动 Runtime Gateway

按照上面的说明启动 Runtime Gateway 服务。

### 第三步：配置插件

1. 在 Godot 编辑器中点击「NeoGodot 配置」
2. 设置 Runtime Gateway 地址（如果不是默认地址）
3. 保存配置

### 第四步：使用 AI 助手

1. 在编辑器右侧的「NeoGodot AI 助手」面板中
2. 输入你的需求描述，例如：
   - "生成一个玩家移动控制器脚本"
   - "创建一个简单的主菜单 UI 场景"
   - "帮我写一个碰撞检测函数"
3. 点击「生成」按钮
4. 等待 AI 生成内容
5. 生成的资源会自动保存到 `ai_generated/` 目录

### 第五步：运行示例

NeoGodot 包含示例项目，位于 `ai_generated/` 目录：
- `scripts/Main.gd` - 主脚本示例
- `scripts/Player.gd` - 玩家控制器示例
- `scenes/Main.tscn` - 主场景示例
- `scenes/Player.tscn` - 玩家场景示例

你可以直接在编辑器中打开并运行这些示例！

### 第六步：撤销和重做

所有通过 AI 助手生成的操作都支持撤销和重做：
- 使用编辑器的「编辑 → 撤销」（Ctrl+Z）撤销操作
- 使用「编辑 → 重做」（Ctrl+Y）重做操作

---

## 常见问题

### Q1: 插件启用失败怎么办？

**A**:
- 检查 Godot 版本是否为 4.x
- 确认 `addons/neo_godot/` 目录结构完整
- 查看编辑器控制台的错误信息
- 尝试重新加载项目

### Q2: Runtime Gateway 启动失败？

**A**:
- 确认 Python 版本为 3.9+
- 检查是否安装了所有依赖：`pip install -r requirements.txt`
- 检查端口 8000 是否被占用，可在 `.env` 中修改端口
- 查看控制台错误信息

### Q3: 无法连接到 Runtime Gateway？

**A**:
- 确认 Runtime Gateway 正在运行
- 检查插件配置中的 URL 是否正确
- 确认没有防火墙阻止连接
- 尝试在浏览器访问 http://localhost:8000/v1/health

### Q4: AI 生成没有响应？

**A**:
- 检查 API Key 是否正确配置
- 确认 Runtime Gateway 的日志有收到请求
- 查看编辑器控制台和 Runtime Gateway 控制台的错误信息
- 尝试使用模拟数据测试（无需真实 API Key）

### Q5: 如何导出游戏？

**A**:
1. 在编辑器中打开「项目 → 导出」
2. 添加导出预设
3. 配置导出选项
4. 点击「导出项目」
5. 注意：导出时不需要 Runtime Gateway，它仅用于开发阶段

### Q6: 示例项目无法运行？

**A**:
- 确认项目已正确导入
- 检查脚本路径是否正确
- 查看编辑器控制台的错误信息
- 确保所有依赖节点都已正确配置

### Q7: 性能不佳如何优化？

**A**:
- 使用 Profiler 分析性能瓶颈
- 减少 draw calls
- 优化纹理大小
- 使用 LOD（Level of Detail）
- 启用压缩选项

### Q8: 如何获取帮助？

**A**:
- 查看在线文档
- 阅读本指南和 [ARCHITECTURE.md](ARCHITECTURE.md)
- 查看 [README.md](README.md) 获取项目概述
- 提交 Issue 到 GitHub 仓库

---

## 下一步

- 阅读 [ARCHITECTURE.md](ARCHITECTURE.md) 了解 NeoGodot 技术架构
- 查看 [runtime/README.md](runtime/README.md) 了解 Runtime Gateway 的更多信息
- 探索示例项目并开始创建自己的游戏！
- 查看 [FINAL_VERIFICATION.md](FINAL_VERIFICATION.md) 了解项目验证状态

---

祝你使用 NeoGodot 开发愉快！🎮🚀
