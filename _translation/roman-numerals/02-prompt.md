# 02 — roman-numerals 章翻译约束

在 00-book-prompt.md 全书规范之上，本章额外约束：

## 标题
- H1 定为：`# 基于属性的测试入门`（按 SUMMARY，不照搬上游 "Roman Numerals"）。
- 小节标题尽量与 iteration 章译文统一：Write the test first → 先写测试；Try to run the test → 试着运行测试；Write the minimal amount… → 写出刚好能让测试运行的最少代码，并检查失败测试的输出；Write enough code to make it pass → 写足够的代码让测试通过；Refactor → 重构。
- `An intro to property based tests`（H2）→ 基于属性的测试入门；`### Property based tests`（总结里）→ 基于属性的测试。

## 术语（首现加注一次）
- 基于属性的测试（property based tests）；基于示例的测试（example based tests）；瘦垂直切片（thin vertical slices）；减数（subtractor）；面向对象（OO）；无符号整数；swap 抖动（swap thrashing）；往返转换（round-trip）。
- 阿拉伯数字 = digits/体系；阿拉伯数 = 数值本身（对应参数 `arabic`）。后记辨析用：数字（digit）、记数形式（numeral）、数（number）。
- Kata 保留英文；DRY 保留英文；`:shrug:` 原样保留。

## 代码与输出
- 一切字符串字面量（测试描述 `"1 gets converted to I"` 等）不译，保证与 console 输出自洽。
- `// earlier..` `// later..` 译为 `// 前面的代码……` `// 后面的代码……`。
- `// true` 与 `// 11111111 ÿ 255 377 'ÿ' ff FF U+00FF` 是结果/输出标注，不译。
- `<details>/<summary>` HTML 标签原样，summary 文本译为「点开看看为什么（技术解释）」——注意引号体例：正文用弯引号。

## 语气
- 保留自嘲与吐槽："best book ever right?"（本书史上最佳，对吧？）、"kill it when you're bored :)"、Dave 引文里的 "f off"（让他滚蛋）、"way too precise"（较真儿）。
- 表格（Arabic/Roman 符号表）保留结构，表头译为「阿拉伯数字 / 罗马数字」。
