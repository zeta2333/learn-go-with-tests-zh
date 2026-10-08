# 02 — 本章特有约束

遵循 00-book-prompt.md 全书规范 + 用户术语表，另有本章细则：

## 术语定名（本章首现，全书以此回填）

- blocking → **阻塞**（首现写作"阻塞（blocking）"）
- data race → **数据竞争**（首现写作"数据竞争（data race）"）；输出 `WARNING: DATA RACE` 不译
- race condition → **竞态条件**（总结部分出现，区别于 data race）
- race detector → **竞态检测器**（首现斜体原文 *race detector* 保留对应强调）
- send statement → **发送语句**；receive expression → **接收表达式**（均加斜体，对应原文强调）
- stacktrace → 堆栈跟踪
- premature optimization → 过早优化
- toolchain → 工具链；language spec → 语言规范；go directive → `go` 指令
- process → 执行流程 / 流程（**禁用"进程"**，避免 OS 歧义；与全书"sync processes = 同步流程"同源）

## 保留英文

- goroutine、channel（首现加注（通道））、make、map、struct、slice、stub（`slowStubWebsiteChecker` 等标识符当然不动）、benchmark 相关命令输出
- 标题：`### Channels` 保留英文（与 `## Select`、`## Context` 等专有名词式标题同类）
- 章标题 H1：**并发**

## 幽默点对策

- 泡茶段：保留短句连发的动作节奏；"blankly staring at the kettle" 要有画面感。
- "Or pretend that you did. Up to you." → "或者就当看到的是上面那个结果，随你便。"
- "long and scary" → "又长又吓人"；"... many more scary lines of text ..." 在代码块内，不译。
- aside 标题的省略号呼应对："……" 前后保留。

## 结构对应

- blockquote（`**A note on ...**`）保留引用块与加粗形式。
- 引用块内第二个黑体段落仍是同一 blockquote（原文 `>` 空行续块），注意别断开。
- 文末 4 条引用式链接定义（`[DI]`/`[wrf]`/`[godoc_race_detector]`/`[popt]`）原样保留；`[DI]` 指向 `dependency-injection.md` 不改。
- Wrapping up 的 4 条列表与原文一一对应，斜体保留。
