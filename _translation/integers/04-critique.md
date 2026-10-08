# integers 章审校诊断（对照 source.md，只诊断）

## 准确性
1. **具名返回值段**："It should generally be used when the meaning of the result isn't clear from context" — 初译"只有当……才该用它"，加了原文没有的排他性（only）。应弱化为"当……不太看得出来时，才适合用它"。
2. **猫鼠段**："with some different numbers to force that test to fail" — 初译"逼着这种实现露馅"意译偏移，原意就是"换几个不同的数字让那个测试挂掉"，应贴回原句。
3. **强调格式越权**："the example will also be executed" 原文无斜体，初译擅自加了 *执行* 的斜体。按规则 2 与原文格式一一对应，应去掉。
4. "In the strictest sense of TDD" — 初译"严格来说，按照 TDD 的规矩"可接受，但"strictest"的比较级意味（最严格）可再贴一点："按最严格的 TDD 标准来要求"。
5. "you can make [Testable Examples]" — "做可测试示例"搭配略生硬，"编写"更自然。

## 中文表达
6. "Run the test `go test`" 初译"运行测试 `go test`"OK；上下两条短祈使句（运行/看看）保留短促节奏即可，无改动。
7. pkgsite 长导航段：初译步骤链完整，"在里面你应该能看到"指代清晰，通过。
8. "散落在代码库之外的代码示例"稍文，可改"放在代码库之外的"，更口语。

## 格式与体例
9. 代码块 8 个、语言标记、链接 8 条（7 外链 + 1 内链）、斜体/加粗清单核对：除第 3 条外全部一一对应；无直角引号；无 Gitbook 转义残留；`// Output: 6` 已按约束保持原样；`// Add takes...` 注释已译。
10. 内部链接 `hello-world.md#最后一次重构` 已按约定改写（锚点统一留给主控终审）。

结论：4 处需修订（1、2、3、5），2 处可选润色（4、8），其余通过。
