# 01 — 源文分析（concurrency）

## 内容概述

本章是全书并发入门，TDD 味道比别章淡，主体是一次"性能重构"：

1. 场景铺垫：同事写了 `CheckWebsites`（依赖注入过的 `WebsiteChecker`），生产环境嫌慢。
2. Write a test：写基准测试（`BenchmarkCheckWebsites` + `slowStubWebsiteChecker`）量化慢（约 2.25 s）。
3. 引入并发：烧水泡茶的比喻 → *blocking* 概念 → `go` 语句 + *goroutine*；第一次尝试直接写 map，测试失败（返回空 map）。
4. "A quick aside into the concurrency universe... / ... and we're back"：两个幽默小节，承认并发结果不可预测。
5. sleep 2 秒的坏修法 → `fatal error: concurrent map writes` → *data race* 概念 → `-race` 竞态检测器及输出解读。
6. Channels：`result` 匿名字段结构体 + `chan result`，发送语句/接收表达式（`<-` 两个方向），逐个消费结果；基准从 2.25 s 降到 0.023 s。
7. 源文含一段 blockquote（Go 1.22 循环变量语义变更、`go.mod` 版本旧时的坑与修法）——上游较新加入的内容。
8. Wrapping up + "Make it fast"：Make it work, make it right, make it fast；Knuth "过早优化"名言。

注意：任务提示中的 Checkers 棋例与 "two too fun" 双关在当前上游版本中**不存在**（已在更早版本移除），相关特别说明本章不适用。

## 本章新术语（英 → 中定名）

| 英文 | 定名 | 说明 |
| --- | --- | --- |
| blocking | 阻塞 | 首现加注（blocking），与 select 章一致 |
| goroutine | goroutine | 保留英文（词汇表） |
| channel | channel | 保留英文，首现加注（通道）；正文标题 "Channels" 保留英文 |
| data race | 数据竞争 | 首现加注（data race）；`WARNING: DATA RACE` 输出原文不动 |
| race condition | 竞态条件 | 注意与 data race 区分：race detector 段用 data race，总结用 race condition |
| race detector | 竞态检测器 | Go 官方文档译法 |
| send statement | 发送语句 | Go spec 术语 |
| receive expression | 接收表达式 | Go spec 术语 |
| anonymous function | 匿名函数 | 词汇表已有 |
| anonymous struct field | （匿名字段） | `result` 结构体的匿名/嵌入字段，随文解释即可 |
| process | 流程 | 原文用 *process* 指执行流而非 OS 进程；按全书特别说明统一译"流程"（synchronise processes = 同步流程同源），仅在明喻"另一个读者"处保持叙述性 |
| concurrent map writes | （不译） | 运行时错误输出，逐字节保留 |
| premature optimization | 过早优化 | Knuth 名言 |
| Make it work, make it right, make it fast | 先让它能跑，再让它对，最后让它快 | 名言意译，保留引文块与链接 |
| benchmark | 基准测试 | 词汇表已有 |
| stacktrace | 堆栈跟踪 | -race / panic 输出语境 |

## 翻译难点与对策

1. **"process" 一词多义**：原文 "An operation that does not block in Go will run in a separate *process* called a *goroutine*"、"communication between different processes"。这里 process ≈ 执行流，译"流程"会丢掉"独立执行单元"感，译"进程"又是 OS 歧义。对策：首现译作"（独立的）执行流程"，后文视语境用"流程"或"goroutine"，保证不出现 OS"进程"。
2. **泡茶比喻**：生活化、节奏感强（连续动作短句）。对策：保留连串动作的并列节奏，"put the kettle on" 译"把水壶坐上/烧上水"，英式冷幽默 "blankly staring at the kettle" 译出呆滞盯壶的画面感。
3. **两个 aside 小节标题**："A quick aside into the concurrency universe..." / "... and we're back." 对策："岔开一句，进一下并行的宇宙……" / "……好了，我们回来了。" 保留省略号呼应。
4. **"Or pretend that you did. Up to you."**：作者的自嘲式玩笑，直译保趣："或者就当它出现过，随你。"
5. **"long and scary" / "scary lines of text"**：口语化，译"又长又吓人""吓人的一大段文字"。
6. **blockquote（Go 1.22 注记）**：技术密度高（language spec / go.mod / toolchain / loop variable semantics）。术语：language spec = 语言规范；go directive = `go` 指令；toolchain = 工具链（保留英文更稳，随文括注一次）。
7. **代码/输出块**：全部逐字节保留；两处 Go 注释（`// Send statement`、`// Receive expression`）随章翻译；`// Output:` 无；`fatal error:`、`WARNING: DATA RACE`、堆栈原文一律不动。
8. **链接**：`[DI]: dependency-injection.md` 保留目标文件名（跨章内部链接规则）；3 条外链 URL 原样保留；章首代码目录链接指向 quii 原仓库 `concurrency` 目录。
9. **无图片**。Gitbook 转义：源文干净，无 `\.` 类残留；注意译文别引入。
10. **斜体强调**：原文大量 `_word_` 斜体（didn't、blocking、goroutine、anonymous functions、send statement、receive expression、race condition、data race 等），译文一一对应 `*词*`。
