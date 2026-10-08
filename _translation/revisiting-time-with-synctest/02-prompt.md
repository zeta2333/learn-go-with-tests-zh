# 02 — 本章翻译约束

## 术语定名（本章新增，回填候选）

- bubble → **气泡**（首现"气泡（bubble）"，此后用"气泡"）
- fake clock / fake time → **虚拟时钟** / **虚拟时间**（首现括注 fake clock/fake time）
- durably blocked → **持久阻塞**（首现括注 durably blocked；bullets 与后文统一）
- race detector → **竞态检测器**
- deadlock → **死锁**
- timer heap → **定时器堆**
- spike → **用完即弃的小程序（spike）**
- `testing/synctest`、`synctest.Test`、`synctest.Wait()`、`-race`、`StdOutAlerter`、
  `NewAlerter`、`BlindAlerter` 等代码标识符一律反引号、不译。

## 与 Time 章的呼应（必须保住）

- 标题 H1：# 用 `testing/synctest` 重访时间（任务指定）
- "the chapter on time" → [Time 一章](time.md)
- "Just enough information on `testing/synctest`" → 关于 `testing/synctest`，知道这些就够了
- "blind" → 盲注；alert → 提醒；schedule → 调度/安排（沿用 docs/time.md 用词）

## 跨章链接

三个目标章节均已译出，一律站内相对链接：
- [Time 一章](time.md)
- [如果你的测试让你痛苦，请倾听这个信号，思考你的代码设计](http-handlers-revisited.md)（×2）
- [Select 一章](select.md)

## 代码块纪律

- 仅第 4 块（StdOutAlerter 生产代码）译 4 条 `//` 注释；其余 17 块逐字节一致。
- DATA RACE 报告、`ok github.com/quii/learn-go-with-tests/synctest/vN` 输出一字不动。
- 无 Example 函数，无图片。

## 幽默与语气对策

- `Ouch.` → 单独短句"哎哟。"，保留惊讶感。
- `Nobody is going to wait for that...` 译出抱怨口吻。
- `Clean, every time. Very nice.` 保持三个短句节奏。
- `that's on me, not the tool` → "那是我的问题，不是工具的"。
- AI 写作说明节整体保持作者第一人称的自嘲坦率，忌公文腔。

## 其他

- 弯引号""；中英之间空格；不出现直角引号「」。
- 强调斜体 *...* 位置与原文一一对应。
- "share memory by communicating" 谚语用通行译法：
  "不要靠共享内存来通信，而要靠通信来共享内存"。
