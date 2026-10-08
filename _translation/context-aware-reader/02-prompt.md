# 02 本章约束

## 术语定名

- context-aware → 支持 context 的（正文）；H1 固定为 `Context-aware Reader`（主控指定）
- delegation pattern → 委托模式（首现括注英文）
- delegate（被包装的底层 Reader）→ 正文说"被委托的对象 / 底层的 `io.Reader`"，字段名 `delegate` 不译
- compose → 组合；wrap → 包装；re-use → 复用
- 与 Context 章一致：cancellation=取消、cancel=取消（`cancel` 函数名不译）、derive=派生、deadline=截止时间
- happy path → 正常路径（happy path），本章首现加注
- subtest 名、代码、终端输出逐字节保留；`// Output:` 规则本章不涉及（无 Example 函数）

## 幽默/语气对策

- "Context aware reader?" → "支持 context 的 Reader？"；"Context aware?" → "何谓"支持 context"？"——保留设问递进
- "I know, I know, this seems silly and pedantic" → "我知道，我知道……" 保住自嘲
- "This is still progress." → 短句收尾，保住作者的小得意
- "let the compiler help you" → 与 hello-world 章"听编译器的话"呼应

## 硬性注意

- 内部链接 `[In a previous chapter](context.md)`：Context 章已译，保留站内相对链接 `context.md`
- 外链三个（GitHub 代码目录、Pace 博客、Wikipedia 委托模式）原样保留
- 无图片，无 Gitbook 转义符需清理
- 源文 H1 为 "Context-aware readers"（复数），按主控指定单数定题；`_something_` 斜体、`_some_`、`_compile_`、`_delegating_` 斜体一一保留
- Wikipedia 引文（blockquote）译成中文，与 Context 章译 go doc 引文的做法一致
