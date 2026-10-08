# 04 — 批判性审校：初译稿 vs 原文（只诊断）

## Accuracy

- **"Interesting!" 语气添加**：初译"有意思吧！"多了寻求认同的"吧"，原文只是发现真相时的感叹。→ 改"有意思！"
- **"专为……而生"过度文学化**："because it's a great general purpose interface for 'put this data somewhere'"，"专为……而生"偏书面夸张，与 conversational 口语基调稍隔。→ 改"专管'把这份数据放到某个地方去'"。
- **"供某个服务层使用，那测试多半很难写"**：原文 "If you have a global database connection pool for instance that is used by some kind of service layer, it is likely going to be difficult to test and they will be slow to run."——"some kind of service layer"的泛指口气丢了，且"难写"应为"难测"（difficult to test 指代码难测）。→ 重组："如果某个服务层用到了一个全局的数据库连接池，相关代码多半很难测，测试跑起来也慢。"
- **"可以长这样"**："Just to recap, here is what that function could look like"——"可以长这样"生硬（"可以"是情态误植）。→ "大概长这样"。
- **"要求"与"期望"不一致**：同一句里 `Fprintf` "期望第一个参数……"，随后又译"要求（expects）的正是一个 `io.Writer`"。→ 统一"期望"。
- **DI 首现缺依托**：正文后段和标题直接用"DI"，初译虽在首段写了"依赖注入（DI）"，符合要求，保留；无需修改。（复核项，非缺陷。）
- 其余逐段核对：11 个代码块与原文逐字节一致（唯一允许的差异——`Printf` 源码块内的 `//` 注释已按要求翻译）；两处行内错误输出（`di_test.go:16`、`di.go:14:7`）原样保留；4 个外链 + 相对链接 `./structs-methods-and-interfaces.md` 均在。

## Native Voice

- **量词误用**："DI 多半就是你需要的那件工具"——"件"不作工具的量词。→ "那个工具"。
- **bullet 平行结构**：三条 bullet 的加粗引导语，原文 "Test our code" / "Separate our concerns" / "Allow our code to be re-used..." 均为动词短语；初译"**关注点分离**"是名词，破坏平行。→ 改"**分离关注点**"（保留术语字根，符合"separation of concerns → 关注点分离"的定名精神）。
- **"一个 `io.Writer`——标准库 `io` 包里定义的一个接口（interface）"**：连用两个"一个"，重复。→ "一个 `io.Writer`——`io` 包里定义的一个接口（interface）"。
- **"期望第一个参数传给它什么呢"**："传给它"赘余。→ "希望第一个参数传进来的是什么"。
- **"有了一点熟悉"**：搭配别扭（熟悉不说"一点"）。→ "有了几分熟悉"。
- 其余表达（"多得很""说白了就是'传个参数'""听编译器的话""派上了用场""拿你的函数试试新东西"）口语自然，节奏贴近样章，保留。

## Notes & Adaptation

- `io.Writer` 首现加注落在 `Fprintf` 签名后的"一个 `io.Writer`——……接口（interface）"处，符合本章特别说明；首段"接口方面的知识"未重复加注，符合"注一次"规则。✓
- "具体类型（concrete type）"首现加注恰当（Go 特有对照概念，术语表外新增，需回填 EXTEND.md）。✓
- "separation of concerns" 以"分离关注点/关注点分离"落地 ✓；mock 保留英文 ✓。
- 幽默点核查："多得很"（_a lot_）、"叫法高级了点"（fancy word）、"又写数据库又处理 HTTP 请求"的反问节奏、"它并不邪恶"（it's not evil）、"就去买一本吧"（go buy it!）均已落地。
- 标题"再聊聊 io.Writer"未加反引号，与原文标题格式一一对应 ✓。

## Summary

无事实/代码/链接错误；共 6 处需修正（有意思吧、专为而生、服务层句、可以长这样、要求/期望、量词"件"），4 处润色（bullet 平行结构、双"一个"、传给它、一点熟悉）。
