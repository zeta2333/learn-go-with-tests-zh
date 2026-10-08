# 01 分析 — pointers-and-errors

## 内容概述

本章是全书第一次正面讲 Go 的两大特色机制：指针与错误。以 Bitcoin 钱包为主线：

1. `Wallet` 结构体 + `Deposit`/`Balance` 方法 → 值接收者不生效 → 引出"Go 传参皆复制"，用 `&`/`%p` 打内存地址实验验证 → 改为指针接收者 `*Wallet` → 结构体指针自动解引用。
2. 重构：`type Bitcoin int` 基于已有类型造新类型；实现 `fmt.Stringer`（`String() string`），测试输出变 `10 BTC`。
3. 新需求 `Withdraw`：余额不足应报错 → `error` 接口、`nil`、运行时 panic → `errors.New` → 错误信息重复 → 提炼为哨兵变量 `ErrInsufficientFunds`（错误即值）。
4. errcheck linter 发现"成功路径未检查错误"→ 补 `assertNoError`。
5. 较新的补充节：`fmt.Errorf` + `%w` 错误包装（Go 1.13）、`errors.Is`/`errors.Unwrap`/`errors.As`，并前向引用 maps、error-types 两章。
6. 总结：指针 / nil / 错误 / 造新类型四组要点。

TDD 循环标题多轮复现（先写测试/试着运行测试/写最少量的代码…/写足够的代码…/重构），沿用上一章定稿译法。

## 本章新术语（全书首现，需定名并加注）

| 英文 | 定名 | 备注 |
|---|---|---|
| pointer | 指针 | 术语表已有定名，本章首现加注（pointer） |
| dereference | 解引用 | 本章新词，首现加注（dereference） |
| struct pointer | 结构体指针 | 与"自动解引用"链接 golang.org/ref/spec#Method_values |
| pointer receiver / value receiver | 指针接收者 / （值接收者） | receiver 沿用上一章"接收者" |
| error | 错误；类型名保留 `error` | `errors.New`/`fmt.Errorf`/`ErrInsufficientFunds` 原样保留 |
| nil | nil（不译） | 与 `null` 类比讲解 |
| runtime panic | 运行时 panic | panic 保留英文 |
| nillable | 可能是 nil 的（nillable） | 一次性轻注 |
| error wrapping | 错误包装 | `%w` 一节 |
| unwrap / 解包 | errors.Unwrap 语境用"解包/取出" | 动词灵活处理 |
| sentinel value | 哨兵值 | errors.As 一段首现加注一次 |
| flaky (test) | flaky（不稳定） | 总结处首现轻注 |
| linter | linter（静态检查工具） | errcheck 一段轻注一次 |
| single source of truth | 唯一的事实来源 | 意译即可 |
| overdraft facility | 透支功能 | |
| Stringer | Stringer（接口名，不译） | |
| errcheck | errcheck（工具名，不译） | |

已有定名沿用：struct 结构体、method 方法、receiver 接收者、field 字段、interface 接口、helper 辅助函数、断言、重构、格式化动词/格式化字符串、占位符、包、编译器。

## 翻译难点

1. **代码块 35 个（33 go + 2 无语言标记）必须逐字节一致**。多处编译器输出/终端输出是行内代码（反引号单行），同样原样保留。唯一可动的 go 注释：`errors.Is` 示例里的 `// still true, ...`（随章翻译）；但 `fmt.Println(err)` 示例里的 `// processing withdrawal for account acc-123: ...` 是**程序输出**，虽写成注释也保留英文。
2. **"传参即复制"是本章核心命题**，表述必须准确：`In Go, **when you call a function or a method the arguments are** _**copied**_.` 的加粗+斜体加粗嵌套要复原。
3. 幽默点：Fintech/比特币的自嘲开头、_very secure wallet_、career in fintech secured + bask、not always saints、goof 掉的 "uhhh bitcoins?"。
4. 较新的 %w/errors.Is 一节句长句多（Unwrap 机制一句到底），需拆短而不丢信息。
5. Gitbook 转义：本章源文未见 `\.` 类转义（0 处），无需清理。
6. 上游疑似笔误：`with leading `0x`s and the  escape character` —— 缺了 `` `\n` `` 且多一个空格（原书应为 "the `\n` escape character"）。按规范不改原文，译文按现有文字自然带过，报告中注明。
