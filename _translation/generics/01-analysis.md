# generics — 译前分析

## 内容概述

全书泛型入门章。作者从手写 `AssertEqual` / `AssertNotEqual` 断言辅助函数切入：先体会静态类型约束的好处，再演示 `interface{}` 如何丢掉类型安全（编译器帮不上忙、运行时才出错、被迫用反射），由此引出泛型：

1. 泛型函数：`[T comparable]` 类型参数语法；`comparable` 约束 vs `any`；`T any` 泛型与 `interface{}` 的本质区别（仍限定单一类型）。
2. 泛型数据结构：先写 `StackOfInts` / `StackOfStrings` 两份重复实现 → alias + `interface{}` 的统一 `Stack` 及其代价 → 泛型 `Stack[T any]`；顺带讲类型推断（多数调用无需写 `[T]`）与显式实例化（`NewStack[int]()`）。
3. 总结：泛型比 `interface{}` 更简单；"泛型会把 Go 变成 Java 吗？——不会"；你早就在用泛型（数组/切片/map）；抽象不是贬义词；Make it work, make it right, make it fast（先具体后泛化，三次法则）。

## 本章新术语（英→中定名）

| 英文 | 定名 | 处理 |
|---|---|---|
| generics | 泛型 | 首现加注（generics） |
| type parameter | 类型参数 | 首现加注（type parameters） |
| constraint | 约束 | 首现加注（constraint） |
| instantiate / instantiation | 实例化 | 原文未出现该词；在"创建 `Stack[Orange]`"概念处轻量补注 |
| type inference / infer | 类型推断 | 首现加注（type inference） |
| type assertion | 类型断言 | 首现加注（type assertion） |
| reflection | 反射 | 术语表已定，本章首现加注一次 |
| stack | 栈 | 首现加注（stack）；`Push`/`Pop` 方法名保留英文，括注 压入/弹出 |
| LIFO | 后进先出（LIFO） | — |
| alias | 别名 | 首现轻注 |
| FUD | 保留英文 | 括注 fear, uncertainty and doubt + 意译 |
| comparable / any / interface{} | 保留英文 | 代码原样，不作中文 |
| developer experience (DX) | 开发体验 | 仅出现在代码字符串字面量，不译 |

## 翻译难点

1. 幽默点密集：`*ahem*`（咳咳，暗讽"所谓的泛型"）、"Who needs generics?"、`yuck`、"Thank goodness I am so smart and good-looking" 自嘲式自夸、`- No.` 单行冷幽默、dunk on AbstractSingletonProxyFactoryBean。全部要保住，不译平。
2. "apples and oranges" 比喻贯穿全章（示例类型就叫 `Apple`/`Orange`），一律直译"苹果/橙子"，首现保留 wiki 链接。
3. 两个**无语言标记**代码块：编译错误输出块须逐字节一致；`myApples` 示例块里的 `// You can't do this!` 注释**不能译**（verify.py 只对 \`\`\`go 块豁免注释差异）。
4. `[stack](https://en.wikipedia.org/wiki/Stack_(abstract_data_type))` 的 URL 内含未转义括号，须逐字节照抄。
5. 源文笔误：`AssertEquals`（应为 `AssertEqual`）、"e.t.c."、"the TDD process that arrived me at"（语法）、注释 "from out interface{}"（应为 of）。标识符 `AssertEquals` 按原文保留在反引号里。
6. "type parameters which is just a fancy way of saying…" 的调侃语气、"Say what?"式反问要自然。
7. 两处块引用是作者内心独白，要译出内心戏的节奏。
