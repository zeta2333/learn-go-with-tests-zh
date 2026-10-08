# 04 — 审校诊断（对照原文，只诊断）

## 准确性

1. 【准确度欠佳】"It uses `exec.Command` which allows you to execute an external command
   **to the process**" 草译"执行一个相对于进程的外部命令"——"相对于进程"生硬且易误读。
   原意是"让你的进程得以执行外部命令"。
2. 【语义微偏】提问第一段 "I am executing a command ... **which generated XML data**"：
   命令的产物是 XML 数据（陈述事实），草译"执行一个命令来生成 XML 数据"读起来像目的状语。
   宜改为"……执行了一个命令，它会生成 XML 数据"。
3. 【可保留】原文引语里 "os.exec" 与前文 "os/exec.Command()" 拼写不一致，属提问者笔误，
   译文统一为 os/exec 即可（正文非代码，不逐字节）。

## 中文表达

4. 【表达】"Testable code is decoupled and single purpose" 草译"解耦的、单一用途的"——
   "单一用途的"偏名词化翻译腔，建议"可测试的代码是解耦的，而且只做一件事"。
5. 【表达】"任何人都可以拿任何能给出 `io.Reader` 的东西（这极其常见）来复用这个函数"
   两个"任何"叠用拗口；建议"任何返回 `io.Reader` 的东西（这极其常见）都能拿来配合这个函数使用"。
6. 【语气】末段 "is a breeze" 草译"成了一件轻松的事"偏平；可更口语："易如反掌"。
7. 【表达】"所以把它留着，确保一切照常工作" 稍碎，可作"所以我们会把它留住，
   确保整体依然正常工作"。

## 加注

8. seam 首现括注（seam）得当；integration test 括注与 http-server 章一致，得当。
   stdout 按常识不加注，符合本章说明。

## 体例核对

9. 五个代码块逐字节一致（verify 已过）；唯一注释翻译无误。
10. 链接：5 条 URL 全保留；`./dependency-injection.md` 相对链接正确（目标章已译）。
11. 无直角引号、无转义残留、无图片。
12. 加粗强调段 "**GetData 的问题在于……**" 保留加粗，断句正确。

## 结论

无硬伤，4 处表达修订后即可定稿。
