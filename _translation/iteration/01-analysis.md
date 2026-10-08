# Iteration 章分析

## 内容概述

本章以 `Repeat` 函数为载体完整走一遍 TDD 循环（先写测试 → 最小代码让测试能跑 → 写代码让测试通过 → 重构），教学主体有二：

1. **`for` 循环**：Go 唯一的循环关键字（没有 `while`/`do`/`until`）；三段式语法无括号、花括号必须写；`var` 显式声明 vs `:=` 短变量声明；`+=` 赋值运算符；`const repeatCount`。
2. **基准测试（benchmark）**：`BenchmarkRepeat(b *testing.B)`、`b.Loop()`（Go 1.24+ 新写法）、`b.N`、`go test -bench=.`、`-benchmem`（`B/op`、`allocs/op`）；顺带讲字符串不可变与 `strings.Builder` 的性能优化。

## 术语（本章出现 / 新增）

| 英 | 中 | 备注 |
|---|---|---|
| benchmark | 基准测试 | 术语表已有 |
| `b.Loop()` / `b.N` | 保留英文 | 新版 testing API，按任务要求 `b.N` 保留 |
| Add AND assignment operator | Add AND 赋值运算符 | 新术语，名称保留英文 |
| operand | 操作数 | 常见数学词，不加注 |
| immutable | 不可变（immutable） | 首现括注一次 |
| setup / cleanup | 准备 / 清理 | 代码注释里同步翻译 |
| flag（`-benchmem`） | 标志 | |
| TDD | TDD | 术语表已有，本章仅结尾出现 |

## 翻译难点

1. 源文件是上游新版：基准测试用 `b.Loop()` 而非旧版 `for i := 0; i < b.N; i++`；`b.N` 只在说明段落出现一次，保留原样。
2. 原文 "The standard library provides the \`strings.Builder\`[stringsBuilder] type"：悬挂式引用链接（定义在章末），渲染效果是代码后面孤零零跟一个 "[stringsBuilder]" 链接，属上游排版瑕疵；译文改为把链接直接套在 `strings.Builder` 上，章末引用定义行不再保留（URL 不变，verify 的链接检查仍通过）。
3. Gitbook 转义：`\(on my computer\)` 需去掉反斜杠。
4. 幽默点：_Keep the discipline!_、Which is pretty ok!、play with the production code as much as you like —— 保住口语的轻松劲，不译平。
5. "We can also use `var` to declare functions" 严格说应为"声明函数类型的变量"，原文即不严谨，按原文直译，报告中提示。
6. 两个 text 输出块（goos/goarch/ns/op）逐字节原样。
