# 02 — os-exec 章特有约束

## 新术语定名（本章生效）

- seam → 接缝（seam），首现加括注，正文只出现一次
- integration test → 集成测试（与 http-server 章一致，首现可用 *集成测试*（integration test））
- testdata → 保留英文 `testdata`（提问者语境里的"我造的测试数据"）
- dependency injection → 依赖注入（既有，不再注）
- separation of concerns → 关注点分离（既有，不再注）

## 体例与语气

- blockquote 中的 reddit 提问按第一人称直译，口语化，保留 `ie`（即）处的举例语气。
- "A few things" → 「有这么几点」一类简短引入。
- 英式客套 "I have taken the liberty of..." 保留幽默感。
- 加粗整句 "**The problem with GetData...**" 保持加粗、保持单段。
- 标题层级、列表嵌套（无序列表下的缩进子项）与原文一一对应。

## 代码块

- 5 个代码块逐字节一致；唯一允许翻译的是 go 块里的 `//` 注释（共 1 处）。
- XML 块、测试断言字符串 `"HAPPY NEW YEAR!"`、`"CATS ARE THE BEST ANIMAL"`、
  `strings.NewReader` 里的内嵌 XML（含换行与缩进）一律原样。

## 链接

- `./dependency-injection.md`：目标已译，保持相对链接与文件名不变，锚点无。
- `https://golang.org/pkg/os/exec/#example_Cmd_StdoutPipe`：外链原样保留。
- 其余（GitHub 代码目录、reddit 两链）原样保留。
- 无图片。

## 禁止

- 不用直角引号「」；弯引号 ""。
- 不引入翻译腔连词堆叠；短句优先。
- 不动 docs/、mkdocs.yml。
