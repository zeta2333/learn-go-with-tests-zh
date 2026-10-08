# 02 — 本章特有约束

## 术语定名（本章首现，回填 glossary 候选）

- higher-order function → 高阶函数（首现括注英文）
- fold / reduce → 保留英文；正文首现 "reduce" 或 [fold](…)（折叠）给一次括注
- identity element → 单位元（identity element）；neutral element → 中性元素
- type constraint → 类型约束
- boilerplate code → 样板代码
- declarative → 声明式
- idiomatic → 惯用；idioms → 惯用法
- ergonomics → 易用性
- 组合函数（combining function）、累加函数（accumulating function）仅用于 wiki 引文

## 与前两章的一致性

- TDD 步骤标题沿用《数组和切片》定稿：先写测试 / 试着运行测试 /
  写最少的代码让测试能运行，并检查失败的测试输出 / 写足够的代码让测试通过 / 重构。
- 回顾性表述沿用：数组、切片、可变参数函数、零值、`append`、"尾部"（tail）、空白标识符等已定名。
- 上一章《数组和切片》章名译作《数组和切片》，本章链接文字用"数组和切片"。
- generics.md 尚无中译，链接一律保留 `generics.md` / `./generics.md` 原样（mkdocs 按上游文件名解析）。

## 幽默点对策

- "Don't conflate easiness, with simplicity" / "unfamiliarity, with complexity"：
  两句加粗排比，用"别把 X 和 Y 混为一谈"句式；easy=容易、simple=简单，全章严格区分。
- "In addition, the identity element is 0." 双关 → "拿加法来说，单位元是 0"。
- "Monzo, Barclays, et al." → "Monzo、Barclays 这些银行"（保银行名，玩笑自明）。
- "endless™️"、"flawless" 见 01-analysis。
- "computer-sciencey" → "一股计算机科学的学究气"。

## 技术性硬约束

- Go 代码块仅译 `//` 注释（Sum / SumAllTails 的文档注释各出现两次，两处译文保持一致）；
  `// Output:` 无；字符串字面量、t.Run 描述、编译错误、测试输出逐字节不动。
- 两个裸围栏（无语言标记）保持无标记。
- 标题层级照抄上游（"先写测试"等步骤在本章是 H2；"Fold/reduce are pretty universal"、
  "Names matter" 等是 H3）；`## Find` 保留英文（函数名）。
- 含括号外链 URL 原样保留，不得加 `%28%29` 转义或 `<...>` 包裹。
- 斜体 `_..._`、加粗 `**...**` 与原文一一对应。
- 章首代码链接保留 quii 仓库 arrays 目录；链接文字体现 "continuation from Arrays and Slices"。
