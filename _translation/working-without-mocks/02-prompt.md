# 02 — 翻译提示词：Working without mocks（本章特有约束）

## 任务

将 `working-without-mocks.md` 由英文精翻为简体中文（zh-CN），出版级质量。样章 `_translation/hello-world/translation.md` 为文风基准。本章是全书最重要的论述章，语气从容自信，论证链严密，幽默点保住不译平。

## 章标题

H1 定为：**不用 mock 的测试**（主控指定）。

## 术语策略

- mock、stub、spy、fake **保留英文**（术语表）；test double → 测试替身（首现加注）。
- **contract 为本章核心新词**：首现写"契约（contract）"，此后正文统一用 contract（与 fake 等全英文词族一致、与代码 `API1Contract` 呼应）。仓库链接文字"示例仓库"即可。
- SUT 首现："被测对象（subject under test，SUT）"，此后用 SUT。
- 集成测试 / 黑盒 / 有状态·无状态 / 装饰器模式 / 渐进主义 / 服务层 / 用例 / 用户故事 / 预发（staging）环境 / 开发者体验（DX）。
- Given / When / Then 保留英文关键词（BDD 惯例），加粗斜体格式照旧；`***Then**,*` 的斜体逗号怪格式照搬。
- "API first" → "API 优先"；该段 wiki 场景的 "API contracts" 译"API 契约"（非可执行 contract 机制）。

## 链接处理（本章特殊）

本章是首个源文含 quii.gitbook.io 绝对链接的章节，verify 要求源文全部 URL 在译文中出现。处理如下（与 00-book-prompt 第 2 条的意图对齐）：

1. **URL 一律原样保留**（含 4 个 gitbook 链接）——verify 的 URL 完整性检查是硬门槛，gitbook 绝对 URL 按外链处理。跨章链接留待终审统一切换为本地 `.md`（mocking.md / dependency-injection.md / scaling-acceptance-tests.md ×2），届时 verify 的 URL 检查需同步放宽。
2. 指向**未翻译**章节的链接（仅 Anti-patterns）：链接文字后加"（英文原版）"，即 `[反模式（英文原版）](…)`，便于终审查找替换。
3. 指向**已翻译**章节的链接（Mocking、Dependency Injection、Scaling Acceptance Tests ×2）：链接文字用中文章名"Mocking"/"依赖注入"/"扩展验收测试"（初判 scaling 未翻译有误，docs/scaling-acceptance-tests.md 实际存在，已更正），URL 暂留 gitbook。
4. 章首无"本章所有代码"链接（源文即无），不得添加。
5. 全部外链（quii.dev ×2、GOOS、YouTube、go-fakes-and-contracts ×2、imgur ×3）URL 原样保留。

## 图片

3 张 i.imgur.com 外链图片 URL 原样保留，alt 文字翻译（系统架构 / 用 fake 做集成测试 / fake 与 contract 示意）。不拷贝、不改路径。

## 代码块硬规则

- 16 个代码块：15 go + 1 mermaid，**数量、语言标记、顺序与原文一致**。
- mermaid 块逐字节一致（英文标签不动）。
- Go 块仅 `//` 注释随章翻译，其余逐字节一致；`// Output:` 无。
- `<u>…</u>` 2 处保留；加粗/斜体/嵌套格式（`***…***`）一一对应。
- Gitbook 转义：源文无；直角引号「」禁用；双引号沿用样章 hello-world 及多数已发布章节的直引号 " 体例（弯引号""仅部分后期章节使用），此分歧报告主控终审统一。

## 标题定名

tl;dr（保留）→ 测试替身入门 → stub 和 mock 的问题 → 一个真实案例 → 麻烦来了 → 测试策略 → 集成测试 → 有请 fake 登场 → fake 带来更多封装的好处 → fake 的维护成本 → 软件的演进 → 更胜一筹的开发者体验 → 用装饰器应付非正常路径 → 这些额外的代码不是浪费吗？→ 这套方法怎么融入 TDD？→ 讲数据库测试的那一章呢？→ 总结 → 把你的系统当作一组模块 → 可我要做的东西很小，API 也很稳定啊 → 让你的依赖成为一等公民。

## 幽默点对策（必保）

- "palette cleanser" → "清口小菜"（烹饪比喻）。
- "*magic* (business value)" → "_magic_（业务价值）"。
- 免责声明戏仿 → "如有雷同，纯属巧合"（保粗斜体）。
- "fun and unexpected ways" → 以各种"有趣"的方式坏掉（反讽引号）。
- "(or integrated!)" → "（或者叫集成！）"。
- "chase coverage scores, right?" → "总不是为了刷覆盖率吧？"
- "superpower" → "超能力"；"battle-tested fake" → "身经百战的 fake"。
- "Dave 禁令"（`ErrDaveIsForbidden`）→ deadpan 直译。
- "I need to be more clever for" → 自嘲直译："要求我自己更聪明才行"。
- "Henry Ford 幽灵"博文 → 链接文字译"亨利·福特的幽灵正在毁掉你的开发团队"。
