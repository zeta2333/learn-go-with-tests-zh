# 01 — 内容分析：Mocking（learn-go-with-tests）

## Content Summary

- **主题**：以"从 3 倒数到 Go!"的 `Countdown` 程序贯穿全章，讲 **mock（测试替身中的 spy）与依赖注入**：`time.Sleep` 拖慢测试且未被测到 → 把睡眠依赖抽成 `Sleeper` 接口 → 测试里注入 `SpySleeper`/`SpyCountdownOperations` 记录调用 → `ConfigurableSleeper` 用函数字段注入 `time.Sleep` 本身 → 最后论述"mock 是否邪恶"与测试该测行为而非实现。
- **作者**：Chris James（quii），语气轻松直接；本章是全书关于"何时该 mock、何时是设计出了问题"的核心论述章。
- **结构**：标准 TDD 循环标题（先写测试/试着运行测试/写最少量代码/写足够代码/重构）多轮重复；末尾 Wrapping up 总结 + Bonus（Go 1.23 迭代器改写 `Countdown`）。
- **前置依赖**：直接引用上一章 dependency-injection（`io.Writer`、`bytes.Buffer` 注入手法）。
- **代码块 37 个**（Go 源码 + 编译器/测试错误输出 + 1 个程序输出），Go 块内**无 `//` 注释**，全部需逐字节一致；正文另有 1 个**缩进式**文档引用块（Go 1.23 range-over-func 签名，含弯引号，不属 fenced 块，verify 不查，仍按原文保留英文）。
- **外链 5 个 + 相对链接 1 个**：原仓库 `tree/main/mocking`、`dependency-injection.md`（跨章内部链接，保留上游文件名）、stackoverflow（abstraction vs generalization）、wikipedia DRY、martinfowler TestDouble（出现 2 次）、tip.golang.org/go1.23。

## Terminology

| 英文 | 中文 | 备注 |
|------|------|------|
| mock | mock | 术语表：保留英文 |
| spy / Spies | spy | 保留英文；_spy sleeper_、_Spies_ 斜体对应 |
| test double | 测试替身 | 术语表词；首现加注英文 |
| stub | stub | 术语表：保留英文（总结节出现一次） |
| dependency injection (DI) | 依赖注入 | 沿用上一章译名 |
| interface | 接口 | 上一章已注，本章不再展开加注 |
| subtest | 子测试 | 术语表词 |
| magic values | 魔法值 | 与 hello-world"魔法字符串"一致 |
| named constants | 具名常量 | |
| plumbing | 管线 | "overall plumbing working right" → 整体管线搭对 |
| thin slice / thin vertical slices | 细窄的纵向切片 | 保留"切片"意象（与 Go 切片双关无害） |
| rabbit holes | 兔子洞 | 保留比喻，首现轻点"越陷越深" |
| "big bang" approach | "大爆炸"式的做法 | 保留引号比喻 |
| backtick syntax | 反引号语法 | |
| de-facto | 事实标准 | |
| red flag | 危险信号 | |
| "Mocking considered harmful" | 《Mocking considered harmful》（mock 有害论） | 戏仿 Dijkstra 名文，标题保留英文加括注意译 |
| can get in the sea | 请它直接滚进大海 | 英式吐槽 get in the sea，保幽默直译 |
| handywork | 手艺 | 原文拼写 handywork（通常 handiwork），照常译 |
| type alias | 类型别名 | Bonus 节，Go 特有概念首现加注 |
| iterator / yield | 迭代器 / 产出 | yield 保留英文（Go 1.23 术语） |

保留英文：`Countdown`、`Sleeper`、`SpySleeper`、`DefaultSleeper`、`ConfigurableSleeper`、`SpyTime`、`SpyCountdownOperations`、`time.Sleep`、`io.Writer`、`bytes.Buffer`、`os.Stdout`、`fmt.Fprint/Fprintln`、`iter.Seq[T]`、`write`/`sleep` 常量名等代码标识符。

## Tone & Style

- 第二人称教学、短句、步骤因果链严格对应；作者口头禅式感叹（"Perfect!"、"be amazed at your handywork"）保住不译平。
- 幽默点：慢测试"ruin developer productivity"的宣言式加粗；"configure that sleepiness however they like"（那份"瞌睡"）；《Mocking considered harmful》的戏仿梗；"can get in the sea"英式毒舌；Martin Fowler 引文的冷幽默（"only on projects that you want to succeed"）；"Your test is too concerned with implementation details" 系列的自查清单口吻。
- 重点章节：**"But isn't mocking evil?" 一整节是全书论述核心**，措辞务必清楚、有力，不牺牲准确性换俏皮。

## Translation Challenges

- 同一套 TDD 小节标题重复多轮，译文必须**每轮完全一致**（先写测试/试着运行测试/……），便于读者形成节奏。
- "spy on the calls"、"one spy for them both"：spy 作动词/名词混用，中文需顺（"spy 住这些调用"/"为它们俩做_一个_ spy"）。
- 错误信息块 `sleeper.Sleep undefined ... but does have sleep` 与正文"非常清晰的错误信息"呼应，正文要点出 `Sleep`/`sleep` 大小写之别（方法未建）。
- "just break it!"（故意把代码改坏验证测试有效性）+ 括注 commit 提醒，语气是鼓励式的，不能译成警告腔。
- 三条"mock 滥用征兆"bullet 各带一条对策子 bullet，嵌套层级与原文严格对应。
- Bonus 节缩进文档块为英文原文引用（含弯引号 “range”），保留不动；`iter.Seq[T]` 说明句的"键/值"措辞与文档块 K/V 对应。
