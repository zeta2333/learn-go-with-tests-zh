# 04 — 批判性审校：初译稿 vs 原文（只诊断）

## Accuracy

- **TDD 首现未加全称标注**：「Hello, YOU」一节"这就是最基本的测试驱动开发"是全书 TDD 缩写首次出现处，按术语表应写"测试驱动开发（TDD）"，后文"按照 TDD 循环"才有依托。→ 修正。
- **"probably" 语气丢失**：Go modules 一节"If the tests pass, then you are probably using an earlier version of Go"，初译"如果你的 Go 版本比较老，测试会直接通过"把"大概率/多半"的口吻说死了。→ 补"多半/应该"。
- **常量一节轻微过度引申**："It's worth thinking about creating constants to capture the meaning of values and sometimes to aid performance."，初译"是值得养成习惯的做法"多出了"习惯"义，原文只是"值得考虑"。→ 收敛为"值得考虑"。
- 其余逐段核对：代码块、终端输出（含原文即有的 `'Hello, Chris''` 尾引号）、错误信息、URL、转义点号（example\.com\/hello）均与原文一致，无增删。

## Native Voice

- **引号体例混用**：正文里「领域」「钩子」「零值」用直角引号，"Hello, World"又用弯引号，全书体量下必须统一。→ 统一为中文弯引号""，代码字面量一律进反引号。
- **"但是现在，校验消息是否符合预期这件事出现了重复代码"**：「这件事出现了重复代码」名词堆砌、生硬。→ 改为"但现在检查消息是否符合预期的代码是重复的"。
- **"有了 TDD，我们应该有信心轻松把这个功能做出来！"**：语气尚可，但"有了 TDD"与前句衔接突兀，原文 "We should be confident that we can easily use TDD to flesh out this functionality!" 的自信口吻可以更自然。→ "有 TDD 在手，我们该有信心把这个功能轻松地一步步长出来！"
- **"反过来，不写测试……"**：原文 "By not writing tests, you are committing to..."，"反过来"是自加的衔接词，可保留但下句"你等于是在承诺"更贴 committing to。→ 微调。
- **"雕虫小技"**：略文绉绉，与 conversational 基调稍隔。→ "这点东西看似不起眼"方向更口语。
- **"运行它，输入 `go run hello.go` 即可"**：自然，保留。
- 整体无欧化长句、"被"字滥用问题；祈使句节奏贴近原文。

## Notes & Adaptation

- 「钩子」「接口（interface）」「子测试（subtests）」「格式化动词」等首现加注恰当，无过度注释。
- "Hello, YOU" 标题保留原文的决定维持；正文首段已交代"指定问候对象"的语境，读者可解。
- "one...last...refactor?" 译"最后一次……重构？"节奏保留 ✓。
- 幽默点核查："好家伙"（Goodness me）、"了不起的函数"（amazing）、"谁能想到……"（Who knew）均落地。

## Summary

无严重准确性问题（0 处事实/代码/链接错误），共 3 处需修正（TDD 标注、probably 语气、常量句收敛），5 处润色（引号统一 ×1 类、重复代码句、TDD 衔接句、反过来句、雕虫小技句）。
