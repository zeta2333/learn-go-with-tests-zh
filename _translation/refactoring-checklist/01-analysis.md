# 01 — 内容分析：Refactoring checklist（learn-go-with-tests）

## Content Summary

- **主题**：这是一份**操作性清单**章，不写代码教程，而是回答"重构到底是什么、不是什么，以及每个 TDD 循环该在脑子里过一遍哪些动作"。核心定义：重构 = 改进现有代码且**不改变行为**，因此不该动测试；要改测试时你其实在做"设计"，应照样走 TDD。
- **结构**：前半讲概念边界（重构 vs 设计 vs 大设计、"见树又见林"），中半是逐条清单（内联变量 / 提取变量 / 广义 DRY / 提取魔法值 / 公开方法易扫读 / 值的创建挪到构造时 / 消灭注释），每条都带 IntelliJ/GoLand 快捷键和小型 Go 示例；后半讲例外（IDE 安全重命名）、工具使用心法、"重构不需要请示"和总结。
- **人物与引用**：Martin Fowler 三处引言（思考即重构 / 注启发则 / 截止时间与生产力）+ 荐书《Refactoring》(2nd ed)；Collins 词典对习语 see the wood for the trees 的定义（带外链）；Wikipedia 对 magic number 的定义（带外链）。**Kent Beck 本章未出现**（主控说明中的"Kent Beck 重构节奏"是背景提示，正文没有）。
- **代码块**：13 个，全部 `go`。多为示意片段（如 `WishHappyBirthday` 第二个代码块没有闭括号，原文如此，必须逐字节保留）；含占位注释 `// some fascinating emailing code`、`//etc`、`// etc..`、`//todo: handle codes, err etc`、`// etc`（按全书规则随章翻译为中文）。
- **图片**：1 张外链图 `https://i.imgur.com/4sgUG7L.png`（提取变量操作截图），原样保留 URL。
- **行内格式**：两处 `<u>` 下划线标签原样保留；`*…*` 与 `_…_` 两种斜体混用按原文位置保留；无 Gitbook 转义符；无章内链接、无"本章所有代码"链接（本章原文就没有）。

## Terminology

| 英文 | 中文 | 备注 |
|------|------|------|
| refactoring | 重构 | 术语表词；H1 定为"重构清单" |
| behaviour change | 行为变更 | 与"设计变更"对举 |
| method signature | 方法签名 | |
| private / public method | 私有 / 公开方法 | |
| extract variable | 提取变量 | 重构手法名 |
| inline variable | 内联变量 | 重构手法名 |
| extract method | 提取方法 | 重构手法名 |
| DRY (Don't repeat yourself) | DRY（不要重复自己） | DRY 保留英文，首现括注 |
| magic value / magic number | 魔法值 / 魔法数字 | 术语表：魔法数字 |
| coupling | 耦合 | 前章已用 |
| cohesion | 内聚 | 本章新 |
| constructor function | 构造函数 | 术语表词 |
| field | 字段 | 术语表词 |
| source control | 版本控制 | 术语表词 |
| commit / revert | commit / revert（动词可"提交/回退"） | 术语表 |
| feedback loop | 反馈回路 | |
| safety net | 安全网 | |
| mental checklist | 心理清单 | |
| muscle memory | 肌肉记忆 | |
| well-factored | 组织良好 / 分解得当 | |
| ceremony | 仪式性代码 | "boring, distracting ceremony" |
| navigate to symbol | 跳转到符号 | IDE 术语 |
| time-sink | 时间黑洞 | |
| deadline | 截止时间 | 术语表词 |
| see the wood for the trees | 只见树木，不见森林 | Collins 定义整句带链翻译 |

保留英文不译：`DRY`、IDE、`io.Reader`、`POST` 及一切代码标识符（`WishHappyBirthday`、`CreateWidget`、`createWidgetPayload`、`createWidgetURL`、`Timeout` 等）；快捷键 `command+option+n` 等全部反引号保留；IntelliJ/GoLand 产品名。

## Tone & Style

- 清单体例：条目动词开头、短句、祈使语气（"跑测试""commit 或 revert"）。
- 幽默/锐利点：`// some fascinating emailing code`（自嘲式占位注释）；"You're doing something else"（点名式泼冷水）；"Have you learned how to navigate codebases using your tooling effectively?"（blunt reply 的直球）；"refactoring should not be a decision for others to make"（结尾劝诫）。

## Translation Challenges

- 习语标题 "Seeing the wood for the trees" → "见树又见林"，词典定义引文在链接内整句意译，英/美式英文说法保留英文原词。
- "drive this change with a test first" → "由测试先行驱动这次变更"；"drive out the change" → "把变更驱动出来"。
- "wrap up irrelevant hows into whats" → "把不相干的'怎么做'打包进'做什么'"——what/how 对仗必须保住。
- "an essential character in the narration of the method" → "方法的叙事里的主角"——叙事隐喻保留。
- "toggling the code with inline and extract" → 用内联和提取来回"切换"。
- 负面清单式 bullet（you can't: / you can:）保持清单体例、动词开头。
- `WishHappyBirthday(person Person)` 代码块原文即缺闭括号，不改（原文笔误原样保留）。
