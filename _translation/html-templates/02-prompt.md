# 02 — 本章特有约束

## 标题与加注
- H1：`HTML 模板`（任务指定）
- 章首代码链接沿用样章句式：**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/blogrenderer)**
- 首现加注（一次）：审批测试（Approval Tests）、视图模型（view model）、无逻辑（logic-less）、嵌入（embed）、上帝对象（God Object）、非导出（unexported）、黄金文件（golden files）、快照测试、转义、代码注入、静态站点生成器、组合测试（Combinatorial Testing）
- 不再加注：关注点分离、依赖注入、基准测试、切片、结构体、接口、方法（前章已注）
- 包名 `html/template`、`text/template`，类型 `template.Template`、`template.HTML`、`embed.FS`，标识符 `sanitiseTitle`/`SanitisedTitle`/`postViewModel`/`newPostVM`/`FuncMap`/`io.Discard`/`b.Loop()` 一律保留英文 + 反引号
- Mustache、Hotwire、Gopher 保留英文

## TDD 循环标题（与前章统一）
- Write the test first → 先写测试
- Try to run the test → 试着运行测试
- Write the minimal amount of code for the test to run and check the failing test output → 写最少的代码让测试能运行，并检查失败的测试输出
- Write enough code to make it pass → 写足够的代码让测试通过
- Refactor → 重构；出现多轮，措辞一致；Wrapping up → 总结

其余标题：
- What we're going to build → 我们要构建什么
- Introducing templates → 初识模板；Back to the code → 回到代码；More refactoring → 继续重构；Embed? → 关于 embed
- Next: Make the template "nice" → 下一步：把模板弄"好看"些
- Introducing Approval Tests → 初识审批测试（Approval Tests）
- Are we still doing TDD? → 我们还算在做 TDD 吗？
- Expand the markup → 扩充标记
- An excuse to mess around with Benchmarking → 一个玩玩基准测试的借口
- Back to the real work → 回到正事
- On testing 3rd-party libraries → 聊聊第三方库的测试
- Render index → 渲染索引页
- Passing functions into templates → 向模板传入函数
- Separating concerns → 关注点分离
- Rendering the markdown body → 渲染 markdown 正文
- What we've learned → 本章收获
- On logic-less templates → 再聊无逻辑模板
- Not just for HTML → 不只用于 HTML
- References and further material → 参考资料与延伸阅读

## 代码与输出
- 39 个代码块与原文逐字节一致（含 tab、空行、`handlebars`/`markdown` 语言标记、无标记输出块）
- 唯一可翻译的 `//` 注释在第 5 块：`// if you're continuing from the read files chapter, you shouldn't redefine this` → `// 如果你在接着"读取文件"一章继续写，就不需要重新定义这个`
- `//go:embed "templates/*"` 是编译器指令（共 3 处），不是注释，一字不动
- 模板动作 `{{.}}`、`{{.Title}}`、`{{range .Tags}}`、`{{define "top"}}`、`{{template "top" .}}`、`{{sanitiseTitle .Title}}` 等全部原样
- 输出怪样不改：`<li></li>`、缺 `--- FAIL` 尾行、`\"` 转义、`Hello%20World`、`22124 53812 ns/op`

## 格式
- `_..._` 与 `*...*` 统一为 `*...*`；**Yikes**、**Tests give us space to think**、**don't go against the grain**、**unexported** 等加粗一一对应
- 引文（html/template 包文档、embed 包文档、go-approval-tests README、template.HTML 文档）译成中文，引文内 URL/代码名原样
- 弯引号""，禁用「」；中英之间加空格
- 图片：仅 1 张外链 `https://i.imgur.com/0MoNdva.png`，URL 原样保留（本章无 .gitbook 图片需要拷贝）
- 章内链接目标保持上游：`/reading-files.md`、`reading-files.md`、`./dependency-injection.md`；正文提及 reading-files 章用「读取文件」

## 风格
- conversational，幽默保真对策：
  - "the latest flavour of the month frontend framework built upon gigabytes of transpiled JavaScript, working with a Byzantine build system" → 时下最流行的那款前端框架、动辄几个 G 的转译 JavaScript、外加一套拜占庭式的构建系统
  - "**Yikes**. Not the nicest code i've written" → **好家伙**。这不是我写过的最好看的代码（i've 小写是原文随意，中文不必体现）
  - "An excuse to mess around with Benchmarking" → 一个玩玩基准测试的借口（自嘲保住）
  - "don't go against the grain" → 别逆着纹理来（木工比喻，与"顺着工具的天性"呼应）
  - "grease the wheels of rendering" → 给渲染这台机器上点润滑油
  - "Tests give us space to think" → 测试给了我们思考的空间
- 技术准确性：`template.HTML` 的安全语义、转义行为、`ExecuteTemplate` 与 `Execute` 的区别、`ParseFS` 一次解析多处复用、gomarkdown parser 不可复用的原因——不添不减
