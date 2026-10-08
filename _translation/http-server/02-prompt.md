# http-server 章 — 翻译约束

## 术语定名（本章生效）

- handler → **处理器**；`http.Handler`、`Handler` 接口、`http.HandlerFunc`、`ServeHTTP`、`http.ResponseWriter`、`http.Request` 等代码标识符不译
- handler 在"HTTP handler"语境下也译处理器（DI 章译作"编写 HTTP handler 时"——本章统一为"处理器"，与 scaling-acceptance-tests 章一致）
- integration test → 集成测试（首现括注 integration test）
- Test Pyramid → 测试金字塔（The Test Pyramid），原文为斜体无链接，照排斜体
- spy / stub / mock / goroutine / map / interface（代码语境）按全书术语表
- Red, green, refactor → 红、绿、重构
- in-memory → 内存版 / 内存中
- "Faking it" → 保留英文引语 + 括注意译

## 呼应依赖注入章

- 原文 "From the DI chapter, we touched on HTTP servers with a `Greet` function" 译为指向 `[依赖注入一章](./dependency-injection.md)` 的内链，`Greet`、`fmt.Fprint`、`ResponseWriter` 表述与该章定稿一致（该章用了"你正是用这个 writer 把响应*写*出去的""`http.ResponseWriter` 同样实现了 `io.Writer`"）
- 链接：`[依赖注入一章](./dependency-injection.md)`（该章已译，普通内链）
- sync 章已译且标题保留英文：`[Sync 一章](./sync.md)`

## 幽默点对策

1. Kent Beck 引语："Make the test work quickly, committing whatever sins necessary in process." → "尽快让测试通过，过程中不管犯下什么'罪行'。"（sins 译"罪行/作孽"，后文 commit sins 呼应）
2. "commit sins, then refactor (and then commit to source control)" —— commit 一语双关（作孽/提交），标题译"先作孽，再重构（然后再 commit 到版本控制）"，保住文字游戏
3. "Sometimes I heavily roll my eyes…" → "有时候 TDD 布道者说……我会狠狠翻白眼"，自嘲语气保住
4. "Chicken and egg" → "先有鸡还是先有蛋"
5. "Not great, but until we store data that's the best we can do." → 语气别译平
6. "Great! You've made a REST-ish service." → "漂亮！你已经做出了一个类 REST 的服务。"

## 硬性注意

- 所有代码块逐字节一致（Go 注释 `//server.go`、`//server_test.go` 等文件名注释保留原样，不算需要翻译的英文句子；verify 会剔除 `//` 注释，但保持原样最稳）
- 错误输出、测试输出逐字节保留（含 `Pepper's_score`、`got '', want '20'` 等）
- 无图片、无 Gitbook 转义、无 `<http://` 泄漏
- 章首代码链接：`https://github.com/quii/learn-go-with-tests/tree/main/http-server`
- pkg.go.dev / golang.org 外链原样保留（原文用的 `golang.org/pkg/...` 旧域名，不改）
