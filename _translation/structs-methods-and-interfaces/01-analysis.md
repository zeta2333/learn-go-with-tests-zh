# 01 分析 — structs-methods-and-interfaces

## 内容概述

以"计算矩形周长/面积"起步，经历三轮 TDD 循环：
1. `Perimeter`/`Area` 裸 float64 函数 → 顺带讲浮点数比较的坑（0.1+0.2 != 0.3）；
2. 引入**结构体** `Rectangle`/`Circle` → 函数重名冲突 → 引入**方法**（receiver 语法）；
3. 引入**接口** `Shape`（隐式满足、解耦）→ 引入**表驱动测试**（匿名结构体 + 用例列表），
   再加 `Triangle` 演示扩展，最后讲测试输出可读性（`%#v`、字段命名、`t.Run` 命名子测试）。

本章是全书第一个"定义自己的类型"的章节，结尾总结部分分量较重。

## 本章新术语（全书术语表尚未收录）

| 英 | 中定名 | 说明 |
| --- | --- | --- |
| method | 方法 | Go 特有，首现加注 |
| receiver | 接收者 | 方法语法核心概念，首现加注 |
| table driven tests | 表驱动测试 | 本章核心，首现加注 |
| anonymous struct | 匿名结构体 | 首现加注 |
| field | 字段 | 结构体语境，首现加注 |
| decoupling / decoupled | 解耦 | |
| type-safety | 类型安全 | |
| concrete types | 具体类型 | |
| ad hoc polymorphism | 特设多态 | 维基链接文本，保留链接 |
| format string | 格式化字符串 | 注意与"格式化动词"区分 |
| tolerance | 容差 | 浮点比较语境 |
| interface resolution is implicit | 接口是隐式满足的 | 句式而非术语 |

已收录术语（直接用）：struct 结构体、interface 接口、slice 切片、statically typed 静态类型、
standard library 标准库、helper 辅助函数、subtest 子测试、compile/compiler 编译/编译器、
refactor 重构、production code 生产代码。

## 翻译难点

1. **浮点比较段**（`Example_floatComparison` 之后两段）：解释字面量任意精度求值 vs float64，
   逻辑链密，须逐句对齐，不能简化。
2. **方法定义句**："A method is a function with a receiver. A method declaration binds an
   identifier, the method name, to a method…" 近乎 Go spec 腔，需译得像定义又不生硬。
3. **表驱动测试的措辞**：本章核心，"list of test cases that can be tested in the same manner"
   "extra noise" "great fit" 等要译清楚。
4. Kent Beck 引文：断言句有粗体强调，且注明"强调是我加的"，须保留结构。
5. 多处 Gitbook 转义：`\([fmt options](...)\)`、`\(`testing.T`\)`、`\(remember to import it\)`、
   `\(emphasis in the quote is mine\)`、`\([ad hoc polymorphism](...)\)` — 全部清理。
6. 重复的 TDD 小节标题（"Write the test first"等出现 2-3 次）译法须全书一致：
   先写测试 / 试着运行测试 / 写最少量的代码让测试得以运行，并查看失败的输出 /
   写足够的代码让测试通过 / 重构。
7. 编译错误行、`%g`/`%#v` 输出样例逐字节保留；`r Rectangle`、用例列表两个无语言标记代码块照抄。

## 原文疑点

- 未发现坏链；9 个外链均在。
- "The `%#v` format string" 严格说是格式化动词（verb），按原文照译"格式化字符串"。
- 标题 "Wrapping up" 译"总结"（与 hello-world 一致）。
