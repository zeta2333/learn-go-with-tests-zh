# 02 — json 章翻译约束

## 本章特有定名

- 章标题（H1）：`JSON、路由与嵌入`
- league → 联盟；league table → 联盟积分表（首现括注 league）
- ServeMux → 首现：[`ServeMux`](原链接)（请求多路复用器）
- embedding → 嵌入；`http.Handler` 嵌入进结构体的叙述围绕「PlayerServer 获得嵌入类型的全部方法」展开
- Encoder/Decoder → 编码器 / 解码器；Encode/Decode 保留英文（方法名）
- serialize / deserialize → 序列化 / 反序列化
- stub 作动词 → 预置（stub）；StubPlayerStore 是代码名不译
- response spy → 响应 spy（沿用 mocking 章 spy 不译）

## 标题对齐全书惯例

- Write the test first → 先写测试
- Try to run the test → 试着运行测试
- Write enough code to make it pass → 写足够的代码让测试通过
- Write the minimal amount of code for the test to run and check the failing test output → 写最少的代码让测试能运行，并检查失败的测试输出
- Refactor → 重构；One final refactor → 最后一次重构
- Wrapping up → 总结

## 幽默/语气点

- "Let's commit some sins and get the tests passing in the quickest way we can" → 保住自嘲："先造点孽"。
- "Notice the lovely symmetry in the standard library." → "可爱的对称性"。
- "live with the uncomfortable feeling of an incomplete implementation" → 忍着"实现不完整"的别扭劲儿。
- "park that for now" → 先搁置。

## 链接处理

- 章首代码链接 → 原样保留 quii 仓库 `tree/main/json`。
- `[In the previous chapter](http-server.md)` → http-server 未译：`[上一章](https://github.com/quii/learn-go-with-tests/blob/main/http-server.md)（英文原版）`。
- Effective Go 两条链接、pkg/net/http 链接原样保留。

## 代码块纪律

- 39 个代码块逐字节一致；Go 注释随章翻译（如 `// server.go` 保留、`//server_test.go` 保留——它们是文件名指示，不译）。
- `// Output:` 无；错误输出、JSON 样例、`json:"..."` 标签原样（本章无 struct tag）。
- 玩家名 Chris/Cleo/Tiest/Pepper/Bill/Alice 不译。
