# 02 — 本章翻译约束

## 术语定名（本章首现处理）

- HTTP handler → **HTTP 处理器**（全书既定，与 http-server 章完全一致，不加注）。
- single responsibility principle → **单一职责原则**，首现括注英文。
- separation of concerns → **关注点分离**（术语表既有，本章维基链接处首现，不重复括注英文）。
- persistence layer → **持久层**，首现不括注（构词透明）。
- catch-all → **一律兜底**。
- `ServiceThing`、`ImportantBusinessLogic`、`UserServer`、`UserService`、`MockUserService`、
  `MongoUserService`、`Registration` 等代码名一律保留英文反引号。
- mock、spy、stub 沿用术语表保留英文；`ResponseRecorder` 行文可称"记录器"。
- "构建一个应用"篇 = "Build an application"（沿用 app-intro 章译名）。

## 体例

- 章标题 H1：**再探 HTTP Handlers**（主控指定）。
- 斜体统一用 `*...*`（源文 `_..._` 归一为星号，样章体例）；加粗、行内代码、链接与原文一一对应。
- 文档引文（blockquote 内）译出，其中 HandlerFunc 一句**逐字复用** http-server 章的既有译文：
  「HandlerFunc 类型是一个适配器（adapter），让普通函数可以当作 HTTP 处理器来用。」
- 6 个 go 代码块逐字节保留代码；`//` 注释随章翻译（含 `//todo:` 前缀保留）；无 Output 注释。
- 图片：`![Go 社区常见问题图解](assets/amazing-art.png)`（资源已拷入 docs/assets/）。
- 弯引号""，禁直角引号；中英文之间空格。

## 幽默点对策

| 原文 | 对策 |
|---|---|
| no magic beans, nothing | "没有魔法豆，什么都没有"——保留《杰克与魔豆》的梗，不解释 |
| This is too much. | "这也太多了吧。"——短句收束 |
| Reader, take a breath | "读者朋友，深呼吸"——保留对读者的喊话感 |
| (again for terseness/laziness) | "（依旧是为了省事——说白了就是犯懒）"——自嘲保住 |
| You're cheating! | "你这是在作弊！"——标题里的戏剧化指控保留 |
| terrible API | "糟糕透顶的 API" |
| snap these two units together | "咔哒一声拼在一起"——拟声保画面感 |
| to handle... everything! | "去处理……一切！"——破折号+省略号保住原文的挖苦节奏 |
