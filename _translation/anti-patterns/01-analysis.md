# 01 — anti-patterns 内容分析

## 内容概述

全书 Meta 篇最后一章，一篇论述文（无教学代码、无命令行操作）：列举 TDD 与测试的常见反模式并给出补救办法。共 10 个 H2 反模式条目 + 总结：

1. Not doing TDD at all
2. Misunderstanding the constraints of the refactoring step
3. Having tests that won't fail (or, evergreen tests)
4. Useless assertions
5. Asserting on irrelevant detail
6. Lots of assertions within a single scenario for unit tests
7. Not listening to your tests（下含 4 个 H4：Excessive setup…、Leaky interfaces、Interface pollution、Think about the types of test doubles…、Consolidate dependencies）
8. Violating encapsulation
9. Complicated table tests
10. Summary

结构元素：4 个代码块（1 个示意 cmp.Equal 片段、2 个 handler 设计对比、1 个"复杂表格"struct）、6 个引用块（含两条 "Write a test, see it fail"）、2 处列表带 emoji（Gitbook 短码 `:white_check_mark:` `:question:`，后一处直接用 Unicode ✅）。

## 链接盘点

- 全部为外部链接，**无 quii.gitbook.io 站内链接**（mocking/working-without-mocks 仅以文字提及，不带链接）：
  - YouTube（Dave Farley 视频）
  - rakyll.org/interface-pollution
  - github.com/redis/go-redis
  - quii.dev/Start_naming_your_test_doubles_correctly
  - infoq.com（Rich Hickey《Simple Made Easy》）
- 无图片。

## 本章新术语（英→中定名建议）

| 英文 | 定名 |
|---|---|
| TDD anti-patterns | TDD 反模式 |
| evergreen tests | 常青测试（evergreen tests） |
| useless assertions | 无用的断言 |
| leaky interfaces | 泄漏的接口 |
| leaky abstraction | 泄漏的抽象 |
| interface pollution | 接口污染（interface pollution） |
| violating encapsulation | 破坏封装 |
| mobbing / pairing | 群体编程（mobbing）／结对编程（pairing） |
| red / green / blue (refactor) | 红（弄懂要什么）/ 绿（做出来）/ 蓝（重构） |
| consolidate dependencies | 合并依赖 |
| one assertion per test | 每个测试只做一次断言 |
| test package（`package xxx_test`） | 测试包 |

沿用的既有术语：测试替身、倾听测试（listen to your tests，全书已多次用"倾听"）、表驱动测试、子测试、验收测试、HTTP 处理器（handler）、红绿重构（http-server.md 用"红、绿、重构"）。

## 翻译难点

1. **反模式名称的醒目性**：H2/H4 标题即反模式名，译名后加英文括注，方便读者对照社区通用叫法。
2. **英式冷幽默**："wish you had a different career"（想换个职业）、"a budding pedant yells"（初出茅庐的学究大喊）、"would be very difficult to arrive at"（反讽：这些毛病在 TDD 下还真难犯出来）、"For the millionth time"（第一百万次）。必须保住语气，不能译平。
3. **"more difficult than it _could_ be" 的 can/could 文字游戏**：需用"本可以/本来能"重现对照。
4. **`make it right` 与 "Simple is not easy"**：前者译"把代码做对/改漂亮"；后者是 Rich Hickey 名言，译"简单不等于容易"，链接保留。
5. **emoji 短码**：`:white_check_mark:`/`:question:` 在 mkdocs（无 pymdownx.emoji）下不渲染，统一转 Unicode ✅/❓（与本章后半部分自带的 ✅ 一致）。
6. **术语密度高且短**：conversational 语气 + 短句，避免论文腔。
