# 02 — websockets 章翻译约束

## 定名

- WebSocket：协议名一律保留英文（WebSocket / WebSockets / `*websocket.Conn` 等）。
- 协议词汇：握手（handshake）首现注英文；"Upgrade" 在代码里保留，正文表述用"（协议）升级"。
- 盲注三件套：blind bet → 盲注（首现"盲注"（blind bet））；blind value → 盲注值；blind alert → 盲注提醒。
- 复用既有定名：联盟积分表（league table）、产品负责人、端点（endpoint）、联盟（league）。
- spy / mock / stub / Gorilla WebSocket / Go 工具链词汇保留英文；"serve HTML" 沿用本篇"返回 HTML"的说法。

## 体例

- 全部 55 个代码块逐字节复制原文，仅 `//` Go 注释翻译（`//todo:`、`// (rather than a minute)`、`// etc`）；`html` 块一字不动。
- 行内代码 `` `The blind is now *y*` ``、`` `"{Playername} wins"` `` 保留原样（含星号、引号）。
- 标题定式：项目回顾 / 下一步 / 先写测试 / 试着运行测试 / 写足够的代码让测试通过 / 写最少的代码让测试能运行，并检查失败的测试输出 / 重构 / 收尾。
- 斜体强调 `_..._` 保留为 _..._；弯引号，不用直角引号。

## 幽默点对策（不许译平）

- "Sorry folks. Lobby O'Reilly to pay me to make a 'Learn JavaScript with tests'." → 保留自嘲：游说 O'Reilly 出钱请我写一本《Learn JavaScript with tests》。
- "We committed many sins" → 犯下了不少"罪行"；"nasty, horrible, _working_ software" → 又糟又烂但_能跑_。
- "as if by magic" → 像变魔法一样；"Hooray!" → 万岁！；"This seems too easy!" → 这也太简单了吧！
- "the best (or luckiest) poker player" → 最厉害（或者手气最好）的扑克玩家。

## 已知上游瑕疵（正文可不改，报告中列明）

- "in a go routine"（应为 goroutine）——正文按 goroutine 译。
- "pass through to `StartGame` was `playerServerWS`" 语法混乱且无 `StartGame` 符号（实际是 `game.Start`）——按代码事实译为 `Start`，报告列明。
- 编译错误输出中的包路径 `.../WebSockets/v2`（大写 W）位于代码块，逐字节保留。
- "### What about tests for the JavaScript ?" 问号前多一个空格——标题意译后自然消除。
- `The main changes is` 主谓不一致——意译消除。
