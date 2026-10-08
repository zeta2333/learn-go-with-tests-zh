# 04 — 审校诊断（对照原文，只诊断）

## 准确性

1. **S4（调用传参句）**："调用它的同时还得传入"——原文 "You also have to pass in" 的 also 是"此外/还要"，"的同时"歪曲了句间关系（不是同时做两件事，而是额外要求）。→ 改"调用时还得传入"。
2. **S16（泡茶）**："从橱柜里取出茶叶"——原文 "got the tea out of the cupboard"，后文放的是 "teabag"（茶包）。先说"茶叶"再说"茶包"前后不一致。→ 改"从橱柜里把茶拿出来"，保留模糊。
3. **S17（没有做的事）**：原文刻意重复 "until it boiled / once the kettle had boiled"（学究式啰嗦正是笑点），初稿压缩成一层，趣味受损。→ 镜像重复："一直盯到水开，等水烧开了才去干其余的事"。
4. **S23**："写进 `results` map"——原文此处的 results **无反引号**（"the results map"），行内代码格式须与原文一一对应。→ 去反引号。（S29、S50 原文有反引号，已正确保留。）
5. **S35（竞态检测器）**：初稿把（race detector）括注放在链接**外**："[*竞态检测器*][godoc_race_detector]（race detector）"，读起来断裂。原文强调是 `[_race detector_]`。→ 括注移入链接文本：`[*竞态检测器*（race detector）][godoc_race_detector]`；"察觉"改"发现"（spot）。

## 术语与加注体例

6. **括注位置不统一**：初稿有 `*阻塞（blocking）*`、`*数据竞争（data race）*`、`*发送语句（send statement）*` 等"括注在斜体内"的写法，与 `*流程*（process）`、`词法作用域（lexical scope）` 的"括注在斜体外"混用。→ 统一为：斜体只包中文术语，括注在外：`*阻塞*（blocking）`、`*数据竞争*（data race）`、`*发送语句*（send statement）`、`*接收表达式*（receive expression）`。
7. **匿名函数首现未加注**：Go 特有概念首现应加注一次（S21）。→ "常常会用*匿名函数*（anonymous function）"。
8. **S10**："新的 fake 版 `WebsiteChecker`"——原文 "a new fake implementation"，"implementation" 是"实现"。→ "新的 fake 实现"。

## 中文表达

9. **S7**："可同事渐渐开始收到投诉"——"渐渐"为原文所无（"has started to get complaints"只是"开始"），删去；"可"改"但"更顺。
10. **S19**："干等它结束"与 S17"盯着水壶干等"撞词，且原文此处只是 "makes us wait for it to finish"。→ "它让我们等它结束"。
11. **S26**：a) "欢迎来到并发" → "欢迎来到并发的世界"更自然；b) "处理得不恰当时，你很难预测" → "如果处理不当，你很难预测"；c) "写测试的原因：它能帮我们确认"一句双冒号连用，读感差 → 改逗号衔接。
12. **S30**："要修这个问题"——"修……问题"搭配生硬 → "要解决这个问题"。
13. **S39**："它写入的正是同一块内存，也就是下面这个："——"下面这个"冗余（下一行就是代码块，指向自明）→ "写入的正是同一块内存，也就是"。
14. **S47**："这些操作连同它们的种种细节，让……"——"连同……种种细节"翻译腔 → "正是这些操作及其细节，让不同的流程之间得以通信。"
15. **S55**："参与其间的多个流程"偏书面 → "其中涉及的多个流程"。

## 其他核对结论（无需改动）

- 14 个代码块逐字节一致（两处 Go 功能注释 `// Send statement`、`// Receive expression` 按规则随译，校验器已确认）；`// Output:` 无。
- 标题链沿用既有章内惯例："## 编写测试"（hello-world 先例）、"### 写足够的代码让它通过"（dependency-injection 先例）、"## 总结"、"### Channels" 保留英文。
- `WARNING: DATA RACE`、`fatal error: concurrent map writes`、堆栈、基准输出均未译，正确。
- 链接：4 条引用定义原样保留，`[DI] → dependency-injection.md` 未改；外链 URL 全部一致。
- "url" 小写、"URL" 大写、`result channel`/`results map` 散文式写法均随原文，无混入反引号。
- blockquote（Go 1.22 注记）结构与加粗保留；`>` 空行续块未断开。
- 引号体例：全文弯引号，无「」；无 Gitbook 转义残留；无图片。
- 泡茶比喻、aside 双小节的省略号呼应、"或者就当自己看到了，随你便"幽默保住。
