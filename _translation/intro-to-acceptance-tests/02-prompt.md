# 02 本章翻译约束 — Intro to acceptance tests

## 术语定名（本章首现加注一次）

- graceful shutdown → **优雅关停**（首现："优雅关停"（graceful shutdown））
- grace（标题双关）→ **体面**；grace period → **宽限期**（行业通用，k8s 语境）
- black-box test → 黑盒测试；functional test → 功能测试
- lead time → 前置时间（lead time），标题《前置时间（lead time）？》
- Test Pyramid → 测试金字塔；Decorator pattern → 装饰器模式
- headless web browser → 无头浏览器；north-star → "北极星"
- in-flight requests → 在途的请求（正文可口语化为"还在处理中的请求"）
- boilerplate → 样板代码；shippable → 可发布（**always be shippable** → 随时可发布）
- pod → Pod（保留英文，首现括注"实践中就是我们的软件"照原文）
- SIGTERM / SIGKILL / DORA / K8s / docker-compose / Selenium 保留英文

## 体例

- 标题双关三连："如果不留体面 / 留足体面的时候 / 如何做到体面"；技术处仍用"优雅关停"，首现比喻句搭桥（把电话"体面地讲完"对应"优雅关停"）。
- k8s 引语（blockquote）与 `Server.Shutdown` 文档引文（blockquote）意译；文档引文口吻保持说明书式的平实，`Shutdown`、`Server`、`Listener` 等标识符保留反引号/原文。
- 六个代码块逐字节一致；`//` 注释译成中文；log/Errorf 字符串不动（含 `"<http://localhost:"` 和 `"cannot run temp converter"` 两处上游笔误）。
- shell 输出块逐字节保留。
- 反馈回路统一为"反馈循环"（与 hello-world 一致）。
- 幽默保真：熄灯走人、手动测试让人不自在、"一坨垃圾也能让验收测试通过"、招聘软广收尾的轻松语气。
- 全部链接为外链，URL 原样；无图、无内链改写。
- 弯引号""，不用「」；中英混排加空格。
