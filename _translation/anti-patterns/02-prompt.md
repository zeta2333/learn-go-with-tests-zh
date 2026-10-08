# 02 — anti-patterns 本章翻译约束

## 标题

- H1 定为：`# 反模式`（主控指定；上游为 "TDD Anti-patterns"）。

## 反模式命名体例

H2/H4 标题 = 译名 + 英文括注（括注格式：`（evergreen tests）`），正文首现再自然带出中文名。定名：

| 原文标题 | 译文标题 |
|---|---|
| Not doing TDD at all | 完全不做 TDD |
| Misunderstanding the constraints of the refactoring step | 误解重构步骤的约束 |
| Having tests that won't fail (or, evergreen tests) | 永不失败的测试（evergreen tests） |
| Useless assertions | 无用的断言 |
| Asserting on irrelevant detail | 断言无关细节 |
| Lots of assertions within a single scenario for unit tests | 单个场景中堆砌大量断言（单元测试） |
| Not listening to your tests | 不倾听你的测试 |
| Excessive setup, too many test doubles, etc. | 准备代码过长、测试替身过多，诸如此类 |
| Leaky interfaces | 泄漏的接口（leaky interfaces） |
| Interface pollution | 接口污染（interface pollution） |
| Think about the types of test doubles you use | 想清楚你用的是哪类测试替身 |
| Consolidate dependencies | 合并依赖（consolidate dependencies） |
| Violating encapsulation | 破坏封装（violating encapsulation） |
| Complicated table tests | 变复杂的表驱动测试 |

## 语气与幽默点对策（必须保住）

- "wish you had a different career" → 「是不是开始憧憬另一种职业生涯了」
- "a budding pedant yells" → 「一位初出茅庐的学究大喊」
- "problems … would be very difficult to arrive at if … TDD had been used" → 保留反讽：「这些问题还真难折腾得出来」
- "For the millionth time" → 「第一百万次」
- "don't be ashamed of the error message" → 「别让错误信息拿不出手」
- "the lazy developer in you be annoyed" → 「你内心那个懒惰的开发者」

## 其他硬性处理

- `:white_check_mark:` → ✅、`:question:` → ❓（mkdocs 无 emoji 扩展，短码不渲染；与本章后文自带 ✅ 统一）。报告里注明。
- 代码块逐字节一致，仅译 Go `//` 注释；上游代码里 `t.Error`（应为 `t.Errorf`）不改，报告笔误。
- 引用块中的错误信息 `` `false was not equal to true` `` 原样保留。
- "Write a test, see it fail" 两条引用块译出：「写一个测试，看它失败」。
- 站内无内部链接；全部 5 个外链 URL 原样保留。
- 倾听测试 → 全书既有用法"倾听（你的）测试"。
- red/green/blue(refactor) → 红/绿/蓝（重构），呼应 http-server.md 的"红、绿、重构"。
- 不用「」；中英之间加空格；代码标识符反引号。
