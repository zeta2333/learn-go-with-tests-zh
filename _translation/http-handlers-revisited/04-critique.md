# 04 — 审校诊断（对照 source.md，只诊断）

## 准确性

1. **首段**（"This book already has a chapter on ... but this will feature a broader discussion on designing them, so they are simple to test"）：
   译文拆成两句并补出"但那一章没有展开设计层面的话题"，属无中生有的解释。应收紧为一句，让"但"字直接衔接"更宽泛的设计讨论"。
2. **"The lines can blur depending on how abstractly you're thinking"**："划分的界线会随你思考的抽象层次不同而变得模糊"——"随……不同而"是翻译腔，且"模糊"的主语链条别扭。宜改写为口语化因果。
3. **清单第 2 条**（"Call some `ServiceThing` to do `ImportantBusinessLogic` with the data I got from step 1"）："用它对第 1 步拿到的数据执行 `ImportantBusinessLogic`"——"用它对……执行"生硬，且漏掉原文第一人称口吻（"my"）。宜"让它拿第 1 步得到的数据去做……"。
4. **清单第 1 条**："写 HTTP 响应：发响应头、状态码，等等"——冒号引出细项改变了原文"写响应，（具体是）发头、状态码等"的并列结构；两处出现，需统一改为逗号并列。
5. **第 3 步**（"I'll just have a catch-all handler of a `500 Internal Server Error` _for now_"）："眼下我先*暂时*一律兜底返回"——"眼下"+"暂时"语义重复；斜体落点应在"眼下"，删"暂时"。
6. **"It wouldn't be surprising that ..."**："毫不意外，……"作句首状语稍有偏移（原意是"要是……也不奇怪"），可接受但可再贴一点："往后的迭代里，我们多半还想……"。
7. **"Santosh Kumar tweeted me"**："在 Twitter 上向我提问"偏正式，原句只是"发了推文问我"。宜口语化。

## 中文表达

8. **"要是你所有的代码都能像你提到的那些例子一样简单易读、简单易测，那岂不是很好？"**："岂不是很好"平淡，原文 "Wouldn't it be nice" 的感叹劲没出来。改"那该多好"。
9. **"做好这些，你会看到测试处理器其实是件轻而易举的小事"**（"By doing this we'll show how ..."）："你会看到"可以，"轻而易举的小事"略叠；改"其实相当轻而易举"更贴 trivial。
10. **"划分的界线……"句**（同准确性 2）。
11. **"这个记录器会把发送出去的内容记录下来"**：可再顺一点——"会把它收到的写入内容一一记下"。（小改）

## 体例与格式检查（结论）

- 代码块 6/6，语言标记与数量一致；注释仅 `//` 行改动，`//todo:` 前缀保留 ✓
- 链接：4 个内链目标文件名未动、7 个外链 URL 全部保留 ✓
- 图片引用 `assets/amazing-art.png`（资源已入库）✓
- 无直角引号、无 Gitbook 转义残留 ✓
- 斜体已归一为 `*...*`，与原文 `_*_` 一一对应 ✓

## 判定

无硬伤；上述 1–9 为修订点，均为措辞级。修订后可作定稿底稿。
