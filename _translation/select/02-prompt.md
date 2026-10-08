# 02 — 本章特有约束

## 标题与加注
- H1：`Select`（Go 关键字，保留英文，不意译）
- 首现加注（一次）：goroutine（Go 的轻量级并发单元）、channel（通道）、匿名函数（anonymous function）、阻塞（blocking）、文件描述符（file descriptor）、不稳定（flaky）、正常情况（happy case）、异常路径（sad path）、DRY（消除重复）
- 不再加注：零值（hello-world 已注）、mock/fake、并发、依赖注入
- `select`、`defer`、`go`、`chan`、`make`、`var`、`nil`、`string`、`int`、`bool` 等 Go 关键字/类型一律保留英文 + 反引号
- "race" 一律译"竞速"；原文未提 data race，严禁自行引入"数据竞争"字样；`WebsiteRacer`/`Racer`/`ping` 为标识符，保留英文
- "synchronise processes" 译"同步流程"（不用"进程"，避免 OS 进程歧义），三处（引言列表、节标题、正文）保持一致

## 代码与输出
- 14 个代码块与原文逐字节一致（组装脚本从 source.md 原样注入，含 tab 与空行；本章无 Go 注释，无注释翻译空间）
- 行内错误输出照抄：`./racer_test.go:14:9: undefined: Racer`、`racer_test.go:25: got '', want 'http://www.quii.dev'`、`./racer_test.go:37:10: assignment mismatch: 2 variables but Racer returns 1 value`
- 第 10 块是无语言标记的 ``` 围栏（FAIL 输出，含子测试名 `TestRacer/returns_an_error_if_a_server_doesn't_respond_within_10s`），原样保留
- 代码内字符串（子测试名、错误消息）一律不动

## 格式
- TDD 循环标题沿用 arrays-and-slices 章：先写测试 / 试着运行测试 / 写最少的代码让测试能运行，并检查失败的测试输出 / 写足够的代码让测试通过 / 重构；第二轮同名标题保持一致；Wrapping up → 总结
- 原文斜体 `_..._` 统一为 `*...*`（anonymous function、at the end of the containing function、real、care、we just want to signal we are done、blocking、multiple、the exact response times、listen to them）；加粗（**this is also how you would write a _real_ HTTP server in Go**，含内嵌斜体）与列表、编号列表（原文三项都是 `1.`）一一对应
- 引号一律弯引号""（"竞速""零值""获胜""真正的""我做完了""happy"）；禁用「」
- 外链 5 条原样保留：quii 仓库 select 目录、golang.org/pkg/net/http/#Client.Get、#Response、httptest、play.golang.org

## 风格
- conversational；幽默保真对策：
  - "not too hung-up on getting things perfect first time" → 别一上来就执着于一步到位
  - "The syntax may look a bit busy but just take your time." → 这段语法看着可能有点密，慢慢来就好
  - "Play with these sleeps to deliberately break the test." → 动手改改这些 sleep 的时长，故意把测试弄挂看看
  - "let's _listen to them_" → 听听测试怎么说（拟人保住）
  - "For such a simple bit of logic, this doesn't feel great." → 就这么一点简单的逻辑，这个代价让人不太舒服
- 技术准确性优先：`time.Sleep`＝收到请求后先睡 N 再响应；`time.After`＝计时结束往 channel 发一个信号；`close(channel)`＝"完成了"的信号；不添不减
