# 01 分析 — error-types（Questions and answers 篇）

## 内容概述

全书 Q&A 篇的一章，回答读者 Pedro 在 Gopher Slack 上的提问：能否不比较错误字符串就测试错误的相等性。通过 `DumbGetter` 函数演示"比较错误消息字符串"这种测试的三大坏处，进而引入自定义错误类型 `BadStatusError` + 类型断言（type assertion）的写法，最后在 Addendum 介绍 Go 1.13 的 `errors.As`。

教学链条：提问 → 现编示例函数 → 先写"字符串比较"式测试并自我批评 → 提出更理想的用法（类型系统）→ 改测试（类型断言）→ 实现 `Error()` 方法 → 修好 `DumbGetter` → 总结收益 → 总结章 → Addendum（`errors.As`）。

## 与其他章的关系

- pointers-and-errors（已译）末尾预告了本章："error types 一章（英文原版）会更深入地讨论这个话题，中译收入后此链接会指向译文"——主控负责换链接，本章无需回指。
- 本章正文没有任何站内跨章链接，无前向引用问题。
- 术语需与 pointers-and-errors 一致：flaky（不稳定）、倾听测试的反馈、`errors.As`/错误链等表述。

## 本章新术语（英→中拟定名）

| 英文 | 定名 | 备注 |
|---|---|---|
| error types | 错误类型 | H1 保留英文 "Error types"（专有名词式章名，主控已定） |
| type assertion | 类型断言 | 沿用 generics.md 已有译法，首现加注（type assertion） |
| status error | 状态错误 | 指非 200 引发的错误 |
| ergonomics | 手感/易用性 | 编程语境，意译，不硬注 |
| custom type | 自定义类型 | |
| type system | 类型系统 | |
| encapsulate | 封装 | |
| call stack | 调用栈 | 首现轻注一次 |
| Addendum | 补充 | H2 标题 |
| Gopher Slack | Gopher Slack | Go 社区 Slack，保留英文 |

## 翻译难点

1. **代码块纪律**：8 个代码块（7 go + 1 无标记）。仅 2 处 `//` 注释可译（`DumbGetter` 的文档注释、`ignoring err for brevity`）；子测试名 `"when you don't get a 200 you get a status error"` 是字符串字面量，**不译**；`t.Fatalf("was not a BadStatusError, got %T", err)` 等错误信息均不译。
2. **失败输出块**：第 3 行行首是 4 空格 + 制表符，须逐字节保留。
3. **双关/语气**："extremely error prone and horrible to write" 中 error prone 与 error 双关，中文用"极易出错"自然带过；"It is still \"just\" an `error"` 带引号的 just 要保住（"仍然'只是'一个 error"）。
4. **`This reflects our desire for the _kind_ of error clearer.`** 原句语法欠通（clearer 应为 more clearly），按意图顺译，不硬仿。
5. **`fall in to the trap`** 原文笔误（应为 fall into），中文正常表达即可。
6. **保留斜体/加粗强调**：`_could_`、`_I_`、`_data_`、`_kind_`、`_actually concerned with_`、`_real positive effects_`、`_you'd_`、`_listen to your tests_`、`_feel_`。
7. 无图片、无 Gitbook 转义、无站内相对链接。

## 外链清单（全部原样保留）

- https://github.com/quii/learn-go-with-tests/tree/main/q-and-a/error-types（章首代码链接）
- https://tour.golang.org/methods/15（type assertion，Go Tour）
- https://blog.golang.org/go1.13-errors（Go Blog）
- https://pkg.go.dev/errors#example-As（errors.As 示例）
