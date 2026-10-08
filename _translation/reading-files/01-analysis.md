# 01 — 章节分析：reading-files

## 内容概述

本章借"把一个文件夹里的 markdown 博客文章解析成 `[]Post`"这个完整需求，演示迭代式、使用者驱动的 TDD：

- 用 Go 1.16 的 `io/fs` 抽象放松与文件系统的耦合，用 `testing/fstest.MapFS` 充当假文件系统；
- 完整走四轮"先写测试 → 试跑 → 最小实现 → 重构"循环（文件数量 → Title → Description → Tags → Body）；
- 讲解 `bufio.Scanner` 逐行扫描、`strings.TrimPrefix`/`Split`/`Builder`、`io.ReadAll` 等读文件手段；
- 结尾对比生产代码 `os.DirFS` 与测试 `MapFS` 的对称性，强调依赖注入与低耦合。

结构与行文特点：同一组 TDD 步骤标题（Write the test first / Try to run the test / …）反复出现四轮；含 5 段英文引文（Kent Beck、io/fs 包文档、Go 1.16 发布说明、fstest.MapFS 文档、bufio.Scanner 文档，另有 Denise Yu 论 slime）；两处 ```markdown 示例文件块；大量终端输出块（无语言标记的 ``` 块）。

## 本章新术语（英 → 中定名）

| 英文 | 定名 |
| --- | --- |
| happy path | happy path（首现括注"快乐路径"，后文保留英文） |
| steel thread | "主钢缆"（steel thread，首现括注） |
| slime / sliming | 保留英文，首现括注（先用假实现糊出骨架） |
| consumer / consumer-driven | 使用者 / 使用者驱动 |
| coupling / loosely coupled | 耦合 / 松耦合 |
| cohesion | 内聚 |
| magic number | 魔法数字 |
| buffer | 缓冲区 |
| metadata | 元数据 |
| in-memory file system | 内存文件系统 |
| DRY | DRY（首现括注 Don't Repeat Yourself） |
| test double | 测试替身（术语表已有） |

代码名一律保留：`io/fs`、`fstest.MapFS`、`os.DirFS`、`io.Reader`/`io.Writer`、`bufio.Scanner`、`embed`。

## 翻译难点

1. TDD 步骤标题重复四轮，译文措辞必须前后一致：先写测试 / 试着运行测试 / 写最少的代码让测试能跑起来，并*确认失败的测试输出* / 写足够的代码让测试通过 / 重构。
2. 5 段英文引文按全书惯例（context 章先例）译成中文；go1.16 发布说明那段的链接嵌在引文里，链接位置原样保留。
3. "parked error handling" 的"停到路边"比喻、Kent Beck 的 "Optimism is an occupational hazard…" 等幽默点要保住。
4. 46 个代码块必须逐字节一致；`go` 块内 `//` 注释随章翻译（`// later`、`// rest of test code cut for brevity`、`//todo: …`、`// ignore a line`），`markdown` 块与无标记块原样。
5. 有一处句子被代码块拆开（"生产代码……与测试……之间的对称性"），语序不能移动。
6. 本章无图片，不涉及资源拷贝；仅一条章内链接指向 `dependency-injection.md`。
