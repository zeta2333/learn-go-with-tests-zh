# 01 — 章节分析：HTML Templates（html-templates）

## 内容概述

本章以"给博客文章渲染 HTML 页面"（`blogrenderer` 包）为例讲 `html/template`：

1. 开篇观点输出：不必事事上前端框架，服务端渲染 HTML + 少量 JS（或 Hotwire）足够多数网站；标准库 `html/template` 比 `fmt.Fprintf` 拼字符串更好维护。
2. 设计前提：沿用 reading-files 章的 `Post`，API 接收 `io.Writer`（可写文件、可直接写 `http.ResponseWriter`）。
3. 第一轮 TDD：只渲染 `<h1>` 标题 → 用 `fmt.Fprintf` 硬拼 → 第二轮加 Description/Tags → 代码变丑（"Yikes"）。
4. 重构进模板：`text/template` vs `html/template`（HTML 输出须用后者，防代码注入）；模板字符串 → 独立 `.gohtml` 文件 + Go 1.16 `embed` 嵌入（`embed.FS`、`//go:embed` 指令、为什么嵌入优于运行时读盘）。
5. 模板"排版"引发测试脆弱 → 引入 Approval Tests（审批测试，`go-approval-tests`）：received/approved 文件、批准工作流；顺带讨论"这还算 TDD 吗"——TDD 是设计工具，不必教条地用于一切。
6. 扩充页面骨架：`{{define "top"/"bottom"}}` + `{{template}}` 复用，`Execute` 改 `ExecuteTemplate`。
7. 基准测试：`b.Loop()` 显示每次重新 Parse 的开销（53812 ns/op → 3131 ns/op）→ 抽 `PostRenderer` 持有解析好的模板。
8. 渲染索引页 TDD：URL 路径需净化（空格→连字符、小写）→ `template.FuncMap` 传函数 → 由此展开"无逻辑模板"的讨论（测试成本、view model、God Objects）→ 两种方案对比，选给 `Post` 加 `SanitisedTitle` 方法。
9. 渲染 markdown 正文：gomarkdown 库；`template.HTML` 防转义；非导出 `postViewModel`；新增长段解释为何 `parser.Parser` 不能复用（内部状态，复用会 panic）。
10. 总结：服务端渲染是横跨几十年的简单技术；DRY；logic-less 的意义；不只用于 HTML（`text/template`）。

39 个代码块（go/markdown/handlebars/无标记输出），1 张外链图片（imgur），大量外链与 3 处章内链接。

## 新术语（英 → 中拟定）

| 英 | 中 | 备注 |
|---|---|---|
| template / templating | 模板 | |
| text/template、html/template | 保留英文（包名） | |
| template action（`{{.}}`、`{{range}}` 等） | 模板动作 | 代码，原样保留 |
| Mustache | Mustache | 专有名 |
| logic-less | 无逻辑（logic-less） | 首现括注，后文可只用中文 |
| approval tests | 审批测试（Approval Tests） | 首现括注；approve → 批准 |
| golden files | 黄金文件（golden files） | |
| snapshot testing | 快照测试 | |
| received / approved 文件 | 保留英文文件名，正文加"received""approved"引号 | |
| view model | 视图模型（view model） | |
| embed | 嵌入（embed） | `//go:embed` 指令名保留 |
| file system | 文件系统 | |
| escape / escaping | 转义 | |
| code injection | 代码注入 | |
| sanitise | 净化 | sanitiseTitle/SanitisedTitle 为标识符，保留 |
| God Object | 上帝对象（God Object） | |
| domain object | 领域对象 | |
| unexported | 非导出（unexported） | |
| static site generator | 静态站点生成器 | |
| ordered list | 有序列表 | |
| markup | 标记 | |
| page furniture | 页面"家具" | 保留作者比喻 |
| combinatorial testing | 组合测试（Combinatorial Testing） | |
| safety-net | 安全网 | |
| benchmark | 基准测试 | 术语表已有 |
| separation of concerns | 关注点分离 | 术语表已有 |
| dependency injection | 依赖注入 | 术语表已有 |
| flavour of the month | 时下最流行 | 幽默译法 |
| Byzantine build system | 拜占庭式的构建系统 | 保留比喻 |

## 翻译难点

1. 39 个代码块逐字节一致：go 块仅第 5 块有一条 `//` 注释要翻（"// if you're continuing from the read files chapter..."）；**`//go:embed "templates/*"` 是编译器指令不是普通注释，绝不能翻**（verify 会忽略注释差异，但翻了代码就坏了，共 3 处）。
2. 模板字符串里的 `{{.Title}}`、`{{range .Tags}}<li>{{.}}</li>{{end}}`、`{{template "top" .}}`、`{{define "top"}}` 全部原样；`handlebars` 语言标记照抄。
3. 输出块怪样保留：L190 失败输出里 want 是 `<li></li>`（与测试代码的 `<li>go</li>` 不符，上游笔误）；该块缺 `--- FAIL` 尾行（截断样例）；L707 输出里的 `\"` 转义；L739 的 `Hello%20World` URL 转义。
4. gomarkdown 段（L967）是长技术段：parser 带内部状态、复用会 panic（旧版本是难懂的 nil pointer dereference）、每次新建反而正确且便宜——因果链不能错。
5. 幽默点：Byzantine build system、"Yikes"、"An excuse to mess around with Benchmarking"（标题自嘲）、"don't go against the grain"、"grease the wheels"、"Wow, like and subscribe..."（在代码块里，不动）、"We don't really want ... one line string"。
6. 斜体两种写法 `_..._` 与 `*...*` 统一为 `*...*`；段落尾部 Gitbook 双空格硬换行清掉。
7. 英式拼写 sanitise/SanitisedTitle 在代码里，一字不动；正文里上游又混写 `SanitizedTitle`（z）与 `[]PostView`，保持原样。
8. 章内链接：`/reading-files.md`（两处）与 `reading-files.md`（两处，无斜杠，上游不一致）目标文件名原样；`./dependency-injection.md` 原样。正文提及 reading-files 章用「读取文件」。
9. `Execute`/`ExecuteTemplate`/`ParseFS`/`FuncMap`/`embed.FS`/`io.Discard`/`b.Loop()` 等标识符保留。

## 原文疑似笔误 / 坏链

1. L190-192 失败输出 want 中 `<li></li>` 应为 `<li>go</li>`（对照 L165-167 测试代码）；输出样例不改。
2. L190-192 输出块缺 `--- FAIL` 结尾行，疑似截断；不改。
3. L806 正文 `[]PostView`、`SanitizedTitle` 与上文定义的 `PostViewModel`、`SanitisedTitle` 拼写不一致（z/s 混用、ViewModel 简写成 View）；行内代码不改。
4. L639 "The old NS per op" 中 NS 大写随意；正文照实译，`53812 ns/op` 行内代码不动。
5. L17 与 L325/L983 章内链接路径前缀不一致（`/reading-files.md` vs `reading-files.md`），各自原样保留。
6. L419 图片为 imgur 外链（http 开头），按规则原样保留 URL；本章无 .gitbook 本地图片需要拷贝。
7. 若干行尾双空格（Gitbook 硬换行残留）、L748/L1004 标题尾随空格：格式噪音，译文清理。
8. L5 "flavour of the month"、L66 "e.t.c." 为作者英式随意写法，译文以自然中文对应。
