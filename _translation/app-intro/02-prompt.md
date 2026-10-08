# 02 本章翻译约束 — app-intro

## H1

`# 构建一个应用`（主控指定，固定）

## 术语与定名

- product owner → **产品负责人**，首现括注英文：产品负责人（product owner）。这是后文各章反复登场的幽默角色，定名要适合反复出现。
- endpoint → 端点；routing → 路由；embedding → 嵌入；persist → 持久化。均为常识词，不加注。
- TDD 不再加注（hello-world 已注全称）。
- "backed by tests" 沿用全站既定说法"有测试护航"。

## 六章预告的定名与链接（全为前向引用，未译）

链接一律改为 `https://github.com/quii/learn-go-with-tests/blob/main/<file>`，链接后紧跟"（英文原版）"；列表末尾补一行斜体译注（仿 pointers-and-errors.md:704 的承诺句式）：

| 原文 | 链接 | 定名 |
| --- | --- | --- |
| HTTP server | http-server.md | HTTP 服务器 |
| JSON, routing and embedding | json.md | JSON、路由与嵌入 |
| IO and sorting | io.md | IO 与排序 |
| Command line & project structure | command-line.md | 命令行与项目结构 |
| Time | time.md | Time |
| WebSockets | websockets.md | WebSockets |

## 幽默点对策

- "hopefully digested"：保留"希望你（真的）消化了"的调侃。
- "as our product owner dictates"：译出"产品负责人发话/想要什么就加什么"的口吻，不译成公文腔。
- 整体保持导语的轻快短句节奏，五段不合并、不拆移。

## 体例

- 无代码块；`time` 包名保留反引号。
- 列表项的分隔符 " - " 译作"——"。
- 不用直角引号；中英之间加空格。
