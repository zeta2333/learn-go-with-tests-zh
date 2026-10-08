# 02 — 翻译提示词：Refactoring checklist（本章特有约束）

## 任务

将《Learn Go with Tests》`refactoring-checklist.md` 由英文精翻为简体中文（zh-CN），出版级质量。样章 `_translation/hello-world/translation.md` 为文风基准。

## 本章特别说明（来自主控）

- **H1 章标题定为：重构清单**。
- 这是一份**操作性清单**：清单条目保持体例、动词开头；条目之间的叙述段保持 conversational 基调。
- **人名规范**：Martin Fowler 保留英文（本章无 Kent Beck）。著作《Refactoring》(2nd ed) 译作"《重构》（Refactoring，第 2 版）"。
- 词典/百科引文（Collins 习语定义、Wikipedia magic number 定义）整句意译，外链原样保留在链接内；英式/美式英文原词保留英文。
- **图片**：仅 1 张外链图 `https://i.imgur.com/4sgUG7L.png`，URL 原样保留，alt 文本翻译。不涉及 `.gitbook/assets` 拷贝。

## 术语表（本章涉及的必须一致）

重构（refactoring）、行为变更（behaviour change）、设计变更、方法签名（method signature）、私有/公开方法（private/public method）、提取变量（extract variable）、内联变量（inline variable）、提取方法（extract method）、DRY（保留英文，首现括注"不要重复自己"）、魔法值（magic value）、魔法数字（magic number）、耦合（coupling）、内聚（cohesion）、构造函数（constructor function）、字段（field）、版本控制（source control）、commit / revert（保留英文）、反馈回路（feedback loop）、安全网（safety net）、心理清单（mental checklist）、截止时间（deadline）、单元测试（unit test）。

保留英文：IDE、IntelliJ/GoLand、快捷键（`command+option+n/v/c/m`、`shift+F6`、`command+b`、`command+left-arrow`）、全部代码标识符、`io.Reader`、`POST`。

## 硬性规则（本章落地）

1. 代码块 13 个（全部 `go`）与原文逐字节一致，仅 `//` 占位注释随章翻译：`// some fascinating emailing code`、`//etc`、`// etc..`、`//todo: handle codes, err etc`、`// etc`。第 2 个代码块（`WishHappyBirthday(person Person)`）原文即无闭括号，原样保留。
2. 无章首"本章所有代码"链接（原文没有，不得自造）。
3. 4 个外链原样保留：Collins、Wikipedia DRY、Wikipedia magic number（URL 含配对括号原样写）、imgur 图片。
4. 两处 `<u>…</u>` 标签原样保留；`*…*`/`_…_` 斜体、`**…**` 加粗与原文一一对应。
5. 原文无 Gitbook 转义符，无需清理；引号统一弯引号，禁用「」。
6. 段落顺序、清单条目顺序、快捷键与重构手法的对应关系严格照原文，不合并、不拆移。

## 标题定译

- Refactoring step, starting checklist → **重构清单**（H1，主控指定）
- Refactoring vs other activities → 重构与其他活动
- Other activities, such as "big" design → 其他活动，比如"大"设计
- Big design → 大设计
- Seeing the wood for the trees → 见树又见林
- Starting mental-checklist → 动手前的心理清单
- Inline variables → 内联变量
- DRY up values with extract variables → 用提取变量 DRY 掉重复的值
- DRY up stuff in general → 更宽泛地 DRY
- Extract "Magic" values. → 提取"魔法"值
- Make public methods/functions easy to scan → 让公开方法/函数一目了然
- But now I don't know how it works! → 可现在我不知道它是怎么工作的了！
- Move value creation to construction time. → 把值的创建挪到构造时
- Comparing and contrasting `CreateWidget` → 对比前后两个 `CreateWidget`
- Try to remove comments. → 试着消灭注释
- Exceptions to the rule → 规则之外
- Use your tools to help you practice refactoring. → 用工具帮自己练习重构
- Don't ask permission to refactor → 重构不需要请示
- Wrap up → 总结

## 幽默点对策

- `// some fascinating emailing code` → "引人入胜"的自嘲要保住："// 一些非常引人入胜的发邮件代码"。
- "**You're doing something else** if you are "refactoring" some code and having to change tests at the same time." → 点名式泼冷水，加粗保留："那你**做的其实是别的事情**"。
- "My blunt reply to this is … Have you learned how to navigate codebases using your tooling effectively?" → 保留直球口吻："我直截了当的回答是：……你学会用工具高效地在代码库里导航了吗？"
- "There's little excuse not to do it." / "a decision for others to make" → 结尾的劝诫语气要译出不留情面的善意。
