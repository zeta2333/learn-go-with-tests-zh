# 04 审校诊断（只诊断，不改稿）

对照 03-draft.md 与 source.md。代码块 17/17 逐字节一致（已脚本校验），语言标记一致。
以下为正文层面的诊断。

## 准确性

1. 【轻微】"gain a lot of re-use from the standard library" → 译"标准库里大量的现成能力都能为你所复用"，
   "为你所复用"搭配生硬，且 re-use 的主语应是使用者。建议改为"你能大量复用标准库的现成能力"。
2. 【轻微】"If you try and run it" → "现在再试着运行"，"再"字暗示此前运行过，原文并无此意。改为"现在试着运行一下"。
3. 【轻微】末条总结 "asserts it behaves how the delegate normally does" → 译"断言它的行为与原来一致"，
   丢了 "the delegate normally does" 的指向（delegate 平时的行为）。建议"断言它的行为和 delegate 平时一模一样"。
4. 【轻微】"use `context` to provide cancellation" → "用 `context` 来提供取消"，"提供取消"动宾略别扭，
   建议补全为"提供取消能力"（与 Context 章措辞一致）。
5. 【轻微】"let's just write a "happy path" test where there is no cancellation, just so we can get familiar with
   the problem without having to write any production code yet" → "先只写……好先熟悉一下这个问题"两个"先"叠用，
   破折号插入偏长。建议断句："眼下我们先只写一个"正常路径"（happy path）的测试，其中没有任何取消发生——
   这样能先熟悉一下问题本身，暂时还不用写任何生产代码。"

## 中文表达

6. 【可选】"正常路径的测试又绿了"——口语化但符合全书对话基调，保留。
7. 【可选】"这一步我们先只把传进来的 `io.Reader` 原样返回"，"先只"连用，改"先偷个懒"更贴上下文语气
   （下一段紧跟自嘲），或删"只"。
8. 【可选】"这个手段就格外有用"——上句主语是 context，指代可更明确："这项能力就格外有用"或直接"context 就格外有用"。

## 加注与体例

9. 加注检查：happy path（本章首现，已注）✓；委托模式（首现括注英文）✓；delegate（代码字段不译，正文括注一次）✓。
   无漏注、无过度加注。
10. 体例检查：无「」；无 Gitbook 转义残留；斜体 `_something_/_some_/_compile_/_delegating_` 均以 *…* 保留 ✓；
    三个外链 URL 原样保留 ✓；站内相对链接 `context.md` 保留 ✓；无图片 ✓。
11. 标题层级与原文一一对应（1×H1、2×H2 设问外的 TDD 循环小标题、1×H3）✓。
    "写最少的代码让测试先跑起来，并查看失败的测试输出"忠实但偏长，属原文标题本身冗长，保留。

## 原文笔误（译文中按语义顺译，不做标记）

- 块引文 "half-way through I when I try to continue"：多一个 "I"。
- "From there let the compiler and failing test output can guide us"："let…can" 语法瑕疵。
- 失败输出块第 48 行 "expected an error but didn't get one" 与测试代码消息
  "expected an error after cancellation…" 不一致——属输出块，按规则逐字节保留。
- 首个测试函数名为 `TestContextAwareReader`，后续输出却是 `TestCancelReaders`——上游叙事就如此，不改。
