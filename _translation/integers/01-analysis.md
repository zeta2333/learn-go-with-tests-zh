# integers 章分析

## 内容概述
全书最短的正章之一，是 TDD 循环在"整数加法"上的第一次完整演练：
1. 先写 `TestAdder`（用 `%d` 而非 `%q`），引入"一个目录一个 package"的规则与 `integers` 包
2. 看编译错误 → 写最少代码（`return 0`）确认失败理由正确 → 顺势补一段具名返回值的"何时该用/何时不该用"
3. "写足够的代码让它通过"一节玩了一个梗：较真的程序员写 `return 4`，引出猫鼠游戏与 Property Based Testing 的预告
4. 重构：文档注释（Go Doc）
5. **Testable Examples**（本章真正的重头戏）：`ExampleAdd`、`// Output: 6` 的特殊语义（编译 vs 执行）、`go test -v` 输出、pkgsite 本地浏览、pkg.go.dev 发布
6. 总结四条清单

## 本章新术语（全书 glossary 尚无）
- format string → 格式化字符串（与已有"格式化动词"配套）
- Testable Examples → 可测试示例
- Example function → Example 函数（"Example"保留英文，同 mock/stub 惯例）
- Property Based Testing → 基于属性的测试
- unit test → 单元测试
- test suite → 测试套件
- type signature → 类型签名
- third-party package → 第三方包
- Go Doc → Go Doc（保留英文）
- pedantic programmer → 较真的程序员（非术语，风格处理）

## 翻译难点
1. **幽默点**："Ah hah! Foiled again, TDD is a sham right?"（反派腔的"Foiled again!"）；"a game of cat and mouse"；"A pedantic programmer"。必须保住调侃语气，不译平。
2. **`// Output: 6` 不能翻译**：它是 Go testing 的功能性指令（决定示例是否被执行），正文还在逐字引用它。Go 代码块注释随译的规则在此要开例外，仅此一处，其余注释照译。
3. **内部链接** `hello-world.md#onelastrefactor`：锚点指向原文章节"One last refactor?"，中文版对应"最后一次……重构？"，链接改写为 `hello-world.md#最后一次重构`（锚点最终统一由主控终审处理）。
4. Gitbook 转义：正文有 `\(in our case two integers\)`，需去掉反斜杠。
5. pkgsite 那段是长导航指令（装 pkgsite → `-open .` → 逐层点开 Integers → func Add → Example），步骤因果链不能乱。
6. 主控给的"本章特别说明"提到 range 遍历、rand 种子——当前源文件里**并没有**这些内容（可能是其他版本章节的描述），以源文件为准，不引入。
