# 02 — 本章特有约束

## 术语定名（本章新增，待回填术语表）

- happy path → 保留英文，首现写 "happy path"（快乐路径）
- steel thread → 首现写 "主钢缆"（steel thread）
- slime → 保留英文，首现括注（先用假实现糊出骨架）
- consumer-driven → 使用者驱动
- loosely coupled → 松耦合；cohesion → 内聚
- magic number → 魔法数字；buffer → 缓冲区；metadata → 元数据
- in-memory file system → 内存文件系统
- DRY → 保留英文，首现括注（Don't Repeat Yourself）

## 处理决定

- 四轮 TDD 循环标题统一措辞：先写测试 / 试着运行测试 / 写最少的代码让测试能跑起来，并\*确认失败的测试输出\*（首轮按原文带斜体，后两轮不带）/ 写足够的代码让测试通过 / 重构。
- 引文全部译成中文（含 MapFS、Scanner 官方文档引文）；引文内的链接 URL 原样。
- `### Writing?` 意译为 `### 写文件呢？`（指写文件操作）。
- 章内链接 `dependency-injection.md` 目标文件名保持上游同名，按同站惯例加 `./` 前缀，链接文本加粗的"依赖注入"。
- 代码块纪律：终端输出块、```markdown 块逐字节一致；`go` 块仅翻译 `//` 注释；`//todo:` 注释译为"// todo：这里需要再想想，一个文件失败时应该整体失败，还是直接忽略？"。
- 上游疑点一律不改、原样保留（见 04-critique 汇总）：测试文件名 `blogpost_test.go`/`blogposts_test.go` 混用；失败输出里的 `parses_the_post` 子测试从未演示添加；结尾 `main.go` 的模块路径 `github.com/quii/fstest-spike` 与前文不同。
