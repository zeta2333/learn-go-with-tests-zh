# generics — 初译审校诊断（对照原文，只诊断不改）

## A. 漏译（严重，必须补）

1. **S0 段漏译**：原文 L13–L17 整段缺失——
   - `## Our own test helpers (`AssertEqual`, `AssertNotEqual`)` 节标题
   - `### Assert on integers` 小节标题
   - "Let's start with something basic and iterate toward our goal" 引入句
   现状：目录要点后直接跳进第一个代码块。
2. **S3 段漏译**：原文 L80–L84 缺失——
   - `### A function that takes a string or an integer? (or indeed, other things)` 小节标题
   - "Another option Go has … `interface{}` which means "anything"" 引入段
   - "Try changing the signatures to use this type instead." 指令句
   现状：接口段落（L78）后直接跳进 `interface{}` 签名代码块，因果链断裂。

## B. 格式

3. 多处闭合代码围栏与正文粘连（初稿 L44/51/71/79/85/127/135/139/150/224/240/282/318/325/345/349/371/403/433/441/452/461/566 等），原文围栏后均有空行；S26（"要用这个构造函数…"）按原文应紧贴围栏（无空行）；S10/S24/S28 三个纯空行分隔段行数不足，导致相邻围栏之间缺空行。

## C. 准确性 / 表达

4. L51 与 L57 两次"把一个 `string` 传给一个期望 `integer` 的函数"，量词"一个"堆叠；第二处可省。
5. L81 嵌套引号『关于"传进函数的东西是什么类型"的有用信息』拗口，改为拆句。
6. L87 "编译期对正在处理的是什么数据毫无信息"语序别扭，且与 L349"一无所知"措辞重复，需错开。
7. L441 "（即泛型类型的实例化（instantiation））"双层括号嵌套，改破折号插入语。
8. L556 "泛型并不是唯一能干的"生硬；原文 "generics are not unique in their ability to make confusing, annoying to use code"。
9. L574 "对于交付这些行为_真正需要_哪些代码"指代含混，应为"要交付的行为"。
10. L318 "把之前的…实现起了别名"动词搭配不当（"给…起别名"）。
11. L287 "并只配一套测试"歧义（"配"可读作"配置"）。
12. L152 "`any` 是 1.18 才加入的"宜作"Go 1.18"。
13. L176/L452/L461 正文指代类型名 `int`/`string` 未加反引号，体例不统一（正文代码标识符一律反引号）。
14. L331 "就算我们有纪律绝不这么干"欠自然 → "就算我们有足够的自律、绝不这么干"。

## D. 合格项（复核通过）

- 30 个代码块逐字节一致；5 个 go 块注释已译，2 个无语言标记块（错误输出、`myApples` 示例含 `// You can't do this!`）未动 ✓
- 全部 12 个外链 + 1 个相对链接原样保留（含带括号 wiki URL）✓
- 加注首现齐备：泛型/约束/类型参数/类型断言/类型推断/实例化/反射/栈/别名 ✓；无「」直角引号 ✓
- 幽默点：咳咳、"还要泛型干什么？"、"真恶心"、"又聪明又英俊"、"- 不会。"独立成行 ✓
- 字符串字面量未译（"interface stack DX is horrid" 等）✓
