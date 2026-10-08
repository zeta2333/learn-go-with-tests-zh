# HTML 模板

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/blogrenderer)**

我们活在一个这样的时代：人人都想用时下最流行的那款前端框架构建 Web 应用，脚下垫着几个 G 的转译 JavaScript，手里还得伺候一套拜占庭式的构建系统；[但也许这并非总是必要的](https://quii.dev/The_Web_I_Want)。

我敢说，大多数 Go 开发者都看重简单、稳定、快速的工具链，可惜前端世界在这方面老是掉链子。

很多网站根本不需要做成 [SPA](https://en.wikipedia.org/wiki/Single-page_application)（单页应用）。**HTML 和 CSS 是呈现内容的绝佳方式**，而你完全可以用 Go 写个网站来输出 HTML。

如果还想要一些动态元素，可以撒一点客户端 JavaScript 进去，或者试试 [Hotwire](https://hotwired.dev)——它让你用服务端的思路做出动态体验。

你当然可以在 Go 里把 [`fmt.Fprintf`](https://pkg.go.dev/fmt#Fprintf) 玩出花来生成 HTML，但本章你会看到：Go 标准库自带一些工具，能以更简单、更好维护的方式生成 HTML。你还会学到几种测试这类代码的高效办法，也许是你以前没遇到过的。

## 我们要构建什么

在[读取文件](/reading-files.md)一章里，我们写过一段代码：接收一个 [`fs.FS`](https://pkg.go.dev/io/fs)（也就是文件系统），为它遇到的每个 markdown 文件各返回一个 `Post`，组成切片。

```go
posts, err := blogposts.NewPostsFromFS(os.DirFS("posts"))
```

当时的 `Post` 是这么定义的：

```go
type Post struct {
	Title, Description, Body string
	Tags                     []string
}
```

下面是一个能被解析的 markdown 文件示例：

```markdown
Title: Welcome to my blog
Description: Introduction to my blog
Tags: cooking, family, live-laugh-love
---
# First recipe!
Welcome to my **amazing recipe blog**. I am going to write about my family recipes, and make sure I write a long, irrelevant and boring story about my family before you get to the actual instructions.
```

如果在"写博客软件"这条路上继续走下去，我们就会拿这些数据生成 HTML，交给 Web 服务器，在收到 HTTP 请求时返回。

就我们的博客而言，要生成两种页面：

1. **查看文章**。渲染某一篇文章。`Post` 的 `Body` 字段是一个含有 markdown 的字符串，所以需要把它转换成 HTML。
2. **索引**。列出所有文章，并附上查看具体文章的超链接。

我们还希望全站观感一致，所以每个页面都得配上那些常规的 HTML"家具"，比如 `<html>`、还有装着 CSS 样式表链接和我们想要的其他东西的 `<head>`。

写博客软件时，如何构建 HTML、如何把它送到用户的浏览器上，做法上有好几种选择。

我们会把代码设计成接收一个 `io.Writer`。这样一来，调用我们代码的人就有了灵活的余地：

- 写入 [os.File](https://pkg.go.dev/os#File)，这样就能以静态文件的方式对外提供
- 直接把 HTML 写到 [`http.ResponseWriter`](https://pkg.go.dev/net/http#ResponseWriter)
- 或者随便写到什么东西里都行！只要实现了 `io.Writer`，使用者就能从一个 `Post` 生成 HTML

## 先写测试

老规矩，先别一头扎进去，想想需求。这么一大坨需求，怎么拆成一个够小、够得着、能让我们专注的步骤呢？

在我看来，"真的能看到内容"比索引页优先级更高。没有索引页，我们也照样能发布产品，直接分享指向精彩内容的链接。一个没法链到正文的索引页没什么用。

不过，按前文说的那样渲染一篇文章，感觉还是块头不小：一堆 HTML 家具、把正文 markdown 转成 HTML、列出标签，等等。

到了这一步，我还不怎么在乎具体标记长什么样，轻松的第一步是先确认能把文章标题渲染成 `<h1>`。这*感觉上*就是能让我们往前挪一小步的最小第一步。

```go
package blogrenderer_test

import (
	"bytes"
	"github.com/quii/learn-go-with-tests/blogrenderer"
	"testing"
)

func TestRender(t *testing.T) {
	var (
		aPost = blogrenderer.Post{
			Title:       "hello world",
			Body:        "This is a post",
			Description: "This is a description",
			Tags:        []string{"go", "tdd"},
		}
	)

	t.Run("it converts a single post into HTML", func(t *testing.T) {
		buf := bytes.Buffer{}
		err := blogrenderer.Render(&buf, aPost)

		if err != nil {
			t.Fatal(err)
		}

		got := buf.String()
		want := `<h1>hello world</h1>`
		if got != want {
			t.Errorf("got '%s' want '%s'", got, want)
		}
	})
}
```

接收 `io.Writer` 的决定也让测试变简单了：这里我们写进一个 [`bytes.Buffer`](https://pkg.go.dev/bytes#Buffer)，之后检查它的内容就行。

## 试着运行测试

如果你已经读过本书前面的章节，这套动作现在应该练得很熟了。眼下测试还跑不起来，因为包还没定义，`Render` 函数也不存在。自己照着编译器的提示一步步来，直到测试能跑、并带着一条清晰的消息失败为止。

亲手让测试失败这件事真的很重要。等到六个月后你不小心把测试弄挂时，你会庆幸自己*现在*下过功夫：确认过它失败时给出的消息足够清晰。

## 写最少的代码让测试能运行，并检查失败的测试输出

这是让测试能跑起来的最少代码：

```go
package blogrenderer

// 如果你在接着"读取文件"一章继续写，就不需要重新定义这个
type Post struct {
	Title, Description, Body string
	Tags                     []string
}

func Render(w io.Writer, p Post) error {
	return nil
}
```

测试应该会抱怨：空字符串不等于我们想要的值。

## 写足够的代码让测试通过

```go
func Render(w io.Writer, p Post) error {
	_, err := fmt.Fprintf(w, "<h1>%s</h1>", p.Title)
	return err
}
```

记住，软件开发本质上是一种学习活动。想边干边有所发现、有所学习，我们的工作方式就必须提供频繁、高质量的反馈循环，而最简单的办法就是小步前进。

所以眼下我们不折腾任何模板库。用"普通"的字符串拼装照样能生成 HTML；跳过模板这一步，我们既验证了一小块有用的行为，也顺手为这个包的 API 做了一点点设计。

## 重构

还没什么可重构的，进入下一轮迭代吧。

## 先写测试

现在最基本的版本已经能跑了，接下来迭代测试、扩充功能。这次要渲染 `Post` 里更多的信息。

```go
	t.Run("it converts a single post into HTML", func(t *testing.T) {
		buf := bytes.Buffer{}
		err := blogrenderer.Render(&buf, aPost)

		if err != nil {
			t.Fatal(err)
		}

		got := buf.String()
		want := `<h1>hello world</h1>
<p>This is a description</p>
Tags: <ul><li>go</li><li>tdd</li></ul>`

		if got != want {
			t.Errorf("got '%s' want '%s'", got, want)
		}
	})
```

注意，写这个东西*感觉很*别扭。在测试里看到这么一大坨标记就够难受了，而这还没算上正文，也没算上我们真正想要的那些 HTML——`<head>` 里的内容，以及各种需要的页面家具。

尽管如此，先忍一忍，*暂时*受着这份痛。

## 试着运行测试

它应该会失败，抱怨拿到的字符串不符合预期，因为我们还没渲染 description 和 tags。

## 写足够的代码让测试通过

建议自己动手试试，别照抄代码。你会发现，让这个测试通过*有点烦人*！我自己试的时候，第一版就报出了这样的错误：

```
=== RUN   TestRender
=== RUN   TestRender/it_converts_a_single_post_into_HTML
    renderer_test.go:32: got '<h1>hello world</h1><p>This is a description</p><ul><li>go</li><li>tdd</li></ul>' want '<h1>hello world</h1>
        <p>This is a description</p>
        Tags: <ul><li>go</li><li></li></ul>'
```

换行符！谁在乎啊？呃，我们的测试就在乎，因为它在匹配一个精确的字符串值。它该这么较真吗？为了先让测试通过，我暂时把换行符去掉了。

```go
func Render(w io.Writer, p Post) error {
	_, err := fmt.Fprintf(w, "<h1>%s</h1>\n<p>%s</p>\n", p.Title, p.Description)
	if err != nil {
		return err
	}

	_, err = fmt.Fprint(w, "Tags: <ul>")
	if err != nil {
		return err
	}

	for _, tag := range p.Tags {
		_, err = fmt.Fprintf(w, "<li>%s</li>", tag)
		if err != nil {
			return err
		}
	}

	_, err = fmt.Fprint(w, "</ul>")
	if err != nil {
		return err
	}

	return nil
}
```

**好家伙**。这不是我写过的最好看的代码，而我们的标记其实还处在最最初级的实现阶段。页面后面还需要塞进多得多的内容和元素——很快就能看出，这个思路不合适。

但关键在于：我们有一个通过的测试，我们有了能工作的软件。

## 重构

有了"代码能工作、测试通过"这张安全网，就可以在重构阶段考虑换一种实现思路了。

### 初识模板

Go 有两个模板包：[text/template](https://pkg.go.dev/text/template) 和 [html/template](https://pkg.go.dev/html/template)，二者共用同一套接口。它们做的事情，都是把一个模板和一些数据合在一起，产出一个字符串。

那 HTML 版的差别在哪儿？

> html/template 包实现了数据驱动的模板，用于生成可防御代码注入（code injection）的 HTML 输出。它提供与 text/template 包相同的接口；只要输出是 HTML，就应当用它替代 text/template。

这种模板语言跟 [Mustache](https://mustache.github.io) 非常像，让你能用干净的方式动态生成内容，关注点分离也做得很漂亮。跟你可能用过的其他模板语言相比，它非常克制，用 Mustache 的话说就是"无逻辑"（logic-less）。这是一个重要的、**而且是刻意为之**的设计决定。

虽然本章聚焦在生成 HTML 上，但如果你的项目里满是复杂的字符串拼接和咒语一样的代码，也可以拿起 `text/template` 来整理你的代码。

### 回到代码

下面就是我们博客的模板：

`<h1>{{.Title}}</h1><p>{{.Description}}</p>Tags: <ul>{{range .Tags}}<li>{{.}}</li>{{end}}</ul>`

这个字符串放哪儿定义呢？选择有好几种，但为了保持小步走，先从一个普普通通的字符串开始：

```go
package blogrenderer

import (
	"html/template"
	"io"
)

const (
	postTemplate = `<h1>{{.Title}}</h1><p>{{.Description}}</p>Tags: <ul>{{range .Tags}}<li>{{.}}</li>{{end}}</ul>`
)

func Render(w io.Writer, p Post) error {
	templ, err := template.New("blog").Parse(postTemplate)
	if err != nil {
		return err
	}

	return templ.Execute(w, p)
}
```

我们创建一个带名字的新模板，然后解析模板字符串。接着就能调用它的 `Execute` 方法，把数据传进去——这里是 `Post`。

模板会把 `{{.Description}}` 这类占位替换成 `p.Description` 的内容。模板还提供了一些编程原语，比如用来遍历的 `range` 和条件判断的 `if`。更多细节见 [text/template 文档](https://pkg.go.dev/text/template)。

*这应该是一次纯重构。*测试不需要任何改动，而且应该继续通过。重要的是，代码更好读了，要应付的烦人错误处理也少了一大截。

大家常常抱怨 Go 的错误处理啰嗦，但你可能会发现：更好的路子是换一种写法，让代码从一开始就不容易出错——就像这里这样。

### 继续重构

用上 `html/template` 无疑是进步，但把它作为字符串常量放在代码里并不理想：

- 还是挺难读。
- 对 IDE/编辑器不友好：没有语法高亮，没法重新排版、重构，等等。
- 它看着像 HTML，却没法像"正常"的 HTML 文件那样去编辑它。

我们想做的是让模板住进单独的文件里：这样能更好地组织它们，也能像对待 HTML 文件一样对待它们。

建一个名为 "templates" 的文件夹，在里面创建 `blog.gohtml`，把我们的模板粘贴进去。

然后改一下代码，用 [Go 1.16 自带的嵌入（embed）功能](https://pkg.go.dev/embed)把文件系统嵌进来：

```go
package blogrenderer

import (
	"embed"
	"html/template"
	"io"
)

var (
	//go:embed "templates/*"
	postTemplates embed.FS
)

func Render(w io.Writer, p Post) error {
	templ, err := template.ParseFS(postTemplates, "templates/*.gohtml")
	if err != nil {
		return err
	}

	return templ.Execute(w, p)
}
```

把一个"文件系统"嵌进代码后，我们就能加载多个模板并自由组合。等想在不同模板之间共享渲染逻辑时——比如 HTML 页面顶部的页头（header）和页脚（footer）——这就派上用场了。

### 关于 embed

embed 在[读取文件](reading-files.md)一章里被简单带过。标准库的[文档解释道](https://pkg.go.dev/embed)：

> embed 包提供了对嵌入 Go 程序中的文件的访问。
>
> 导入 "embed" 的 Go 源文件可以使用 `//go:embed` 指令，在编译期用从包目录或其子目录读取的文件内容，来初始化类型为 string、[]byte 或 FS 的变量。

我们为什么想用它？其实，我们*可以*从"普通"文件系统加载模板。但那就得保证：无论这个软件部署到哪里，模板都待在正确的路径上。工作中你可能有好几套环境——开发、预发、线上。要让这条路走得通，你就得保证模板被拷到了正确的位置。

用 embed 的话，文件在构建（build）时就打包进了你的 Go 程序。也就是说，程序一旦构建完成（构建本来也只该做一次），这些文件就永远随叫随到。

方便的是，不但能嵌入单个文件，还能嵌入整个文件系统；而且这个文件系统实现了 [io/fs](https://pkg.go.dev/io/fs)，也就是说你的代码不必关心自己在跟哪种文件系统打交道。

不过，如果你想依据配置使用不同的模板，那可能还是沿用传统方式、从磁盘加载模板更合适。

## 下一步：把模板弄"好看"些

我们其实不想让模板挤成一行字符串。我们想把它摊开来，让它更好读、更好改，就像这样：

```handlebars
<h1>{{.Title}}</h1>

<p>{{.Description}}</p>

Tags: <ul>{{range .Tags}}<li>{{.}}</li>{{end}}</ul>
```

可一旦这么做，测试就挂了。因为我们的测试期望返回一个非常特定的字符串。

可说实话，我们在乎的根本不是空白字符。如果每回对标记做一点小改动，都得费劲巴拉地去更新断言字符串，维护这个测试会变成一场噩梦。随着模板越长越大，这类修改会越来越难驾驭，工作成本也会螺旋失控。

## 初识审批测试（Approval Tests）

[Go Approval Tests](https://github.com/approvals/go-approval-tests)

> ApprovalTests 让你可以轻松地测试较大的对象、字符串，以及任何能存进文件的东西（图片、声音、CSV 等等……）

思路类似于"黄金文件"（golden files），或快照测试（snapshot testing）。不必在测试文件里尴尬地维护一长串字符串，审批工具会替你把输出与你创建的"approved"文件做比对。如果你认可新版本，把它拷贝过去就行。重跑测试，又回到绿色。

在项目里添加依赖 `"github.com/approvals/go-approval-tests"`（命令是 `go get github.com/approvals/go-approval-tests`），然后把测试改成下面这样：

```go
func TestRender(t *testing.T) {
	var (
		aPost = blogrenderer.Post{
			Title:       "hello world",
			Body:        "This is a post",
			Description: "This is a description",
			Tags:        []string{"go", "tdd"},
		}
	)

	t.Run("it converts a single post into HTML", func(t *testing.T) {
		buf := bytes.Buffer{}

		if err := blogrenderer.Render(&buf, aPost); err != nil {
			t.Fatal(err)
		}

		approvals.VerifyString(t, buf.String())
	})
}
```

第一次运行它会失败，因为我们还没批准过任何东西：

```
=== RUN   TestRender
=== RUN   TestRender/it_converts_a_single_post_into_HTML
    renderer_test.go:29: Failed Approval: received does not match approved.
```

它会创建两个文件，长得像下面这样：

- `renderer_test.TestRender.it_converts_a_single_post_into_HTML.received.txt`
- `renderer_test.TestRender.it_converts_a_single_post_into_HTML.approved.txt`

received 文件里是新的、尚未批准的输出。把它拷进空着的 approved 文件，再重跑测试。

拷贝新版本这个动作，就等于你"批准"了这次改动，测试随之通过。

想看看这套工作流怎么转，就按前面讨论的那样把模板改得易读一些（语义上完全没变）：

```handlebars
<h1>{{.Title}}</h1>

<p>{{.Description}}</p>

Tags: <ul>{{range .Tags}}<li>{{.}}</li>{{end}}</ul>
```

重跑测试。由于代码输出与已批准的版本不同，会生成一个新的"received"文件。看看这两个文件，如果对改动满意，把新版本拷过去，再重跑测试即可。记得把 approved 文件 commit 进版本控制。

这套做法让管理 HTML 这种又大又丑的东西的改动简单得多。你可以用 diff 工具查看和管理差异，测试代码也更干净。

![用 diff 工具管理改动](https://i.imgur.com/0MoNdva.png)

这其实只是审批测试一个相当小的用法，它可是你测试武器库里一件极其趁手的工具。[Emily Bache](https://twitter.com/emilybache) 有一个[很有意思的视频：她用审批测试给一个零测试的复杂代码库添加了一套覆盖面惊人的测试](https://www.youtube.com/watch?v=zyM2Ep28ED8)。她提到的"组合测试"（Combinatorial Testing）绝对值得研究研究。

有了这次改动，代码测试充分的好处我们照单全收，而以后折腾标记时，测试也不会再过多碍事。

### 我们还算在做 TDD 吗？

这种做法有个有趣的副作用：它把我们带离了 TDD。你当然*可以*手动把 approved 文件编辑成你想要的样子，跑一遍测试，然后修模板，让它输出你定义的内容。

但那也太傻了！TDD 是一种干活的方法，确切地说是一种设计的方法；这不意味着做**任何事**都得教条地套用它。

重要的是，我们做对了该做的事：把 TDD 当作**设计工具**，设计出了这个包的 API。至于改模板，我们的流程可以是：

- 对模板做一点小改动
- 跑审批测试
- 目测输出，确认长得对
- 批准
- 重复

小步快跑、每步都能达成的工作方式，它的价值仍然不能丢。想办法让每次改动小一点，不断重跑测试，让自己手头的事能拿到真实反馈。

如果开始动模板*_周围_*的代码，那当然可能就该回到 TDD 的工作方法了。

## 扩充标记

大多数网站的 HTML 都比我们现在的丰富。起码得有个 `html` 元素，配上 `head`，或许还要些 `nav`。通常也少不了页脚（footer）。

如果网站会有不同的页面，我们就希望这些东西只定义一处，让全站观感保持一致。Go 模板支持我们定义一些"小节"，供其他模板导入。

改一下现有模板，导入 top 和 bottom 两个模板：

```handlebars
{{template "top" .}}
<h1>{{.Title}}</h1>

<p>{{.Description}}</p>

Tags: <ul>{{range .Tags}}<li>{{.}}</li>{{end}}</ul>
{{template "bottom" .}}
```

然后创建 `top.gohtml`，内容如下：

```handlebars
{{define "top"}}
<!DOCTYPE html>
<html lang="en">
<head>
    <title>My amazing blog!</title>
    <meta charset="UTF-8"/>
    <meta name="description" content="Wow, like and subscribe, it really helps the channel guys" lang="en"/>
</head>
<body>
<nav role="navigation">
    <div>
        <h1>Budding Gopher's blog</h1>
        <ul>
            <li><a href="/">home</a></li>
            <li><a href="about">about</a></li>
            <li><a href="archive">archive</a></li>
        </ul>
    </div>
</nav>
<main>
{{end}}
```

还有 `bottom.gohtml`：

```handlebars
{{define "bottom"}}
</main>
<footer>
    <ul>
        <li><a href="https://twitter.com/quii">Twitter</a></li>
        <li><a href="https://github.com/quii">GitHub</a></li>
    </ul>
</footer>
</body>
</html>
{{end}}
```

（当然，想放什么标记随你！）

现在我们需要指定具体执行哪个模板。在博客渲染器里，把 `Execute` 换成 `ExecuteTemplate`：

```go
if err := templ.ExecuteTemplate(w, "blog.gohtml", p); err != nil {
	return err
}
```

重跑测试。应该会生成一个新的"received"文件，测试失败。检查一下，满意的话，把它拷贝覆盖旧版本，即为批准。再重跑测试，应该就通过了。

## 一个玩玩基准测试的借口

继续推进之前，先想想我们的代码现在都干了些什么：

```go
func Render(w io.Writer, p Post) error {
	templ, err := template.ParseFS(postTemplates, "templates/*.gohtml")
	if err != nil {
		return err
	}

	return templ.ExecuteTemplate(w, "blog.gohtml", p)
}
```

- 解析模板
- 用模板把一篇文章渲染到一个 `io.Writer`

虽然在大多数场景下，每篇文章都重新解析模板带来的性能影响相当可以忽略，但*不*这么做的功夫同样可以忽略，而且还能顺手让代码整洁一点。

想看看不用一遍遍解析能有多大影响，可以用基准测试工具量一量我们的函数有多快。

```go
func BenchmarkRender(b *testing.B) {
	var (
		aPost = blogrenderer.Post{
			Title:       "hello world",
			Body:        "This is a post",
			Description: "This is a description",
			Tags:        []string{"go", "tdd"},
		}
	)

	for b.Loop() {
		blogrenderer.Render(io.Discard, aPost)
	}
}
```

在我的电脑上，结果是这样的：

```
BenchmarkRender-8 22124 53812 ns/op
```

为了不再一遍又一遍地重新解析模板，我们来创建一个类型，让它持有解析好的模板，并提供一个负责渲染的方法：

```go
type PostRenderer struct {
	templ *template.Template
}

func NewPostRenderer() (*PostRenderer, error) {
	templ, err := template.ParseFS(postTemplates, "templates/*.gohtml")
	if err != nil {
		return nil, err
	}

	return &PostRenderer{templ: templ}, nil
}

func (r *PostRenderer) Render(w io.Writer, p Post) error {
	return r.templ.ExecuteTemplate(w, "blog.gohtml", p)
}
```

这确实改动了代码的接口，所以得更新测试：

```go
func TestRender(t *testing.T) {
	var (
		aPost = blogrenderer.Post{
			Title:       "hello world",
			Body:        "This is a post",
			Description: "This is a description",
			Tags:        []string{"go", "tdd"},
		}
	)

	postRenderer, err := blogrenderer.NewPostRenderer()

	if err != nil {
		t.Fatal(err)
	}

	t.Run("it converts a single post into HTML", func(t *testing.T) {
		buf := bytes.Buffer{}

		if err := postRenderer.Render(&buf, aPost); err != nil {
			t.Fatal(err)
		}

		approvals.VerifyString(t, buf.String())
	})
}
```

还有我们的基准测试：

```go
func BenchmarkRender(b *testing.B) {
	var (
		aPost = blogrenderer.Post{
			Title:       "hello world",
			Body:        "This is a post",
			Description: "This is a description",
			Tags:        []string{"go", "tdd"},
		}
	)

	postRenderer, err := blogrenderer.NewPostRenderer()

	if err != nil {
		b.Fatal(err)
	}

	for b.Loop() {
		postRenderer.Render(io.Discard, aPost)
	}
}
```

测试应该继续通过。那基准测试呢？

`BenchmarkRender-8 362124 3131 ns/op`。之前的 ns/op 是 `53812 ns/op`，进步相当可观！以后再添加别的渲染方法——比如说索引页——代码也会更简洁，因为模板解析不用重复写了。

## 回到正事

就渲染文章而言，还剩的重要部分就是真正渲染 `Body` 了。还记得吗，那应该是作者写下的 markdown，所以需要转换成 HTML。

这就留给你——亲爱的读者——当作业吧。你应该能找到一个 Go 库来代劳。用审批测试来验证你做的事。

### 聊聊第三方库的测试

**注意**。别太执着于在单元测试里显式地测第三方库的行为。

给不归你控制的代码写测试是浪费，还会增加维护负担。有时你或许想用[依赖注入](./dependency-injection.md)来控制某个依赖，并在测试里 mock 它的行为。

不过就本例而言，我把"markdown 转 HTML"视为渲染的一个实现细节，审批测试给我们的信心已经足够了。

### 渲染索引页

我们要做的下一个功能是渲染索引页（Index），把文章列成 HTML 有序列表（ordered list）。

这次是在扩展我们的 API，所以该把 TDD 的帽子重新戴上了。

## 先写测试

索引页表面上看起来简单，但写测试仍会促使我们做出一些设计抉择：

```go
t.Run("it renders an index of posts", func(t *testing.T) {
	buf := bytes.Buffer{}
	posts := []blogrenderer.Post{{Title: "Hello World"}, {Title: "Hello World 2"}}

	if err := postRenderer.RenderIndex(&buf, posts); err != nil {
		t.Fatal(err)
	}

	got := buf.String()
	want := `<ol><li><a href="/post/hello-world">Hello World</a></li><li><a href="/post/hello-world-2">Hello World 2</a></li></ol>`

	if got != want {
		t.Errorf("got %q want %q", got, want)
	}
})
```

1. 我们拿 `Post` 的标题字段当作 URL 路径的一部分，但 URL 里不太想出现空格，所以把空格替换成连字符。
2. 我们给 `PostRenderer` 添加了一个 `RenderIndex` 方法，同样接收一个 `io.Writer` 和一个 `Post` 切片。

要是这里我们固守"事后补测试 + 审批测试"的路子，就没法在一个可控的环境里回答这些问题。**测试给了我们思考的空间**。

## 试着运行测试

```
./renderer_test.go:41:13: undefined: blogrenderer.RenderIndex
```

## 写最少的代码让测试能运行，并检查失败的测试输出

```go
func (r *PostRenderer) RenderIndex(w io.Writer, posts []Post) error {
	return nil
}
```

上面的代码应该会带来这样的测试失败：

```
=== RUN   TestRender
=== RUN   TestRender/it_renders_an_index_of_posts
    renderer_test.go:49: got "" want "<ol><li><a href=\"/post/hello-world\">Hello World</a></li><li><a href=\"/post/hello-world-2\">Hello World 2</a></li></ol>"
--- FAIL: TestRender (0.00s)
```

## 写足够的代码让测试通过

虽然*感觉上*这事应该挺容易，实际却有点别扭。我是分几步做完的：

```go
func (r *PostRenderer) RenderIndex(w io.Writer, posts []Post) error {
	indexTemplate := `<ol>{{range .}}<li><a href="/post/{{.Title}}">{{.Title}}</a></li>{{end}}</ol>`

	templ, err := template.New("index").Parse(indexTemplate)
	if err != nil {
		return err
	}

	if err := templ.Execute(w, posts); err != nil {
		return err
	}

	return nil
}
```

一开始我不想折腾单独的模板文件，只想让它先跑起来。把模板提前解析、分离出去，这些我都视为以后可以再做的重构。

这一版还过不了，但已经很接近了：

```
=== RUN   TestRender
=== RUN   TestRender/it_renders_an_index_of_posts
    renderer_test.go:49: got "<ol><li><a href=\"/post/Hello%20World\">Hello World</a></li><li><a href=\"/post/Hello%20World%202\">Hello World 2</a></li></ol>" want "<ol><li><a href=\"/post/hello-world\">Hello World</a></li><li><a href=\"/post/hello-world-2\">Hello World 2</a></li></ol>"
--- FAIL: TestRender (0.00s)
    --- FAIL: TestRender/it_renders_an_index_of_posts (0.00s)
```

可以看到，模板代码把 `href` 属性里的空格转义（escape）掉了。我们需要一种办法把字符串里的空格替换成连字符。又不能直接遍历 `[]Post` 在内存里做替换，因为链接文本（锚文本）里的空格，我们还是想原样展示给用户。

办法有好几个。先来探索第一个：往模板里传函数。

### 向模板传入函数

```go
func (r *PostRenderer) RenderIndex(w io.Writer, posts []Post) error {
	indexTemplate := `<ol>{{range .}}<li><a href="/post/{{sanitiseTitle .Title}}">{{.Title}}</a></li>{{end}}</ol>`

	templ, err := template.New("index").Funcs(template.FuncMap{
		"sanitiseTitle": func(title string) string {
			return strings.ToLower(strings.Replace(title, " ", "-", -1))
		},
	}).Parse(indexTemplate)
	if err != nil {
		return err
	}

	if err := templ.Execute(w, posts); err != nil {
		return err
	}

	return nil
}
```

*在解析模板之前*，你可以往模板里加一个 `template.FuncMap`，它让你定义能在模板内部调用的函数。这里我们定义了一个 `sanitiseTitle` 函数，然后在模板里用 `{{sanitiseTitle .Title}}` 调用它。

这是个强大的特性。能往模板里传函数，你就能玩出很多很酷的花样，可是，该吗？回到 Mustache 和无逻辑模板的原则：他们为什么倡导无逻辑？**模板里有逻辑到底有什么问题？**

就像前面展示的，为了测试模板，*我们不得不引入一种完全不同类型的测试*。

想象一下，你往模板里引入了一个函数，它有几种不同的行为分支和一堆边界情况，**你要怎么测它**？按当前的设计，你测这段逻辑的唯一手段就是*渲染 HTML 然后比较字符串*。这不是什么轻松或理智的逻辑测试方式，*_重要的_*业务逻辑更不该这么测。

尽管审批测试技术降低了维护这些测试的成本，它们仍然比你会写的大多数单元测试更昂贵。它们对标记的任何细微改动依然敏感，只不过我们让这种敏感变得更容易管理了。我们仍然要努力架构代码，让自己不必围绕模板写很多测试；并尽力做好关注点分离——凡是不必住在渲染代码里的逻辑，都妥妥地分出去。

受 Mustache 影响的模板引擎给了你一个有用的约束，别老想着绕开它；**别逆着纹理来**。相反，拥抱[视图模型](https://stackoverflow.com/a/11074506/3193)（view model）的思路：构造一些专用类型，里面装着渲染所需的数据，并且装成模板语言用起来方便的样子。

这样一来，生成那包数据的任何重要业务逻辑都可以单独做单元测试，远离 HTML 和模板这滩浑水。

### 关注点分离

那还能怎么做呢？

#### 给 `Post` 加个方法，然后在模板里调用它

模板代码里可以对我们传入的类型调用方法，所以可以给 `Post` 加一个 `SanitisedTitle` 方法。这能简化模板，而且愿意的话，这段逻辑也能轻松地单独做单元测试。这大概是省事程度最高的解法，虽然未必是最简单的那个。

这个方案的坏处是，它终究还是_*视图*_逻辑。系统的其他部分对它毫无兴趣，它却从此成了核心领域对象 API 的一部分。这种做法日积月累，可能会让你养出[上帝对象](https://en.wikipedia.org/wiki/God_object)（God Object）。

#### 创建专用的视图模型类型，比如 `PostViewModel`，只装我们刚好需要的数据

渲染代码不再跟领域对象 `Post` 耦合，而是改收一个视图模型。

```go
type PostViewModel struct {
	Title, SanitisedTitle, Description, Body string
	Tags                                     []string
}
```

我们代码的调用方就得做从 `[]Post` 到 `[]PostView` 的映射，顺带生成 `SanitizedTitle`。保持整洁的一个办法，是提供一个 `func NewPostView(p Post) PostView`，把映射封装起来。

这样渲染代码就保持无逻辑，也算我们能做到的最严格的关注点分离了；代价是渲染文章的流程稍微绕了一点。

两个方案都行，这里我更倾向第一个。随着系统演化，你要警惕为了给渲染这台机器上润滑油而不断堆砌临时方法；当领域对象到视图的转换变得更复杂时，专用视图模型才会真正派上用场。

那就把方法加到 `Post` 上：

```go
func (p Post) SanitisedTitle() string {
	return strings.ToLower(strings.Replace(p.Title, " ", "-", -1))
}
```

然后我们的渲染代码就能回到一个更简单的世界：

```go
func (r *PostRenderer) RenderIndex(w io.Writer, posts []Post) error {
	indexTemplate := `<ol>{{range .}}<li><a href="/post/{{.SanitisedTitle}}">{{.Title}}</a></li>{{end}}</ol>`

	templ, err := template.New("index").Parse(indexTemplate)
	if err != nil {
		return err
	}

	if err := templ.Execute(w, posts); err != nil {
		return err
	}

	return nil
}
```

## 重构

测试这下应该能过了。现在可以把模板挪进文件（`templates/index.gohtml`），并在构造渲染器时一次性加载：

```go
package blogrenderer

import (
	"embed"
	"html/template"
	"io"
)

var (
	//go:embed "templates/*"
	postTemplates embed.FS
)

type PostRenderer struct {
	templ *template.Template
}

func NewPostRenderer() (*PostRenderer, error) {
	templ, err := template.ParseFS(postTemplates, "templates/*.gohtml")
	if err != nil {
		return nil, err
	}

	return &PostRenderer{templ: templ}, nil
}

func (r *PostRenderer) Render(w io.Writer, p Post) error {
	return r.templ.ExecuteTemplate(w, "blog.gohtml", p)
}

func (r *PostRenderer) RenderIndex(w io.Writer, posts []Post) error {
	return r.templ.ExecuteTemplate(w, "index.gohtml", posts)
}
```

由于解析了不止一个模板进 `templ`，现在得调用 `ExecuteTemplate`，并按需指明*要渲染哪个*模板。不过希望你也同意：我们最终抵达的这版代码相当漂亮。

有一点_*轻微*_的风险：要是有人重命名了某个模板文件，就会引入 bug。不过我们跑得飞快的单元测试会很快抓住它。

包的 API 设计令人满意了，基本行为也用 TDD 驱动出来了，现在把测试改成用审批测试：

```go
	t.Run("it renders an index of posts", func(t *testing.T) {
		buf := bytes.Buffer{}
		posts := []blogrenderer.Post{{Title: "Hello World"}, {Title: "Hello World 2"}}

		if err := postRenderer.RenderIndex(&buf, posts); err != nil {
			t.Fatal(err)
		}

		approvals.VerifyString(t, buf.String())
	})
```

记得先跑测试看它失败，然后再批准这次改动。

最后，给索引页也加上我们的页面家具：

```handlebars
{{template "top" .}}
<ol>{{range .}}<li><a href="/post/{{.SanitisedTitle}}">{{.Title}}</a></li>{{end}}</ol>
{{template "bottom" .}}
```

重跑测试，批准改动，索引页就大功告成了！

## 渲染 markdown 正文

我鼓励过你自己试试，下面是我最终采取的方案：

```go
package blogrenderer

import (
	"embed"
	"github.com/gomarkdown/markdown"
	"github.com/gomarkdown/markdown/parser"
	"html/template"
	"io"
)

var (
	//go:embed "templates/*"
	postTemplates embed.FS
)

type PostRenderer struct {
	templ *template.Template
}

func NewPostRenderer() (*PostRenderer, error) {
	templ, err := template.ParseFS(postTemplates, "templates/*.gohtml")
	if err != nil {
		return nil, err
	}

	return &PostRenderer{templ: templ}, nil
}

func (r *PostRenderer) Render(w io.Writer, p Post) error {
	return r.templ.ExecuteTemplate(w, "blog.gohtml", newPostVM(p))
}

func (r *PostRenderer) RenderIndex(w io.Writer, posts []Post) error {
	return r.templ.ExecuteTemplate(w, "index.gohtml", posts)
}

type postViewModel struct {
	Post
	HTMLBody template.HTML
}

func newPostVM(p Post) postViewModel {
	vm := postViewModel{Post: p}
	extensions := parser.CommonExtensions | parser.AutoHeadingIDs
	mdParser := parser.NewWithExtensions(extensions)
	vm.HTMLBody = template.HTML(markdown.ToHTML([]byte(p.Body), mdParser, nil))
	return vm
}
```

我用的是非常出色的 [gomarkdown](https://github.com/gomarkdown/markdown) 库，效果正如我所愿。

注意，每次调用 `newPostVM` 都会新建一个 `parser.Parser`，而不是构造一次后存到 `PostRenderer` 上复用。一般而言，能构造一次就复用的东西都值得复用——省下重复构造的开销。但这个惯性直觉在这里会失灵：gomarkdown 的解析器在构建文档树的过程中会保留内部状态，跨多次 `Parse` 调用复用它并不安全——第二次使用同一个实例时，你会得到一个 panic（在旧版本里，则是一个更让人摸不着头脑的空指针解引用）。`PostRenderer` 一生要 `Render` 很多篇文章，每次调用新建一个解析器才是正确的用法——反正这也很便宜，毕竟跟解析本身的开销相比，构造解析器不值一提。

如果你自己动手试过，可能会发现渲染出来的正文里 HTML 都被转义了。这是 Go 的 html/template 包的安全特性，为的是防止恶意的第三方 HTML 被输出。

要绕过这一点，需要在传给渲染的类型里，把你信得过的 HTML 用 [template.HTML](https://pkg.go.dev/html/template#HTML) 包起来：

> HTML 封装一段已知安全的 HTML 文档片段。不要把它用于来自第三方的 HTML，也不要用于含未闭合标签或注释的 HTML。可靠的 HTML 净化器的输出，以及经本包转义过的模板，都可以放心地与 HTML 配合使用。
>
> 使用这个类型存在安全风险：被封装的内容应来自可信来源，因为它会被原封不动地包含在模板输出中。

所以我创建了一个**非导出**（unexported）的视图模型（`postViewModel`），因为我仍然把它视为渲染的内部实现细节。我不需要单独测它，也不想让它污染我的 API。

渲染时我构造一个视图模型，把 `Body` 解析进 `HTMLBody`，然后在模板里用这个字段来渲染 HTML。

## 总结

把[读取文件](reading-files.md)一章和本章学到的东西合起来，你就能轻轻松松做出一个测试充分、简洁的静态站点生成器（static site generator），开起自己的博客。再找些 CSS 教程，还能让它漂漂亮亮。

这套思路不止适用于博客。从任意数据源取数据——数据库、API 也好，文件系统也罢——把它转换成 HTML 再由服务器返回，这是一门横跨几十年的简单手艺。人们总爱抱怨现代 Web 开发的复杂，可你确定这复杂不是你自己硬加给自己的吗？

Go 做 Web 开发非常舒服，尤其是当你想清楚了自己要做的网站到底有什么真实需求的时候。在服务端生成 HTML，往往比用 React 这类技术打造一个"Web 应用"更好、更简单、性能更佳。

### 本章收获

- 如何创建并渲染 HTML 模板。
- 如何组合多个模板，把相关标记 [DRY](https://en.wikipedia.org/wiki/Don't_repeat_yourself)（Don't Repeat Yourself，消除重复）掉，帮全站保持一致的观感。
- 如何向模板传函数，以及为什么这么做之前要三思。
- 如何写"审批测试"，帮我们测试模板渲染器这类东西产出的大坨丑陋输出。

### 再聊无逻辑模板

老话重提：这一切的核心都是**关注点分离**。想清楚系统各部分各自的职责是什么，很重要。太多人把重要的业务逻辑漏进模板里，职责搅成一团，系统从此难懂、难维护、难测试。

### 不只用于 HTML

别忘了 Go 还有 `text/template`，可以从模板生成其他种类的数据。如果你发现自己需要把数据转换成某种结构化输出，本章讲的技术一样能用上。

### 参考资料与延伸阅读

- [John Calhoun 的 "Learn Web Development with Go"](https://www.calhoun.io/intro-to-templates-p1-contextual-encoding/) 有一系列关于模板的优秀文章。
- [Hotwire](https://hotwired.dev)——你可以用这些技术来创建 Hotwire Web 应用。它出自 Basecamp 之手，那是一家以 Ruby on Rails 为主业的公司；不过由于它是服务端方案，我们用 Go 同样能用。
