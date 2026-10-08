# 04 — anti-patterns 对照审校诊断（只诊断，不改稿）

## A. 准确性

1. **Dave Farley 引语漏译**：原文 "TDD gives you the fastest feedback possible on your design"，初译漏掉 "possible"（尽可能快的）。→ 「TDD 能为你的设计提供_尽可能_快的反馈」。
2. **"trying to practice TDD" 语气过重**：初译「嘴上在做 TDD」加了原文没有的讥讽，原意是中性的"尝试实践"。→ 「很多开发者也在尝试实践 TDD，却经常无视……」。
3. **"a small and coherent set of functions"**：「一小撮」带贬义色彩（帮派感）。→ 「一组小而内聚的函数」。
4. **"What if the requirements expand?"**：「需求要是扩张了」搭配生硬。→ 「需求要是膨胀了呢？」。
5. **"At first pass it's reasonable to say…" 是两句**：初译用冒号合并成一句，原文的节奏（先让步、再补刀"It only has 2 dependencies!"）更好。→ 拆回两句。
6. **"Or at least, it won't fail in the way the test is supposed to be protecting against"**：两个"它"指代缠夹。→ 改写为「至少，它不会在它_本该_防住的那个点上失败」。
7. **标题英译括注大小写不统一**：「（leaky interfaces）」应为「（Leaky interfaces）」，与原文标题一致；各 H2/H4 括注统一取原标题原样。
8. **"Leaky abstraction" 首现**：正文首现处宜按全书规范加英文括注「泄漏的抽象（leaky abstraction）」。

## B. 中文表达

9. **"your documentation"（Useless assertions 节）**：「会在你的这份"文档"里制造噪音」指代突兀；这里是全书反复的"测试即文档"梗。→ 「不仅会给这份充当文档的测试平添'噪音'、让测试更难读」。
10. **"they can be messy to read and understand"**：「读起来费劲、理解起来费劲」重复拖沓。→ 「读起来费解，理解起来更费劲」或「可读性和可懂度都会一团糟」。
11. **"with a poor test suite"**：「手边还跟着一套蹩脚的测试套件」的「跟着」略怪。→ 「身边还配着一套蹩脚的测试套件」或「还得忍受一套蹩脚的测试套件」。
12. **"Going back to the drawing board"**：「回到起点重来」可以更口语：「回到画板前重来」太直译；取「推倒重来，回到第一步：」。
13. **"_Listen_, complicated tests `==` complicated code"**：破折/冒号衔接更利落：「_听好了_：复杂的测试 `==` 复杂的代码」。
14. **"far from simple"**：「离'简单'越来越远」稍偏；原意是"远远谈不上简单"，且要和上句 "Simple is not easy" 呼应。→ 「事情可能就远远谈不上'简单'了」。
15. **"Revisit the mess" 句**：初译「之后每次要改代码、重返这片烂摊子时」把 "Do you then have to…" 的疑问语气丢了。→ 保留反问：「等到要改代码、得重返这片烂摊子的时候，你是不是开始憧憬另一种职业生涯了？」（疑问语气其实已在，确认句末问号即可）。
16. **"单个场景中堆砌大量断言（单元测试）"标题**：括注体例与其他条目（英文括注）不一致。定稿改为「单个场景里塞满断言（单元测试）」——此处括注表范围而非英译，可接受；在术语报告中登记完整英文原名。另一方案「单元测试的单个场景里塞满断言」更顺，取后者。
17. **"总结（Summary）"**：Summary 非反模式名，无需英文括注，全书各章均用「## 总结」。
18. **"e.g an acceptance test driving a web browser"**：「驱动一个网页浏览器」量词冗余。→ 「驱动浏览器的验收测试」。

## C. 加注与体例

19. mobbing/pairing 首现加注「群体编程（mobbing）」「结对编程（pairing）」：恰当，保留。
20. 子测试、表驱动测试、验收测试、mock/stub/spy、测试替身：全书已有定名，不再加注：恰当。
21. `:white_check_mark:`/`:question:` 转 ✅/❓：确认执行（mkdocs 无 emoji 扩展），报告注明。
22. 引号：初译无直角引号；「"我们应该发一封邮件"」用弯引号：正确。
23. 代码块：4 块语言标记与内容（除注释）待 verify 校验；上游 `t.Error("got %+v, ...")` 疑为 `t.Errorf` 笔误，按规范保留原文，报告登记。
24. 段落/列表顺序与原文逐条对应：已确认无合并拆移。
