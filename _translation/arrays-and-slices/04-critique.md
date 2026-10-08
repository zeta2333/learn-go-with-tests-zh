# 04 — 审校诊断（对照原文，只诊断不改）

## A. 准确性

1. 【导语第 2 段】"When you have arrays, it is very common to have to iterate over them" —— 初译"有了数组，紧接着一件很常见的事就是要遍历它们"，"紧接着"是原文没有的时间递进义。应为"用上数组之后……很常见……"。
2. 【go mod 段】"rename the main module in `go.mod` to any other name" —— 初译漏了"名"字：改的是 go.mod 里声明的主模块**名**，不是模块文件。
3. 【Sum pass 段】"add each item onto `sum`" —— 初译"加到 `sum` 上"欠"累加"义；且本段 "iterate 5 times" 译成"迭代 5 次"，与导语的"遍历"用词不统一，此处实义是循环 5 次。
4. 【可变参数】"can take a variable number of arguments" 译"接收数量可变的参数"，与"可变参数函数"形成"可变……可变"叠用，且"数量可变"偏翻译腔。
5. 【tail/head】首现未按本书体例加英文括注，读者无从对应后文 tail 变量名（代码里 `tail := numbers[1:]`）。
6. 【exported】"Hiding variables and functions that don't need to be exported" —— "导出"是 Go 特有概念（首现），按全书规则应加注（exported）。
7. 【尾段例子】"We've used slices and arrays with integers" —— 初译"我们只拿整数用了切片和数组"生硬，且"只"的位置偏离原义（原文没有"只用过"的排他强调，是"本章以整数为例"）。
8. 【slices.Equal 段】"where you don't need to worry about the types like the above case" —— 初译"像上面那种情况就不用自己操心比较的问题了"，把原文含混的 "the types" 直接跳过了；应落到"像上面那样自己写循环比较"上，语义才闭合（原文此处本身表意含混，按上下文义译）。

## B. 中文表达

9. H3 "数组与它们的类型" —— 直译生硬，"它们的"无信息量。
10. "质疑你的测试的价值，这一点很重要。" —— "你的测试的价值"双"的"拗口，句式倒装多余。
11. "测试太多真的会变成一个问题" —— "变成一个问题"弱；原文 turn in to a real problem 有"实打实的麻烦"义。
12. "先把你漂亮的工作 commit 下来吧" —— "工作"对应 great work 偏平，此处是"成果/作品"义。
13. "你应该会看到类似这样的测试输出" —— 原文有冒号，漏标点。
14. "因为它会波及我们的用户" —— "波及"书面、轻。原文 affect our users 是"坑到用户"，可更口语且保留 friend/enemy 对仗的力度。
15. "我们选择用 `_`……忽略索引值" —— 通顺，保留。

## C. 体例与一致性

16. "Try to run the test" / "Try and run the test" 两种原文标题已统一为"试着运行测试"——确认全书统一策略正确，非误译。
17. 加注核对：数组（array）✓、固定容量（fixed capacity）✓、索引（index）✓、切片（slice）✓、可变参数函数（variadic functions）✓、覆盖率（coverage）✓、长度/容量 ✓、底层数组 ✓、浅比较（shallow compare）✓、可比较（comparable）✓、运行时（runtime）✓（首现在 mySlice[10] 段，先于 panic 段，顺序正确）、作用域（scope）✓、类型安全（type-safety）✓；待补：tail、head、exported。
18. 代码块 19 个、行内错误输出、bash/text 块、底部引用定义（含未被引用的 `[deepEqual]`）均与原文一致 ✓；`go test -cover` 输出块原样 ✓。
19. 转义清理：`[N]type{...}`、`[...]type{...}` 两个列表项已按正文处理，未加反引号，与原文格式对应 ✓；`\(within reason\)`、`\(the "head"\)` 已清理 ✓。
20. 弯引号体例 ✓，无「」；链接 16 条逐一核对无缺漏 ✓。

## 结论

无结构性错误；修订集中在 A1–A8、B9–B14 与 C17 的三处补注。
