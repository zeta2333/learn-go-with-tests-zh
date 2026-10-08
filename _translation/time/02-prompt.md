# time 章翻译约束（02-prompt）

## 章标题

H1：`Time`（主控指定，不译）。

## 标题定名（沿用 io 章已定稿的 TDD 循环标题）

- Just enough information on poker → 关于扑克，知道这些就够了
- Reminder of the code → 回顾一下现有代码
- `time.AfterFunc` / `time.Duration` → 保留代码原名（注意修正原文标题笔误 `time.Afterfunc` → `time.AfterFunc`，报告中说明）
- Write the test first → 先写测试
- Try to run the test → 试着运行测试
- Write the minimal amount of code for the test to run and check the failing test output → 写最少的代码让测试能运行，并检查失败的测试输出
- Write enough code to make it pass → 写足够的代码让测试通过
- Refactor → 重构
- Wrapping up → 总结
- A quick project recap → 项目快速回顾
- More examples of good separation of concerns → 关注点分离的更多例子
- An example of a function implementing an interface → 用函数实现接口的例子

## 术语与表述

- 盲注（blind）首现加注；blind bet=盲注；chips=筹码；Texas Hold'em=德州扑克（首现括注）。
- 产品负责人（product owner）不重注（app-intro 已注）。
- dummy 保留英文，首现括注"哑对象"；mock/spy/fake/stub 一律英文。
- "mocking the time" 类表述与 mocking 章一致：mock 掉时间 / 用依赖注入替换"真正的"时间。
- `time.AfterFunc` 描述沿用 context 章句式："安排……在一段时间后调用"。
- "listen to your tests" → 听测试的话（加粗处保留加粗）。
- vararg → 可变参数（`...string` 语法）。
- type conversion → 类型转换，链接 https://go.dev/tour/basics/13 原样。

## 风格要点

- 数字与盲注表逐字核对：5 分钟基时 + 每人 1 分钟；6 人 = 11 分钟；测试表 11 组（100→8000，间隔 10 分钟 / 7 人 12 分钟）不得改动。
- 幽默点：cheat a little（耍滑头）、naughty（不太听话）、free to commit whatever sins（随我们犯什么罪）、Ouch!、naming is awkward（起名之难）、"you're so silly" 保留英文原文（它是断言里的字符串字面量）。
- `you're so silly`、`Lloyd is a killer`、`Pies`、`Ruth wins`、`Shaun wins` 等字符串字面量与代码一律原样。
- 代码块、终端输出逐字节一致；`// game.go` 等文件名注释保留原文。
- 引号用弯引号""；无直角引号。

## 链接与图片

- 本章无跨章链接、无图片（已确认）。6 个外链原样保留：
  1. https://github.com/quii/learn-go-with-tests/tree/main/time（章首代码链接）
  2. https://golang.org/pkg/time/#AfterFunc
  3. https://golang.org/pkg/time/#Duration（标题链接）
  4. https://martinfowler.com/articles/mocksArentStubs.html（dummy 引文）
  5. https://golang.org/pkg/time/（Wrapping up 的 time 文档）
  6. https://go.dev/tour/basics/13（Type Conversion）

## 交付

产出 03-draft → 04-critique（只诊断）→ 05-revision → translation.md；verify.py 通过。
