# 01 分析 — Intro to acceptance tests

## 内容概述

全书"Testing fundamentals"篇第一章。作者从 `$WORK` 的真实痛点（K8s 部署时服务被杀导致在途 HTTP 请求失败）引入"优雅关停"（graceful shutdown），介绍了 `http.Server.Shutdown` 与 `os/signal.Notify`，以及他自己写的 `go-graceful-shutdown` 包；随后论证手动测试的不可持续，引出验收测试（acceptance test）的概念：黑盒、只测公开接口、对内部重构免疫。列优点/缺点清单，讲 lead time 与测试金字塔，最后演示如何用 Go 标准库（`os/exec` 编译并拉起被测程序、`syscall.SIGTERM`、轮询端口）写自动化验收测试，并以"给开源包配验收测试"收尾。

## 结构

- 开头 4 段引子（无"本章所有代码"链接，包链接在正文中段出现）
- Just enough info about Kubernetes
- If you do not have grace / When you have grace / How to have grace（grace 三连小节）
- Graceful shutdown package（含 main 示例）
- Tests and feedback loops
- Acceptance tests（What are they? / Benefits / Potential drawbacks / Lead time?）
- How to write basic acceptance tests（步骤 / 编译运行程序的大代码块 / The acceptance test(s) / Small investment with a big pay-off）
- Wrapping up（Taking it further / The next chapter / Improving the quality of open-source）
- Recruitment plug for `$WORK`

## 代码块（6 个）

1. `main()` 示例（gracefulshutdown 装饰器）——2 条 `//` 注释需译
2. 同一 `main()` 重复出现（测试程序）——同样 2 条注释
3. `acceptancetests` 包大代码块——1 条注释需译
4. `TestGracefulShutdown`——4 条注释需译
5. `assert.CanGet`——无注释
6. `shell` 终端输出——逐字节保留

## 本章新术语（英 → 中定名）

| 英文 | 定名 | 备注 |
|---|---|---|
| graceful shutdown | 优雅关停 | 首现加注英文 |
| grace / grace period | 体面 / 宽限期 | 标题双关用"体面"，宽限期用行业通用"宽限期" |
| in-flight (requests) | 在途的/处理中的 | |
| termination lifecycle | 终止生命周期 | |
| black-box test | 黑盒测试 | 首现加注 |
| functional test | 功能测试 | 首现加注 |
| lead time | 前置时间 | 首现加注英文，正文有定义 |
| Test Pyramid | 测试金字塔 | |
| Decorator pattern | 装饰器模式 | |
| headless web browser | 无头浏览器 | |
| north-star | 北极星 | |
| boilerplate | 样板代码 | |
| always be shippable | 随时可发布 | |
| out of the box | 开箱即用 | |
| DORA metrics | DORA 指标 | 保留 DORA |
| regression | 回归 | 术语表已有语境，防回归 |
| incidents channel | 事故告警频道 | |

已有术语：验收测试、单元测试、辅助函数、断言、反馈循环（沿用 hello-world"反馈循环"）、goroutine/channel 保留英文、`pod` 保留英文 Pod。

## 翻译难点

1. **grace 双关**：小节标题三连（do not have grace / have grace / how to have grace）+ grace period + graceful shutdown。策略：技术名词"优雅关停"，标题双关用"体面"（"不留体面/留足体面/如何做到体面"），正文首现处用电话比喻自然搭桥。
2. **k8s 拟人引语**与 **Server.Shutdown 官方文档引文**均为散文引文，按规范意译（非代码块），函数/类型名保留反引号。
3. **代码块内注释**按规则①随章翻译，但字符串字面量（log 消息、错误消息）逐字节保留，含上游笔误（见下）。
4. 幽默点：熄灯走人（lights out）、"你内心的工程师应该浑身不自在"、"写一坨垃圾验收测试照样过"、招聘软广的随意语气。
5. 无跨章内链、无图片；所有链接均为外链，原样保留。

## 原文疑似笔误（保留不改，报告用）

1. 代码块内 `url = "<http://localhost:" + port` —— Gitbook 自动链接符 `<...>` 泄漏进 Go 代码，上游应为 `"http://localhost:"`。按规则逐字节保留。
2. 错误消息 `"cannot run temp converter: %s"` —— 从旧版温度转换章节复制粘贴的残留，与服务器无关。保留。
3. 正文 "wait for it listen on 8080" —— 漏 to，语法笔误，译文按正确语义译。
4. "the test will fail" 前后时态混用（would/will）——不影响翻译。
