# NeoGodot 架构概览

本文档详细介绍 NeoGodot 游戏引擎的技术架构，帮助开发者理解引擎的内部工作原理。

## 目录

1. [整体架构](#整体架构)
2. [核心模块](#核心模块)
3. [渲染系统](#渲染系统)
4. [场景系统](#场景系统)
5. [脚本系统](#脚本系统)
6. [扩展机制](#扩展机制)

## 整体架构

NeoGodot 采用模块化设计，主要由以下几个层次组成：

```
┌─────────────────────────────────────────┐
│           用户层（编辑器/游戏）          │
├─────────────────────────────────────────┤
│              场景系统                    │
├─────────────────────────────────────────┤
│    核心模块  │  渲染系统  │  脚本系统   │
├─────────────────────────────────────────┤
│              服务器层                    │
├─────────────────────────────────────────┤
│              平台抽象层                  │
└─────────────────────────────────────────┘
```

### 设计理念

- **数据驱动**：场景、资源均以数据形式存储
- **节点系统**：采用面向对象的节点树架构
- **跨平台**：平台抽象层统一管理不同平台差异
- **可扩展**：模块化设计便于扩展和定制

## 核心模块

### core/ - 核心系统

核心模块提供引擎运行所需的基础功能：

```
core/
├── config/         # 引擎配置
├── crypto/         # 加密功能
├── debugger/       # 调试系统
├── error/          # 错误处理
├── extension/      # 扩展系统
├── input/          # 输入管理
├── io/             # 文件 IO
├── math/           # 数学库
├── object/         # 对象系统
├── os/             # 操作系统抽象
├── string/         # 字符串处理
├── templates/      # 数据结构模板
└── variant/        # 变体类型系统
```

#### 关键组件

1. **Object 系统**：所有引擎对象的基类，提供反射、信号槽机制
2. **Variant**：动态类型系统，支持任意类型的数据存储和传递
3. **Math 库**：提供向量、矩阵、四元数等数学运算
4. **IO 系统**：统一的文件访问接口，支持虚拟文件系统

## 渲染系统

### 渲染架构

NeoGodot 支持多种渲染后端：

- **Vulkan**：现代高性能渲染 API（推荐）
- **OpenGL 3.3**：兼容性渲染后端
- **Direct3D 12**：Windows 平台专用（通过 ANGLE）

### 渲染模块

```
drivers/
├── gles3/          # OpenGL ES 3.0 驱动
├── vulkan/         # Vulkan 驱动
├── d3d12/          # Direct3D 12 驱动
└── metal/          # Metal 驱动（macOS/iOS）
```

### 渲染管线

1. **场景剔除** - 视锥体剔除、遮挡剔除
2. **材质处理** - Shader 编译、材质实例化
3. **绘制调用** - 批量绘制、状态管理
4. **后期处理** - 效果栈、色调映射

## 场景系统

### 节点树结构

场景系统采用节点树架构：

```
Root (Node)
├── Main (Node2D)
│   ├── Player (CharacterBody2D)
│   └── Camera2D
└── UI (CanvasLayer)
    └── Control
```

### 场景模块

```
scene/
├── 2d/             # 2D 场景系统
├── 3d/             # 3D 场景系统
├── animation/      # 动画系统
├── audio/          # 音频系统
├── gui/            # GUI 系统
├── main/           # 主循环、节点
├── resources/      # 资源系统
└── theme/          # 主题系统
```

#### 关键节点类型

- **Node**：所有节点的基类
- **Node2D**：2D 空间节点
- **Node3D**：3D 空间节点
- **Control**：UI 控件基类
- **CanvasLayer**：画布层

## 脚本系统

### 支持的语言

- **GDScript** - Python 风格的内置脚本语言（推荐）
- **C#** - 通过 Mono 模块支持
- **C++** - 原生扩展模块
- **GDExtension** - 外部动态库扩展

### 脚本模块

```
modules/
├── gdscript/       # GDScript 语言
├── mono/           # C# 支持
└── (其他语言模块)
```

### 脚本特性

- **热重载** - 运行时重新加载脚本
- **信号槽** - 事件驱动通信
- **反射系统** - 运行时类型信息
- **导出变量** - 编辑器可配置属性

## 服务器层

### 服务器架构

服务器层提供核心功能服务：

```
servers/
├── audio/          # 音频服务器
├── camera/         # 相机服务器
├── debugger/       # 调试服务器
├── display/        # 显示服务器
├── text/           # 文本服务器
└── xr/             # XR 服务器
```

### 服务器职责

每个服务器负责特定领域的功能管理，提供统一的 API 供上层调用。

## 平台抽象层

### 平台支持

```
platform/
├── android/        # Android 平台
├── ios/            # iOS 平台
├── macos/          # macOS 平台
├── web/            # Web 平台
├── windows/        # Windows 平台
└── linuxbsd/       # Linux/BSD 平台
```

### 抽象接口

平台抽象层统一了不同操作系统的差异，主要包括：

- 窗口管理
- 文件系统
- 输入处理
- 线程管理
- 时间获取

## 扩展机制

### GDExtension

NeoGodot 支持通过 GDExtension 系统编写原生扩展：

1. 创建动态库（.dll/.so/.dylib）
2. 实现 GDExtension 接口
3. 在项目中注册扩展
4. 通过 Godot 调用扩展功能

### 模块系统

引擎模块位于 `modules/` 目录，编译时静态链接：

```python
# 模块结构示例
modules/
└── mymodule/
    ├── SCsub
    ├── config.py
    ├── mymodule.h
    └── mymodule.cpp
```

## 构建系统

### SCons 构建系统

NeoGodot 使用 SCons 作为构建工具：

```bash
# 基本构建命令
scons platform=windows target=editor

# 常用选项
scons platform=windows target=template_release debug_symbols=yes
```

### 构建目标

- **editor** - 编辑器可执行文件
- **template_debug** - 调试模板
- **template_release** - 发布模板

## 示例项目架构

```
ai_generated/
├── scripts/        # 脚本文件
│   ├── Main.gd
│   └── Player.gd
├── scenes/         # 场景文件
│   ├── Main.tscn
│   └── Player.tscn
├── ui/             # UI 资源
└── sfx/            # 音效资源
```

## 总结

NeoGodot 继承了 Godot Engine 优秀的架构设计，同时进行了增强和优化。其模块化、可扩展的架构使得引擎既易于使用，又具有强大的定制能力。

如需深入了解特定模块，请参考对应模块的源代码和文档。
