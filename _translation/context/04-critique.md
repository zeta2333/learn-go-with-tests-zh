# 04 — Context 章审校诊断（对照原文，只诊断）

代码块、链接、输出样例经 verify.py 校验已一致。以下为行文与准确性诊断。

## 准确性

1. **"The function `Server` takes a `Store`… Store is defined as:"** — 原文第二处 "Store" 无反引号，初译写成 "`Store` 的定义如下"，违反"行内代码与原文一一对应"。→ 去掉反引号。
2. **"It's important that you derive your contexts … throughout the call stack for a given request."** — 初译"沿着一次请求的整个调用栈"，"for a given request" 译"一次请求"偏弱。→ "沿着相应请求的整个调用栈一路传播下去"。
3. **"…derive a new `cancellingCtx` from our `request` which returns us a `cancel` function"** — 初译"它会同时返回一个 `cancel` 函数"，主语含糊（是派生动作返回，不是 ctx 返回）。→ "同时得到一个 `cancel` 函数"。
4. **"use `select` to effectively race to the two asynchronous processes"** — 初译丢了 "effectively"。→ "实际上就是让这两个异步过程赛跑"。
5. **"One of the main points of `context` is that it is a consistent way of offering cancellation."** — 初译"一个核心意义……用一致的方式来提供取消"语序别扭。→ "`context` 的主要意义之一就在于：它提供了一种一致的取消方式。"
6. **go doc 引文中的加注** — 初译给 WithCancel/WithDeadline/WithTimeout 都加了中文注（"WithCancel（取消）……"），超出需要且不对称。按本章约束只需 deadline 首现加注。→ 改为 "WithCancel、WithDeadline（截止时间 deadline）、WithTimeout（超时）或 WithValue"。
7. **"wait for that goroutine to finish its work or for the cancellation to occur"** — 初译"要么 goroutine 完成工作，要么取消发生"，"取消发生"生硬。→ "要么等 goroutine 完成工作，要么等取消发生"。
8. **"relies on the downstream functions to respect any cancellations"** — 初译"依赖下游函数去尊重……取消"，"尊重"是翻译腔。→ "由下游函数自己去响应可能发生的任何取消"。
9. **"We surely shouldn't be calling `Cancel()` before we fetch on _every request_"** — 初译"再去 fetch"中英混杂且小写动词悬空。→ "再去取数据"（`Cancel()` 已带反引号，语义不损）。
10. **"assert that it does not get cancelled"** — 初译"断言它不会被取消"，"它"指代不明（距 store 太远）。→ "断言 store 不会被取消"。

## 中文表达

11. **收获列表第 3 条** — "并利用 goroutine……借助它取消自身"，"利用/借助"叠用。→ "如何编写接收 `context` 的函数，借助 goroutine、`select` 和 channel 利用它取消自身"。
12. **"coupling of map keys from one module to another"** — 初译"在一个又一个模块之间产生耦合"啰嗦。→ "在模块与模块之间制造耦合"。
13. **标题格式** — "### 那 `context.Value` 呢？"：原文标题中 context.Value 无反引号，按行内格式一一对应原则去反引号。

## 已核实无需改动

- "Our happy path should be... happy." 译"我们的正常路径这下应该……正常了"，双关保住。
- Štrba 玩笑、"(Pause for a moment…)"旁白、"Feeling a bit uneasy? Good."节奏均到位。
- 取消（cancellation）首现加注在首段 ✓；截止时间（deadline）加注在第 6 条修正后落于 go doc 引文 ✓。
- 5 处引文意译与 structs 章先例一致；所有链接 URL 原样保留 ✓。
- "This makes this test pass but it doesn't feel good, does it?" 反问语气保住 ✓。
- 术语一致：spy/goroutine/channel/select 保持英文；`context` 一律反引号英文 ✓。
