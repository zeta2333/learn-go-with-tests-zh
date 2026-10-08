# reflection 章翻译约束

## 术语定名（本章生效）

- reflection → 反射；正文首现：_反射_（reflection）。章标题 H1 定为「反射」。
- 匿名函数（anonymous function）、闭包（closure）、匿名结构体、元编程（metaprogramming）、类型安全、快乐路径（happy path）、栈溢出（stack overflow）均按首现轻注一次。
- channel 一词在本书属首次出现（channels 章在本章之后），按术语表在此轻注一次"通道"；`chan` 类型保留代码原样。
- spy 保留英文，首现轻注（监视）；mock/stub 等不出现。
- `reflect.TypeOf`、`reflect.ValueOf`、`Value`、`Kind`、`Field`、`NumField`、`Elem`、`Recv`、`Call`、`Index`、`MapKeys`、`MapIndex`、`Interface`、`Len`、`String`、`uintptr` 全部保留代码字体，不译。
- 表驱动测试沿用 structs 章定名，不再加注。
- `interface{}` 行文解释为"任意类型"；`any` 说明是它的别名。

## 结构硬约束

- 48 个代码块逐字节照抄原文：go 块用 tab；无语言标记的 case 片段块用 4 空格缩进，一个空格都不能动。
- 唯一允许翻译的注释：末块 `// cycle!` → `// 循环引用！`；`// fatal error: stack overflow` 属错误信息样例，保留。
- "Write the test first / Try to run the test / Write the minimal… / Write enough… / Refactor" 循环标题沿用既有章定名：先写测试 / 试着运行测试 / 写最少的代码让测试能运行，并检查失败的测试输出 / 写足够的代码让测试通过 / 重构。
- walk 的每次演化（含回退到 walkValue 版本）顺序不可调换、代码块不可合并。

## 语气对策

- 推文 "difficulty level: recursively." → "难度等级：递归地。"保留原文的语病式幽默。
- "It's also a great source of confusion." → 保住自嘲："同时也是制造困惑的一大源泉。"
- "yucky" / "darn" / "wonky" → "恶心" / "真气人" / "别扭"，保住懊恼式口语。
- 结尾警句 "do your best to avoid using it" 要干脆有力："请尽全力避免使用它"。

## 其他

- 直角引号禁用；弯引号""。
- `_斜体_` 下划线标记随原文保留。
- 全文中文—英文/代码之间加空格。
