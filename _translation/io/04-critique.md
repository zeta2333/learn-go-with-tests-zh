# 04 — 批判性审校：初译稿 vs 原文（只诊断）

## Accuracy

- **"effectively empty" 误译（必须修正）**："`os.File` has a truncate function that will let us effectively empty the file"，初译"能*有效地*清空文件"。此处 effectively 是"在效果上/实际上"，不是"有效地"（efficiently 的假朋友）。→ 改为"能让我们达到清空文件的效果"。
- **编译器报错方向表述含混（建议修正）**："The compiler will fail in a number of places where we are expecting an `io.ReadWriteSeeker` but we are sending in `*os.File`"——上游这句话方向说反了（实际是 tape 字段改为 `*os.File` 后，编译器在"传入 `io.ReadWriteSeeker`、而代码期望 `*os.File`"的地方报错）。照直译会传播错误认知，改动方向又违反忠实原则。→ 折中：改为方向中性的表述"编译器会在若干地方报错——有的地方还在传 `io.ReadWriteSeeker`，而代码期望的已经是 `*os.File`"，语义与真实报错一致，也未添原文没有的细节。
- **"100% not idiomatic" 数字丢失**：初译"这绝对不是惯用写法"丢掉了原文的"100%"调侃。→ "**这 100% 不是惯用写法。**"
- **"somewhat perturbed" 程度略过**：初译"相当恼火"，somewhat 是克制的英式轻描淡写。→ "颇为光火"→ 收敛为"颇为恼火"。
- **"portable" 术语漂移**：初译"数据非常好搬运"。portable 是标准术语"可移植"。→ "数据的可移植性非常好"，保留口语后半句。
- 其余逐段核对：64 个代码块（verify 已过）、终端输出、错误信息、URL、`//server.go` 等文件名注释、`// 再读一次` ×3、`// 等等……` 均与原文对应，无增删。

## Native Voice

- **辅助函数引入句结构走样**："Let's create some helper functions which will create a temporary file with some data inside it, and abstract our score tests"，初译"我们来写几个辅助函数：一个负责创建临时文件并写入初始数据，顺便把得分相关的测试抽象一下"——"顺便"弱化了第二个辅助函数（assertScoreEquals）的独立地位，且"几个……一个……"搭配别扭。→ "我们来写几个辅助函数：一个负责创建临时文件并写入初始数据，另一个把得分断言抽象出来"。
- **Tape 缺一点趣味注**："I'm going to call it `Tape`"——磁带的梗（永远从头写）后文才点破，首现加"（磁带）"二字能让中文读者立刻会心。→ "我打算叫它 `Tape`（磁带）"。
- **"编译器都会扶着你"**：略萌、偏离 "the compiler will help you with every change" 的平实语气。→ "每一次改动，编译器都会帮你把关"。
- **sort.Slice 引文**：初译"按照给定的 less 函数对给定的切片进行排序"，两个"给定"重复。→ "使用传入的 less 函数对传入的切片排序"。
- **"我们的产品负责人相当恼火"**：见上 Accuracy 条，收敛程度词即可，句子结构保留。
- 整体节奏、短句、祈使句贴合样章；无「」、无翻译腔长定语链；中英空格合规。

## Notes & Adaptation

- 首现加注核查：集成测试（integration test）✓、嵌入类型（embedding）✓（"还记得嵌入吗？"二现不重注 ✓）、截断（truncate）✓、多态（polymorphism）✓、正常路径（术语表既有，前章已注，本章不重注 ✓）、产品负责人（app-intro 已注 ✓）、DRY（首现括注 ✓）。
- 上一章链接按规范指向 GitHub 原版并注明（英文原版）✓，与 app-intro.md 现行格式一致。
- 幽默点核查："万岁！"（hooray!）、"我就得解释一遍依赖管理了！"、"一心二用"（juggling two things at once）、"视而不见"、"跟预期的一样！"、吉他类比、"简单！"（Easy!）均落地。
- "对写入来说，我们这套方案相当短视"（fairly short-sighted）保住了自嘲 ✓。

## Summary

无事实性错误之外的硬伤；1 处必须修正的误译（effectively），1 处上游表述反向需中性化处理，2 处细节回补（100%、somewhat/portable），4 处中文表达润色。修订后进入定稿润色。
