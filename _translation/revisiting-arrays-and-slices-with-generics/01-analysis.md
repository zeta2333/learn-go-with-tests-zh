# 01 — 分析：Revisiting arrays and slices with generics

## 内容概述

Go 基础篇收尾章。用泛型把《数组和切片》一章的 `Sum`/`SumAll`/`SumAllTails` 中反复出现的
"遍历 + 累加" 模式抽象成高阶函数 `Reduce`（functional programming 的 fold/reduce），
随后用 TDD 做 bad bank 例子，遇到 "reduce 成不同类型" 的问题，把 `Reduce` 泛化成 `[A, B any]`；
再扩展银行代码展示声明式风格；最后给出 `Find` 实现，并讨论命名（Map）、idiomatic 争议与参考资料。

结构上照旧走 TDD 步骤标题（先写测试 / 试着运行测试 / 写最少的代码……/ 重构），
但本章这些步骤标题是 H2（上游如此），需保持层级一一对应。

## 本章新术语（英 → 中定名）

| 英文 | 定名 | 说明 |
| --- | --- | --- |
| higher-order function | 高阶函数 | 首现加注（higher-order function） |
| generics | 泛型 | 上一章章名，正文链接指向 generics.md |
| fold / reduce | fold / reduce（折叠 / 归约） | 概念名与函数名保留英文，首现括注 |
| identity element | 单位元 | 数学名词，加注（identity element），also 中性元素 neutral element |
| type constraint | 类型约束 | |
| predicate | 谓词 | 仅出现在代码里（参数名），不入正文 |
| boilerplate (code) | 样板代码 | |
| declarative | 声明式 | 与 imperative（命令式）相对 |
| idiomatic / idioms | 惯用 / 惯用法 | |
| ergonomics | 易用性 | 指代码用起来的顺手程度 |
| use-case | 用例 | |
| combining function | 组合函数 | wiki 引文内 |
| accumulating function | 累加函数 | |

沿用既有术语：数组、切片、可变参数函数、零值、单元测试、重构、版本控制（source control）、
类型安全、子测试、断言、覆盖率（本章未再出现）、尾部/头部（tail/head）。

## 翻译难点与对策

1. **两段 Wikipedia 引文**（fold 定义、identity element 定义）：blockquote 翻译，术语准确、句子理顺，
   "recursive data structure" → 递归数据结构。
2. **双关/幽默**：
   - "In addition, the identity element is 0." —— "in addition" 既是"此外"又是"对加法而言"，
     译成"拿加法来说，单位元是 0"，语义不丢。
   - "The possibilities are endless™️" —— 保留 ™️ 标记："可能性是无穷无尽的™️"。
   - "As you can see, this code is flawless." —— 自嘲（`strings.Contains(name, "Chris")` 选出自己），
     译"如你所见，这段代码无懈可击"。
   - "ready to challenge Monzo, Barclays, et al." —— 英国银行梗，保留银行名。
   - "Go is supposed to be simple" 引文与 easy vs simple（Rich Hickey 演讲）——
     "容易"（easy）与"简单"（simple）必须区分译，否则论证垮掉。
3. **Go 代码块注释随章翻译**：`// Sum calculates...`、`// SumAllTails calculates...` 两处各出现两次。
   字符串字面量、终端输出、编译错误逐字节保留。
4. **两个无语言标记的代码围栏**（编译错误、测试失败输出）保持裸 ```。
5. **链接**：`arrays-and-slices.md` ×2、`./generics.md`、`generics.md` 保留上游文件名；
   外链含括号 URL（Fold_(higher-order_function)、Map_(higher-order_function)）原样保留。
6. **强调标记**：原文用 `_..._` 斜体（a lot / essence / declarative / what / how / business logic /
   different / radically / will / might / before），译文一一保留。
7. 列表项 2（"Iterate over the collection..."）原文句末无句号，镜像处理。
