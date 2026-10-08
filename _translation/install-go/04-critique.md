# install-go 章 — 审校诊断（只诊断，不改文）

对照 source.md 逐句核查 03-draft.md，问题如下。

## A. 准确性

1. **"A `go.mod` file will be generated"** — 初译"它会生成一个 `go.mod` 文件"，主语错位（"它"像指 Go 或命令，悬空）。原文被动句，语义是"（执行上面命令后）就会生成"。改为"这样就会生成一个 `go.mod` 文件"。
2. **"a single directory"** — 初译"某个固定目录"，"固定"是添的、"单一"这层丢了。改"某一个单一目录"或"同一个目录"。取"某一个单一目录（通常是 `~/go`）"。
3. **"with a simple key combination"** — 初译"用一组简单的按键"，key combination 是"组合键"，不是"按键"。修正。
4. **"acts as the anchor of the project"** — 初译"整个项目的锚点"，"整个"原文没有（the anchor of the project），删去，回到"项目的锚点"。

## B. 中文表达

5. "making the outcome predictable" — 初译"让结果可预测"，欧化。改"结果因此可以预测"。
6. "An improvement over the default linter can be configured using GolangCI-Lint" — 初译"可以配置出一个比默认 linter 更好的选择"，"配置出一个……选择"动宾不搭。改写："可以用 GolangCI-Lint 配置出比默认 linter 更好的代码检查方案"。
7. "Your IDE should describe a function in terms of…" — 初译"把……都描述给你"，生硬。改"为你展示函数的文档、参数和返回值"。
8. "Understanding a function's context" — 初译"使用语境"，代码语境下"使用场景"更自然。
9. "Keeping this reasonably current" — 初译"保持大致跟进"不顺。改"这个版本号保持基本跟手"仍别扭，定为"让这个版本号别太落伍"（保留口语叮嘱感），后半句"能帮你省掉日后一些莫名其妙的调试"保留。
10. "verified against those hashes" — 初译"并逐个对照哈希校验"，"逐个"是添的但合理；改为"并依据这些哈希逐一校验"，既贴原文 those hashes 又保留复数感。

## C. 体例与加注

11. "resolve imports" 两处，import 是 Go 标识符，按全书"代码标识符一律反引号"体例加反引号：解析 `import`。
12. 加注检查：模块（Modules）、MVS 全称、linter（代码静态检查工具）首现括注均已做，无需再加；GOPATH、`go.mod`、`go.sum`、`package.json`、IDE 均为代码/通用词，不加注。
13. 第二个列表项（Extract method/function）原文句末无句号，初译保持了无句号，正确，不要"顺手补齐"。

## D. 其他

14. 原文 "an opinioned formatter" 疑似笔误（应为 opinionated），初译按"颇有主见的格式化工具"处理正确，保留幽默，上报主控。
15. 代码块 4 个、语言标记（sh/无/sh/sh）、`go.mod` 示例含结尾空行——初译已一致，修订时勿动。
16. 链接 4 处 http + 1 处内部相对链接 concurrency.md，初译均已保留。

## 结论

初译整体准确，无漏译；修订点集中在 A1–A4、B5–B10、C11，均为局部替换，不涉及结构调整。
