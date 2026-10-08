# 01 — scaling-acceptance-tests 章分析

## 内容概述

本章是《Intro to acceptance tests》的后续（该章尚未翻译），讲如何用"契约（specification，作者用词）—DSL—驱动器（driver）—系统"四层结构把验收测试与实现细节解耦，使验收测试只在行为变化时才变。全程以 go-specs-greet 项目实操：

1. 好坏验收测试的解剖（意外复杂性 vs 本质复杂性、关注点分离）
2. 第一个系统：HTTP API（Testcontainers + Docker 起容器、driver 实现 Greeter 接口）
3. 第二个系统：gRPC（Protocol Buffers、protoc 生成代码、sync.Once 重构 driver）
4. 重构：adapters/、domain/ 目录结构、合并 Dockerfile、-short 拆分测试
5. 迭代新增 Curse 功能；作业：HTTP 版 Curse + 单元测试驱动领域逻辑
6. 总结：规格即文档、Cucumber、Screenplay Pattern、GOOS

标题原文 "Scaling Acceptance Tests (and light intro to gRPC)"，任务指定 H1 为「扩展验收测试」。

## 章内结构（H2 清单，须一一对应）

1. Prerequisite material（前置材料）
2. Recap（回顾）
3. Anatomy of bad acceptance tests（坏验收测试的解剖）→ H3 Tight-coupling
4. Anatomy of good acceptance tests（好验收测试的解剖）→ H3 On types of complexity / Separation of concerns / Testing on steroids（下有 4 个 H4）/ Acceptance tests changing for the right reasons / Acceptance tests as a method for software development（下有 H4 The perils of bottom-up）
5. Enough talk, time to code
6. Write the test first / First system: HTTP API（H3 在其前面）
7. Try to run the test / Write the minimal amount of code... / Write enough code to make it pass / Refactor / Reflect —— 此 TDD 循环多轮重复（HTTP、gRPC、Curse 各一轮），标题相同会出现多次
8. A slight diversion in to the "adapter" design pattern
9. Making the change easy（H3）/ Consolidating Dockerfile（H3）/ Separating different kinds of tests（H3）/ When should I write acceptance tests?（H3）
10. Iterating on our work
11. Implementing Curse for the HTTP server
12. Enhance both systems by updating the domain logic with a unit test
13. Wrapping up → H3 What has been covered / Further material

注意 "Write the test first" 等标题出现 3 次（HTTP、gRPC、Curse 各一轮），"Refactor" 出现 3 次，"Reflect" 2 次，"Try to run the test" 3 次。

## 本章新术语（定名见 02-prompt.md）

- specification（作者用 specification 而非 contract 作为核心词，任务说明里的 "contract" 在原文中以 "specifications" 出现）→ 待定
- driver → 驱动器
- acceptance test (AT) → 验收测试
- accidental complexity → 偶然复杂性
- essential complexity → 本质复杂性
- tight-coupling → 紧耦合
- brittle / flaky → 脆弱 / 不稳定（flaky 指时好时坏）
- headless web browser → 无头浏览器
- bike-shed → 生产力闹剧式争论（bike-shedding 梗）
- staging environment → 预发布环境
- dev/prod parity → 开发/生产环境一致性
- DSL (domain-specific language) → DSL（领域特定语言）
- north-star → 北极星（指引方向的目标）
- top-down / bottom-up → 自顶向下 / 自底向上
- adapter pattern → 适配器模式
- ports and adapters → 端口与适配器（六边形架构）
- blast-radius → 爆炸半径（改动波及面）
- Testcontainers → Testcontainers（保留）
- Protocol Buffers / protoc → Protocol Buffers / protoc（保留）
- remote procedure call (RPC) → 远程过程调用（RPC）
- service definition → 服务定义
- test pyramid → 测试金字塔
- short flag / testing.Short() → -short 标志
- red step → 红灯步骤（TDD 的失败阶段）
- Example Mapping → Example Mapping（BDD 实践名，保留）
- Screenplay Pattern → Screenplay Pattern（保留，或"剧本模式"）
- Cucumber → Cucumber（保留）
- GOOS → GOOS（《测试驱动开发面向对象的软件方法》？通常保留 GOOS 缩写）
- iteration 0 → 第 0 次迭代
- green → 测试变绿

## 翻译难点

1. **同一标题多次出现**：每轮 TDD 循环的 H2 标题相同，译文需保持一致（同标题同译法），但按规则"标题意译为自然中文"，每处可按上下文微调吗？不行——同一原文标题应统一译名，避免读者混淆。决定：`Write the test first`→先写测试；`Try to run the test`→试着运行测试；`Write the minimal amount of code for the test to run and check the failing test output`→写最少的代码让测试跑起来，并检查失败输出；`Write enough code to make it pass`→写足够的代码让测试通过；`Refactor`→重构；`Reflect`→复盘。
2. **"specification" vs 任务给的 "contract"**：原文全篇用 specification，无 contract。任务说明中"契约（contract）"应映射为"规格（specification）"？需谨慎：任务写 "'contract' 译'契约'（首现加注英文）"。原文没有 contract 一词。核心词 specification 定名"规格说明"还是"规格"？决定用"规格"（简洁，"规格说明"太啰嗦），首现加注英文。这需要在报告中说明偏离任务字面要求的原因：原文未出现 contract。
   - 再想想：任务说讲"用契约（contract）解耦数据源测试（Postgres/内存实现）"——这更像 intro-to-acceptance-tests 或另一章的内容？本章无 Postgres/内存实现内容。任务描述与本章实际内容有出入（可能模板化描述）。按原文实况翻译，specification→规格。
