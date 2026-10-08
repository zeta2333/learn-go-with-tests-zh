# 01 — json 章分析

## 内容概述

上一章（http-server）的延续：给记分服务器加 `/league` 端点。三条主线：
1. **路由**：用 `http.NewServeMux` 把 `/league` 和 `/players/` 分发给不同 handler，几轮重构后把 router 提升为 `PlayerServer` 的字段，最后改为**嵌入** `http.Handler`。
2. **嵌入（embedding）**：结构体嵌入接口；Effective Go 引文；缺点（会暴露嵌入类型的全部公开方法/字段）。
3. **JSON 编解码**：`json.NewDecoder(...).Decode(&got)` / `json.NewEncoder(w).Encode(...)` 的对称性；为什么不直接断言 JSON 字符串；`content-type` 响应头；最后把 `GetLeague` 补进 `InMemoryPlayerStore` 并过集成测试。

标准 TDD 循环骨架（先写测试 → 试着运行测试 → 写足够的代码让测试通过 → 重构）重复四轮。

## 本章新术语（英→中定名）

| 英文 | 定名 | 备注 |
|---|---|---|
| routing / router | 路由 / 路由器 | `router` 作变量名不译 |
| `ServeMux` (request multiplexer) | 请求多路复用器 | 首现括注 |
| embedding / type embedding | 嵌入 / 类型嵌入 | 与 html-templates 章「嵌入（embed）」一致 |
| endpoint | 端点 | 沿用 app-intro |
| marshal/unmarshal | 本章未出现，用 Encoder/Decoder 叙事 | serialize→序列化，deserialize→反序列化 |
| league / league table | 联盟 / 联盟积分表 | 首现括注（league） |
| content-type header | `content-type` 响应头 | |
| integration test | 集成测试 | 开发者常识，不加注 |
| stub（动词） | 预置（stub） | 名词保持英文 |
| spy | spy | 沿用 mocking 章，保持英文 |
| boilerplate | 样板代码 | |
| brittle | 脆弱 | |
| path variables | 路径变量 | |
| product owner | 产品负责人 | app-intro 已注过，不再注 |

## 翻译难点

- 大量代码块（39 个）必须逐字节一致；错误输出含 `json-and-io/v4` 模块路径，照抄。
- "commit some sins" 幽默 → 「先造点孽」一类口语化表达，保住自嘲语气。
- Effective Go 引文块：引文本身译出，出处链接保留。
- 上一章链接 `http-server.md` **尚未翻译** → 按规范改指上游 GitHub 并标（英文原版）。
- 无图片。外链仅 GitHub 与 golang.org 文档若干。

## 原文疑似笔误

- 正文 "`InMemoryStore` is implemented"（代码里类型叫 `InMemoryPlayerStore`）——上游笔误，正文照抄不动（行内代码）。
- 编译错误输出中的模块路径 `github.com/quii/learn-go-with-tests/json-and-io/v4` 与本章目录 `json` 不一致——上游输出本身如此，代码块照抄。
