# 01 — 内容分析：Revisiting time, with testing/synctest

## 内容概述

Go 1.25 新包 `testing/synctest` 的专章，是 Time 章（docs/time.md，已译）的续篇。

- 开篇回顾 Time 章的困境：扑克 CLI 的盲注提醒用 `time.AfterFunc` 调度，测试只能靠
  依赖注入 + spy 断言"调度了什么"，真正调用 `time.AfterFunc` 的代码从未被测过。
- 讲 `testing/synctest` 最小必要知识：bubble（气泡）、虚拟时钟、**持久阻塞**、
  `synctest.Test` / `synctest.Wait`。
- TDD 逐步重写 `StdOutAlerter`：
  1. 真实时间版（6 秒）→ 说明为何不可行；
  2. 只包进气泡、删掉 sleep → 失败（时钟不会自己走）；
  3. sleep 加回来 → 通过且瞬时，但 `-race` 抓出数据竞争（sleep ≠ 同步）；
  4. 加 `synctest.Wait()` → 修复；
  5. "什么都不该发生"测试 → `Wait()` 无界导致时钟越过断言时刻，又现竞争；
  6. 重构为基于 channel 的 `NewAlerter`（select+default、阻塞接收天然同步），
     不再需要 Wait/Sleep/锁。
- 总结所学、四个 gotcha、延伸材料，最后是一节"本章由 AI（Claude）辅助写作"的
  说明（作者口吻，须完整保留）。

## 结构（18 个代码块，0 图片）

H1 + 3 个相对链接章节引用（time.md、http-handlers-revisited.md×2、select.md）。
外链：quii 仓库 synctest 目录、pkg.go.dev/testing/synctest×2、
go.dev/blog/codelab-share、go.dev/blog/synctest、go.dev/doc/go1.25。

## 本章新术语（全书未出现过）

| 英文 | 定名 | 备注 |
|---|---|---|
| bubble | 气泡（bubble） | synctest 核心概念，首现括注 |
| fake clock / fake time | 虚拟时钟 / 虚拟时间 | 首现括注 fake clock |
| durably blocked | 持久阻塞（durably blocked） | 首现括注 |
| race detector | 竞态检测器 | `-race` 工具 |
| deadlock | 死锁 | |
| timer heap | 定时器堆 | 运行时实现细节 |
| spike（throwaway program） | 用完即弃的小程序（spike） | AI 写作说明里出现 |
| flaky / flakiness | 时灵时不灵／不稳定 | |
| stand-in | 替身（此处指内存替身） | |

沿用的既有术语：盲注（blind）、提醒/调度提醒（alert/schedule）、spy、
依赖注入、数据竞争、竞态条件、goroutine、channel、副作用、子测试等。

## 翻译难点

1. **与 Time 章呼应**：标题 "Revisiting time" → "重访时间"（仿已译
   "用泛型重访数组与切片"）；Time 章已有"关于扑克，知道这些就够了"，本章
   "Just enough information on testing/synctest" → "关于 testing/synctest，
   知道这些就够了"，刻意保留呼应感。
2. **TDD 循环标题沿用既定译法**：先写测试 / 试着运行测试 / 写足够的代码让测试
   通过 / 重构 / 总结（docs/time.md 原样）。
3. **幽默/口语点**：`Ouch`（哎哟）、`let's earn it`（先吃苦头）、
  `out of habit`（习惯使然）、`Worth sitting with for a second`（值得停下来细品）、
  `Very nice.`（短句独立成段）、`that's on me, not the tool`（是我的问题，不是工具的）。
4. **长难段**：`Wait()` 无界导致竞态的解释段（timer heap / goroutine 11 并发）逻辑
   链长，须保住因果与强调（*while*、*guarantees*、*for*）。
5. **AI 写作说明**：作者的自嘲与坦率是本节灵魂，不能译成公文体。
6. 代码块 4 含 4 条 Go 注释需翻译；其余 17 块逐字节保留（包括 DATA RACE 输出、
   `ok github.com/quii/...` 模块路径 v1–v4）。

## 链接处理

三个链接目标章节**均已译出**（docs/time.md、docs/http-handlers-revisited.md、
docs/select.md），按规范一律用站内相对链接（`time.md` 等），无需（英文原版）注记。
