# http-server 章 — 内容分析

## 内容概述

用 TDD 从零构建一个记录玩家胜场数的 HTTP 服务器（`GET /players/{name}` 查分、`POST /players/{name}` 记胜）。
教学主线：

1. 红-绿-重构纪律（Kent Beck "commit sins" 引语）
2. 先写测试：`httptest.NewRecorder` + `http.NewRequest`，硬编码 "20" 让测试通过（"Faking it"）
3. `ListenAndServe` / `http.Handler` / `ServeHTTP` 接口；`http.HandlerFunc` 适配器把普通函数变成 Handler
4. 第二个测试逼出路由（`strings.TrimPrefix`）；重构出 `GetPlayerScore` → 接口 `PlayerStore` → `PlayerServer` 变结构体（呼应依赖注入章）
5. stub store（`map[string]int`）；main 里临时 `InMemoryPlayerStore`
6. 404 场景暴露测试缺口（"最小代码"反而暴露断言缺口），加 `assertStatus`
7. POST 场景：`StatusAccepted`；重构出 `processWin`/`showScore`；扩展 stub 做 spy（`winCalls`）
8. 集成测试 `TestRecordingWinsAndRetrievingThem`；实现真正的 `InMemoryPlayerStore`；测试金字塔
9. 收尾：并发安全提示（互斥锁，指向 sync 章）；总结 `http.Handler` / 接口与 DI / "commit sins then refactor"

## 本章新术语

| 英文 | 定名 | 说明 |
|---|---|---|
| handler | 处理器 | `http.Handler` 等类型名保留英文；书中已有的 scaling-acceptance-tests 章也译"处理器" |
| HTTP Handler interface | `Handler` 接口 | 类型名不译 |
| type casting | 类型转换 | `HandlerFunc(PlayerServer)` 处 |
| adapter | 适配器 | HandlerFunc 文档引语 |
| endpoint | 端点 | 常识词，不注 |
| routing / route | 路由 | 常识词 |
| hard-coded (value) | 硬编码 | |
| in-memory | 内存版（实现）/内存中的 | |
| integration test | 集成测试 | 全书首现加注 |
| spy / stub / mock | 保留英文 | 依全书术语表 |
| Red, green, refactor | 红、绿、重构 | 与 generics 章译法一致 |
| "Faking it" | "Faking it"（先拿假货糊弄过去） | Kent Beck 说法，保留英文+意译 |
| Test Pyramid | 测试金字塔 | 与 intro-to-acceptance-tests 章一致 |
| mutex | 互斥锁 | 与 sync 章一致 |
| REST-ish service | 类 REST 服务 | |
| scaffolding | 脚手架 | |

## 跨章链接

- "From the DI chapter" → 依赖注入章已译：`[依赖注入一章](./dependency-injection.md)`（后向引用，普通内链）
- "Read more about mutexes in the sync chapter" → sync 章已译（标题保留英文 "Sync"）：`[Sync 一章](./sync.md)`
- 其余为 pkg.go.dev / golang.org 外链，原样保留

## 翻译难点

1. Kent Beck 引语 "Make the test work quickly, committing whatever sins necessary in process." —— 保幽默："尽快让测试通过，过程中需要犯什么'戒'就犯什么戒"。sin 双关（后文 commit sins / commit to source control 的文字游戏要设法保住："犯戒" vs "commit（提交）代码"）。
2. "Chicken and egg" 小节标题 —— 译"先有鸡还是先有蛋"。
3. "roll my eyes" 段落 —— 自嘲幽默要保住："翻白眼"。
4. "This is allowed!" —— 口语强调。
5. 主测试函数名 `TestGETPlayers` 等代码一律不动；`//server.go` 注释随章翻译成 `// server.go`？—— 不行！verify 只剔除 `//` 注释内容，但为保逐字节一致，`//server.go` 原样保留（它是文件路径提示，非英文句子，保留即可，不译）。
   实际上 `//server.go` 属于 Go 注释，译与不译都会被 verify 忽略；约定俗成保留原样（文件名无需翻译）。
6. 错误信息、测试输出全部逐字节保留（含 `Pepper's_score` 下划线、引号样式）。
7. 无图片。无 Gitbook 转义符。无自动链接泄漏。
