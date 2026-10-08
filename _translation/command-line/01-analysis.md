# 01 — 章节分析：command-line

## 内容概述

本章把扑克项目拆成"一个库 + 两个应用"：产品负责人要新增一个命令行应用，用户输入 `Ruth wins` 就记录一次胜场，且与 Web 服务器共享同一份数据库。

- **项目结构调整**：引入 Go 社区的 `cmd/<app>` 约定，把两个 `main` 包挪进 `cmd/webserver`、`cmd/cli`，其余代码归入 `poker` 包，通过 `poker.FunctionName` 导入使用；
- **相对路径陷阱**（本仓库版源文新增的两段）：`dbFileName` 相对"运行时所在目录"解析，两个应用必须从同一目录启动才能共享 `game.db.json`；
- **行走骨架**：先让 `cmd/cli` 跑起来打印一句话，再走三轮 TDD（先写测试 → 试跑 → 最小实现 → 通过 → 重构）：
  1. `CLI` 集成 `PlayerStore`（`PlayPoker` 空方法 → `RecordWin("Cleo")`）；
  2. 注入 `io.Reader`（`strings.NewReader` 模拟 `os.Stdin`）→ 记录指定玩家；
  3. 用 `bufio.Scanner` 真正按行读输入（`extractWinner` 剥掉 " wins"）；
- **集成教训**：接进真正的 `main` 时撞上"未导出字段不能隐式赋值"，由此引出 `package foo_test` 外部测试包的纪律，以及"要不要把 stub / 辅助函数公开"的讨论（Mitchell Hashimoto 演讲先例），最终把 `StubPlayerStore`、`AssertPlayerWin` 挪进公开的 `testing.go`，并给 `CLI` 加构造函数 `NewCLI`；
- **收尾重构**：`FileSystemPlayerStoreFromFile` 封装"开文件 + 建 store + 返回关闭函数"，两个 `main` 对称收敛；总结包结构、读输入、简单抽象三点。

30 个代码块（26 个 go、3 个终端输出/编译错误、1 个 tree 目录树），无图片，无跨章 markdown 链接（"上一章"为纯文字指代）。1 段英文文档引文（bufio 包文档 blockquote，按惯例译中文）。

## 本章新术语（英 → 中定名）

| 英文 | 定名 |
| --- | --- |
| command line application / CLI | 命令行应用 / CLI |
| binary | 二进制可执行文件（后文"可执行文件"） |
| project structure | 项目结构 |
| walking skeleton | 行走骨架（walking skeleton） |
| cmd convention | `cmd` 目录约定 |
| unexported / exported | 未导出 / 导出（首现括注 private/public 语义） |
| constructor | 构造函数（术语表已有） |
| standard input / `Stdin` | 标准输入 |
| relative path / current working directory | 相对路径 / 当前工作目录 |
| buffered I/O | 缓冲 I/O |
| wire up / integrate / integration | 接入 / 集成 |
| DRY | DRY（首现括注 Don't Repeat Yourself，别重复自己） |
| closing function | 负责关闭的函数 |
| re-invent the wheel | 重复造轮子 |
| stub | stub（保留英文，术语表已有） |

代码名一律保留：`PlayerStore`、`FileSystemPlayerStore`、`StubPlayerStore`、`CLI`、`PlayPoker`、`NewCLI`、`extractWinner`、`readLine`、`os.Stdin`、`os.OpenFile`、`bufio.Scanner`、`strings.NewReader`、`poker`。

## 翻译难点

1. TDD 步骤标题与前章统一：先写测试 / 试着运行测试 / 写最少的代码让测试能运行，并检查失败的测试输出 / 写足够的代码让测试通过 / 重构（io 章口径）。
2. `A reminder of the code` 沿用 io 章先例"目前的代码"。
3. 30 个代码块逐字节一致；仅 go 块内的散文注释翻译（`// todo for you - the rest of the helpers`），文件路径注释（`// CLI_test.go`、`// CLI.go`、`// testing.go`、`// cmd/.../main.go`）保留。
4. 源文第 108 行原句残缺（"imports that package the features we've written available"），按上下文补全语义译出，并在报告标注疑似笔误。
5. 幽默点：IDE 一片飘红、"难用得要命！"、重复造轮子等要保住语气。
6. 原文 `### Simple abstractions leads to simpler code re-use` 主谓不一致（leads → lead），标题意译不受影响。
