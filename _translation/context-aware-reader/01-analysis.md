# 01 分析 — Context-aware Reader（q-and-a 篇）

## 内容概述

问答体例短章（约 300 行），演示如何用 TDD 开发一个"支持 context 取消"的 `io.Reader`：
Mat Ryer 与 David Hernandez 在 Pace Dev Blog 文章的实践。

结构：
1. 开场 + 代码仓库链接
2. `io.Reader` 快速复习（`Read(p []byte) (n int, err error)`）
3. "context aware" 的含义：Reader 速度无保证，可能需要中途取消；组合 `context.Context` 与 `io.Reader`
4. 测试挑战：平时 Reader 都是交给 `json.NewDecoder` 等函数用；本章要直接验证"取消后读不到剩余内容"
5. 先写正常路径测试（无取消，`strings.NewReader("123456")` 分两次读 "123"、"456"）
6. TDD 循环两轮：`NewCancellableReader` 从 `return rdr` → 返回 `readerCtx` 结构体 → `Read` 先查 `ctx.Err()` 再委托
7. 总结：小接口易组合；委托模式（delegation pattern）；先包装 delegate 并断言其原有行为

代码块 14 个（3 个 go 接口/测试演示 + 6 个 go 渐进实现 + 5 个终端输出），无图片。

## 本章新术语

| 英文 | 定名 | 说明 |
|---|---|---|
| context-aware reader | 支持 context 的 Reader | H1 按主控要求保留英文 `Context-aware Reader` |
| delegation pattern | 委托模式 | 维基引文一并译出 |
| delegate（名词） | 被委托的对象 | 代码标识符 `delegate` 保留英文；正文动词"委托" |
| compose / composed | 组合 | 小接口易于组合 |
| wrap | 包装 | `NewCancellableReader` 的语义 |
| re-use | 复用 | — |

沿用已有术语：cancellation=取消、deadline=截止时间、derive=派生（Context 章已定）、
happy path=正常路径（本章首现加注英文）、standard library=标准库、production code=生产代码。

## 翻译难点

- 问答体例开头的对话感："Context aware reader?" / "Context aware?" 两级设问标题要保留设问语气。
- TDD 循环小标题（先写测试 / 试着运行测试 / 写最少的代码… / 写足够的代码…）须与 Context 章
  既有译法对齐（"先写测试""试着运行测试""写足够的代码让测试通过"）。
- 幽默点："I know, I know, this seems silly and pedantic"——自嘲式让步，保住语气。
- 原文笔误数处（见报告），按语义顺译，代码块一律不动。
- `delegate` 字段名出现在代码里，正文首次提及处加轻量括注，避免读者迷失。
