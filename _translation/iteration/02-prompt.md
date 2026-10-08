# Iteration 章特有约束

- H1 定为：迭代。
- 代码块共 10 个：8 个 Go + 2 个 text 输出块。Go 块内仅 `//` 注释随章翻译（只有 Benchmark 结构示例块有 3 行注释：setup→准备工作、code to measure→要测量的代码、cleanup→清理工作）；text 输出块与原文逐字节一致。
- 术语：benchmark=基准测试（术语表词，不加英文注）；`b.Loop()`、`b.N`、`strings.Builder`、`WriteString`、`Repeat`、`ExampleRepeat` 保留英文；`+=` = Add AND 赋值运算符（名称保留英文）；immutable=不可变（immutable）首现括注一次。
- TDD 步骤标题与 hello-world 章同族措辞：先写测试 / 试着运行测试 / 写出刚好能让测试运行的最少代码，并检查失败测试的输出 / 写足够的代码让测试通过 / 重构。
- 悬挂引用链接 `[stringsBuilder]` 改为行内链接套在 `strings.Builder` 上（URL：https://pkg.go.dev/strings#Builder），章末引用定义行删除。
- 去除 Gitbook 转义：`\(on my computer\)` → （在我的电脑上）。
- 幽默保留：_保持纪律！_、"相当不错了！"、"随便折腾生产代码"、"摆弄摆弄它们"。
- `go test -bench=.` / `go test -bench="."` / `go test -bench=. -benchmem` 均为行内代码，原样保留。
