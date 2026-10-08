# 02 — 翻译提示词：Why unit tests（本章特有约束）

## 任务

将《Learn Go with Tests》`why.md`（Meta 篇观点文）由英文精翻为简体中文（zh-CN），出版级质量。样章 `_translation/hello-world/translation.md` 为文风基准。本章没有代码教程约束的束缚，重在完整传达作者的**论证节奏**与**幽默**。

## 本章特别说明（来自主控）

- H1 章标题定为：**为什么写单元测试，以及如何让它们为你所用**。
- 观点文：无 TDD 步骤标题循环；重点是 Lehman 定律 → 重构 → 单元测试 → 设计 → TDD 的递进论证链，段落顺序严格对应，不合并不拆移。
- 如含图片：上游 `.gitbook/assets` 本地图拷 `docs/assets/`（空格改 `-`）；**外链图片 URL 原样保留并报告**。本章 2 张图均为 imgur 外链，原样保留。

## 术语定名（本章新词，必须一致）

- Lehman's laws of software evolution → Lehman 软件演化定律（首现括注英文）；人名 Manny Lehman（曼尼·莱曼）
- The Law of Continuous Change → 持续变化定律；The Law of Increasing Complexity → 复杂度递增定律
- factorisation → 因式分解；legacy → 遗留系统；legacy-proof → 不易沦为遗留系统
- implementation detail → 实现细节；abstraction level → 抽象层级；collaborator → 协作者（首现括注）
- vanity metrics → 虚荣指标；black-box tests → 黑盒测试；user journeys → 用户路径
- Lego bricks → 乐高积木；rabbit hole → 兔子洞；safety net → 安全网；time-sink → 时间黑洞
- Agile → 敏捷（Agile）；red/green → 红/绿；bad old days → "美好的旧时光"（反讽引号保留）
- 沿用术语表：测试驱动开发（TDD，标题处首现全称）、单元测试、重构、覆盖率、基准测试、linter（首现括注）、mock/spy 保留英文

## 代码块硬约束

1. **原文 0 个围栏块**，译文同样不得引入围栏块；3 个缩进式（4 空格）Go 块**逐字节一致**：第二块内的 **tab 缩进**、各块内纯空格占位行、上游笔误（`Hello(“Chris”, es)` 的弯引号与裸 `es`、`//etc..`）一律原样保留。
2. 实现方式：03-draft/05-revision 中以 `@@CODE1@@` `@@CODE2@@` `@@CODE3@@` 独占一行占位，最后用脚本从 source.md 按缩进块原样注入生成 translation.md，杜绝手打误差。

## 链接与格式

- 6 个外链 URL 原样保留：YouTube、`http://www.quii.dev/Scala_-_Just_enough_rope_to_hang_yourself`（http、下划线）、Wikipedia ×2（`%28%29`/`%27` 不动）、martinfowler。
- 2 个 imgur 图片仅译 alt 文本，URL 不动。
- 4 个引用块（`>`）保留标记；上游 `_italic_` 统一转 `*…*`，`**bold**` 保留；无跨章链接、无章首代码链接（本章没有）。
- "#### An example in Go" 两处译文逐字一致（Go 示例）。
- 直角引号「」一律不用；中文与英文/代码间加空格；标题层级与原文一一对应。

## 幽默点对策（保住，不译平）

- "here's wordy version of it" → "还有一个更啰嗦的文字版"（上游漏了冠词 a，属笔误，译文按正常语义译，报告不回改）。
- "enough rope to hang yourself" → "给你一根足够上吊的绳子"（Scala 自嘲，直译保梗）。
- "If the software is 'lucky'" → "如果软件'走运'"（引号讽刺保留）。
- "Lehman was on a roll in the 70s" → "Lehman 在 70 年代手感火热，又给我们送上了一条值得细品的定律"。
- "said to a developer on their first day of programming without a second thought" → 对第一天上班的程序员脱口而出、连想都不想——"重构"被用滥的讽刺。
- "so why not?" → "何乐而不为？"（此处是反讽，语气轻快不严肃）。
- "I say bad old days but this still happens!" → "我嘴上说着'旧时光'，可这种事现在还在上演！"
- "This is the opposite of what we are promised!" → "这跟我们被承诺的完全相反！"（英式感叹，保留力度）。

## 重点句

- "**our tests have falsely elevated the importance of our implementation details**" → 加粗落锤："我们的测试错误地抬高了实现细节的地位"。
- "They were _never_ about only being against a single class/function/whatever" → 重音落"从来"。
- Fowler 引文与两条定律引文：格言化、简短有力。
