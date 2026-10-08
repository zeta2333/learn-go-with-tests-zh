# 02 — Sync 章特有约束

在 `00-book-prompt.md` 全书规范与用户级术语表基础上，本章追加：

## 术语定名（本章首现加注）

- wait group → **等待组**；`sync.WaitGroup` 一律保留英文原样，首次出现处括注（等待组）。
- race condition → **竞态条件**（race condition）。
- Mutex → 类型名 `Mutex`/`sync.Mutex` 保留英文；作普通名词时译**互斥锁**，godoc 引文里 "mutual exclusion lock" 译互斥锁并括注。
- embed/embedding → **嵌入**；不要译"内嵌/嵌入式"。
- constructor → **构造函数**。
- invariant → **不变式**（invariant）。
- lock-free → **无锁**；atomic → **原子**/原子性。

## 标题译法（对齐 select 章）

- `Write the test first` → 先写测试（出现两次，保留重复）
- `Try to run the test` → 试着运行测试（两次）
- `Write the minimal amount of code for the test to run and check the failing test output` → 写最少的代码让测试能运行，并检查失败的测试输出
- `Write enough code to make it pass` → 写足够的代码让测试通过
- `Refactor` → 重构；`Wrapping up` → 总结
- `An alternative: sync/atomic` → 另一种选择：sync/atomic
- `Copying mutexes` → 拷贝互斥锁
- `When to use locks over channels and goroutines?` → 什么时候用锁，而不是 channel 和 goroutine？
- `Don't use embedding because it's convenient` → 别因为方便就用嵌入
- H1 定为 `Sync`（任务指定）

## 代码块纪律

- `go` 块仅译 `//` 注释：`// 1. read / 2. increment / 3. write` → `// 1. 读取 / 2. 自增 / 3. 写回`，其余逐字节一致。
- 无语言标记块（编译错误、`=== RUN` 输出、goroutine 交错示意、`go vet` 输出）逐字节照抄，包括 `got 939, want 1000`。
- Refactor 节两个相邻 go 块不合并。

## 幽默/语气对策

- "Go experts like us" 保留自嘲：对我们这样的 Go 专家来说……小菜一碟。
- "This _looks_ nice but while programming is a hugely subjective discipline, this is **bad and wrong**" 保留英式毒舌的反差句式，加粗不丢。
- "your poor users" → 你可怜的用户；"nefarious code" → 居心不良的代码；"This seems like a really bad idea" 图注 → 这看起来真是个坏主意。

## 图片

- 全章唯一图片为外链 `https://i.imgur.com/SWYNpwm.png`（不在 `.gitbook/assets/`，上游即外链）：保留原 URL，仅译 alt 文本；无需拷贝资源。
