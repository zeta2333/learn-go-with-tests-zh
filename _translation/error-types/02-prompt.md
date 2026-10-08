# 02 本章约束 — error-types

在 00-book-prompt.md 全书规范基础上，本章额外遵守：

## 术语定名（本章首现加注一次）

- H1 保留英文 **Error types**（主控已定）；正文"error types / error 类型"语境译"错误类型"
- type assertion → 类型断言（首现：`[类型断言](链接)（type assertion）` 不成立——链接文字就是"类型断言"，加注放在正文叙述处）→ 处理：链接文字"类型断言"，句子中后接"（type assertion）"一次
- error 接口 → `` `error` 接口``；`BadStatusError`、`DumbGetter`、`errors.As`、`StatusTeapot`、`httptest` 等标识符一律原样反引号
- flaky → "flaky（不稳定）"（本章首现加注一次；pointers-and-errors 已注过，主控终审统一）
- call stack → 调用栈（首现"调用栈（call stack）"）
- 状态错误 = status error；魔法字符串 = magical string（沿用术语表 magic string→魔法字符串）
- "the error interface" → "`error` 接口"

## 与 pointers-and-errors 的一致性

- "listen to your tests" → "倾听测试的反馈"（该书已用）；本章 "This book tries to emphasise _listen to your tests_" → "本书一直强调*倾听测试的反馈*"
- `errors.As` 提取自定义类型的表述与 pointers-and-errors 新增的"检查被包装的错误"小节口径一致（返回 bool、提取进目标值）
- Bitcoin 示例无直接出现，无需处理

## 幽默/语气点

- "Let's make up a function" → "现编一个函数"（自嘲口吻：函数就叫 DumbGetter）
- "Is the exact error message string what we're _actually concerned with_ ?" → 反问语气保住："我们*真正关心的*，真的是错误信息字符串一字不差吗？"
- "The ergonomics of our test would be reflected on another bit of code trying to use our code." → "手感"意象："我们的测试用起来是什么手感，别的代码用起我们的代码来就是什么手感。"
- "extremely error prone and horrible to write" → "极易出错，而且写起来苦不堪言"
- "It is still "just" an `error`" → 引号里的 just 不丢："它仍然"只是"一个 `error`"

## 硬性点

- 8 个代码块逐字节一致（7 go + 1 无标记失败输出）。
- 可译注释仅 2 处：`// DumbGetter will get the string body of url if it gets a 200`、`// ignoring err for brevity`。
- 子测试名字符串 `"when you don't get a 200 you get a status error"`（出现 3 处代码块内）不译。
- 失败输出第 3 行行首 4 空格 + TAB，原样保留。
- 4 个外链 URL 原样保留；无图片；无 Gitbook 转义；无直角引号。
- 源文笔误不改不复刻：`fall in to`、`concerned with_ ?`（问号前空格）、`clearer`（应为 more clearly）——按中文自然表达。
