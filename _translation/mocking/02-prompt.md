# 02 — 翻译提示词：Mocking（本章特有约束）

## 任务

将《Learn Go with Tests》`mocking.md` 由英文精翻为简体中文（zh-CN），出版级质量。样章 `_translation/hello-world/translation.md` 为文风基准。

## 本章特别说明（来自主控）

- H1 章标题定为：**Mocking**（保留英文）。
- **mock/stub/spy 按术语表保留英文**；"spying" 一节讲 spy 测试替身，spy 作名词/动词都要顺。
- 倒计时（countdown）示例贯穿全章，`Countdown`、"Go!"、`countdownStart`/`finalWord` 等一律英文原样。
- **"But isn't mocking evil?" 一节是全书论述重点**："何时该 mock"的每条诊断与对策措辞务必清楚准确，幽默不压过信息。
- `time.Sleep` 与注入依赖讲测试耗时的部分（"Our tests take 3 seconds to run" 一组 bullet）：**慢测试毁生产力**是加粗宣言，语气要重。
- "测试替身（test double）"术语表已有，总结节首现处加注英文一次。

## 术语表（本章涉及的必须一致）

mock、stub、spy（保留英文）；测试替身（test double）；依赖注入（dependency injection/DI）；接口（interface）；子测试（subtest）；魔法值（magic values）；具名常量（named constants）；管线（plumbing）；兔子洞（rabbit holes）；"大爆炸"式的做法（"big bang" approach）；危险信号（red flag）；类型别名（type alias）；迭代器（iterator）；产出（yield）。

保留英文不译：`Countdown`、`Sleeper`、`SpySleeper`、`DefaultSleeper`、`ConfigurableSleeper`、`SpyTime`、`SpyCountdownOperations`、`time.Sleep`、`io.Writer`、`bytes.Buffer`、`os.Stdout`、`fmt.Fprint`、`fmt.Fprintln`、`iter.Seq[T]`、《Mocking considered harmful》。

## 硬性规则（本章落地）

1. **代码块 37 个**与原文逐字节一致（Go 块内无注释，零差异）；其中 31 块含 tab 缩进与空行（块 26/27 的 `want := []string{...}`、块 31 末尾多一空行），以脚本从 source.md 原样注入，不手打。
2. 正文中的**缩进式文档引用块**（Go 1.23 range-over-func 三行签名，含弯引号）保留英文原样。
3. 章首"本章的所有代码都可以在这里找到"链接保留指向 `tree/main/mocking`。
4. 跨章内部链接 `[the previous section](dependency-injection.md)` → `[上一章](dependency-injection.md)`，目标文件名不动。
5. 外链 URL（stackoverflow、wikipedia DRY、martinfowler TestDouble×2、tip.golang.org/go1.23）原样保留。
6. 标题意译（多轮重复的小节标题每轮**逐字一致**）：Write the test first → 先写测试；Try and run the test → 试着运行测试；Write the minimal amount of code for the test to run and check the failing test output → 写最少量的代码让测试跑起来，并检查失败的测试输出；Write enough code to make it pass → 写足够的代码让它通过；Refactor → 重构；## Mocking（章中）→ 该谈谈 Mocking 了；Still some problems → 还有问题；Extending Sleeper to be configurable → 让 Sleeper 变得可配置；Cleanup and refactor → 清理与重构；But isn't mocking evil? → 可 mock 不是邪恶的吗？；But mocks and tests are still making my life hard! → 可 mock 和测试还是让我的日子很难过啊！；Can't I just use a mocking framework? → 我就不能用个 mock 框架吗？；Wrapping up → 总结；More on TDD approach → 再聊聊 TDD 方法；### Mocking（总结内）→ Mocking；Bonus - Example of iterators from go 1.23 → 附加内容 —— Go 1.23 的迭代器示例。
7. 去除 Gitbook 转义（本章正文少，留意 `_italic_` 全部转 `*…*`）；直角引号一律不用，弯引号""。
8. 段落顺序、TDD 步骤因果链、bullet 嵌套层级严格对应，不合并、不拆移。

## 幽默点对策

- "be amazed at your handywork" → "为自己的手艺惊叹吧"（自嘲式骄傲，保住）。
- "configure that sleepiness however they like" → "想怎么配置这份'瞌睡'都行"。
- "Slow tests ruin developer productivity" → "**慢测试毁掉开发者的生产力**"（宣言加粗，一字不软）。
- "You question TDD and make a post on Medium titled "Mocking considered harmful"" → 保留英文标题戏仿梗 + 括注"（mock 有害论）"。
- "can get in the sea" → "都请它直接滚进大海"（英式毒舌直译，不加解释）。
- Martin Fowler 引文 → "什么时候该用迭代式开发？只在你希望成功的项目上，才用迭代式开发。"（冷幽默靠"只在你希望成功"落地，署名 Martin Fowler 单独一行留在引用块外）。
- "just break it!" → "那就故意把它弄坏！"（鼓励式，随后括注先 commit 的提醒语气放轻）。
