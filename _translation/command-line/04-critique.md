# 04 — 审校诊断（03-draft.md 对照 source.md，只诊断不改）

## 准确性

1. **[中] 两句并一句**：开头 "The HTTP server won't be interesting to us … but the abstraction it uses will. It depends on a `PlayerStore`." 是两个句子，初译用冒号并为一句（"重点在它背后的抽象：它依赖一个 `PlayerStore`。"）。教学节奏上应拆回两句。
2. **[中] 指代含糊 + 强调点偏移**："Now let's write _another_ test … to force us into actually reading it." 初译"现在我们再写*一个*测试……逼我们真正去读它。"——强调应落在 *another*（再/另一个），且"它"可误读为"测试"，实指用户输入。
3. **[小] should 语气**："You should get an error" 译作"你会看到一个错误"，应保留"应该会"的预期语气。
4. **[小] 漏译 nuance**：Hashimoto 段 "anyone using our `poker` package won't have to create their own stub `PlayerStore` **if they wish to work with our code**"，初译"任何想用我们 `poker` 包的人"漏掉"写代码/与我们的代码协作"的条件从句意味。
5. **[小] "so far / other" 漏译**："In all other examples so far" 译作"在之前所有的例子里"，"到目前为止的其他"两层意思丢了。
6. **[小] "stumbled into"**："We have now stumbled into more questions on package design" 译作"我们这就又撞出了几个……新问题"，"这就又"生硬，"撞出"不如"一头撞上/又撞见"自然。
7. **[核对无误]** 第 108 行残缺原句按语义补全（"提交到公共仓库后，任何 Go 开发者都能导入这个包用上我们写好的功能"），与上下文吻合；两段 `dbFileName` 相对路径新增说明完整译出，无遗漏；30 个代码块逐字节一致（唯一翻译注释 `// todo for you…` 已按规则处理）；4 条外链、章首代码链接、`tree` 输出、终端/编译错误块均原样。

## 中文表达

8. **[中] Markdown 强调体例错误**："但既然我们一直主张*总体上*_不_测包内部的东西"——`_不_` 在 CJK 字符之间是词内下划线，CommonMark 不渲染为斜体，且全书体例统一用 `*`。需合并成一个 `*…*` 强调段，如"*通常都不*测包内部的东西"。
9. **[小] 冗余**："测试就应该回到全部通过的状态"啰嗦，可改"测试就应该重新变绿了"（scaling-acceptance-tests 章有"变绿"先例）。
10. **[小] "我们来扩展测试，把这个行为覆盖进去"**——"覆盖进去"稍翻译腔，可改"把它也测起来"或"让测试覆盖到它"。
11. **[小] "最简单的绕开办法"**——"绕开办法"（get around）稍硬，可作"最简单的解法/最省事的出路"。
12. **[核对无误]** 幽默点保住：IDE 一片红色、"难用得要命！"、重复造轮子、"轻车熟路"；句式无长定语链，无"被"字滥用；中英文间空格一致。

## 加注

13. **[核对无误]** 未导出（unexported，即私有）、行走骨架（command line interface 处的括注）、DRY（Don't Repeat Yourself）首现均已有注；"接口"按既有章节惯例不再重复加注（di 章已注过 接口（interface））。"构造函数"为全书术语表既有词，未加注，符合惯例。
14. **[小] "未导出（unexported，即私有）"** 的"即私有"可留可去：原文正是 "unexported (private) fields"，保留有据。

## 体例

15. **[核对无误]** 无直角引号；代码字面量均在反引号内；`package mypackage_test` 标题原样；文件路径注释保留、散文注释已译；无图片、无跨章链接需求（源文本就没有）；无 Gitbook 转义残留。
