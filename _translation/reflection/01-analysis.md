# reflection 章分析

## 内容概述

以 Peter Bourgon 的推文挑战开篇（用 `walk(x interface{}, fn func(string))` 遍历结构体里的所有 string 字段），引出反射。
行文分两块：

1. 概念铺垫：`interface{}` 是什么、为什么不能到处用它（类型安全 vs 灵活性），何时才该用反射。
2. TDD 主线：从"带一个 string 字段的结构体"起步，递进到多字段 → 非 string 字段（Kind）→ 嵌套结构体（递归）→ switch 重构 → 指针（Elem）→ getValue 封装 → 切片 → 先按类型分发的重构（含一次"回头看的坏重构"：numberOfValues/getField 抽象在 map 上失败，回退）→ walkValue 去重 → map（顺序问题，assertContains/assertLength）→ chan（Recv）→ func（Call）。结尾总结 + 新增小节"已知局限：循环引用"（栈溢出，留作练习）。

代码步骤环环相扣，每个 walk 版本都在前一版基础上演化，必须与原文步骤一一对应，不可合并。

## 本章新术语（英→中定名）

| 英文 | 定名 | 说明 |
|---|---|---|
| reflection | 反射 | 章标题与全文核心词，首现注（reflection） |
| metaprogramming | 元编程 | 首现注 |
| type safety | 类型安全 | 开发者常识，轻注一次 |
| `interface{}` / `any` | 保留代码原样 | 行文解释为"任意类型"；`any` 注明是别名 |
| anonymous function | 匿名函数 | 首现注（本章特别要求） |
| closure | 闭包 | 首现注（本章特别要求） |
| anonymous struct | 匿名结构体 | 首现注 |
| happy path | 快乐路径 | 首现注（happy path） |
| spy | spy | 术语表：保留英文，首现轻注（监视） |
| 表驱动测试 | table based test | structs 章已定名"表驱动测试"，不再加注 |
| panic | panic | 保留英文（arrays 章已出现） |
| channel / chan | channel（通道） | 全书首现于本章，按术语表轻注一次；`chan` 类型保留代码 |
| goroutine | go func() 原样 | 本章仅代码中出现，不展开 |
| stack overflow | 栈溢出 | 首现注 |
| circular reference / cycle | 循环引用 / 环 | 新增小节用词 |
| DRY | 去重（DRY） | 动词化用法 DRYs up |
| uintptr / Kind / Field / NumField / Elem / Recv / Call / Index / MapKeys / MapIndex | 保留代码原样 | 本章特别要求 |

## 翻译难点

1. 推文 "difficulty level: recursively."：原文故意用副词接在冒号后制造语病式幽默，译作"难度等级：递归地。"保留生硬感。
2. "a great source of confusion"：Go 博客引文的收尾自嘲，译"同时也是制造困惑的一大源泉"，不能译平。
3. "darn."（map 打破抽象处）与 "it's yucky"：作者的懊恼式幽默，用"真气人""实在有点恶心"保住语气。
4. "in retrospect bad refactor... didn't get too upset about it"：自嘲+安抚并存。
5. "the first and only field"、"the first level of the type's hierarchy" 等精确限定语不可丢。
6. 48 个代码块（含大量无语言标记的 case 片段块，4 空格缩进）逐字节照抄；go 块用 tab。唯一可译注释是最后一块的 `// cycle!`（译为 `// 循环引用！`）；`// fatal error: stack overflow` 是错误信息样例，保留英文。
7. "How to extract the `Value` (`Field` or `Index`)" 中 "How many fields there are" 的 fields 实际涵盖切片元素，正文按"有多少个值"处理，避免误导。
8. "Non zero-argument functions" = 带参数（非零参数）的函数，勿误译为"零参数"。

## 原文疑似笔误 / 待报告

- 推文中 "all strings fields"：应为 "string fields"（笔误，正文意译即可）。
- "We can iterate through all values sent through channel until it was closed with Recv()"：语法欠通（was closed），意译为"用 `Recv()` 一直读取 channel 里发来的值，直到它被关闭"。
- 无图片、无坏链；7 个链接均有效指向。
