# 01 — Sync 章分析

## 内容概述

本章用一个"并发安全计数器"贯穿 TDD 循环，讲三件事：

1. 常规 TDD：先写 `Counter` 的单测（`Inc`/`Value`），最小实现，重构出 `assertCounter`。
2. 并发安全：新增"1000 个 goroutine 并发自增"的失败测试，引出 `sync.WaitGroup`（等待组）；借输出 `got 939, want 1000` 解释 `c.value++` 实为"读—自增—写"三步、步骤交错导致更新丢失，即竞态条件（race condition）；用 `sync.Mutex` 加锁修复。
3. 两个进阶话题：① 反对把 `Mutex` 嵌入结构体（嵌入会把 `Lock`/`Unlock` 变成公开 API，造成耦合隐患）；② `go vet` 能查出"按值拷贝互斥锁"，改用指针 + 构造函数 `NewCounter`；③ 新版上游内容：`sync/atomic`（`atomic.Int64` 等）作为保护单值的无锁替代方案。

结尾总结 sync 包要点，并引 Go wiki「Mutex or Channel」给出选型口诀：传所有权用 channel，管状态用互斥锁。

## 本章新术语（全书术语表尚未收录）

| 英文 | 定名 | 说明 |
|---|---|---|
| wait group | 等待组 | 任务说明指定；`sync.WaitGroup` 保留原样 |
| Mutex / mutual exclusion lock | 互斥锁 | `Mutex` 作为类型名保留英文 |
| race condition | 竞态条件 | 首现加注（race condition） |
| embed / embedding | 嵌入 | Go 结构体嵌入，标题"嵌入"即可 |
| public interface | 公开接口 | |
| coupling / couple | 耦合 / 耦合到 | |
| constructor | 构造函数 | 指 `NewCounter` 一类函数 |
| invariant | 不变式 | 首现加注（invariant） |
| lock-free | 无锁 | |
| atomic / atomicity | 原子的 / 原子性 | |
| interleave | 交错 | 描述 goroutine 步骤交错 |
| go vet | go vet | 工具名保留 |

已有术语沿用：goroutine、channel、并发、结构体、方法、指针、零值、断言、辅助函数、子测试、基准测试。

## 翻译难点

- **重复的 H2 标题**：`Write the test first` 与 `Try to run the test` 各出现两次，是上游刻意的 TDD 循环节奏，须按原文重复，不得合并改写；沿用 select 章译法「先写测试」「试着运行测试」保持跨章一致。
- **句子式标题**：`I've seen other examples where the sync.Mutex is embedded into the struct.` 是 H2，需整句意译。
- **三处文档引文（blockquote）**：WaitGroup、Mutex 的 godoc 描述与 Go wiki 引文，按 context 章先例译成中文，代码标识符（Add/Done/Wait/Lock/Unlock、sync.Mutex）保留。
- **三种代码块要区分对待**：`go` 块中 `//` 注释随章翻译（`// 1. read` 等）；无语言标记的终端输出/goroutine 交错示意块逐字节保留；`// Output:` 本章没有。
- **幽默点**：`Go experts like us`（自嘲）、`This looks nice but ... bad and wrong`（英式毒舌）、`your poor users`、`nefarious code`、`This seems like a really bad idea` 图注——都要保住语气，不译平。
- **图片**：全章仅一张图，外链 imgur（`https://i.imgur.com/SWYNpwm.png`），不在上游 `.gitbook/assets/` 中（该目录只有 math 章的时钟图），按规则保留外链原样，无图可拷。
- **原文疑似笔误**：Refactor 一节正文写 "a small assertion function `assertCount`"，下方代码实际定义的是 `assertCounter`。按规则笔误不改，报告中上报。

## 结构对应备忘

- 两个相邻 ```go 块（Refactor 节）须保持为两个独立块。
- 内部链接 `concurrency.md` 保持上游同名文件；外链 8 处全部原样。
- `_probably_`、`_looks_`、`_really_` 等斜体强调对应保留。
