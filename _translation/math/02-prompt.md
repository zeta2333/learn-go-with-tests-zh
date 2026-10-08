# 02 — Math 章特有约束

在 `00-book-prompt.md` 全书规范与用户级术语表基础上，本章追加：

## 术语定名（首现加注一次）

- acceptance test → **验收测试**（术语表已有，本章首现处括注英文）
- unit circle → **单位圆**（unit circle）
- radian → **弧度**（radian）；2π 一整圈的表述保持
- unit vector → **单位向量**（unit vector）
- trigonometry → **三角函数**（行文自然优先；"the X coordinate will be cos(a)" 等公式表述保持 cos/sin 原样）
- scale / flip / translate → **缩放 / 翻转 / 平移**（代码注释 `// scale` 等同步译为 `// 缩放` 等）
- magic number → **魔法数字**；remainder operator → **取余运算符**（remainder operator）
- analogue clock → **模拟时钟**；hand → 指针（hour/minute/second hand → 时针/分针/秒针）；clockface → 表盘（包名 `clockface` 保留）
- unmarshal → **反序列化**（`xml.Unmarshal` 保留）；bezel 保留英文（仅代码/XML 注释）

## 标题译法（高频重复，跨章统一）

- H1 定为 `数学`（任务指定）；`## Math` → `## 数学`；`## \`math\`` → `## \`math\` 包`
- `The Problem` → 问题；`An Acceptance Test` → 验收测试；`Thinking time` → 思考时间
- `Write the test first` → 先写测试（9 次，保留重复）
- `Try to run the test` → 试着运行测试（13 次）
- `Write the minimal amount of code for the test to run and check the failing test output` → 写最少的代码让测试能运行，并检查失败的测试输出
- `Write enough code to make it pass` → 写足够的代码让测试通过
- `Refactor` → 重构；`Repeat for new requirements` → 为新需求重复以上步骤
- `Floats are horrible` → 浮点数真讨厌；`A note on dividing by zero` → 关于除以零
- `Parsing XML` → 解析 XML；`Draw the clock` → 画时钟；`Draw the hour hand` → 画时针
- `Hour Hand Point` → 时针端点；`On TDD Zealotry` → 关于 TDD 狂热
- `A recap on packages` → 回顾一下包；`Wrapping up` → 总结
- `A Program... and a Library` → 一个程序……以及一个库；`The Most Valuable Test` → 最有价值的测试

## 代码块纪律（118 个，最多的一章）

- `go` 块逐字节一致，仅译 `//` 注释：
  - `// A Point represents a two-dimensional Cartesian coordinate` → `// Point 表示一个二维笛卡尔坐标`
  - `// SecondHand is the unit vector of the second hand of an analogue clock at time `t` / // represented as a Point.` → `// SecondHand 是模拟时钟在时间 `t` 时秒针的单位向量，` / `// 以一个 Point 表示。`
  - `// SVGWriter writes an SVG representation of an analogue clock, showing the time t, to the writer w` → `// SVGWriter 把显示时间 t 的模拟时钟的 SVG 表示写入 writer w`
  - `// scale / // flip / // translate / //translate` → `// 缩放 / // 翻转 / // 平移 / //平移`
  - `// REPLACE THIS!` → `// 换成你自己的！`；`// fails to compile` → `// 无法通过编译`
  - `// ...`、`//...` 无文字，原样保留
- `xml` 块（示例时钟）、无语言标记块（编译/测试输出、`numberOfSeconds * π / 30` 等式、目录树、`sh` 块）逐字节一致，注释一并保留（XML 的 `<!-- bezel -->` 不译）。
- 字符串字面量、`%f`/`%.3f`、坐标数值、`e-16` 浮点输出、时间常量（1337 年、312 年）一律不动。

## 图片（9 张，已拷至 docs/assets/）

- `assets/example_clock.svg`、`assets/TDD-outside-in.jpg`、`assets/unit_circle.png`、`assets/unit_circle_coords.png`、`assets/unit_circle_params-1.png`、`assets/unit_circle_12_oclock.png`、`assets/clock.svg`、`assets/clock-1.svg`、`assets/clock-2.svg`
- 原 `<.gitbook/assets/unit_circle_params (1).png>` 等带空格写法改写后不再需要 `<>` 包裹；alt 意译。
- 外链（youtube、github、wikipedia 等）URL 原样保留。

## 幽默点对策

- `How hard can that be?` → 能有多难？
- `Behold, a passing test.` → 且看，测试通过了。
- `Wait, what?` / `Wait, what (again)?` → 等等，什么情况？/ 等等，（又来）？
- `Hooray maths!` → 数学万岁！
- `Oh boy am I not trying to win any prizes for beautiful code with _this_ mess` → 保留自嘲
- `This stinks. Well, it doesn't quite _stink_ stink` → 味儿不对 + 斜体强调
- `and not land on the moon`（画 SVG vs 登月）→ 保住夸张
- `Floating point arithmetic strikes again.` → 浮点运算又双叒来了
- `If - _when_ - we come back to this code` → 如果——_应该说当_——
- Jennifer Aniston `Here comes the science bit` → 科学环节到了（链接原样）
- `really, really WEIRD clocks` → 非常、非常_怪_的钟（大写强调转斜体加"非常"叠用）

## 其他

- Kent Beck 名言与 Henry Spencer 书引按先例译中文，署名与书名（英文斜体）保留。
- 文末孤儿脚注 "1. In short..." 原位保留翻译（上游错位，不挪动）。
- 上游笔误（`zak`、`the some coverage`、`clockface_test` 少后缀等）不修，正文如实照译，报告上报。
