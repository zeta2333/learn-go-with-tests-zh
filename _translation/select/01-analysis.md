# 01 — 章节分析：Select

## 内容概述

本章是并发教学的延续，用一个 `WebsiteRacer` 函数贯穿两轮完整 TDD 循环：

1. 第一轮：比较两个 URL 的响应速度，返回较快者
   - 朴素实现：串行 `http.Get` + `time.Now`/`time.Since` 计时
   - 真实网站不可靠 → `net/http/httptest` 创建 mock 服务器（匿名函数、`http.HandlerFunc` 类型、"真服务器也这么写"）
   - 重构：抽 `measureResponseTime`、`makeDelayedServer`；引入 `defer` 延迟清理
   - 换思路：`select` + goroutine 并发竞速；`ping` 返回 `chan struct{}`、`close(channel)` 当完成信号、为什么用 `struct{}`；"一定要用 `make` 创建 channel"（零值 `nil` 的坑，附 Playground 链接）
2. 第二轮：10 秒超时返回 error
   - 测试改双返回值；`time.After` 兜底
   - 慢测试问题 → 超时可配置：`Racer`（默认 10 秒）委托 `ConfigurableRacer`
   - "听测试的话"：happy path 不用传超时，sad path 用可配置版本

结尾总结 `select` 与 `httptest` 两个工具。无图片，无引用式链接，外链 5 条。

## 新术语（英 → 中拟定）

| 英 | 中 | 备注 |
|---|---|---|
| select | `select`（保留英文） | Go 关键字；章标题 H1 也保留英文 `Select` |
| race / "races" them | 竞速 | 本章核心比喻；原文未提 data race，不得自行引入"数据竞争"混淆 |
| synchronise processes | 同步流程 | processes 意译"流程"，避免被读成 OS"进程"；待终审全书统一 |
| goroutine | goroutine | 术语表已有；本章首现轻量括注"Go 的轻量级并发单元" |
| channel | channel | 术语表已有；本章是 channel 首个正文出现章，首现加注（通道） |
| chan struct{} / close / make | 保留代码 | |
| blocking | 阻塞（blocking） | 首现加注 |
| zero value | 零值 | 术语表已有，hello-world 已注，本章不注 |
| anonymous function | 匿名函数（anonymous function） | 首现加注 |
| file descriptor | 文件描述符（file descriptor） | leak → 泄漏 |
| mock / fake | mock / fake（保留英文） | 术语表已有 |
| flaky | 不稳定（flaky） | 测试语境：外部服务时好时坏 |
| edge cases | 边界情况 | |
| defer | `defer`（保留英文） | Go 关键字 |
| DRY | DRY（消除重复） | 首现轻注一次 |
| happy case / "happy" test | 正常情况（happy case）/ "happy" 测试 | 首现加注一次，后文照原文保留英文 happy |
| sad path | 异常路径（sad path） | 首现加注 |
| time.After / time.Now / time.Since / time.Duration | 保留代码 | |
| under the hood | 在底层 | |
| naive | 朴素 | |
| The Go Playground | The Go Playground | 专有名保留英文 |

## 翻译难点

1. 14 个代码块全部无 Go 注释，须与原文逐字节一致（含 `t.Run` 子测试名字符串、全部错误输出）；行内错误输出 3 处照抄。
2. `time.Sleep` 表述要准确：慢服务器"收到请求后先睡一小段时间再响应"；`time.After` 是"设定时间到了往 channel 发一个信号"，不是"定时中断/杀掉"。本章无缓冲 channel 内容，不得自行发挥。
3. `chan struct{}` 段原文措辞不严谨（"a `chan struct{}` is the smallest data type"，严格说是 `struct{}` 零内存），翻译贴近原意、不放大错误。
4. 幽默点：not too hung-up on getting things perfect first time；The syntax may look a bit busy but just take your time；Play with these sleeps to deliberately break the test；let's _listen to them_（听测试怎么说）；For such a simple bit of logic, this doesn't feel great。
5. `URL` 原文有的带反引号（`URL`s）有的不带，译文一一对应。
6. 第二轮循环的 "Write the test first" 等标题与第一轮完全相同，译名与前章统一且两轮一致。
7. Gitbook 转义：本章未见转义残留；但有 3 处格式小毛病（见下）。

## 原文疑似笔误 / 坏链

1. L309 "we're using\t`_` for now"——正文 "using" 与 `_` 之间误入一个制表符，译文按空格处理。
2. L77 链接 `https://golang.org/pkg/net/http/#Client.Get` 锚点指向 `Client.Get` 方法，正文讲的却是包级函数 `http.Get`（锚点疑应为 `#Get`）；按规则 URL 原样保留。
3. L243-244 "so we\nget no allocation"——句中硬换行（Gitbook 段内换行），译文并成一段。
4. L254-255 Playground 链接段与 `#### `select`` 标题之间无空行，译文补空行。
5. L318 具名返回值写成 `error error`（变量名与类型同名）是原书刻意写法，非笔误，代码不动。
6. Playground 链接 `https://play.golang.org/p/IIbeAox5jKA` 无法在本环境验证存活，按规则原样保留。
