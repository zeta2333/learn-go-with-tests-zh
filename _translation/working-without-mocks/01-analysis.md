# 01 — 内容分析：Working without mocks（learn-go-with-tests）

## Content Summary

- **主题**：全书最重要的论述章。论点：mock/stub/spy 把"对依赖行为的假设"临时编码进每个测试，假设未经系统验证，威胁测试套件价值；主张改用 **fake（有状态的真身替身）+ contract（契约：可对 fake 和真实依赖重复执行的行为规约）**，获得可验证、可复用、可演进的测试替身。
- **结构**：tl;dr → 测试替身入门（stub/spy/mock/fake 分类学）→ stub 和 mock 的问题（六 API 项目案例：flaky 测试、测试策略困境、集成测试缺口）→ fake 登场（服务层用例、用户故事、mermaid 时序图、断言状态而非 spying）→ 封装收益与维护成本 → **contract 详解**（API1Contract 代码、用同一 contract 测内存版与真实实现）→ 软件演进流程（6 步）→ 开发者体验 → 装饰器覆盖非正常路径 → "额外代码是浪费吗" → 与 TDD 的关系 → 测试数据库之问（"Don't mock the database driver"）→ 总结（Farley 引文、渐进主义、模块化、一等公民依赖）。
- **前置**：Mocking 章、依赖注入章（均已翻译）；引用 Anti-patterns、Scaling Acceptance Tests（**未翻译**，前向引用）。
- **代码块 16 个**：15 个 Go + 1 个 mermaid 时序图。Go 块内 `//` 注释随章翻译（verify 允许）；**mermaid 块必须逐字节保留**（verify 对非 go 块全等比较，标签保持英文）。
- **图片 3 张**：全部为 i.imgur.com 外链（架构图、集成测试图、fakes-and-contracts 图），按规则原样保留 URL，alt 文字翻译。
- **外链/跨章链接 13 个**：quii.gitbook.io ×4（mocking、DI、anti-patterns、scaling×2）、quii.dev ×2、go-fakes-and-contracts 仓库 ×2、GOOS 官网、YouTube（Rich Hickey "Simple Made Easy"）、imgur ×3。**注意：本章是首个源文含 quii.gitbook.io 绝对链接的章节**，verify 的 URL 完整性检查（urls(src) − urls(tra)）要求这些 URL 在译文中原样出现，与"跨章链接改写为本地 .md"规则冲突 → 处理：URL 保留，未翻译章节在**链接文字**处加"（英文原版）"注记（详见 02-prompt）。

## Terminology（新术语定名）

| 英文 | 中文 | 备注 |
|------|------|------|
| test doubles | 测试替身 | 术语表已有；本章首现加注 |
| fake | fake | 保留英文（术语表） |
| contract | contract | **新定名**：首现"契约（contract）"，正文统一用 contract（与 mock/stub/spy/fake 全英文词族一致，且代码标识符即 `API1Contract`）；"API first"段落谈 wiki 上的 API 契约时可用"API 契约" |
| subject under test (SUT) | 被测对象 | **新定名**：首现"被测对象（subject under test，SUT）"，此后用 SUT |
| stub / spy / mock | stub / spy / mock | 保留英文 |
| integration test | 集成测试 | 新术语 |
| black-box | 黑盒 | |
| happy path / non-happy path | 正常路径 / 非正常路径 | 术语表已有 happy path |
| hexagonal / ports & adapters architecture | 六边形架构 / "端口与适配器"（ports & adapters）架构 | |
| service layer | 服务层 | |
| use case | 用例 | |
| stateful / stateless | 有状态 / 无状态 | |
| decorator pattern | 装饰器模式（decorator pattern） | |
| flaky tests | 不稳定的测试（flaky tests） | |
| developer experience (DX) | 开发者体验（DX） | |
| in-memory fake | 内存版 fake | |
| incrementalism | 渐进主义（incrementalism） | |
| modular system | 模块化系统 | |
| "mockist" approach | "mock 主义"（mockist）的路数 | |
| palette cleanser | 清口小菜 | 保留烹饪比喻幽默 |
| user story | 用户故事 | |
| Given / When / Then | 保留英文 | BDD 关键词，加粗斜体格式照旧 |
| rollback | 回滚 | |
| staging environment | 预发（staging）环境 | |
| GOOS | GOOS | 《Growing Object-Oriented Software, Guided by Tests》 |

保留英文：`RecipeBook`、`StubRecipeStore`、`SpyRecipeStore`、`MockRecipeStore`、`FakeRecipeStore`、`API1/API2`、`API1Contract`、`API1Decorator`、`XXXFunc`、`Pantry`、`planner`、`inmemory`、`sqlite`、`ErrDaveIsForbidden`、`someRecipes`、`NewCustomerReq` 等全部代码标识符；`tl;dr`。

## Tone & Style

- 论述章语气与教学章不同：从容、笃定、带阅历感（"I have seen too many times..."），不宜口语化过度；但幽默点必须保住：
  - "as a palette cleanser"（清口小菜）
  - "*magic* (business value) would happen"（_魔法_（业务价值）就会发生）
  - "Any resemblance to actual persons, living or dead, is purely coincidental."（如有雷同，纯属巧合——戏仿免责声明）
  - "fun and unexpected ways"（以各种"有趣"的方式坏掉——反讽引号）
  - "(or integrated!)"（（或者叫集成！））
  - "you don't write tests to chase coverage scores, right?"（总不是为了刷覆盖率吧？）
  - "felt like a superpower"（像有了超能力）
  - "the system will not allow you to add 'Dave'"（Dave 禁令—— deadpan 保留）
  - "I find I need to be more clever for"（自嘲：得更聪明才玩得转）
- 关键论断句加粗（"you may have passing tests but failing software" 等），语气要重、要准。

## Translation Challenges

- 术语密度高且成对出现（stateful/stateless、black-box/white-box、encapsulation），前后必须一致。
- 4 个 quii.gitbook.io 链接与 verify 冲突的处理（见上）。
- mermaid 块逐字节保留；Go 块仅译 `//` 注释，其余逐字节一致（含 `assert.NoErr`、`expect.Equal` 等原文自造辅助）。
- `<u>...</u>` 下划线强调 2 处需保留；`***Given***` 等加粗斜体、`***Then**,*` 的斜体逗号怪格式照旧。
- 原文疑似笔误：`inspectiong`（代码注释内，译时消失）、`labourious`、`allow you to use restrict the need to use`（赘词，按意图译）、"##  Where's"双空格。
