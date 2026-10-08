# http-server 章 — 初译审校诊断（只诊断，不改稿）

## A. 准确性

1. **A1 依赖注入章引用缺呼应**（P1）："From the DI chapter…" 初译只写"在依赖注入一章里"。原文此处无链接，按"链接与原文一一对应"规则**不加内链**（主控终审可统一决定是否补链），但文字必须明确指向已译章节并呼应 Greet 例子。初译已做，仅确认表述与 DI 定稿一致（DI 章原句："net/http 的 `ResponseWriter` 也实现了 io `Writer`"）。
2. **A2 sync 章引用同理**（P1）：初译擅自加了 `[Sync 一章](./sync.md)` 内链，原文无链接 → **删掉链接**，保留文字提及。
3. **A3 "### Fix the issues" 译名不准**（P2）：初译"修好编译问题"，但本节问题含编译错误和测试 panic，不只编译 → 应为"修好这些问题"。
4. **A4 HandlerFunc 文档引语未翻译**（P1）：初译保留了英文 blockquote。项目惯例（sync、context 章）是把 Go 文档引语译成中文、关键术语括注 → 应译："> HandlerFunc 类型是一个适配器（adapter），让普通函数可以当作 HTTP 处理器使用。如果 f 是一个签名合适的函数，HandlerFunc(f) 就是一个会调用 f 的 Handler。"
5. **A5 "## Wrapping up" 译名不统一**（P2）：hello-world 章定稿将 "Wrapping up" 译作"## 总结"，初译"## 收尾" → 统一为"## 总结"。
6. **A6 happy path 未按术语表处理**（P2）：初译"离"正常路径"更近"，术语表要求首现加注英文 → "正常路径"（happy path）。
7. **A7 斜体对应缺失**（P2）：原文 `This is where _mocking_ shines`、`we can _spy_ on its calls`、`_spy_ on what our handler writes` 初译丢了斜体。mock/spy 保留英文但斜体要保住：`_mock_ 大显身手`、`_spy_ 住`。
8. **A8 _The Test Pyramid_ 斜体**（P3）：初译"推荐你去了解一下*测试金字塔*（The Test Pyramid）"把斜体放在中文上，可接受；统一为 *测试金字塔*（The Test Pyramid）。
9. **A9 "problem space"**（P3）：初译"问题域"，可，保留。
10. **A10 "how many games players have won"**（P3）：初译"赢了多少场游戏"，语境是比赛场次 → "赢了多少场比赛"更自然。
11. **A11 "we just want the compiler passing as soon as we can"**（P2）：初译"只求编译器尽快闭嘴"语气过强，超出原文 → "眼下只求尽快让编译通过"。
12. **A12 "opening ourselves up to potentially _more_ compilation problems"**（P3）：原文有 _more_ 斜体强调，初译"越滚越多"丢了强调 → "招致*更多*的编译问题"。

## B. 中文表达

13. **B1 "让它通过返回一个硬编码的值来通过"**（P2）："通过"重复，拗口 → "靠返回一个硬编码值让它通过，以此起步"。
14. **B2 "做些辅助函数来去去重（DRY）"**（P2）："去去重"叠字别扭 → "写几个辅助函数，让测试代码 DRY 一些"（DRY 首现可轻点一次：DRY（don't repeat yourself））。第二处"把这段代码 DRY 一下"可保留。
15. **B3 "我们该怎么增量地把它做出来？"**（P3）："增量地"生硬 → "我们该怎么增量式地把它搭建出来？"
16. **B4 "为了让它硬造一个结构体总觉得不太对劲"**（P3）：初译"为了它硬造一个结构体总觉得不太对劲"，通顺，保留。
17. **B5 "做了最不地道的事"**（P3）：bare minimum 意为"最低限度"，初译意译成"最不地道"略偏，但配合"（明知它不对）"的插入语义成立；改为"我只做了最低限度的敷衍（明知它不对）"更贴。
18. **B6 "是不好使的"**（P3）："按预期使用这个软件，它是不好使的"口语成立，保留。
19. **B7 "多到让你坐立不安"**（P3）：than you may be comfortable with → "坐立不安"略重，改"多到让你心里发毛"或"可能超出你的舒适区"；取"可能会让你心里不踏实"。
20. **B8 "临时驻扎在这儿……它就得让位了"**（—）：生动贴切，保留。

## C. 体例与校验

21. **C1 全角/弯引号**：初译正文引号均为弯引号""，无直角引号，合规。
22. **C2 代码块**：52/52 逐字节一致（`//server.go` 等文件名注释保留原样），合规。
23. **C3 术语一致性**：处理器（handler）、集成测试（首现括注 integration test）、辅助函数、子测试、stub/spy/mock 保留英文、互斥锁、goroutine 保留——与全书术语表一致，合规。
24. **C4 章首代码链接、外链**：quii 仓库链接、golang.org/pkg 各外链原样保留，合规。
25. **C5 小节标题 "### Storing scores"** → "### 存储分数"（初译已对）；"### Run the application" → "### 运行应用程序"（已对）。
26. **C6 无图片、无 Gitbook 转义残留、无自动链接泄漏**，合规。

## 结论

无需结构性返工。修订要点：A2/A3/A4/A5/A6/A7/A11/B1/B2 为主，其余小修。
