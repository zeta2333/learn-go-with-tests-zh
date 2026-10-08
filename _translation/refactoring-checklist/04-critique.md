# 04 — 审校诊断：03-draft.md 对照原文（只诊断，不改文）

## 准确性

1. **"engineer the overall design" 误译**（见树又见林节）："很难去经营更大系统的整体设计"——"经营"不对，engineer 此处是"谋划/打造"。应改："就很难为更大的系统谋划出整体设计"。
2. **"as you see fit" 偏离**（注释掉测试那条）："按你自己的节奏"是"节奏"义，原文是"酌情、怎么合适怎么来"。应改："再怎么合适怎么来，逐个处理剩下的测试"。
3. **"needlessly duplicated code" / "find designs" 结尾段**："无谓重复代码、深层嵌套的系统里，设计要难找得多"——主语错位，原文是"在这样的系统里要发现设计难得多人"。应改写理顺。
4. **"Frequent, small refactoring is necessary for better design"**："是通向更好设计的必经之路"略有拔高，necessary 是"必不可少"。建议："**要想设计更好，频繁的小幅重构必不可少**"。
5. **Wikipedia magic number 定义**："含义不明、或出现多次的唯一值，最好（ preferably）用命名常量替换"——"唯一值"位置造成歧义（好像"出现多次"和"唯一"矛盾）；另有"（ preferably）"内部多余空格（笔误）。应改为："含义不明的值，或出现多次、最好用命名常量替换的值"或类似理顺。
6. **"a bout of refactoring"**："一阵重构"量词欠妥，改"一轮重构"。
7. **"It also, shouldn't be a time-sink"**：译文准确，保留。
8. **代码块逐字节核对**：13 个块全部与原文一致（`WishHappyBirthday(person Person)` 无闭括号、第 12 块尾部空行、`//etc` 无空格等细节均保留）；注释按规则译为中文，verify 的 Go 注释剥离逻辑可放行。✓
9. **链接**：4 个外链（Collins / Wikipedia DRY / Wikipedia magic number / imgur 图）全部原样保留在译文中。✓
10. **两处 `<u>` 标签**：均已保留。✓

## 中文表达

11. **开篇句翻译腔**："变得相当轻松，近乎第二天性"——"第二天性"书面且生硬，原文口吻随意。建议："多数情况下都能凭直觉轻松完成"或"近乎本能"。
12. **"支撑它的测试"**：样章 hello-world 用过"背后还有测试撑腰"，此处 "a test to back it up" 可复用"撑腰"保持全书口吻（可选）。
13. **"DRY 要小心行事"**：DRY 作动词加"小心行事"读着别扭。建议："DRY 时要小心谨慎"。
14. **"But now I don't know how it works!" 段首长句**："对这种偏好'由更小函数和方法组合而成'的重构，一个常见的反对意见是……"定语链偏长。建议拆短："这种重构偏好用更小的函数和方法互相组合，对此常见的一条反对意见是……"。
15. **"consolidate this elsewhere"**："合并到别处"可改"归拢到别处"，与样章"归拢"用词呼应。
16. **"your design skills increase quickly"**："迅速增长"平淡且书面，建议"**你的设计能力会长进飞快**"。
17. **"You shouldn't feel shy about trying out ideas"**："不必害羞"生硬，建议"尝试想法时不必不好意思"。
18. **快捷键反引号不统一**：原文快捷键有的带反引号（`command+option+n`）有的不带（command+option+v、command+option+c、command+option+m 二处、shift+F6 带等），初译已统一加反引号。依据全书规则 4"代码字面量进反引号"，这是有意的规范化，非偏差——保留。
19. **" try it" 引文内直引号**：初译"先试试看"处引号已用弯引号。✓ 全文无「」。✓

## 加注

20. DRY 首现已有"（Don't repeat yourself，DRY）"括注。✓
21. "self-documenting"（自文档化）为开发者常识词，不加注。✓

## 结论

诊断 20 条：准确性 6（第 1-6 条需修），表达 8（第 11-18 条需酌修），其余确认无误。进入 05-revision.md 逐条修复。
