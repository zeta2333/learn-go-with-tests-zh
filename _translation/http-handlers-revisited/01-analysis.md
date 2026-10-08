# 01 — 分析：Revisiting HTTP Handlers（再探 HTTP Handlers）

## 内容概述

"Questions and answers"（问答）篇的一章。以社区里"怎么测带 MongoDB 依赖的 http 处理器"这一真实提问为引子，
用单一职责原则与关注点分离重新设计处理器：把请求解析/校验、调用 `UserService`、按结果响应三件事留下，
其余（数据库连接、密码哈希、插入记录）推给依赖注入的接口背后。结论：**Go 的 HTTP 处理器就是函数**，
测试难不是测试的问题而是设计的问题。

结构：引言（含漫画一张）→ 一个例子（Registration 大函数）→ 处理器该做什么 → Go 的处理器
（HandlerFunc + teapot 示例）→ 调用 ServiceThing（新设计 + 测试）→ 数据库代码呢（作弊！）
→ 更健壮可扩展的设计 → 总结。

- 代码块 6 个（均为 go），其中 4 个含需翻译的 `//` 注释；无 `// Output:`；无终端输出块。
- 图片 1 张：`.gitbook/assets/amazing-art.png`（上游本地图片 → 拷入 docs/assets/，引用改 `assets/amazing-art.png`）。
- 内链 4 个目标章（http-server、structs-methods-and-interfaces、dependency-injection、error-types）均已译出，
  链接目标保持上游同名文件，无锚点。
- 无 Gitbook 转义残留；无自动链接泄漏。

## 本章新术语（英 → 中定名）

| 英文 | 定名 | 备注 |
|---|---|---|
| HTTP handler | HTTP 处理器 | 沿用 http-server 章 |
| single responsibility principle | 单一职责原则 | 新，首现加注英文 |
| separation of concerns | 关注点分离 | 沿用术语表 |
| adapter | 适配器 | 沿用 http-server 章 HandlerFunc 文档引文的译法 |
| `ServiceThing` / `ImportantBusinessLogic` | 保留英文代码名 | 原文戏拟的占位名 |
| catch-all | 一律兜底（返回） | "catch-all handler of a 500" |
| persistence layer | 持久层 | 新 |
| magic beans | 魔法豆 | 《杰克与魔豆》梗，保留幽默 |
| `ResponseRecorder` | 保留英文代码名，行文称"记录器" | 沿用 http-server 章 |
| business logic | 业务逻辑 | 通用词，不加注 |
| decouple / coupled | 解耦 / 耦合 | 通用词 |

## 翻译难点

1. 大量半口语半原则性的句子（"That is too much." / "You're cheating!"），要保住随口聊天的劲儿，不译成论文腔。
2. `(the example always sends a 400 BadRequest which I don't think is right)`、`(again for terseness/laziness)`
   这类括号里的自我吐槽必须保住幽默。
3. "Reader, take a breath and look at the code above" —— 对读者喊话的节奏要留住。
4. 文档引文两处：HandlerFunc 描述须与 http-server 章逐字一致；ResponseWriter 描述为首现。
5. 源文小笔误："is focused a small number of concerns"（缺 on）、"What is a HTTP Handler and what should it do ?"
   （问号前多空格）——按语义正常译，不必复刻。
