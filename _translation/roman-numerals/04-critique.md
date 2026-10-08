# 04 — 03-draft 对照原文审校诊断（只诊断，不改稿）

## A. 准确性

1. **Builder godoc 引文未译**（"### The Romans were into DRY too…" 之前的 blockquote）。sync 章先例：正文 blockquote 里的 godoc 引文要译。draft 里留了英文原句，需译为中文（这是散文引文，不是代码块）。
2. **"Technical explanation" 一节 "Reading from the bottom"**：draft 译作"从下往上读"，未点明对象是测试代码，读者会疑惑。应作"从测试代码的底部往上读"。
3. **"Try adding the following to the assertion code"**：draft 译"试着往断言代码里加上下面这段"，但下文代码实为在断言头部加一个 guard 后的完整版本，译"改成下面这样"更准。
4. **"stay out of 'red' for as long as possible"**：draft "尽可能让自己少停在'红'的状态"弱化了 as long as possible 的持续含义，应作"尽可能久地不让自己回到'红'的状态"。
5. **OO 段主语丢失**："Usually you are capturing a concept or data inside some imperative code…"，draft 改成无主语"通常这会把……"，丢掉了"你（程序员）"的规劝语气。
6. **"(as much as some would like to tell you)"**：draft "巴不得你这么想"指代含糊（这么想=什么？），应为"尽管总有人劝你干脆别管这些启示"。
7. **`if arabic > 3999` 那段 note 里 "assume we should treat `0` as an `int` value"**：draft "但它假定 `0` 按 `int` 值对待"生硬，实义是"`0` 会被当作 `int`"。原文本就绕口，译文应理顺而非复制绕口。
8. **"work through the Arabic number, trying to add symbols to our result if they fit"**：draft "顺着阿拉伯数往下处理：只要符号合适，就把它加进结果"丢了 trying（尝试）的试探感，宜作"逐个试着把符号加进结果，合适就留下"。
9. **"If you run the test they now actually run"**：单数测试被译成"它们"，改"它"。

## B. 中文表达

10. **"如果你没听说过[罗马数字]：那就是罗马人记数的方式。"** 冒号用法别扭，改破折号或"先补个课：罗马数字就是罗马人记数的方式"。
11. **首段 Kata 括注位置**："（kata 是编程道场里的练习题）"紧跟链接读起来打断句子，改用破折号后置。
12. **"TDD 工作流正有助于推行迭代式开发"**："正有助于推行"翻译腔，改"TDD 工作流恰好能助推这种迭代式开发"。
13. **"注意我用了切片的用法"**："用了……的用法"叠床架屋，改"注意我用切片只切出了一个用例"。
14. **"再用另一个函数转换回数，得到的还是最初那个数"**："转换回数"拗口（数/数字连续撞车），改"再转回数字时，拿到的仍是最初那个数"。
15. **"把它的值加进  `arabic`"**：沿袭了上游的双空格（上游笔误），中文排版应删除。
16. **"本书离不开社区宝贵反馈的滋养"**："滋养"偏文艺，与全书口语基调不合，改"本书能写成，离不开社区的宝贵反馈"。
17. **"本着完全公开的原则"**：full disclosure 直译感，改"为了完全透明起见"。

## C. 结构与体例核对（结论）

- 41+1 处代码块经 verify.py 修复（见下）后全部逐字节一致；console 输出、子测试名、`// true`、`// 11111111 ÿ …` 均未译 ✓
- `// earlier..` `// later..` 已随章翻译 ✓；`<details>` 结构保留、仅译文本 ✓
- 标题层级与原文一一对应（含 cases[:4] 处上游本就没有"试着运行测试"小节，未擅自补）✓
- 内链 `iteration.md#benchmarking` → `iteration.md#基准测试` ✓
- 无直角引号、无 Gitbook 转义残留 ✓
- 斜体沿用原文 `_…_` 体例（与 reflection 章一致）✓

## D. 工具链问题（本章特有，已处理）

- 上游 source.md 第 741 行的代码围栏为 `" ```go"`（带 1 个前导空格）。CommonMark 允许围栏缩进 0–3 空格，GitHub 渲染正常；但 verify.py 原正则只认行首围栏，导致 751 行起配对整体错位，把三段英文散文当成"代码块"逐字节比对——译文无论怎么写都不可能通过。
- 处理：最小修复 verify.py 正则（`^```` → `^ {0,3}```），并回归验证 reflection/iteration/hello-world 三章仍 OK。source.md 保持与上游逐字节一致，不做改动。
