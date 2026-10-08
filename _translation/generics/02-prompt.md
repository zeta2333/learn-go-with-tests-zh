# generics — 本章翻译约束（02-prompt）

## 术语定名（均在章内首现处加注一次，之后裸用中文）

generics → 泛型；type parameter → 类型参数；constraint → 约束；instantiate → 实例化；
type inference → 类型推断；type assertion → 类型断言；reflection → 反射；
stack → 栈；alias → 别名；LIFO → 后进先出（LIFO）。
`comparable`、`any`、`interface{}`、`Push`、`Pop`、`AssertEqual` 等代码标识符一律反引号保留英文。
`T` 是"标签/类型参数名"，不要译成"标记符号"之类。

## 硬约束

- 原文共 30 个代码块，一一对应；仅 ```` ```go ```` 块中的 `//` 注释随章翻译（含注释的块：泛型 Assert 完整示例、interface{} 栈测试、三处 TestStack）。
- 两个无语言标记代码块逐字节一致，其中 `var myApples []Apple` 块里的 `// You can't do this!` 不译。
- 字符串字面量不译：`"asserting on integers"`、`"interface stack DX is horrid"`、`"got %d, want %d"` 等。
- 所有 URL 原样保留；尤其 `https://en.wikipedia.org/wiki/Stack_(abstract_data_type)` 带括号；`./structs-methods-and-interfaces.md` 相对链接不动（锚点无）。
- 章首代码链接指向 quii 原仓库 `tree/main/generics`。
- H1 定为：泛型。
- 斜体沿用原文 `_..._` 下划线体例；引号统一弯引号""，禁用「」。

## 幽默/语气对策

- `*ahem* generic functions` → *咳咳*"泛型"函数（保留"所谓"的讽刺）
- `Who needs generics?` → 还要泛型干什么？（反问保住）
- `yuck` → 真恶心。
- `Thank goodness I am so smart and good-looking` → 多亏我又聪明又英俊（自嘲式自夸直译）
- `- No.` → `- 不会。` 独立成行，冷幽默节奏不变
- `It's easy to dunk on AbstractSingletonProxyFactoryBean` → 嘲讽 AbstractSingletonProxyFactoryBean 很容易（类名保留）
- `the output is a bit ropey` → 输出有点不伦不类/拿不出手
- `type assertion gymnastics` → 类型断言的杂技
- 两处 `>` 块引用为内心独白，保留"嗯……/好，我想试试……"的自言自语感
