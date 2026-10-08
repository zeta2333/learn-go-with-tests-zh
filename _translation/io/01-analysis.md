# 01 — io 章分析

## 内容概述

"构建一个应用"篇第四章（前接 json 章，后者尚未译出）。延续 poker 扑克计分应用：产品负责人要求 ① 服务器重启后得分不丢；② `/league` 按胜场数排序返回。本章用 JSON 文件实现 `FileSystemPlayerStore`，途中系统学习 `io.Reader` / `io.ReadSeeker` / `io.ReadWriteSeeker` 接口族、临时文件测试辅助、`Tape` 封装"从头写"语义、构造函数错误处理、`file.Stat()` 处理空文件，最后用 `sort.Slice` 完成排序。收尾讨论"测试私有类型/不用接口"是否违反规则，以及吉他类比（先懂规则才能破规则）。

- 源文件 5582 词（英文），64 个代码块（```` ``` ```` 计 128 个围栏）。
- 代码块类型：约 40 个 ```go、其余为编译错误/测试失败输出（须逐字节一致）。
- 无图片。
- 内部链接仅 1 处：`[In the previous chapter](json.md)` —— json 章未译出，按规范改为上游 GitHub URL + （英文原版）。
- 外链：章首代码目录 quii/learn-go-with-tests/tree/main/io、golang.org/pkg/io/#ReadSeeker、#Seeker、pkg.go.dev/os#CreateTemp、superuser.com chmod 666、golang.org/pkg/sort/#Slice。全部原样保留。

## 本章新术语（英 → 定名）

| 英文 | 定名 | 备注 |
|---|---|---|
| in-memory | 内存版 / 存在内存里 | 描述性用法，不强注 |
| integration test | 集成测试 | 全书 docs 尚未出现，首现加注 |
| ReadSeeker / Seeker / ReadWriteSeeker | 保留英文 | 接口名，行文解释构成 |
| truncate | 截断 | `Truncate` 方法名保留 |
| temporary file | 临时文件 | `CreateTemp` 保留英文 |
| DRY | DRY | 首现括注"别重复自己" |
| technical debt | 技术债 | |
| polymorphism | 多态 | 首现加注 |
| red state | 红灯状态 | TDD 语境（失败即"红"） |
| product owner | 产品负责人 | 与 app-intro 译法一致 |
| happy path | 正常路径 | 术语表既有 |
| idiomatic | 惯用 / 地道 | |
| League（类型） | 保留英文 `League` | 代码类型名 |

## 翻译难点

1. TDD 循环小节标题沿用全书定式：先写测试 / 试着运行测试 / 写最少的代码让测试能运行，并检查失败的测试输出 / 写足够的代码让测试通过 / 重构。
2. 幽默点：产品负责人 "somewhat perturbed"（颇为不悦）、"hooray!"、"I would have to explain dependency management!"（不想讲依赖管理才选文件）、网络段子 `if err != nil`、吉他类比、"Easy!"。全部保住，不译平。
3. "She is also not pleased that we didn't interpret the /league endpoint should return..." 原文语法松散，按语义顺成中文。
4. 第 954 行长段（新增段落，讲 `Encoder.Encode` 一次性 Write、`tape` 每次 Encode 只 Seek 一次的安全性论证）逻辑链必须严格对应，不可简化。
5. Go 代码块注释随章翻译的仅 4 处文件头doc注释 + `// read again`（×2）+ `//etc...`；`//server.go`、`//file_system_store.go` 等文件名提示注释保留原样。
6. "Didn't we just break some rules there?" 小节标题口语化处理。
7. 上一章链接：json.md 未译出 → GitHub URL + （英文原版），与 app-intro.md 既有格式一致。
