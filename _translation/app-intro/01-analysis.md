# 01 分析 — app-intro（构建一个应用）

## 内容概述

"Build an application" 篇的开篇导语，仅 5 个自然段 + 6 条章节预告列表，无代码块、无图片、无标题层级（只有 H1）。

- 承上启下：*Go Fundamentals* 篇已学完，本篇开始迭代式地构建一个（随章节长成扑克游戏的）Web 应用。
- 六个预告条目分别链接到 `http-server.md`、`json.md`、`io.md`、`command-line.md`、`time.md`、`websockets.md`。

## 本章新术语

| 英文 | 定名 | 说明 |
| --- | --- | --- |
| product owner | 产品负责人 | Scrum 角色名，首现括注英文；全书后文反复出现的幽默角色 |
| endpoint | 端点 | Web 常识词，不加注 |
| routing | 路由 | 常识词，不加注 |
| embedding | 嵌入 | 指 Go 的 struct embedding，章标题语境里译"嵌入"即可 |
| persist | 持久化 | 常识词 |

## 翻译难点

1. **六条前向引用全是未译章节**（docs/ 与 _translation/ 中均无对应章节），按全书规则 2 改指上游 GitHub blob URL，并在链接后注"（英文原版）"；仿照 pointers-and-errors.md:704 的既有先例，列表末尾补一行译注说明日后会切回本站链接。
2. **章名定名需与导航体例一致**（mkdocs nav：Go 标识符保留英文如 Map/Select/Sync/Context，描述性标题意译如"HTML 模板"）：
   - HTTP server → HTTP 服务器
   - JSON, routing and embedding → JSON、路由与嵌入
   - IO and sorting → IO 与排序
   - Command line & project structure → 命令行与项目结构
   - Time → Time（`time` 包名，保留英文，同 Select/Sync/Context）
   - WebSockets → WebSockets（专有名词）
3. "as our product owner dictates" 是全书贯穿的玩笑（想象中的产品负责人不断加需求），语气要保住，不能译成干巴巴的"根据产品负责人的要求"。
4. "backed by tests" 全站已有既定说法"有测试护航/保驾护航"（见 generics.md、reflection.md），沿用。
5. "hopefully digested" 的自嘲式口吻（"希望"你真消化了）要保留。
6. 无代码块、无图片、无外链 http URL；verify.py 实际校验点只有：无直角引号、无转义残留、代码块计数（0=0）。

## 其他核查结论

- 源文件与上游 commit 4675d96（本站翻译基线）一致。
- 本章无 `.gitbook/assets` 图片引用，无需拷贝资源。
- app-intro 列表中 command-line 章名是 "Command line & project structure"，上游 SUMMARY.md 里同一章写作 "Command line & package structure"，两处都以 app-intro 原文为准翻译。
