# 01 — websockets 章分析

## 内容概述

"Build an application" 篇最后一章。把扑克应用的命令行功能搬进浏览器：

1. 用 `html/template` 让 `/game` 返回 HTML 页面（含内嵌 JS，前端用原生 `WebSocket` 连 `/ws`）。
2. 引入外部库 `gorilla/websocket`，用 `httptest.NewServer` + `websocket.DefaultDialer.Dial` 测试驱动出服务端的 WebSocket 处理（upgrade/握手、读消息、记胜者）。
3. 把 `Game` 接口复用进 `PlayerServer`；`BlindAlerter.ScheduleAlertAt` 加 `io.Writer` 参数，让盲注提醒能发往任意目的地。
4. 让 `playerServerWS` 实现 `io.Writer`，把 WebSocket 连接本身作为盲注提醒的输出目的地。
5. 测试异步行为：`within`（goroutine + select + `time.After` 超时）、`retryUntil` 轮询重试，替代 `time.Sleep`。
6. 收尾总结。

## 本章新术语（全书未出现过）

| 英文 | 定名 | 说明 |
|---|---|---|
| WebSocket / WebSockets | WebSocket（不注） | 协议名，保留英文 |
| handshake | 握手（handshake） | 首现注一次 |
| upgrade / Upgrade | 升级 / `Upgrade`（代码） | "we're not shaking hands yet" 等处 |
| full-duplex | 全双工（full-duplex） | Wikipedia 引言块 |
| blind bet / blind value / blind alert | 盲注 / 盲注值 / 盲注提醒 | command-line、time 章未译，本章首立；扑克标准译法"盲注" |
| league table | 联盟积分表 | 沿用 json.md 既有定名 |
| product owner | 产品负责人 | 沿用 app-intro/io/json 既有定名（不再加注） |
| canned message | 预设消息 | GameSpy 配置的固定消息 |
| polling | 轮询 | 总结处 |
| symlink | 符号链接 | 开发者常识，不加注 |
| markup | 标记 | HTML 标记 |

沿既有约定：spy/mock/stub/Gorilla 等保留英文；"store" 不译。

## 翻译难点 / 对策

- **代码块 55 个**，语言标记有 `go`/`html`/无标记三种，逐一与原文对齐；`html` 块内嵌 JS 含 `'ws://'` 字符串，必须逐字节一致。
- Go 注释翻译点：`//todo: Don't discard the blinds messages!`（两处）、`// (rather than a minute)`、`// etc`——按规则①随章翻译，verify.py 会忽略注释差异。
- Wikipedia 引言块（blockquote）按 html-templates 章 godoc 引言先例整体意译。
- 幽默点："Sorry folks. Lobby O'Reilly…"（游说 O'Reilly 出钱写《Learn JavaScript with tests》）、"We committed many sins"、"nasty, horrible, working software"、"as if by magic"、"Hooray!"、"This seems too easy!"。
- TDD 循环节标题沿用系列定式：先写测试 / 试着运行测试 / 写足够的代码让测试通过 / 写最少的代码让测试能运行，并检查失败的测试输出 / 重构；"Wrapping up" 沿用 scaling-acceptance-tests 章"收尾"。
- 无图片、无跨章链接、无 Gitbook 转义符——正文只有 5 个外链（quii 仓库 ×1、html/template 文档 ×2、Wikipedia ×1、gorilla ×1），全部原样保留。
