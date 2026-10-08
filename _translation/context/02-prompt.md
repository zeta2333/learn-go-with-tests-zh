# 02 — Context 章特有约束

## 术语定名（本章首现加注）

- cancellation → **取消**（首现：取消（cancellation））
- deadline → **截止时间**（首现：截止时间（deadline）；仅出现在 `WithDeadline` 枚举处）
- timeout → 超时
- happy path → **正常路径**（首现：正常路径（happy path））
- derive → 派生；request-scoped → 请求范围的；call stack → 调用栈
- `context` 是标准库包名，一律保留英文、进反引号；`Context` 类型名同理
- goroutine / channel / select / spy 沿用全书规则保持英文，不加注（前章已介绍）
- context-aware 若需表述，写"感知 context 的"或"支持 context 的"

## 结构与标题

- H1：`Context`（专有名词式标题，保留英文）
- H2 循环标题用全书统一：`## 先写测试` / `## 试着运行测试` / `## 写足够的代码让测试通过` / `## 重构`（本章有多组循环，重复使用）
- 其余 H2：`## 总结` 前的收尾节译作 `## 收尾`；`### 本章我们的收获`（What we've covered）、`### 那 context.Value 呢？`、`#### 但是……`、`### 延伸阅读`（Additional material）

## 引文处理

- 5 处英文引文全部译成中文（先例：structs 章 Kent Beck 引文意译），保留 blockquote 结构、强调与所有链接 URL
- Štrba 那句玩笑要保住幽默："If you use ctx.Value in my (non-existent) company, you're fired" → 保留 "(non-existent)" 的自嘲：在"我这家（并不存在的）公司"

## 幽默/语气点

- "your snappy Go application that you're so proud of" — 自夸式自嘲，保住
- "This makes this test pass but it doesn't feel good, does it?" — 反问保住
- "(Pause for a moment and think of the ramifications...)" — 括号旁白保住
- "Feeling a bit uneasy? Good." — 短句节奏保住
- "Our happy path should be... happy." — 双关，译"我们的正常路径应该……恢复正常吧"或类似保留俏皮感

## 硬性检查点

- 28 个代码块逐字节一致；唯一 go 注释 `// todo: log error however you like` 译为 `// todo: 按你喜欢的方式记录日志`
- 输出样例（含 `=== RUN`、`--- FAIL`）不动
- 6 个外链 URL 原样保留，blog.golang.org/context 三处都要在
- 无直角引号「」；中英之间加空格；代码标识符反引号
- 无图片
