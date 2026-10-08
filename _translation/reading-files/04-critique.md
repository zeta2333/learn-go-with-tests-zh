# 04 — 审校诊断（对照 source.md，只诊断不改动）

预检：`verify.py` 对 03-draft 通过（47 个代码块一致、链接完整）。以下为逐段对照发现的问题。

## A. 准确性

1. 【误译】"our new package does not have a `NewPostsFromFS` function, that returns some kind of collection"——初译"也没有返回某种集合"，读起来像包里缺一个"集合"；实义是缺一个"能返回某种集合的函数"。应改为"还没有一个能返回某种集合的 `NewPostsFromFS` 函数"。
2. 【用词】"create a post for each file we encounter"——原文小写 post（尚未成型的领域概念），初译作"一篇 Post"并大写。统一为"一个 post"。
3. 【拗口/因果】"The TDD practitioner in you might be annoyed we didn't see a failing test before writing the code to propagate the error…"——初译"写把 `fs.ReadDir` 的错误传播出去的代码之前"动宾堆叠拗口。建议重排："在写下把 `fs.ReadDir` 的错误传播出去的代码之前，我们并没有先看到失败的测试，你内心的 TDD 实践者也许会有点恼火"。
4. 【混淆风险】"We already have our structure."——structure 呼应上文 Denise Yu 引文里的 "skeleton"（骨架），初译"结构"易与 Go 的 struct 混淆。改"骨架我们已经有了"。
5. 【生硬】"This is _not_ iterative"——初译"这样*一点也*不迭代"不合中文搭配。改"这样做*根本*谈不上迭代"。
6. 【直译腔】"and return us some posts"——初译"它还我们一批文章"拗口。改"它给我们返回一批文章"。
7. 【公文腔】"We've been asked to create the package…"——初译"我们受命要开发的"偏公文，不符 conversational 风格。改"我们的任务是开发……"。
8. 【欧化】"Up until making it pass should now feel comfortable and familiar."——初译"到把它做通过为止的这套流程"费解。改"把测试推到通过为止的这整套流程，你现在应该已经轻车熟路了"。
9. 【加注建议】"exported members" 是 Go 特有概念，本章首现建议轻量括注（exported）。

## B. 体例

10. 【引号，必改】正文残留 12 处 ASCII 直引号，违反规则 4（统一弯引号）："自底向上"、"happy path"、"真实"、"slime"、"骨架"、"规矩"、"有能用的软件"、"打开文件的代码"/"解析文件内容的代码"、"扫描一行、然后读出文本"、"取剩余数据"、"主钢缆"、"来真的"。逐一换为弯引号；代码块内直引号不动。
11. 【一致性】章标题"## 迭代式的测试驱动开发"与 01-analysis 暂拟名"迭代式、测试驱动的开发"不一致，以定稿"迭代式的测试驱动开发"为准（更顺口）。

## C. 表达润色（可选）

12. Denise Yu 引文"能让你一次专注一件事"→"能让你一次只专注一件事"，更贴 "one at a time"。
13. "所以先无视这个错误"→"所以先对这个错误视而不见"更口语；亦可保留。取后者微调为"先无视它"简化。
14. 终段"或许还要更早"稍别扭，可改"甚至可能更早"。

## D. 上游原文疑点（原样保留，不修）

- 测试文件名混用：命令建的是 `blogposts_test.go`，编译错误却报 `./blogpost_test.go`（单数），后又出现 `blogposts_test.go:48`。
- 失败输出里出现 `TestNewBlogPosts/parses_the_post` 子测试，正文从未演示添加该子测试。
- 结尾 `main.go` 的导入路径 `github.com/quii/fstest-spike` 与前文 `github.com/quii/learn-go-with-tests/reading-files` 不一致。
- `golang.org/pkg/...` 旧域名链接（现已重定向到 pkg.go.dev），按规则原样保留。
- 无图片；章内链接仅 `dependency-injection.md` 一处。
