# 02 — io 章翻译约束

## 术语与定名

- `io.Reader` / `io.Writer` / `io.ReadSeeker` / `io.ReadWriteSeeker` / `Seeker`：接口名一律保留英文；正文叙述用"`Reader` 接口""`ReadSeeker`"等，与依赖注入章（io.Writer 行文）一致。
- 嵌入：首现写"嵌入（embedding）"。
- 集成测试：首现写"集成测试（integration test）"。
- 多态：首现写"多态（polymorphism）"。
- 技术债、临时文件、截断、正常路径（术语表既有）。
- 产品负责人（product owner）——沿用 app-intro。
- `Tape`、`League`、`FileSystemPlayerStore` 等代码名一律不译。
- "red state" → "红灯状态"，配合"尽快让软件跑起来"的语境，可点一句 TDD 的红/绿。

## 标题定式（沿用全书）

- `## The code so far` → `## 目前的代码`
- `## Store the data` → `## 存储数据`
- `## Write the test first` → `## 先写测试`
- `## Try to run the test` → `## 试着运行测试`
- `## Write the minimal amount of code for the test to run and check the failing test output` → `## 写最少的代码让测试能运行，并检查失败的测试输出`
- `## Write enough code to make it pass` → `## 写足够的代码让测试通过`
- `## Refactor` → `## 重构`
- `### Seeking problems` → `### 寻位的问题`（Seek 双关，正文点明）
- `### Another problem` → `### 又一个问题`
- `## More refactoring and performance concerns` → `## 更多重构与性能考量`
- `## Didn't we just break some rules there? Testing private things? No interfaces?` → `## 我们这不是刚坏了规矩吗？测试私有类型？不用接口？`
- `## Error handling` → `## 错误处理`
- `## Sorting` → `## 排序`
- `## Wrapping up` → `## 总结`

## 代码块纪律

1. 64 个代码块一一对应，非 Go 块逐字节一致；Go 块仅译 `//` 注释。
2. 需译注释清单：块 1（server.go）的 4 条 doc 注释；`// read again` ×2 → `// 再读一次`；`//etc...` → `// 等等……`。
3. `//server.go`、`//file_system_store.go`、`//league.go`、`//tape.go`、`//tape_test.go`、`//file_system_store_test.go`、`//server_integration_test.go`、`// main.go` 等文件名提示注释保留原样（与 http-server 章约定一致）。
4. 无 `// Output:` 注释。

## 其他

- `[In the previous chapter](json.md)` → `[上一章](https://github.com/quii/learn-go-with-tests/blob/main/json.md)（英文原版）`（json 章未译出；app-intro 已用同款格式）。
- 无图片；全部外链原样保留。
- 排序稳定性：原文只用了 `sort.Slice`，未提 `SliceStable`，译文不得引入原文没有的内容（前向引用规则禁止添油加醋）。
- 弯引号""，禁用「」；中文与代码/英文间加空格。
