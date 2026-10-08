# 02 本章约束 — structs-methods-and-interfaces

在 00-book-prompt.md 全书规范基础上，本章额外遵守：

## 术语定名（本章首现加注一次）

- struct 结构体、method 方法、interface 接口、receiver 接收者、field 字段
- table driven tests 表驱动测试（本章核心词，首次出现写全："表驱动测试"（table driven tests））
- anonymous struct 匿名结构体
- ad hoc polymorphism 特设多态（作为维基链接文字）
- format string 格式化字符串（≠ 格式化动词 format verb）
- 类型安全、解耦、具体类型、容差：通用译法，不加注

## 复现 TDD 循环标题（统一译法，出现多次必须一致）

- Write the test first → 先写测试
- Try to run the test → 试着运行测试
- Write the minimal amount of code for the test to run and check the failing test output
  → 写最少量的代码让测试得以运行，并查看失败的输出
- Write enough code to make it pass → 写足够的代码让测试通过
- Refactor → 重构

## 幽默/语气点

- "that feels overkill here" → "有点杀鸡用牛刀"式口语
- "Wait, what?" → "### 等等，这是怎么回事？"
- "great item in your toolbox" / "extra noise" → 工具箱里的好东西 / 多出来的"噪音"
- "we have not defined Triangle yet" → "我们还没定义 `Triangle` 呢"（保留俏皮）

## 硬性点

- 31 个代码块逐字节一致（仅 go 块内 `//` 注释翻译：只有最终 TestArea 里一条注释）；
  两个无语言标记块（`r Rectangle`、用例列表）原样照抄。
- 块引用 `> type Circle has no field or method Area` 是编译器原话，保留英文。
- 9 个外链全部保留；Gitbook 转义 5 处清理。
- `%.2f`/`%g`/`%#v` 的讲解段落措辞须与 hello-world 章"格式化动词/占位符"呼应。
