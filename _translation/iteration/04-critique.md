# 04 审校诊断（对照 iteration.md 原文，只诊断不改）

## 准确性

1. H2 "Write the minimal amount of code for the test to run and check the failing test output"：初译"写出让测试能运行的最少代码"丢了 "minimal amount ... to run" 里"刚好够用"的纪律含义，且与 hello-world 章"写刚好够让测试通过的代码"不同族。→ 改"写出刚好能让测试运行的最少代码，并检查失败测试的输出"。
2. "`Loop()` returns true as long as the benchmark should continue running"：初译"还该继续跑"偏口语、略失准。→ 改"还需要继续运行"。
3. "The `for` syntax is very unremarkable"：初译"毫无出奇之处"，与后半句"跟大多数类 C 语言一个样"语感重复且生硬。→ 改"平平无奇……如出一辙"。
4. "To test this it ran it 10000000 times"：初译量词"遍"，全书教学语境统一用"次"。→ 改"跑了 10000000 次"。
5. "experiment with them"：初译"实验它们"生硬。→ 改"摆弄摆弄它们"，与本章轻松语感一致（对应 play with 的劲头）。
6. "Investing time learning the standard library will really pay off over time"：初译"假以时日回报会非常大"书面腔。→ 改"日积月累，回报会非常大"。
7. "Isn't it nice to know...?"：初译"这不挺好的吗？"可以，再口语半分 → "这不挺好的嘛？"。
8. 原文 "to declare and initializing variables" 语法笔误（应为 initialize），译文按正确含义"声明并初始化"处理，不改原文。
9. 原文 "We can also use `var` to declare functions" 不严谨（实为声明函数类型的变量），仍按原文直译"声明函数"，留待报告。
10. "Only the body of the loop is timed; it automatically excludes setup and cleanup code"：初译"准备和清理代码会自动排除在基准测试计时之外"语义正确，保留，仅把分号后改为"准备与清理"以求节奏。

## 中文表达

11. "这在 Windows Powershell 里" → "如果你用的是 Windows Powershell"更顺（原文 or if you're in Windows Powershell）。
12. 其余段落通读无翻译腔；短句节奏、祈使句使用符合样章风格。

## 加注与体例

13. 基准测试：术语表词，未加英文注——OK。
14. 不可变（immutable）：首现括注一次——OK。
15. `_..._` 斜体、`**...**` 加粗（含 "**注意：**" 冒号位置随原文两种写法）、标题层级与原文一一对应——OK。
16. 悬挂引用链接 `[stringsBuilder]` 已按 02-prompt 约定改为行内链接——OK。
17. 无直角引号、无 Gitbook 转义残留——待 verify 确认。
