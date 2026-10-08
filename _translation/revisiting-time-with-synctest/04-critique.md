# 04 — 审校诊断（对照 03-draft.md 与 source.md，只诊断不改稿）

## 准确性

1. ✅ 18 个代码块与原文逐字节一致（Go 注释除外），语言标记全部相同。
2. ❌ **斜体强调丢失/错位（违反"强调一一对应"）**：
   - timer heap 段 "…, *while* `Wait()` is still deciding whether to return"，
     草稿译作"而此时 `Wait()` 还在盘算要不要返回"，*while* 的强调丢了。
   - 同段 "no upcoming deadline for *us* to wait on"，草稿把强调放在了
     "*即将到来*"（原文强调的是 *us*），应改为"可供*我们*等待"。
3. ❌ "Additional material" 译作"延伸材料"，全书既定惯例是"延伸阅读"
   （docs/context.md）；Go 博客条目按惯例加中文导语。
4. ⚠️ "that nothing has happened yet" 草稿为"什么都不该发生"，丢了 "yet"
   （到目前为止还没发生）的时点义；后文引用同一短语处同理。
5. ⚠️ "unrealistically tiny durations that only vaguely resemble the real thing"：
   草稿"跟真实场景只有点形似"意思对，但"vaguely"的"貌合"感可再贴近。

## 中文表达

6. ❌ ¶5 "运行使用 `time.Sleep`、`time.AfterFunc` 之类工具的真实代码、原封不动的代码"
   ——顿号并列读起来卡；"real, unmodified" 宜合并为一个修饰序列。
7. ❌ "`ScheduleAlertAt` 被以 `10 * time.Minute` 和 `200` 调用过"——"被以"拗口。
8. ⚠️ "气泡的虚拟时钟不会自己定着表往前走"——"定着表"生造，宜作"按着自己的
   计时器"。
9. ⚠️ "这正是 `synctest` 存在要解决的问题"——"存在要解决"杂糅，宜作
   "为之而生"。
10. ⚠️ "测试过了。但为了一个提醒，它花了实打实的 6 秒。"——原文 "It passes.
    It also takes six real seconds, for one alert." 两短句节奏，"也"的转折语气
    （通过≠划算）可以更贴。
11. ⚠️ "相邻最远的两个能隔上 1 小时 40 分钟"——原文 "some as far as … apart"
    指"有的提醒彼此隔得足有 1 小时 40 分钟"，"相邻最远"表述绕。
12. ⚠️ "无论哪种时序，都没有什么能兜底"——"safe"宜直白作"安全保障"。
13. ⚠️ "气泡恰好做了它被设计出来要做的事"——冗长，可作"设计上该做的事"。
14. ⚠️ "需要内存里的替身时，可以求诸 `net.Pipe` 之类的工具"——"求诸"文白夹杂。
15. ⚠️ "本章的好几个坑——…首当其冲——"——"首当其冲"义为"最先受到攻击"，
    此处是"其中最典型"，宜作"尤其是"。
16. ⚠️ "我们把同一个测试包进气泡里"——"包进"可，但加"原样"更贴
    "the same test"。
17. ⚠️ "干等"在 ¶4、¶5、¶11 出现三次，可微调其一。

## 加注与体例

18. ✅ 首现加注：气泡（bubble）、虚拟时钟（fake clock）、持久阻塞
    （durably blocked）、死锁（deadlock）、小程序（spike）均已括注一次。
19. ✅ 弯引号、中英空格、反引号使用正确；无直角引号；无 Gitbook 转义残留。
20. ✅ 三个跨章链接均为站内相对链接（time.md / http-handlers-revisited.md /
    select.md），与已译章节体例一致。

## 结论

无事实性错误；主要问题是 2 处斜体强调、1 处标题惯例、若干中文打磨点。
按上述 1–17 修订后可进入定稿。
