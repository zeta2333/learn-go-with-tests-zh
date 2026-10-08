# maps 章 — 本章特有约束

## 定名（首现加注一次）

- map → map（不译）；`map[K]V` 类声明进反引号
- key → 键；value → 值（叙述中；代码里的 `word`/`definition` 等标识符不动）
- Dictionary（类型）→ 代码中 `Dictionary`；叙述"词典"
- definition → 释义；word → 单词
- comparable → 可比较；reference type → 引用类型
- panic → panic（首现括注"程序崩溃"）
- CRUD → CRUD（增删改查）
- 错误变量名 `ErrNotFound` / `ErrWordExists` / `ErrWordDoesNotExist` / `DictionaryErr` 均为代码标识符，保留

## 体例

- 章标题 H1：`Map`（主控指定，保留英文）
- 小节标题按全书循环体例意译：
  - Write the test first → 先写测试
  - Try to run the test / Try and run the test → 尝试运行测试
  - Write the minimal amount of code for the test to run and check the output → 写出让测试运行的最小代码，看看输出
  - Write enough code to make it pass → 写够让测试通过的代码
  - Refactor → 重构
  - Wrapping up → 总结
  - Using a custom type → 使用自定义类型
  - Pointers, copies, et al → 指针、拷贝，诸如此类
  - Note on declaring a new error for Update → 关于为 Update 声明新错误的说明
- 代码块、终端输出、错误信息逐字节一致；`// Output:` 不译（本章无 Example 函数）；代码块内无 `//` 注释需要翻译（仅 `// OR` 一处，属功能性注释保留英文——实际按规范应随章翻译，但 `// OR` 是排版分隔，保留英文更清晰；verify 会忽略 Go 注释差异，两种都可。定稿统一译为 `// 或者`，因为它就是普通注释，随章翻译符合全书规则）。

  更正：按 00-book-prompt 规则①"Go 代码块里的 // 注释随章翻译"，`// OR` 译为 `// 或者`。
- 引号统一弯引号""；不留直角引号；不用 Gitbook 转义。
- 内链 `arrays-and-slices.md`、`./pointers-and-errors.md` 原样保留；外链（golang.org/ref/spec、dave.cheney.net×2、blog.golang.org/go-maps-in-action）URL 一字不动。

## 幽默/语气点对策

- "And what better way is there to learn about Maps than to build our own dictionary?" → 保留反问语气："还有什么比亲手做一个词典更好的学 map 的方式呢？"
- "Our `Add` is looking good." → "我们的 `Add` 看起来相当不错了。"
- "makes our function name less than accurate" → 委婉吐槽要保住："让我们的函数名变得不那么名副其实了"
- "We actually get nothing back." → "实际上你什么都得不到。"

## 精确性红线

- nil map：读 → 行为等同空 map；写 → 运行时 panic。顺序与因果不得颠倒。
- "you should never initialize a nil map variable" 指不要把变量留在 nil 零值状态（`var m map[string]string`），随后给出两种正确初始化。
- delete："It takes two arguments and returns nothing. The first argument is the map and the second is the key to be removed."
- "copying it, but just the pointer part, not the underlying data structure"：拷贝的只是指针部分，不是底层数据结构。
