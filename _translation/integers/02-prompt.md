# integers 章特有约束

## 新术语定名
- format string → 格式化字符串
- Testable Examples → 可测试示例
- Example function → Example 函数（Example 保留英文）
- Property Based Testing → 基于属性的测试（首现括注英文）
- unit test → 单元测试；test suite → 测试套件；type signature → 类型签名
- Go Doc、readme 保留英文

## 硬性例外
- `// Output: 6` 是功能性注释，**保持原样不译**；正文凡引用它处也逐字保留反引号原文。
- 其余 Go 代码块内 `//` 注释随章翻译（如 `// Add takes two integers...` → `// Add 接收两个整数，返回它们的和。`）。

## 幽默对策
- "Ah hah! Foiled again, TDD is a sham right?" → 保留反派被戳穿的夸张腔：类似"啊哈！又被摆了一道——这么说 TDD 果然是个骗局咯？"
- "a game of cat and mouse" → "猫捉老鼠"的游戏（保留 wikipedia 链接）。
- "A pedantic programmer may do this" → "较真的程序员可能会这么写"。

## 标题
- H1：整数
- Write the test first → 先写测试
- Try and run the test → 试着跑一下测试
- Write the minimal amount of code for the test to run and check the failing test output → 写最少的代码让测试跑起来，并查看失败的测试输出
- Write enough code to make it pass → 写足够的代码让测试通过
- Refactor → 重构
- Testable Examples → 可测试示例
- Wrapping up → 总结（与 hello-world 章保持一致）

## 其他
- 内部链接改写为 `hello-world.md#最后一次重构`；全部外链 URL 原样保留。
- `\(in our case two integers\)` 等转义清理。
- 目录树、`go test -v` bash 输出、编译错误行均逐字节保留。
