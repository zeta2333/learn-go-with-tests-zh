# 01 — Context 章分析

## 内容概述

本章讲如何用标准库 `context` 管理长时间运行的、占用资源的进程（通常跑在 goroutine 里）：当引发它的动作被取消或失败时，要通过一致的方式把这些进程停下来。

教学主线是一个经典场景：web server 收到请求后触发一个可能很慢的取数过程（`Store.Fetch`），用户在数据取回前取消了请求，要确保后台进程被告知放弃。按 TDD 循环走了三轮：

1. 第一轮：接口加 `Cancel()`，server 手动调用 `store.Cancel`。spy 里用 `context.WithCancel` + `time.AfterFunc` 模拟 5ms 后取消；实现用 goroutine + `select` 对 `ctx.Done()` 做竞速。
2. 重构后反思：手动取消不够惯用（idiomatic）。引 Go doc 与 Go Blog：context 应沿调用栈传播，由下游自行响应取消。于是把 `Fetch` 改为接收 `ctx context.Context`，返回 `(string, error)`。
3. 第二、三轮：happy path 先行，再处理错误路径——需要自造 `SpyResponseWriter` 断言"取消时不应写出任何响应"；最终 server 只传 `r.Context()` 并忽略取消带来的 error。

结尾 "Wrapping up"： covered 列表；讨论 `context.Value`（引 Michal Štrba 玩笑、Jack Lindamood "inform, not control"）；Additional material 两条外链。

## 关于"River 例子"的核实

任务提示里问"讲 context-aware 的 River 例子？"——**本章没有 River 例子**。全章示例只有 web server + `Store`（spy 测试替身）。River 不在原文中出现，无需处理。

## 本章新术语（英 → 中定名）

| 英文 | 定名 | 备注 |
|---|---|---|
| cancellation | 取消 | 首现加注（cancellation） |
| deadline | 截止时间 | 首现加注（deadline）；文中仅以 `WithDeadline` 出现 |
| timeout | 超时 | `WithTimeout` 处 |
| happy path | 正常路径 | 首现加注（happy path） |
| context-aware | 感知 context 的 | 未在原文出现原词，本章按语义处理 |
| derive (a Context) | 派生 | derive new Context values → 派生新的 Context 值 |
| request-scoped context | 请求范围的 context | |
| propagate | 传播 / 一路传递 | cancellation 传播用"传播" |
| call stack / call-stack | 调用栈 | |
| idiomatic | 惯用 | "is it idiomatic?" → 符合 Go 的惯用法吗 |
| type-safety | 类型安全 | |
| untyped map | 无类型的 map | |
| trace id | 追踪 ID | |
| smell | 坏味道 | "it's a smell" → 一种坏味道（smell） |
| ergonomics | 用起来的体验 | ramification 句里意译 |
| roll your own | 自己动手写 | "roll our own spy" |

既有术语沿用 glossary：spy/mock/ Goroutine/channel/select 保持英文；测试替身、辅助函数、断言、接口、结构体、并发等已定名。

## 翻译难点

1. **英文引文块（blockquote）多**：Go Blog 两段、go doc 一段、Štrba 一句、Lindamood 一句。样章与 structs 章的先例是把引文译成中文（保留链接与强调）。全部意译，保留 `>` 结构与强调位置。
2. **第一轮实现"故意做错"的语气**："This makes this test pass but it doesn't feel good, does it?" 的自嘲反问要保住；"Remember to be disciplined with TDD" 的自律语气与 hello-world 章《纪律》一节呼应，用"守住纪律/自律"。
3. **技术表述准确性**："context 携带取消信号与请求范围数据"这类概括不能失真；`Done()` 返回"当 context 结束（done）或被取消时收到信号的 channel"要照原文逻辑说，不加戏。
4. **`Select` 竞速的说法**："effectively race the two asynchronous processes" → "让两个异步过程赛跑/竞速"；第二处 "race each other to determine what we return" 同理，两处措辞可呼应。
5. **代码块逐字节一致**：22 个代码块（19 个 go + 3 个纯输出），其中 go 代码块内 `//` 注释仅一处 `// todo: log error however you like`（按规范译成中文注释）。Go 代码用 tab 缩进，换行为 LF。
6. **标题**：H1 定为 `Context`；四个 TDD 循环 H2 沿用全书定名：先写测试 / 试着运行测试 / 写足够的代码让测试通过 / 重构。
7. **笔误核查**：原文 "can't finish a`Fetch` before"（`a` 与反引号间缺空格）为上游排版瑕疵，译文按正常排版写；"functional signatures" 应为 "function signatures"，按语义译"函数签名"。未发现坏链。
8. **无图片**。外链 6 个 URL 均需原样保留（blog.golang.org/context 出现 3 次）。
