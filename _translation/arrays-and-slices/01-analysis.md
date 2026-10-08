# 01 — 章节分析：Arrays and slices

## 内容概述

本章用 5 轮完整 TDD 循环讲解数组与切片：

1. `Sum([5]int)`：数组字面量两种写法、`array[index]`、经典 for 循环
2. 引入 `range` 重构；讲"大小编码进类型"→ 引出切片
3. `Sum([]int)`：切片类型、`[]int` vs `[5]int` 编译错误
4. `SumAll(...[]int)`：可变参数函数、切片不能用 `==` 比较、`slices.Equal`（Go 1.21）、`make`/`append`、`len`/`cap`、底层数组
5. `SumAllTails`：切片表达式 `slice[low:high]`、空切片 panic（运行时错误 vs 编译期错误）、函数赋值给变量（`checkSums` 匿名辅助函数）、类型安全与缩小 API 暴露面

另穿插：`go mod init main` 的坑、测试覆盖率 `go test -cover`、"每个测试都有成本"。

## 新术语（英 → 中拟定）

| 英 | 中 | 备注 |
|---|---|---|
| array | 数组 | 术语表新增，首现加注 |
| fixed capacity | 固定容量 | |
| index | 索引 | |
| iterate / iteration | 遍历 / 迭代 | |
| range | `range`（保留英文） | Go 关键字 |
| blank identifier | 空白标识符 | 原文带链接 |
| slice | 切片 | 术语表已有，本章首现加注 |
| variadic function / varargs | 可变参数函数 / 可变参数 | |
| coverage | 覆盖率 | 用户指定；首现"覆盖率（coverage）" |
| length / capacity | 长度 / 容量 | |
| underlying array | 底层数组 | |
| make / append / len / cap | 保留英文 | 内置函数 |
| head / tail | 头部 / 尾部 | |
| shallow compare | 浅比较 | |
| comparable | 可比较 | 原文带链接 |
| 2D slices | 二维切片 | |
| compile-time error / runtime error | 编译期错误 / 运行时错误 | |
| type-safety | 类型安全 | |
| scope | 作用域 | |
| Go playground | Go Playground | 专有名保留英文 |
| surface area of API | API 的暴露面 | |

## 翻译难点

1. **Gitbook 转义多**：`\[N\]type{...}`、`\[...\]type{...}`、`\(within reason\)`、`\(the "head"\)` 均需去反斜杠按正文写；这两个列表项是正文不是行内代码，不得加反引号（与原文格式一一对应）。
2. **19 个代码块全部无 Go 注释**，须与原文逐字节一致；`panic` 输出是 ```text 块、`go test -cover` 输出和 `go test` 报错是 ```bash 块，原样保留。
3. 大量单行编译错误/输出是**行内代码**（如 `sum_test.go:13: got 0 want 15 given, [1 2 3 4 5]`），逐字节照抄，含原文空格与既有笔误（如 `t.Run("make the sums of tails of"` 的 "tails of"）。
4. **幽默点**：potentially ruin someone's day；Compile time errors are our friend / runtime errors are our enemies（对仗拟人）；Oh no!；Slices can be sliced! / How to slice, slices!（文字游戏）；stop them in their tracks。
5. **长句**：`make`/`len`/`cap` 一段（原文一句话 60+ 词）、`slices.Equal` 一段，拆句不得改变因果与限定关系。
6. 引用式链接 `[slice type][slice]`、`[blog-slice]` 及底部 4 条引用定义（含未被引用的 `[deepEqual]` 死定义）URL 须原样保留。
7. "Try to run the test" 与 "Try and run the test" 两种标题写法并存 → 统一译"试着运行测试"。
8. 原文疑似笔误：line 305 "the types like the above case" 表意含混（应为"像上面那样自己比较"）；line 501 `"make the sums of tails of"`（代码内，不改）；line 191 "problems were"（语法误，应为 was，按义译）。
