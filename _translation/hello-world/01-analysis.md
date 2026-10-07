# 01 — 内容分析：Hello, World（learn-go-with-tests）

## Content Summary

- **主题**：Go 语言教程第一章。以传统 `Hello, world` 为载体，带读者走完第一轮完整的 TDD 循环（写失败测试 → 让编译通过 → 看测试失败 → 最小实现 → 重构），途中顺势引入 Go 的核心语法与工具链。
- **作者**：Chris James（quii），资深 Go 开发者，语气轻松直接、常有一两句幽默，对读者非常友好，同时强调工程纪律（版本控制、测试规范）。
- **核心论点**：Go 内置测试框架 + TDD 循环 = 快速、有反馈、有纪律的学习与开发方式。
- **目标读者**：会基本编程概念、想学 Go 的开发者；本文是全书第一章，大量"第一次"（包、函数、测试、模块）需要自然带出而不堆砌注释。
- **结构**：约 3700 词，20 余个二级/三级标题，30 个代码块（Go 源码、终端输出、shell），无图片，外链较多（Wikipedia、golang.org 文档、pkg.go.dev、go.dev spec）。

## Terminology

术语表见 EXTEND.md（用户级）。本章实际用到的高频项：

| 英文 | 中文 | 备注 |
|------|------|------|
| test-driven development (TDD) | 测试驱动开发（TDD） | 首现全称 |
| package / `main` | 包 / `main` 包 | |
| module | 模块 | go mod init 语境 |
| side effect | 副作用 | |
| domain | 领域 | "domain code" → 领域代码 |
| subtest | 子测试 | |
| assertion | 断言 | |
| helper | 辅助函数 | `t.Helper()` |
| benchmark | 基准测试 | `*testing.B` |
| interface | 接口 | 首现加注 |
| named return value | 具名返回值 | |
| zero value | 零值 | |
| short variable declaration | 短变量声明 | `:=` |
| format verb / placeholder | 格式化动词 / 占位符 | `%q` 语境 |
| magic string | 魔法字符串 | |
| source control / commit | 版本控制 / commit | commit 保留英文 |
| refactor | 重构 | |
| state of flow | 心流 | |
| statically typed | 静态类型 | |
| testing framework | 测试框架 | |
| hook | 钩子 | `*testing.T` 语境 |

专有名词保留原文：`fmt`、`testing`、`Hello, world`、Go modules、pkgsite、`go doc`、`$PATH`、Linux/macOS/Windows 路径。

## Tone & Style

- 原文口语化、第二人称直呼读者、偶尔幽默（"Who knew you could get so much out of Hello, world?" / "Goodness me" / "_amazing_ function"）。
- 目标风格：**conversational**（像朋友当面讲解），但面向 **technical** 读者——不加冗余注释，术语首现加英文原文即可。
- 幽默处要保住，不译平；指令句用"你"开头的祈使句，短促自然。

## Translation Challenges

- "It is traditional for your first program..." → 直译生硬 → 按惯例/规矩开头，口语化重组。
- "listen to the compiler" → 隐喻，意为"重视编译器报错" → 译"听编译器的话"，保留拟人。
- "In a word, modules" → 短促幽默 → "一个词：模块"。
- "goodness me" → 英式感叹 → "好家伙"。
- "_amazing_ function" → 自嘲式夸张 → 保留强调："我们这个'了不起的'函数"。
- "Hello, YOU" 标题 → 与 "Hello, world" 对仗的玩笑 → 保留原文 "Hello, YOU" 不译。
- "one...last...refactor?" 标题 → 省略号节奏 → "最后一次……重构？"
- "quality-of-life feature" → 游戏化用语 → "幸福感满满的设计/提升体验的设计"。
- 代码块与终端输出**一字不改**（含原文的输出样例、路径、错误信息）；正文中的代码引用保留反引号。
- 章首"本章所有代码"链接指向原仓库 hello-world 目录，保留指向 GitHub 原仓库。
- 教学节奏：每段"写测试→编译错误→改代码"的因果链不能断，翻译时保持步骤顺序与原文一一对应，不合并、不拆移段落。
