# 02 本章约束 — pointers-and-errors

在 00-book-prompt.md 全书规范基础上，本章额外遵守：

## 术语定名（本章首现加注一次）

- pointer 指针（首现"指针（pointer）"，加粗/斜体内正常写）；dereference 解引用（首现加注）；struct pointers 结构体指针
- receiver 沿用上一章"接收者"，不再加注；pointer receiver → 指针接收者
- error 译"错误"；作类型名、`errors.New`、`fmt.Errorf`、`ErrInsufficientFunds`、`.Error()` 一律原样反引号
- nil、panic、linter（轻注一次：静态检查工具）、Stringer、errcheck 保留英文
- error wrapping 错误包装；unwrap 语境译"解包/取出"；sentinel value 哨兵值（加注一次）
- flaky → "flaky（不稳定）"轻注一次；single source of truth → "唯一的事实来源"
- 新类型语法段：`type MyName OriginalType` 原样；"domain specific functionality" → 领域特定的功能

## 复现 TDD 循环标题（沿用上一章定稿，出现多次必须一致）

- Write the test first → 先写测试（×3）
- Try to run the test / Try and run the test → 试着运行测试（原文两处拼法不同，统一译法）
- Write the minimal amount of code for the test to run and check the failing test output
  → 写最少量的代码让测试得以运行，并查看失败的输出（×3）
- Write enough code to make it pass → 写足够的代码让测试通过（×3）
- Refactor → 重构（×3）

## 幽默/语气点

- "**Fintech loves Go** and uhhh bitcoins?" → "**金融科技圈爱死 Go 了**，还有，呃……比特币？"（保留 bold 边界与迟疑语气）
- _very secure wallet_ → *固若金汤的钱包*（斜体保留）
- "With our career in fintech secured, run the test suite and bask in the passing test" → "金融科技的职业前程已然无忧……尽情沐浴在通过测试的喜悦里吧"
- "we're not always saints, but we shouldn't let it slide either" → "总不能时时刻刻都当圣人，但也不能放任不管"
- "uhhh bitcoins" / "amazing banking system"（反讽）不译平

## 硬性点

- 35 个代码块（33 go + 2 无标记）逐字节一致；单行反引号内的编译器输出（`./wallet_test.go:...`、`wallet_test.go:...`）原样保留。
- go 注释仅 `errors.Is` 示例的 `// still true, ...` 翻译；`fmt.Println(err)` 块里 `// processing withdrawal ...` 是输出样例，保留英文。
- 8 个外链 + 3 个站内相对链接（structs-methods-and-interfaces.md、maps.md、error-types.md）原样保留；Dave Cheney 博客文章标题意译，URL 不动。
- 加粗斜体嵌套：`In Go, **...arguments are** _**copied**_.` → "在 Go 里，**……实参都会被***复制***。"（用星号形式避免 CJK 与下划线的 CommonMark 边界问题）
- 源文正文直引号 → 译文统一弯引号""；本章无 Gitbook 转义需清理。
- 上游笔误不改：`the  escape character`（缺 `` `\n` ``）；`int` 复数口吻（they're）等按中文习惯顺句。
