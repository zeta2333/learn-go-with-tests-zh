# time 章分析

## 内容概述

全书第一次进入"应用篇"的收尾阶段。产品负责人要求给命令行扑克应用加"盲注提醒"功能：按玩家人数决定的时间间隔，打印逐步上涨的盲注金额。教学主线是**如何测试依赖时间的逻辑**——不真等 10 分钟，而是把时间调度抽象成 `BlindAlerter` 接口注入进来，用 spy 观察调度行为。

章节脉络（严格对应原文段落序）：

1. 开场 + 扑克盲注规则（5 分钟基时 + 每人 1 分钟；盲注 100 起步翻倍）
2. 回顾 command-line 章的 `CLI` 代码
3. `time.AfterFunc` / `time.Duration` 介绍；说明 Go 不能比较函数，所以要在 `time.AfterFunc` 外包一层可 spy 的抽象
4. 先写测试：`SpyBlindAlerter`，断言有一个 alert 被调度 → 编译错 → 定义 `BlindAlerter` 接口 + dummy spy 修其他测试 → `ScheduleAlertAt(5*time.Second, 100)` 硬编码通过
5. 扩成表驱动测试（11 组盲注/时间）→ 循环 + 递增 `blindTime` 通过
6. 重构：抽 `scheduleBlindAlerts` 方法；测试里两个匿名 struct 收敛成 `scheduledAlert` 类型 + `String()` 方法（未给 `assertScheduledAlert` 实现，留练习）
7. 落地到应用：`BlindAlerterFunc` 函数类型实现接口 + `StdOutAlerter`；`main` 里用 `poker.BlindAlerterFunc(poker.StdOutAlerter)`；顺带讲"任何类型都能实现接口，不止 struct"
8. 人数提示：`CLI` 加第 4 个依赖 `out io.Writer`，prompt 写进 stdout；输入 "7\n" 后按 12 分钟间隔调度
9. 重构大戏：**听测试的话**——4 个依赖说明职责过多；抽出 `Game` 类型（`Start`/`Finish`），再把 `NewCLI` 改为接收 `game`；把游戏相关断言挪进 `TestGame_Start`/`TestGame_Finish`；把 `Game` 改名为 `TexasHoldem`、新接口叫 `Game`，`CLI` 面向接口 + `GameSpy`
10. 非数字输入的边界场景：不 start、打印错误信息；`BadPlayerInputErrMsg` 常量；`assertMessagesSentToUser`（vararg）
11. 练习收尾：`Lloyd is a killer` 场景
12. Wrapping up：项目回顾（5 章）、`time.AfterFunc`/`time.After`/`time.NewTicker`、关注点分离更多例证、先重构生产代码再重构测试、DI 记录意图；最后"函数实现接口"专题（`BlindAlerterFunc` 惯用法 + `type Blog map[string]string` 实现 http.Handler）

## 本章新术语（英 → 中定名）

| 英文 | 定名 | 备注 |
|---|---|---|
| blind / blind bet | 盲注 | 扑克术语，首现加注（blind） |
| Texas Hold'em (poker) | 德州扑克 | 首现括注 |
| chips | 筹码 | |
| blind increment | 盲注递增间隔 | 代码标识符 `blindIncrement` 不译 |
| schedule / scheduling | 调度 | `ScheduleAlertAt` 等标识符不译 |
| alert | 提醒/警报 | 语境多为"盲注提醒" |
| prompt | 提示（语） | `PlayerPrompt` 标识符不译 |
| dummy | dummy（哑对象） | 沿用全书惯例：test double 各类名保留英文 |
| vararg | 可变参数 | arrays-and-slices 章已定 |
| type conversion | 类型转换 | http-server 章用过 type casting（类型转换）；此处用规范说法 |
| pipelined wording: "listen to your tests" | 听测试的话 / 倾听测试 | mocking、select 章同款 |
| product owner | 产品负责人 | app-intro 已注，本章不重注 |
| dependency injection (DI) | 依赖注入 | 术语表已有 |

既有术语照表：mock/spy/stub/fake 保持英文；表驱动测试；子测试；关注点分离；零值；构造函数；竞态条件（本章不涉及）。

## 翻译难点与对策

1. **扑克背景的轻科普**："Just enough information on poker" 要译出"给你刚刚好的背景"的口气，规则列表逐条对应，数字一个不能错（5 分钟 + 每人 1 分钟；6 人 11 分钟；100 起翻倍）。
2. **"We're just going for the simplest scenario first and then we'll iterate"** 等口语化过渡，保持作者碎碎念的节奏。
3. **"Strictly speaking ... but let's cheat a little"**：自嘲语气要保住（"严格来说……不过咱们稍微耍个滑头"）。
4. **"naughty"**（"have been somewhat naughty not integrating with our application"）：英式自嘲，译"有点不听话/偷懒了"。
5. **"Ouch! A lot of changes."**：单句成段，语气词要脆。
6. **"It is here we realise that naming is awkward sometimes."**：译出"起名果然是计算机科学两大难题之一"式的无奈但不加戏。
7. **"Remember, we are free to commit whatever sins we need to make this work."**：sin 双关（commit 罪行/commit 代码），保住"先造再收拾"的调侃。
8. **Fowler 引文**：正文翻译，Dummy 保留英文并括注哑对象。
9. **代码块全部逐字节保留**；Go 注释随章译（本章源码块内注释极少，仅 `game.go`、`main.go` 两处路径注释 `// game.go` / `// cli.go` / `// main.go` 属于正文性注释，保留不译也可——它们标注的是文件名，不是英文句子，决定：保留原样）。
10. **无跨章链接、无图片、无 Gitbook 转义**（已 grep 确认）；6 个外链全部原样保留。
11. 原文疑似笔误：`### time.Afterfunc`（应为 `AfterFunc`）——标题按正确大小写 `### time.AfterFunc` 处理并报告；`{20 * time.Minute, 300}` 盲注表与"翻倍"描述不一致系原文如此，照译不改；"We read in the `numberOfPlayersInput` into a string" 与代码片段不完全对应，照译。
