# 01 — roman-numerals 章分析

## 内容概述

全书极少数"标题与教学主线"错位的章节：上游 H1 是 Roman Numerals，但 SUMMARY/SUMMARY 中文站按 SUMMARY 定为"基于属性的测试入门"（本章真正的新知识点）。

结构分四段：
1. **罗马数字转换器 `ConvertToRoman`**：标准 TDD 循环（先写测试 → 试运行 → 最少代码 → 通过 → 重构）反复迭代 1→2→3→4→5→9→10→39→50→1984。中途引入 `strings.Builder`、DRY 规则讲解（连续重复 ≤3、减数 I/X/C 及"家族"限制）、把 `switch` 重构为数据（`RomanNumeral` 结构体 + `allRomanNumerals` 切片）。
2. **反向解析 `ConvertToArabic`**：复用测试用例（`cases[:1]`、`cases[:2]`…逐步解锁），`strings.HasPrefix`/`TrimPrefix` 实现；顺带由蠢代码演化出遍历累加。
3. **基于属性的测试**（本章点题）：三条领域规则 → `testing/quick` 的 `quick.Check`；随机数据暴露 `int` 边界缺陷 → 换 `uint16` → `quick.Config.Values` 自定义生成器（MaxCount 1000，值域 [0, 3999]）。含 Linux 冻结警告（`<details>` 折叠块）。
4. **总结 + 后记**：迭代开发心得；Dave 关于 digit/numeral/number 之辨的长引文（较真但有教学价值）。

## 本章新术语（英 → 中定名）

| 英文 | 定名 | 说明 |
|---|---|---|
| property based tests | 基于属性的测试 | 术语表已有，本章核心，多次出现 |
| example based tests | 基于示例的测试 | 与上者对照，首现括注英文 |
| thin vertical slices | 瘦垂直切片 | 首现括注英文；"有用功能"的窄切片 |
| subtractor | 减数 | 首现括注；IV 中被减掉的 I |
| kata | Kata（保留英文） | 首现轻点一次"编程道场练习题" |
| digit / numeral / number | 数字 / 记数形式 / 数 | 后记 Dave 辨析专用，需前后自洽 |
| unsigned integers | 无符号整数 | uint16 一节 |
| swap thrashing | swap 抖动 | Linux 警告块 |
| round-trip | 往返转换 | uint16 缺口一段 |
| no-op | 空转 | 同上 |
| short-circuiting loops | 让循环提前退出（短路） | 重构一节 |
| OO (object-oriented) | 面向对象（OO） | 首现括注 |
| edge cases | 边界用例 | |

保留英文：`quick.Check`、`quick.Config`、`testing/quick`、`reflect.Value`、`rand.Rand`、`strings.Builder`、`uint16`、`DRY`、`:shrug:`（GitHub 表情 shortcode）。

## 翻译难点与对策

1. **测试用例描述是字符串字面量**：`"1 gets converted to I"`、`t.Run("...", ...)` 的描述决定子测试名与 console 输出（`TestRomanNumerals/4_gets_converted_to_IV_(cant_repeat_more_than_3_times)`）→ 一律不译，console 块逐字节保持。
2. **代码内注释三分法**：`// earlier..` `// later..` 是结构性注释，随章翻译；`// true`、`// 11111111 ÿ 255 ...`（后记 fmt.Printf 那块）是结果/输出标注，不译。
3. **后记 Dave 长引文**：digit/numeral/number 三词辨析是全文最难处，译文需自洽（数字→记数形式→数），且保住 "tell me to f off"、":shrug:" 的口语幽默。
4. **`<details>` 折叠警告块**：blockquote + HTML 结构原样保留，只译文本。
5. **"Arabic number" vs "Arabic numerals"**：原文自己混用（后记专门吐槽这点）。定名：指 0-9 数字符/体系时用"阿拉伯数字"，指 `arabic` 变量承载的数值时用"阿拉伯数"。
6. **内链**：`iteration.md#benchmarking` → `iteration.md#基准测试`（iteration 章译文对应标题为"### 基准测试"）。
7. **幽默点**："best book ever right?"（自嘲式自夸）、"The Romans were into DRY too"（罗马人也懂 DRY）、"stay out of red"（别停在红）、"kill it when you're bored :)"、Dave 的 rant。
8. 表驱动测试描述字段 `Description` 在最终版被删——正文说 "I removed `description`"，保持逻辑对应。
