# 02 — 本章翻译约束：command-line

## 标题与结构

- H1：**命令行与项目结构**（与 SUMMARY 一致）。
- 章首代码链接：`**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/command-line)**`，URL 原样。
- 章节标题对照：
  - A reminder of the code → 目前的代码（沿 io 章）
  - Some project refactoring first → 先来一点项目重构
  - Final checks → 最终检查
  - Walking skeleton → 行走骨架
  - Write the test first → 先写测试；Try to run the test → 试着运行测试
  - Write the minimal amount of code for the test to run and check the failing test output → 写最少的代码让测试能运行，并检查失败的测试输出
  - Write enough code to make it pass → 写足够的代码让测试通过；Refactor → 重构
  - `package mypackage_test` 标题原样保留（反引号代码）
  - Do we want to have our stubs and helpers 'public'? → 要不要把我们的 stub 和辅助函数"公开"？
  - CLI application code / Web server application code → CLI 应用的代码 / Web 服务器应用的代码
  - Wrapping up → 总结；Package structure → 包结构；Reading user input → 读取用户输入
  - Simple abstractions leads to simpler code re-use → 简单的抽象带来更省事的代码复用

## 术语与加注

- 未导出（unexported）、导出（exported）首现括注一次；行走骨架（walking skeleton）首现括注；DRY 首现括注 Don't Repeat Yourself。
- 产品负责人（product owner）、stub、辅助函数、构造函数等沿用既有译名，不再加注。
- `main` 包、`package poker`、`poker.FunctionName` 等代码字面量全部进反引号。

## 幽默/语气点

- "you will suddenly see a lot of red!" → IDE 瞬间一片红色。
- "how easy (or not!) your code is to work with" → 保留"（还是难用得要命！）"式吐槽。
- "re-invent the wheel" → 重复造轮子；"Anecdotally…" 口语化处理。
- "Let's play poker" / "Type {Name} wins to record a win" 是程序输出，在代码块内，原样。

## 硬性注意

- 终端输出/编译错误块（含 `# github.com/...` 行）逐字节保留；`tree` 目录树逐字节保留。
- go 块仅翻译散文式 `//` 注释；文件路径注释保留。
- 本仓库版源文多出两段关于 `dbFileName` 相对路径的说明（"Final checks"前后），如实翻译，不可漏。
- 无图片、无跨章 markdown 链接；4 条外链（github chapter code、pkg.go.dev、golang.org/pkg/bufio、speakerdeck）原样保留。
