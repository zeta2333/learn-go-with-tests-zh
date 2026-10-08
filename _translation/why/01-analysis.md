# 01 — 内容分析：Why unit tests and how to make them work for you

## Content Summary

- **主题**：观点文（非代码教程），全书"Meta"篇。论证链条：软件的价值在于可变 → Lehman 软件演化定律（持续变化定律、复杂度递增定律）→ 重构是管理复杂度的手段、且重构时绝不能改变行为 → 安全重构需要单元测试（信心/文档/快速反馈）→ 单元测试遭抵触的根源是"测错了抽象层级"（用正方形/三角形寓言讲测试错误抬高了实现细节）→ 单元测试是设计问题（自包含解耦的"单元"，乐高积木比喻）→ 三者互相成就 → TDD 是把这一切落地的流程（小步前进、红-绿-重构）。
- **语气**：大量自嘲与英式幽默（Scala 上吊绳、话痨文字版、"美好的旧时光"还在上演），论证节奏感强，幽默不能译平。
- **代码块**：**0 个围栏块**；3 个**缩进式（4 空格）Go 代码块**，verify.py 只比对围栏块，但按全书规则仍须与原文逐字节一致（第二块内含 **tab 缩进**，第一/三块内含多处空格占位行；第三块有上游笔误 `Hello(“Chris”, es)`——弯引号且 `es` 未加引号，**照原样保留**）。译稿中用 `@@CODE1/2/3@@` 占位，脚本从 source.md 原样注入，保证字节精确。
- **链接**：外链 6 个——YouTube 视频、quii.dev（Scala 上吊绳博文，**http** 且 URL 含下划线）、Wikipedia Manny Lehman（`%28 %29` 转义）、Wikipedia Lehman's laws（`%27` 转义）、martinfowler RefactoringMalapropism，全部原样保留。无跨章内部链接、无前向引用。
- **图片**：2 张均为 **imgur 外链**（拼正方形示意），按本章指示原样保留 URL 并报告主控（主控可经 GitHub Actions 代取入库）。无上游 `.gitbook/assets` 图，无需拷贝。
- **引用块**：4 个（Lehman 定律 ×3、Fowler 论重构误用 ×1），译出中文，标记保留。

## Terminology（本章新词定名）

| 英文 | 中文 | 备注 |
|------|------|------|
| Lehman's laws of software evolution | Lehman 软件演化定律 | 首现括注英文；人名 Manny Lehman 保留英文+括注（曼尼·莱曼） |
| The Law of Continuous Change | 持续变化定律 | 章节标题，后文 Capitalized 提及时同译 |
| The Law of Increasing Complexity | 复杂度递增定律 | 同上 |
| legacy / legacy-proof | 遗留系统 / 不易烂成遗留系统 | 首现括注 legacy |
| factorisation | 因式分解 | 数学比喻，全章核心类比 |
| implementation detail | 实现细节 | |
| abstraction level | 抽象层级 | |
| collaborator | 协作者（collaborator） | mock 语境行话，首现括注 |
| vanity metrics | 虚荣指标 | |
| system/black-box tests | 系统/黑盒测试 | |
| user journeys | 用户路径 | |
| root causes | 根本原因 | |
| Lego bricks | 乐高积木 | 全章核心比喻，保留意象 |
| unit | 单元 | 单元测试的"单元"，加引号处随原文 |
| rabbit hole | 兔子洞 | 保留比喻（mocking 章已用） |
| feedback loop | 反馈循环 | |
| safety net | 安全网 | |
| time-sink | 时间黑洞 | |
| hand-off | 交接 | |
| biting off more than they can chew | 贪多嚼不烂 | 习语意译 |
| on a roll | 手感火热 | 幽默点 |
| bad old days | "美好的旧时光" | 反讽，保引号 |
| red / green | 红 / 绿 | TDD 惯用色，括注原色字 |
| Agile | 敏捷（Agile） | 首现括注 |
| feature factory | "功能工厂" | 保留引号讽刺 |

沿用术语表：单元测试（unit test）、测试驱动开发（TDD，标题处首现即全称）、重构（refactor）、覆盖率（coverage）、标准库、基准测试、linter（首现括注"代码静态检查工具"）、mock/spy（保留英文）、副作用、领域。

## Translation Challenges

- 三个缩进式 Go 代码块逐字节一致：含 tab、纯空格行、上游笔误（弯引号 `“Chris”`、未加引号的 `es`、注释 `//etc..` 少一个点），一律不动。
- 幽默点清单：话痨文字版；Scala"足够上吊的绳子"；"I literally spent weeks"（实打实花了几周）；"If the software is 'lucky'"（走运）；"Lehman was on a roll in the 70s"（手感火热+值得细品）；"第一天的程序员被脱口而出'重构一下'”；"This is the opposite of what we are promised!"（说好的承诺呢）；"美好的旧时光……还在上演"；"so why not?"（何乐而不为的反讽）。
- 正方形/三角形寓言是全章论证枢纽，"falsely elevated the importance of our implementation details" 一句要译得有力。
- "#### An example in Go" 出现两次，译文必须逐字一致。
- "They were _never_ about only being against a single class/function/whatever" —— 斜体重音落在 never，中文要落"从来"。
- 两条 Lehman 定律引文与 Fowler 引文为引用块，措辞要像"定律"，简短、格言化。
