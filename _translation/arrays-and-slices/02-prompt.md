# 02 — 本章特有约束

## 标题与加注
- H1：数组和切片
- 首现加注（一次）：数组（array）、切片（slice）、固定容量（fixed capacity）、索引（index）、空白标识符（原文有链接）、可变参数函数（variadic functions）、覆盖率（coverage）、长度（length）/容量（capacity）、底层数组、浅比较（shallow compare）、可比较（comparable，原文有链接）、运行时（runtime）、作用域（scope）、类型安全（type-safety）
- `range`、`make`、`append`、`len`、`cap`、`slices.Equal` 一律保留英文 + 反引号

## 代码与输出
- 20 个代码块与原文逐字节一致（本章 Go 块内没有注释，无注释翻译空间）
- `go test -cover` 命令与 ```bash 输出块（PASS / coverage: 100.0% of statements）原样
- ```text 的 panic 块原样（注意第二行 4 空格缩进）
- 行内错误输出照抄：`_testmain.go:13:2: cannot import "main"`（内含直引号）、`./sum_test.go:22:13: ...`、`sum_test.go:30: got [] want [3 9]` 等
- 代码内的 `t.Run("make the sums of tails of"` 等字符串一律不动（原文笔误保留）

## 格式
- 清理转义：`\[N\]type`、`\[...\]type`、`\(within reason\)`、`\(the "head"\)` → 正文直接写
- 原文的 `_强调_`、`**加粗**`、标题层级一一对应；**Every test has a cost** 保留加粗
- 原文引号词 "default" "tails" "head" "scope" "copy" → 弯引号""；禁用「」
- 相对链接 `[...](iteration.md)` 原样；底部 4 条引用定义原样（含 `[deepEqual]`、`[for]: ../iteration.md#`）

## 风格
- conversational；幽默保真对策：
  - "potentially ruin someone's day" → 弄不好就会毁了别人的一天
  - friend/enemy 对仗：编译期错误是我们的朋友……运行时错误是我们的敌人……
  - "Slices can be sliced!" → 切片还可以再切片！/ "How to slice, slices!" → 如何给切片再切片！
  - "stop them in their tracks" → 当场把他们拦下来
  - "Oh no!" → 糟糕！
- 长句拆分点：`make`/`len`/`cap` 段落拆成 2–3 句；`slices.Equal` 段落拆成 2 句，"浅比较"与"可比较"两个限定都不得丢
- 反复出现的 TDD 循环标题全书统一：先写测试 / 试着运行测试 / 写最少的代码让测试能运行，并检查失败的测试输出 / 写足够的代码让测试通过 / 重构 / 总结
