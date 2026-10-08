# install-go 章 — 分析

## 内容概述

工具链配置章，篇幅短、偏说明文（作者幽默点少）。四个部分：

1. **Go Environment / Go Modules**：Go 1.11 引入 Modules，1.16 起为默认构建模式，不再推荐 `GOPATH`；三段加粗引导的背景补充（modules 之前的世界、modules 如何逐一解决三类问题、为什么代码可以放在 `GOPATH` 之外）；`go mod init` 用法与 `go.mod` 示例；`go.mod` 里的 Go 版本号决定语言语义（举 Go 1.22 `for` 循环变量为例，链接到 concurrency 章）；`go help mod`。
2. **Go Linting**：推荐 GolangCI-Lint，`brew install` 一行。
3. **Refactoring and your tooling**：编辑器应能做到的重构操作（提取/内联变量、提取方法/函数、重命名、go fmt、跑测试）与代码导航（看签名、跳定义、查引用）；结尾一句点题：熟练工具 → 专注代码、减少上下文切换。
4. **Wrapping up**：装好 Go、备好编辑器和基本工具；更多生态看 awesome-go.com。

## 本章新术语

| 英文 | 定名 |
|---|---|
| Modules（大写特指 Go 方案） | 模块（Modules），首现加注；后文可径用 Modules |
| GOPATH | 保留英文（反引号内环境变量名） |
| dependency management | 依赖管理 |
| version selection | 版本选择 |
| Minimum Version Selection (MVS) | 最小版本选择（Minimum Version Selection，MVS） |
| reproducible builds | 可重现构建 |
| module path | 模块路径 |
| language semantics | 语言语义 |
| for loop variables | for 循环变量 |
| linter | linter，首现括注（代码静态检查工具） |
| GolangCI-Lint | 保留英文 |
| tooling | 工具（"你的工具"） |
| Extract/Inline variable | 提取/内联变量 |
| Extract method/function | 提取方法/函数 |
| Rename | 重命名 |
| symbol | 符号 |
| View function signature | 查看函数签名 |
| View function definition | 查看函数定义 |
| Find usages of a symbol | 查找符号的引用 |
| context switching | 上下文切换 |
| cryptographic hash | 加密哈希值 |
| magic values | 魔法值 |

## 翻译难点

- 三段**加粗引导句**（"A bit of context: …" 等）是 FAQ 式补丁段落，句式是"标题式短句 + 句点"，中文要译成读起来自然的加粗引导语，不能译成残句。
- "the toolchain uses it to decide which language semantics apply"：语义 指 Go 兼容性语义（GODEBUG 机制），照实译，不必展开。
- "opinioned formatter"：原文疑似笔误（应为 opinionated），按"有主见的格式化工具"译，保住轻微幽默，并上报笔误。
- "Keeping this reasonably current will save you some confusing debugging later on."：口语化收尾，忌译成"建议保持版本更新以避免混淆"这种公文体。
- `go.mod` 示例代码块无语言标记且**结尾多一个空行**，逐字节保留。
- 内部相对链接 `concurrency.md`（不是 http 链接，verify 不查，但需保留）。
