# 04 — 对照审校诊断（只诊断，不改稿）

对照 source.md 逐节核查 03-draft.md，诊断如下。

## A. 硬伤（必须修）

1. **遗留编辑痕迹**：「紧耦合」一节残留半句废弃译文"等等，这句翻错了，先记下："及带英文单词 desirable 的废句。删除。
2. **intro-to-acceptance-tests 链接**：草稿把 gitbook URL 换成了 GitHub blob URL——但 verify.py 校验"译文缺失原文链接"会 FAIL。且该 URL 本身就指向英文原版页面。决定：**保留原 gitbook URL**，链接文字后加"（英文原版）"标注，兼顾规则精神与校验。02-prompt 中"改为 GitHub URL"的决定据此修正。
3. **Go 代码块注释未随章翻译**（规则①）：Testcontainers 测试里 `// set to false if you want less spam...` 草稿保留英文，须译；生成接口展示块 `// GreeterServer is the server API...` 三行注释须译。`//todo:` 已译✓。Dockerfile `#` 注释按 02-prompt 决定保留英文（规则只放行 Go 的 `//`）。
4. **GOOS 二次出现处缺链接**：Further material 里 `[Growing Object-Oriented Software, Guided by Tests,](http://...)` 草稿写成了普通括号文本，丢失 markdown 链接结构。补回 `[《…》](url)`。
5. **斜体/加粗与原文不对应**：`_before_` 草稿作 `**在合并代码之前**`，应作 `*在合并代码之前*`；`Making the change easy` 首句 `_before_` 未体现。
6. **标题内行内代码**：`### Consolidating \`Dockerfile\`` 草稿丢了反引号；`## Implementing \`Curse\` for the HTTP server` 同。

## B. 准确性（措辞偏离原文）

7. "Would you not hesitate to introduce an `interface`... your `HTTP` handler..."：草稿丢了 `HTTP` 的反引号。补回（"接口（interface）"括注已覆盖 `interface` 的反引号，可接受）。
8. "when you're first starting, this is often the case"：草稿"万事开头难时往往如此"加了原文没有的成语，改回"但刚开始时往往就是这样"。
9. "the red step's rules"：红灯步骤规矩——草稿把"务必记住"接引语冒号，可保留，但补"我们"主语感（"我们务必记住红灯步骤的规矩"）。
10. "you find yourself wasting lots of time updating your ATs"：AT 缩写首现在更早的遗留代码段（"ATs need not be concerned..."），首现加注应放在那里："验收测试（AT）不必关心内部质量"；博客摘录里的 "(AT)" 不再重复加注；Reflect 列表 "until the AT runs" 直接用"验收测试"。
11. "out in the wild"：草稿"野外的验收测试"生硬，改"现实中的验收测试"。
12. "iteratively"：草稿"iterative 地"中英夹杂别扭，改"以迭代的方式"。
13. "excellent-looking"（go-rod）：草稿"外表亮丽的"错位，实为"出色的"。
14. "non-computer people"：草稿"不懂计算机的人"，改"业务人员（不懂技术的人）"口径，与 Wrapping up "least technical person"（最不懂技术的人）一致。
15. "Expensive to maintain, and seem to make changing the software harder than it ought to be"：草稿"比本该有的更难"欧化，改"让改软件变得比理应的更费劲"。
16. "cross your fingers"→"祈祷"✓；"Wait for it to be listening on _some_ port"：草稿"监上某个端口"生硬，改"等它开始在*某个*端口上监听"（补斜体）。
17. RPC 强调结构：草稿"（远程过程调用，**r**emote **p**rocedure **c**all）"改为镜像原文的构词强调："远程过程调用（**r**emote **p**rocedure **c**all）"融进句中。
18. "Hold your nose"："捏着鼻子上"不顺，改"捏住鼻子忍一忍"。
19. "bike-shed...for the billionth time"：草稿"第 N 次生产力闹剧式争论"生造词，改"为…这种鸡毛蒜皮的事吵到第一亿次"（保住 billionth 夸张）。
20. "Whilst this technically isn't a refactor... which our test will give"：草稿"让它支持外部传入，测试里再给它一个"含糊，改"改成可以从外部传入 client，测试里会传一个给它"。
21. "update our tests to pass in the image to build"：草稿"传入要构建的程序"，改"传入要构建的目标名"（参数是 binToBuild）。
22. Wrapping up 首段 "a means of guiding, or as a GOOS says, 'growing' your software methodically"：草稿破折号嵌套拗口，改"你可以把它们当作引导软件的手段——用 GOOS 的话说，有章法地'培育'（growing）你的软件"。
23. "the resiliency of your acceptance tests"：草稿"坚韧"改"韧性"。
24. "Hopefully, with this example, you can see our application's predictable, structured workflow..."：草稿"我们为应用驱动变更的可预测…工作流"定语链过长，改短句。
25. "Testing on steroids"：草稿"驾驭规格的更多玩法"偏离字面（steroids=兴奋剂梗），改"打了鸡血的测试"，保住作者的玩笑。
26. "Sometimes, it makes sense to do some refactoring _before_ making a change."：补"*之前*"斜体对应。

## C. 中文表达润色（不改动事实）

27. "维护成本高"段落列表第 4 条见 #15；第 5 条"反馈又慢又差"可。
28. "这肯定比……简单太多了！"语气过满，原文 "undoubtedly a lot simpler" → "这无疑简单得多"。
29. "想法很美好，但是编译不过"→ 原文 "This would be nice, but it doesn't work"，改"想法很美好，但它跑不通"，编译错误另起句已有。
30. Kent Beck 引用块：中文译文行并入引用块内并加括号，保持 "~Kent Beck" 署名行原位。
31. "干系人"偏 PM 腔但准确，保留；"外表亮丽"见 #13。

## D. 保留项确认（非遗漏）

- `-->` 孤立残留（Further material 末尾）保留，报告中列为上游笔误。
- `cmd/grpc_server/greeter_server_test.go`（与 `grpcserver` 文件夹名不一致）、go_package 行 `github.com/quii/adapters/grpcserver`、正文 `grpcServer.RegisterGreeterServer`/`grpc.Server`、输出块中 `TestGreeterHandler` 与函数名 `TestGreeterServer` 不一致、"We require to provide"、"A slight diversion in to"、"specification have a Curse method"、"how important it is for HTTP handlers should only be responsible"——均为上游原文笔误，代码块与正文按忠实原则保留，汇总报告。
- 两处 tree 输出块中 `|` 与 `│` 混用、fence 前空行——逐字节保留。
- imgur 六图原样保留、alt 翻译；TDD-outside-in.jpg 不属本章，不引用。
- http-handlers-revisited 链接保留 GitHub URL，链接文字加"（英文原版）"。
- 所有代码块、终端输出逐字节一致（verify 会把关）。
