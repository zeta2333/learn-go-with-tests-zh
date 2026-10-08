# 04 审校诊断（只诊断，不改文）— 对照 source.md 逐段核查 03-draft.md

## A. 准确性问题

1. **浮点字面量句**（`Example_floatComparison` 后第 1 段）：
   原文 "The first one is `true` only because it's written as a literal expression - Go evaluates
   those with arbitrary precision, not `float64`, until they're assigned to something."
   译稿"只是因为它是写成一个字面量表达式——"语法不通（"是写成"杂糅），且
   "until they're assigned to something" 的挂靠点含糊。需重写为"按字面量表达式来写……
   直到被赋给某个东西为止"。
2. **不可精确表示的例子归属**："values or calculations that aren't exactly representable,
   like `0.1`, or results of division" —— `0.1` 是"值"、除法结果是"运算"的例子，
   译稿把两个例子并列挂在"值或运算"之后，读者分不清谁修饰谁。宜改为括注式。
3. **"We knew this was in relation to Triangle because we were just working with it"**：
   译稿"只是因为我们刚好正在弄它"多出"只是"，原文无让步/贬抑语气。
4. **"You should end up with tests like this"**：译稿"最后你写出的测试应该差不多是这样"
   ——"差不多"是原文没有的对冲词；"end up with" 是"最终得到"，不是"差不多"。
5. **"you get your reference to its data via the `receiverName` variable"**：
   译稿"拿到对它数据的引用"拗口且"reference"此处并非术语"引用"，实义是"访问数据的入口"。
6. **Kent Beck 引文**："as if it were an assertion of truth" 译成"仿佛它是在陈述一个事实"，
   丢了 assertion（断言）意象；结尾段 "make assertions of truth about shapes and their areas"
   与之呼应，译稿"就像陈述事实一样，断言着……"同样弱化。两处要统一保留"断言"。

## B. 中文表达问题

7. "A struct is just a named collection of fields"：译稿"一组命名字段的集合"偏定义腔，
   "just"（不过是）的轻松语气丢了。
8. "却意识不到拿到的会是错误的答案"："拿到的会是"别扭，宜"却没意识到函数会返回错误的答案"。
9. "Again, the implementation is fine"：译稿"老规矩"不准确，Again 是"又一次（同一循环）"，
   不是"老规矩"。
10. "用 `g` 会在错误信息里打印……"：以"用 g"作主语略生硬，宜"使用 `g` 的话，错误信息里会打印……"。
11. "我们从 `math` 包借来 `Pi` 常量一用"：可再顺口些。
12. "Understand/Putting it together"："对于构建……至关重要"句可，但"能否设计好自己的类型，
    对于……至关重要"主谓搭配（"能否……对于……"）略松，可改"能设计好自己的类型，是……的关键"。

## C. 体例核查（已确认项）

- 31 个代码块与原文逐字节一致（仅末块 `//` 注释已译）；两个无语言标记块照抄无误。
- 初译漏掉 `https://golang.org/ref/spec#Method_declarations` 链接，已补回（[_方法_](…)）。
- Gitbook 转义 5 处均已清除；无直角引号；9 个外链完整。
- 加注位置正确：结构体（struct）、字段（field）、方法（method）、接收者（receiver）、
  接口（interface）、表驱动测试（table driven tests）、匿名结构体（anonymous struct）。
- 特殊判断：`// Output:` 是 Go Example 的机制性注释（等同字符串字面量，test 会校验），
  不按"注释随章翻译"处理，保留原文。
