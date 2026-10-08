# 01 — 内容分析：Dependency Injection（learn-go-with-tests）

## Content Summary

- **主题**：以"问候某人"的小示例引出**依赖注入**（dependency injection）：把打印依赖从 `fmt.Printf`（写死 stdout）改为通过函数参数注入 `io.Writer`，从而让函数可测试、可复用（测试里的 `bytes.Buffer`、真实程序的 `os.Stdout`、HTTP handler 的 `http.ResponseWriter`）。
- **作者**：Chris James（quii），语气延续前几章：轻松、直接、对"企业级 Java 味"的 DI 玄学有明显调侃（"You don't need a framework"）。
- **核心论点**：DI 不需要框架、不会过度复杂化设计；它只是"把依赖当参数传进来"这么朴素的事，收益是可测试性 + 关注点分离 + 复用。
- **前置依赖**：原文首段声明需要先读 structs 一节，需要接口的基本理解——本章是 `io.Writer` 接口在全书的首个正面展示。
- **结构**：约 1100 词，9 个标题（含 2 个三级），11 个代码块（Go 源码、编译错误输出），无图片；外链 4 个（原仓库 di 目录、pkg.go.dev/fmt#Printf、localhost:5001、Amazon 图书页），另有 1 个章内相对链接指向 structs 章。

## Terminology

全书术语表（EXTEND.md）已覆盖本章大部分项：

| 英文 | 中文 | 备注 |
|------|------|------|
| dependency injection (DI) | 依赖注入 | 术语表词；标题定"依赖注入" |
| inject | 注入 | "inject the dependency" → 注入依赖 |
| interface | 接口 | 首现按"接口"语境加注（本章特别说明） |
| concrete type | 具体类型 | interface 的对照面，本章新术语 |
| separation of concerns | 关注点分离 | 本章特别说明指定译法 |
| side effect | 副作用 | |
| dependency | 依赖 | |
| stdout | 标准输出 | 首章已用"标准输出" |
| mock | mock | 保留英文 |
| global state | 全局状态 | |
| database connection pool | 数据库连接池 | |
| service layer | 服务层 | |
| HTTP handler | HTTP handler | handler 保留英文 |
| general purpose | 通用 | "general purpose interface" → 通用接口 |
| command line app | 命令行应用 | |
| web server | web 服务器 | |

保留英文：`io.Writer`、`fmt.Printf`、`fmt.Fprintf`、`os.Stdout`、`bytes.Buffer`、`http.ResponseWriter`、`http.Request`、`http.HandlerFunc`、`http.ListenAndServe` 等代码标识符一律反引号。

## Tone & Style

- 延续样章的 conversational 基调：第二人称、短句、步骤因果链清晰。
- 幽默点：开头"a lot of misunderstandings"的无奈口吻；"which is just a fancy word for pass in"（注入 = 传参的高级说法，自嘲式祛魅）；"What about mocking? I hear you need that for DI and also it's evil"（标题里的社区流言梗）；"so if you enjoyed this, go buy it!"（荐书直球）。

## Translation Challenges

- "(which is just a fancy word for pass in)" → 译出祛魅的幽默："（说白了就是'传个参数'的高级说法）"。
- "**inject** the dependency of printing" → "注入打印这个依赖"。
- "hard-wired into a function" → "硬编码在函数里"。
- "decoupling where the data goes from how to generate it" → "把'数据去哪儿'与'怎么生成数据'解耦"。
- "I hear you need that for DI and also it's evil" → 保留听来的流言口吻："我听说搞 DI 就得用它，而且它还很邪恶"。
- `os.Stdout` 实现了 `io.Writer` 的推导段落：逻辑链（Printf 调 Fprintf 传 os.Stdout；Fprintf 第一参数是 io.Writer ⇒ os.Stdout 满足 io.Writer）必须译得严丝合缝。
- 首行代码块 `func Greet(name string)` 是纯函数片段（无 package/import），与原文一致保留。
- 章首链接指向原仓库 `tree/main/di`；正文还有对 structs 章的相对链接 `./structs-methods-and-interfaces.md`，verify 只校验 http(s) 链接，但按规则行内链接应保留原样。
- 原文 Gitbook 转义：`\(...\)` 多处（inject 括注、via an interface 等）、`_a lot_` `_Motivated by our tests_` 等下划线斜体——译文需去转义、斜体用 `*…*`。
