# 01 — os-exec 章分析

## 内容概述

"Questions and answers"（读者问答）篇的第一章。素材来自 reddit 用户 keith6014 的提问：
如何测试一个内部使用 `os/exec` 执行外部命令（`cat msg.xml` 生成 XML）的 `GetData()` 函数——
要不要加 "test" 模式开关去读测试数据？

作者的回答只有两点：难测通常意味着关注点分离没做对；别加测试模式，用依赖注入。
随后给出猜测的原始代码（`exec.Command` + `StdoutPipe` + `xml.Decoder`），
把代码拆成「取数据」与「解码 + 业务逻辑」两部分：
`GetData(data io.Reader)` 只管解码和 `strings.ToUpper`，
`getXMLFromCommand()` 负责执行命令并返回 `io.Reader`；
原测试保留为集成测试 `TestGetDataIntegration`，单元测试用 `strings.NewReader` 直接喂字符串。
全章约 3K 词以内，正文短，代码块 5 个（4 go + 1 xml），无图片。

## 本章新术语

| 英文 | 定名 | 说明 |
| --- | --- | --- |
| integration test | 集成测试 | 已有先例（http-server 章用「*集成测试*（integration test）」），非全新 |
| seam | 接缝 | 新术语；代码逻辑中的可拆分点，首现加英文括注 |
| testdata | testdata | 提问者自造的测试数据文件/目录名，保留英文（也可意译为"测试数据"） |
| business logic | 业务逻辑 | 常识级，不注 |
| decouple / coupled | 解耦 / 耦合 | 已在依赖注入章使用过的说法 |
| external command | 外部命令 | 常识级 |
| stdout | 标准输出（stdout）| 常识级，正文仅出现一次，轻量处理 |

术语表既有：依赖注入、关注点分离、单元测试、子测试、结构体、可测试示例。

## 翻译难点

1. **问答体例**：开头引用 reddit 提问，blockquote 中的口语（"I have taken..."、
   "What is a good way..."）要保持对话感；提问者第一人称视角不能译成作者视角。
2. **"A few things"** 两个要点是全书答问的固定格式（working-without-mocks 篇类似），
   译成简短的列条开头，如「有这么几点」。
3. **"I have taken the liberty of guessing"** 英式客套+自嘲，保留幽默：「我冒昧猜了猜……」。
4. **"seam"** 隐喻：缝纫意象，"the 'seam' in our logic starts" 译为逻辑的"接缝"，
   保留引号和括注。
5. **"copy and pasted from the excellent documentation"** 轻微自嘲（抄的），
   保留"复制粘贴"的说法。
6. **代码块注释** 仅一条：`// these 3 can return errors but I'm ignoring for brevity` 需翻译；
   两个测试中无注释。字符串字面量（XML 内容、断言消息）逐字节不动。
7. **链接**：`./dependency-injection.md` 目标章已译（docs/dependency-injection.md 存在），
   按规范保持上游同名文件链接，文字译为「依赖注入」；
   golang.org 的文档外链原样保留。
8. 标题 `## Testable code` → 「可测试的代码」。H1 按主控指定保持 `OS Exec`。
