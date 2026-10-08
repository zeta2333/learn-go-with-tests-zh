# maps 章 — 分析

## 内容概述

以"构建自己的词典（Dictionary）"为主线，走完整 TDD 循环，讲透 Go 的 map：

1. `Search`：map 声明（`map[K]V`）、取值 `m[key]`；键类型必须可比较，值类型任意。
2. 查不到词 → 引入第二个返回值 `error`；`v, ok := m[k]` 双返回值形式区分"键不存在"与"值为空"。
3. `Add`：写入 `m[key] = v`；讨论 map 的"引用类型"错觉（Dave Cheney：map 值是指向 `runtime.hmap` 的指针）；nil map 读如空 map、写则 panic；务必用字面量或 `make` 初始化。
4. `Add` 重复词 → 哨兵错误变量 `ErrNotFound` / `ErrWordExists`，`errors.Is` 断言；再把错误做成自定义类型 `DictionaryErr`（string 底层类型实现 `error` 接口）以成为常量。
5. `Update`：与 `Add` 镜像的 `switch err` 结构；顺带讨论"为 Update 单独定义精确错误"的价值（web 应用重定向 vs 报错示例）。
6. `Delete`：内置 `delete(m, key)`；再走一遍返回错误的迭代。
7. 总结：完整 CRUD API + 错误进阶（常量错误、错误包装）。

结构是全书标准的「Write the test first / Try to run / minimal code / make it pass / Refactor」五拍循环，重复 6 轮，段落因果链必须严格对应。

## 本章新术语（英→中）

| 英文 | 定名 | 说明 |
|---|---|---|
| map | map | 术语表既定，保留英文 |
| key / value | 键 / 值 | 章内指令明确 |
| Dictionary | 词典 | 类型名 `Dictionary` 保留；叙述里译"词典" |
| definition | 释义 | 词典语境用"释义"比"定义"自然 |
| comparable type | 可比较类型 | 首现加注 |
| reference type | 引用类型 | 首现加注 |
| sentinel error（未点名） | 哨兵错误 | 原文只说 "extracting it into a variable"，可意译，不必硬造术语 |
| magic error | 写死的错误 | 类比"魔法字符串"，意译 |
| runtime panic | 运行时 panic | panic 保留英文，首现括注"程序崩溃" |
| nil map | nil map | nil 保留英文 |
| CRUD | CRUD（增删改查） | 首现括注 |
| error wrapper | 错误包装 | 总结里 "Writing error wrappers" |
| thin wrapper | 薄封装 | "acts as a thin wrapper around map" |

## 翻译难点

1. **两个首字母大写概念撞车**：类型 `Dictionary`（反引号内，保留）与普通名词 dictionary（译"词典"）。行内代码一律反引号，叙述词用中文，不会混淆。
2. **Dave Cheney 引文**（blockquote）：`A map value is a pointer to a runtime.hmap structure.` —— 原文即英文引用，译文括注翻译："map 的值是一个指向 runtime.hmap 结构的指针"。保留 blockquote 体例。
3. **nil map 行为表述必须精确**：读像空 map、写会 panic；`var m map[string]string` 是零值 nil，不要初始化成这样。不可译反、不可含糊。
4. **`delete` 内置函数**：两个参数、无返回值；第一个是 map，第二个是要删除的键。表述照原文严格对应。
5. **错误输出逐字节保留**：`%!q(<nil>)` 这类 fmt 怪输出、编译错误行号列号全部原样进代码块。
6. **幽默点少而轻**："And what better way is there to learn about Maps than to build our own dictionary?"（反问式英式幽默）、"Our `Add` is looking good."、`less than accurate`（委婉吐槽函数名不再名副其实）。要保住语气，不译平。
7. **标题**：章 H1 定为 `Map`（主控指定）。小节标题沿用全书体例（先写测试 / 尝试运行测试 / 让测试运行的最小代码 / 让测试通过 / 重构 / 总结）。
8. **内链**：`arrays-and-slices.md` 与 `./pointers-and-errors.md` 目标文件名原样保留；无锚点需要改写。
9. 无图片。
