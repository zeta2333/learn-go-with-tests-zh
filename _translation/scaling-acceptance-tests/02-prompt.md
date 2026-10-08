# 02 — 本章翻译约束（scaling-acceptance-tests）

## 章标题

H1：`# 扩展验收测试`
（原文标题含副题 "(and light intro to gRPC)"——H1 按任务指定只用主标题；正文不另补副题。）

## 核心术语定名（本章新词）

| 英文 | 定名 | 说明 |
|---|---|---|
| specification | 规格 | 本章核心词，首现"规格（specification）"；代码标识符 `specifications` 不译 |
| driver | 驱动器 | 首现加注英文；"plug in a driver" 译"接入驱动器" |
| acceptance test (AT) | 验收测试 | 沿用术语表；缩写 AT 首现"验收测试（AT）"，后文可用"验收测试" |
| accidental complexity | 偶然复杂性 | 首现加注 |
| essential complexity | 本质复杂性 | 首现加注 |
| domain logic | 领域逻辑 | 术语表 domain code=领域代码 |
| tight-coupling | 紧耦合 | |
| brittle | 脆弱 | 改个实现就挂 |
| flaky | 时灵时不灵 | flaky 特指不稳定、随机挂 |
| headless web browser | 无头浏览器 | |
| bike-shed | 围绕小事没完没了地争论 | bike-shedding 梗，意译 |
| staging | 预发布环境 | |
| dev/prod parity | 开发/生产环境的一致性 | "at best a white lie" 意译 |
| DSL | DSL | 首现"DSL（领域特定语言）" |
| north star | 北极星 | 指引方向的比喻 |
| top-down / bottom-up | 自顶向下 / 自底向上 | |
| adapter pattern | 适配器模式 | |
| ports and adapters | "端口与适配器"（ports and adapters） | 架构风格名，首现加注 |
| blast-radius | 爆炸半径 | 指改动波及面，加引号 |
| test pyramid | 测试金字塔 | |
| red step | 红灯步骤 | TDD 失败阶段 |
| iteration 0 | 第 0 次迭代 | |
| iteration | 迭代 | |
| remote procedure call | 远程过程调用（RPC） | 原文 (r)emote (p)rocedure (c)all 的强调结构需在译文体现"远程过程调用" |
| service definition | 服务定义 | |
| Protocol buffer compiler | Protocol Buffer 编译器 | |
| Screenplay Pattern | Screenplay Pattern（剧本模式） | 保留英文首现括注 |
| Example Mapping | "Example Mapping" | BDD 技法名保留 |
| GOOS | GOOS | 书名缩写保留，首现写书名《Growing Object-Oriented Software》（Go 语言之外的经典，保留英文名不加中文译名，或括注"《面向对象的软件、测试驱动开发》"？GOOS 无通行中译名，保留原名即可） |
| safety net | 安全网 | |
| white lie | 善意的谎言 | "Dev/Prod parity is, at best, a white lie" |
| greet / curse | 问候 / 诅咒 | Greet/Curse 函数名不译，正文动词意译 |

关于任务说明中的 "contract→契约"：本章原文并未出现 contract 一词，核心概念原文用 specification，故定名"规格"，不做"契约"。报告中说明。

## 复现标题统一译法（出现多次，务必一致）

- `Write the test first` → `## 先写测试`
- `Try to run the test` → `## 试着运行测试`
- `Write the minimal amount of code for the test to run and check the failing test output` → `## 写最少的代码让测试跑起来，检查失败的输出`
- `Write enough code to make it pass` → `## 写足够的代码让它通过`
- `Refactor` → `## 重构`
- `Reflect` → `## 复盘`

## 其他约束

- 代码块逐字节一致；Go 代码块 `//` 注释随章翻译（如 `//todo: we shouldn't redial...`、`// set to false if you want less spam...`、Dockerfile 的 `#` 注释**不译**——注意规则只说 Go 的 `//` 注释随章翻译，Dockerfile `#` 与 protobuf `//`？Dockerfile 注释属"代码块内注释"，规则明文只放行 Go 的 `//`，为稳妥 Dockerfile 的 `#` 注释不译。生成代码里的 `// GreeterServer is the server API...` 是引用的生成代码（Go），可译——但它是展示生成产物，译了更贴合"随章翻译"规则。决定：Go 块内的 // 注释一律翻译（含生成代码展示），Dockerfile `#` 不译。
- `// Output:` 不适用本章。
- 维基百科引用块：保留为 `>` 引用块，内链 URL 全部原样；`[[1\]](url)` 处理成 `[1](url)`（清除转义）。
- 直角引号禁用；中文与代码/英文间加空格。
- `-->` 孤立残留：保留原样，报告。
- 原文 "github.com/quii/adapters/grpcserver"（go_package 行）疑似笔误，代码块不改，报告。
- 链接文字加注：（英文原版）只用于指向未翻译章节的链接（intro-to-acceptance-tests、http-handlers-revisited）。
- imgur 六图原样保留，alt 文本翻译。
