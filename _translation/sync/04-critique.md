# 04 — 对照原文审校诊断（只诊断，不改文）

对照 `source.md` 逐段检查 03-draft.md。代码块已由 verify.py 保证逐字节一致（20 块 OK），以下只谈正文。

## A. 准确性问题

1. **"with a different number" 误读**（第二个"试着运行测试"后）：draft 译"只是数字跟上面不一样"。原意是每次运行失败的数字都会不同（939 只是示例），应译"而且每次失败的数字还都不一样"。
2. **"It's shorthand for something closer to"**：draft "它只是下面这一串操作的简写"丢了 "closer to"（实际情况比这三步还要更底层）的语气，应补"大致"："它其实大致相当于下面的操作"。
3. **"to exercise this"**：draft "来验证这一点"偏弱。exercise = 触发/暴露问题，应译"把这个问题暴露出来"。
4. **"our datatype"**：draft "自定义类型"不准。原文是"我们自己的类型/这个类型"，非术语"自定义类型"。
5. **"It should now run and fail"**：draft "现在应该能运行并失败了"时态别扭，应为"现在测试应该能运行，并且会失败"。
6. **"Try again and it fails"**：draft "再跑一次，它会报如下错误"——"它"指代不明，应补主语"测试"。
7. **"if they are first"**：draft 已意译为"最先调用 `Inc` 的那个 goroutine"，准确，保留。
8. **"callers of your type"**：draft "你的类型的调用者"生硬，改"使用你这个类型的人"。
9. **"can't be used incorrectly the way raw ... could"**：draft 用了被动"被误用"，违反"少用被字"规范；改主动"也堵上了……的误用空间"。
10. **"a single integer, incremented from multiple goroutines"**：draft "被多个 goroutine 自增"被动句，改"一个整数，多个 goroutine 并发地对它自增"。
11. **"Reach for ..." 两处**：draft "就伸手用"不自然，改"就用/就选"。
12. **"That was easy enough"**：draft "这一步已经够简单了"可，但后半 "it must be safe to use in a concurrent environment" 应更贴"它必须能在并发环境下安全使用"，现为"计数器必须在并发环境下使用也安全"稍拗口。

## B. 中文表达问题

13. **"bad and wrong"**：draft "**糟糕且错误的**"偏书面。原文是刻意的叠用（英式幽默），改"**又糟又错**"更传神。
14. **图注 "This seems like a really bad idea"**：draft "这看起来真是个坏主意"平，改"馊主意"更口语、更损，贴合原语气。
15. **"worth reaching for when a full Mutex would be overkill"**：draft "当完整的 `Mutex` 未免小题大做时，值得一用"——"小题大做"搭配不当，overkill 用"杀鸡用牛刀"。
16. **斜体标记不统一**：draft 混用 `*竞态条件*` 与 `_大概率_` 等下划线式；统一为样章的 `*...*` 风格。
17. **"When to use locks over channels and goroutines?"**：draft "什么时候用锁"可加"该"字更上口："什么时候该用锁，而不是 channel 和 goroutine？"
18. **"We've covered a few things"**：draft "我们学习了……一些东西"略平，改"这一章我们接触了 sync 包里的几样东西"。
19. **H2 句子式标题**"我见过别的例子把 `sync.Mutex` 嵌入到结构体里"中间宜加逗号断句。

## C. 加注检查

- 竞态条件、不变式、构造函数、互斥锁（godoc 引文处）、等待组（`sync.WaitGroup` 首现处）均已有注 ✓
- 无重复加注、无漏注 ✓；goroutine、channel、结构体、指针、零值、断言均沿用术语表，不加注 ✓

## D. 结构与一致性

- 重复 H2（先写测试/试着运行测试/写足够的代码让测试通过）与原文一一对应 ✓
- Refactor 节两个相邻 go 块未合并 ✓
- `assertCount`（正文）与代码中 `assertCounter` 不一致系上游笔误，按规范保留原文并上报 ✓
- 图片为外链 imgur，保留 URL、仅译 alt；上游 `.gitbook/assets/` 无本章图片，无资源可拷 ✓
- 内部链接 `concurrency.md` 保持上游同名 ✓；外链 8 处齐全（verify 已核）✓
