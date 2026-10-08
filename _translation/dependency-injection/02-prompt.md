# 02 — 翻译提示词：Dependency Injection（本章特有约束）

## 任务

将《Learn Go with Tests》`dependency-injection.md` 由英文精翻为简体中文（zh-CN），出版级质量。样章 `_translation/hello-world/translation.md` 为文风基准。

## 本章特别说明（来自主控）

- **依赖注入（dependency injection）** 为术语表词，H1 章标题定为：**依赖注入**。
- 本章用"问候某人"示例引出通过函数参数注入 `io.Writer`。
- **`io.Writer` 首现按"接口"语境加注**：在 `Fprintf` 签名引出 `io.Writer` 处，轻量点一次"接口"含义（如"`io.Writer`——标准库里的一个接口"），不展开教程式解释。
- "separation of concerns" 译 **"关注点分离"**。

## 术语表（本章涉及的必须一致）

依赖注入（dependency injection/DI）、注入（inject）、接口（interface）、具体类型（concrete type）、关注点分离（separation of concerns）、副作用（side effect）、依赖（dependency）、全局状态（global state）、数据库连接池（database connection pool）、服务层（service layer）、标准输出（stdout）、通用（general purpose）、命令行应用（command line app）、web 服务器（web server）。

保留英文不译：mock；`io.Writer`、`fmt.Printf`、`fmt.Fprintf`、`os.Stdout`、`bytes.Buffer`、`http.ResponseWriter` 等代码标识符；HTTP handler 中 handler 保留英文。

## 硬性规则（本章落地）

1. 代码块 12 个、终端/编译错误输出与原文逐字节一致；本章 Go 代码块无注释，无需翻译注释。
2. 章首"本章的所有代码都可以在这里找到"链接保留指向 `tree/main/di`。
3. 正文相对链接 `./structs-methods-and-interfaces.md` 原样保留。
4. 外链 URL（pkg.go.dev/fmt#Printf、http://localhost:5001、Amazon）原样保留。
5. 标题意译：Write the test first → 先写测试；Try and run the test → 试着运行测试；Write the minimal amount of code for the test to run and check the failing test output → 写最少量的代码让测试跑起来，并检查失败输出；Write enough code to make it pass → 写足够的代码让它通过；Refactor → 重构；More on io.Writer → 再聊聊 `io.Writer`；The Internet → 互联网；Wrapping up → 总结。
6. 去除 Gitbook 转义：`\(...\)`、`\[\]`、`\_`、`\.`,斜体保持 `*…*` 与原文对应。
7. 段落顺序、TDD 步骤因果链严格对应，不合并、不拆移。

## 幽默点对策

- "It does not overcomplicate your design" / "You don't need a framework"：开头四条 bullet 是对 DI 玄学的祛魅宣言，译得干脆有力。
- "(which is just a fancy word for pass in)" → "（说白了就是'传个参数'，只是叫法高级了点）"。
- "What about mocking? I hear you need that for DI and also it's evil" → "那 mock 呢？听说搞 DI 离不开它，而且它还很邪恶？"——保留以讹传讹的口吻，正文 "(and it's not evil)" → "（它并不邪恶）"。
- "go buy it!" → "就去买一本吧！"
