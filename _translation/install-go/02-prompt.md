# install-go 章 — 本章翻译约束

## 术语定名（英 → 中）

- Modules → 模块（Modules），首现加注一次；行文可回用英文 Modules
- Minimum Version Selection (MVS) → 最小版本选择（Minimum Version Selection，MVS）
- reproducible builds → 可重现构建
- dependency management → 依赖管理；version selection → 版本选择
- module path → 模块路径；language semantics → 语言语义
- linter → linter（首现括注：代码静态检查工具）；GolangCI-Lint、go fmt、brew 不译
- 编辑器功能词条按惯例译动宾短语：提取/内联变量、提取方法/函数、重命名、运行测试、查看函数签名、查看函数定义、查找符号的引用
- symbol → 符号；context switching → 上下文切换；cryptographic hash → 加密哈希值；magic values → 魔法值

## 原样保留

- 全部命令、版本号（1.11 / 1.16 / 1.22 / 1.24）、路径（`~/go`）、文件名（`go.mod`、`go.sum`、`package.json`）
- `go.mod` 示例（含结尾空行、无语言标记）、4 个代码块数量与语言标记
- 所有链接 URL，含内部相对链接 `concurrency.md`
- VS Code/IDE 类界面功能不涉及具体 UI 文案，无需保留界面英文；IDE 一词保留英文

## 幽默点对策

1. "an opinioned formatter"（应为 opinionated）：轻幽默，译"颇有主见的格式化工具"，不译成"官方指定格式化工具"这类平淡表述。
2. "Keeping this reasonably current will save you some confusing debugging later on"：口语收尾，译成叮嘱口吻（"能帮你省掉日后一些莫名其妙的调试"），不公文化。
3. "pretty straightforward"、"with confidence" 等轻快语气用"相当简单""更有底气"等对应，不删。

## 标题

- H1 按主控指定：`# 安装 Go`
- Go Environment → Go 环境；Go Modules → Go 模块；Go Linting → Go 代码检查；Refactoring and your tooling → 重构与你的工具；Wrapping up → 小结