3. **幽默点**：
   - "engineers bike-shed over whether something should be an `<article>` or a `<section>` for the billionth time" — bike-shedding 梗 + 夸张
   - "Hold your nose"（捏着鼻子，忍着恶心先写烂代码）
   - "Commit as many sins as necessary to get the test passing"（引用块）
   - "I test in prod"（自嘲梗，链接标题）
   - "Dev/Prod parity is, at best, a white lie" — white lie 双关（善意的谎言/白色的谎）
   - "Wouldn't it be nice..." 反问语气多处
   - "A lot of fancy words for something relatively simple"（对设计模式的挖苦）
   - "Don't be lazy"
   - "Nice!" 口语感叹
4. **维基百科引用块（adapter pattern）**：大段引用含多个内链，链接 URL 必须原样保留；文字意译。引用块内有 `[[1\]](https://en.wikipedia.org/wiki/Adapter_pattern#cite_note-HeadFirst-1)` 上标引用标记——处理为[1]式保留链接。注意 `\]` 是 Gitbook 转义，需清除（写成 `[1]`）。
5. **代码块大量且长**：40+ 个代码块（go/dockerfile/protobuf/makefile/shell/text/tree），逐字节一致。tree 输出里有 `|       ├──` 混用 `|` 和 `│` 的字符，原样保留。
6. **`go_specs_greet` 等标识符**、错误输出必须逐字节一致。文本输出块（如编译错误、测试失败输出）不译。
7. **正文中的 inline 代码引用**（`./greeter_server_test.go` 等）保持原样。
8. **en-dash / 斜体**：原文用 `_different_`、`*before*` 混用两种斜体标记，mkdocs 都支持，保持一一对应即可（规则说斜体与原文对应；保留原标记字符更安全，verify 不查斜体，但保持一致是好习惯）。
9. "Would you not hesitate to introduce..." 反问句。
10. "Its a big first step" 原文有 "It's"。原文 "the red step's rules"。
11. 最后一段有个孤立的 `-->`（HTML 注释残留，疑似上游笔误），不能译掉？它在正文段落末尾（further material 列表最后一项），是上游遗留的 HTML 注释未闭合标记。verify 不检查。保留原样最安全（原样字符），也可以去掉。规则说"原文即有的笔误都不改"是针对代码块的；正文里这个 `-->` 是明显笔误。为保内容忠实，保留 `-->` 会显示出来很难看；它是未闭合的 HTML 注释开头 `<!--` 缺失……实际上 mkdocs 渲染时裸 `-->` 会原样显示。决定：保留原样（忠实），报告中列为疑似笔误。嗯，但译文站显示一个 `-->` 很丑。上游就是这样的。保留并报告。
12. 长句多（Farley 设计描述、复杂从句），需拆成短中文。
13. "test doubles (e.g. fakes, mocks)" → 测试替身（如 fake、mock）——术语表已有。
14. "business perspective" → 加粗"业务视角"。
15. 数字/格式：`20 minutes later`、`0.181s` 等保持。
16. 原文疑似笔误清单：
    - "It's assumed at this point in the book you're comfortable..."（正常）
    - "A slight diversion in to the..." → "in to" 应为 "into"（笔误）
    - "We require to provide a 'greeter service'" → 中式英语，应为 "We are required to provide" 或 "We need to provide"（按意思译）
    - "the Server" 大小写摇摆（GreetServer/our `Server`）
    - 最后的孤立 `-->`
    - "routeing" 英式拼写（保留意思即可，正文译文无所谓）
    - go.mod 相关：option go_package = "github.com/quii/adapters/grpcserver"; —— 应为 github.com/quii/go-specs-greet/adapters/grpcserver（上游笔误，代码块不改）
    - "grpcServer.RegisterGreeterServer"（应为 grpcserver，正文列表里，代码块外）——按原文？正文里的标识符大小写……原文 "registers it with `grpcServer.RegisterGreeterServer`, along with a `grpc.Server`" 在正文中带反引号。保留原样（不改原文笔误），可报告。
    - "In HTTP Handlers Revisited, we discussed how important it is for HTTP handlers should only be responsible..." — 语法错误（is for X should be），按意思译。
    - 谷歌输出 `TestGreeterHandler` vs 测试函数名 `TestGreeterServer` 不一致（上游输出样例如此，保留）。
17. 图片：6 张 imgur 外链，全部原样保留（含 alt 文本翻译）。无本地图片需求。TDD-outside-in.jpg 不属于本章（那是 math 章的图），本章的 TDD 由外向内概念图是 imgur 的 pxTaYu4/t5y5opw/UYqd7Cq 三张。
18. 链接处理：
    - intro-to-acceptance-tests（gitbook URL）→ 改为上游 GitHub URL +（英文原版）标注，因该章未翻译
    - http-handlers-revisited（已是 GitHub URL）→ 加（英文原版）标注
    - 其余外链（YouTube、GOOS 官网、Docker、Testcontainers、Selenium、martinfowler、cucumber、go-rod、wikipedia、quii.dev 等）原样保留
19. 章首没有"本章所有代码"链接，而是文中 "the finished code for this chapter on GitHub" → go-specs-greet 仓库，保留。
