# 读取文件

* [**本章的所有代码都可以在这里找到**](https://github.com/quii/learn-go-with-tests/tree/main/reading-files)
* [这是我在 Twitch 直播中解这道题并回答观众提问的视频](https://www.youtube.com/watch?v=nXts4dEJnkU)

本章我们来学习如何读取文件、把里面的数据取出来，再做点有用的事。

设想一下：你正和朋友一起开发一套博客软件。想法是这样的：作者用 markdown 写文章，文件顶部附带一些元数据（metadata）。Web 服务器启动时会读取一个文件夹，创建出一批 `Post`；随后另一个独立的 `NewHandler` 函数会把这些 `Post` 当作数据源，支撑博客的 Web 服务。

我们的任务是开发一个包，把给定文件夹里的博客文章文件转换成一组 `Post`。

### 示例数据

hello world.md

```markdown
Title: Hello, TDD world!
Description: First post on our wonderful blog
Tags: tdd, go
---
Hello world!

The body of posts starts after the `---`
```

### 期望数据

```go
type Post struct {
	Title, Description, Body string
	Tags                     []string
}
```

## 迭代式的测试驱动开发

我们采用迭代式的方法，始终朝着目标迈出简单、安全的一小步。

这要求我们把工作拆分开来，但也要小心，别掉进[“自底向上”](https://en.wikipedia.org/wiki/Top-down_and_bottom-up_design)设计的陷阱。

刚上手的时候，别太相信自己那过于活跃的想象力。我们很容易忍不住造出某种抽象，直到最后把所有东西拼在一起才能验证它，比如某种 `BlogPostFileParser`。

这样做*根本*谈不上迭代，还错过了 TDD 本该带给我们的紧密反馈循环。

Kent Beck 说过：

> 乐观是编程这个行当的职业病。反馈是解药。

相反，我们的做法应力求尽快交付*真正的*使用者价值（也就是常说的“正常路径”，happy path）。一旦端到端地交付了一小块使用者价值，对余下需求的迭代通常就顺理成章了。

## 想清楚我们想要什么样的测试

先提醒一下自己起步时的心态和目标：

* **写出你想看到的测试**。站在使用者的角度，想想我们希望怎么使用即将写出的代码。
* 关注*做什么*和*为什么*，别被*怎么做*岔开了注意力。

我们的包需要提供一个函数：给它指一个文件夹，它给我们返回一批文章。

```go
var posts []blogposts.Post
posts = blogposts.NewPostsFromFS("some-folder")
```

要围绕它写测试，我们就得准备某种测试文件夹，里面放一些示例文章。*这并没有什么大错*，但你也在做一些取舍：

* 每个测试都可能需要新建文件，才能测到某个特定的行为
* 有些行为会很难测，比如加载文件失败
* 测试会稍微慢一点，因为要真的访问文件系统

而且这也让我们不必要地跟某个具体的文件系统实现绑在了一起。

### Go 1.16 引入的文件系统抽象

Go 1.16 为文件系统引入了一层抽象：[io/fs](https://golang.org/pkg/io/fs/) 包。

> fs 包定义了文件系统的基础接口。文件系统既可以由宿主操作系统提供，也可以由其他包提供。

这让我们得以放松与具体文件系统的耦合，进而能按需注入不同的实现。

> [在接口的生产者一侧，新的 embed.FS 类型实现了 fs.FS，zip.Reader 也是。新的 os.DirFS 函数提供了一个以操作系统文件树为后端的 fs.FS 实现。](https://golang.org/doc/go1.16#fs)

如果我们采用这个接口，包的使用者天生就能从标准库里挑到好几种现成的选择。学会善用 Go 标准库定义的接口（比如 `io.fs`、[`io.Reader`](https://golang.org/pkg/io/#Reader)、[`io.Writer`](https://golang.org/pkg/io/#Writer)），对写出松耦合的包至关重要。这样的包之后就能在你没想到的其他场景里被复用，而使用者那边几乎不用费什么周折。

在我们这个场景里，说不定使用者想把文章直接嵌入 Go 二进制文件，而不是放进“真实”的文件系统？无论哪种，*我们的代码都不需要关心*。

测试方面，[testing/fstest](https://golang.org/pkg/testing/fstest/) 包提供了一个 [io/FS](https://golang.org/pkg/io/fs/#FS) 的实现供我们使用，有点像我们在 [net/http/httptest](https://golang.org/pkg/net/http/httptest/) 里已经很熟悉的那些工具。

有了这些信息，下面这样感觉是更好的做法：

```go
var posts []blogposts.Post
posts = blogposts.NewPostsFromFS(someFS)
```

## 先写测试

我们应该把范围控制得尽量小、尽量有用。如果能证明我们能够读出一个目录里的所有文件，那就是个不错的起点，这会让我们对自己正在写的软件更有信心。我们可以检查返回的 `[]Post` 数量是否与假文件系统里的文件数量一致。

新建一个项目来完成这一章。

* `mkdir blogposts`
* `cd blogposts`
* `go mod init github.com/{your-name}/blogposts`
* `touch blogposts_test.go`

```go
package blogposts_test

import (
	"testing"
	"testing/fstest"
)

func TestNewBlogPosts(t *testing.T) {
	fs := fstest.MapFS{
		"hello world.md":  {Data: []byte("hi")},
		"hello-world2.md": {Data: []byte("hola")},
	}

	posts := blogposts.NewPostsFromFS(fs)

	if len(posts) != len(fs) {
		t.Errorf("got %d posts, wanted %d posts", len(posts), len(fs))
	}
}
```

注意我们的测试所在的包是 `blogposts_test`。记住，TDD 实践得好时，我们采取的是*使用者驱动*的思路：我们不想测试内部细节，因为*使用者*并不关心它们。在预期的包名后面加上 `_test`，我们就只能访问自己包里的导出成员（exported）——跟这个包的真实用户一模一样。

我们导入了 [`testing/fstest`](https://golang.org/pkg/testing/fstest/)，它让我们能用上 [`fstest.MapFS`](https://golang.org/pkg/testing/fstest/#MapFS) 类型。我们的假文件系统会把 `fstest.MapFS` 传给我们的包。

> MapFS 是一个简单的内存文件系统，供测试使用；它表示为一个 map，键是路径名（即传给 Open 的参数），值是所代表文件或目录的信息。

这感觉比维护一个装满测试文件的文件夹要简单，执行起来也更快。

最后，我们从使用者的视角把 API 的用法固化成了代码，然后检查它创建的文章数量是否正确。

## 试着运行测试

```
./blogpost_test.go:15:12: undefined: blogposts
```

## 写最少的代码让测试能跑起来，并*确认失败的测试输出*

包还不存在。新建一个文件 `blogposts.go`，里面写上 `package blogposts`。接着你需要在测试里导入这个包。我的导入现在长这样：

```go
import (
	blogposts "github.com/quii/learn-go-with-tests/reading-files"
	"testing"
	"testing/fstest"
)
```

现在测试编译不过了，因为我们的新包里还没有一个能返回某种集合的 `NewPostsFromFS` 函数。

```
./blogpost_test.go:16:12: undefined: blogposts.NewPostsFromFS
```

这逼着我们把函数的骨架搭出来，好让测试跑起来。记住，这一步别想太多；我们只是想得到一个能运行的测试，并确认它按预期失败。要是跳过这一步，我们可能会略过对假设的检验，写出一个没什么用的测试。

```go
package blogposts

import "testing/fstest"

type Post struct {
}

func NewPostsFromFS(fileSystem fstest.MapFS) []Post {
	return nil
}
```

测试现在应该正确地失败了

```
=== RUN   TestNewBlogPosts
    blogposts_test.go:48: got 0 posts, wanted 2 posts
```

## 写足够的代码让测试通过

我们其实可以先[“slime”](https://deniseyu.github.io/leveling-up-tdd/)一把让它通过（slime：先用最粗糙的假实现糊上去）：

```go
func NewPostsFromFS(fileSystem fstest.MapFS) []Post {
	return []Post{{}, {}}
}
```

不过，正如 Denise Yu 所写：

> Sliming 的用处在于给你的对象搭出一个“骨架”。设计接口和执行逻辑是两件不同的事，有策略地 slime 测试能让你一次只专注一件事。

骨架我们已经有了。那接下来该怎么办？

既然已经缩小了范围，我们要做的只是读出目录，为遇到的每个文件创建一个 post。打开文件、解析内容，这些先不用操心。

```go
func NewPostsFromFS(fileSystem fstest.MapFS) []Post {
	dir, _ := fs.ReadDir(fileSystem, ".")
	var posts []Post
	for range dir {
		posts = append(posts, Post{})
	}
	return posts
}
```

[`fs.ReadDir`](https://golang.org/pkg/io/fs/#ReadDir) 读取给定 `fs.FS` 中的一个目录，返回 [`[]DirEntry`](https://golang.org/pkg/io/fs/#DirEntry)。

我们对世界理想化的想象立刻就被现实挫败了，因为错误随时可能发生；但记住，此刻我们的重点是*让测试通过*，不是改设计，所以我们先无视它。

剩下的代码很直白：遍历这些条目，为每个条目创建一个 `Post`，然后返回切片。

## 重构

虽然测试过了，可是一旦离开这个场景，我们的新包就没法用了，因为它耦合在具体实现 `fstest.MapFS` 上。但这完全没必要。把 `NewPostsFromFS` 函数的参数改成接受标准库里的那个接口。

```go
func NewPostsFromFS(fileSystem fs.FS) []Post {
	dir, _ := fs.ReadDir(fileSystem, ".")
	var posts []Post
	for range dir {
		posts = append(posts, Post{})
	}
	return posts
}
```

重新跑测试：一切应该照常工作。

### 错误处理

早些时候我们一门心思先让正常路径跑通，把错误处理停在了路边。在继续迭代功能之前，应该承认跟文件打交道时错误是可能发生的。除了读目录，打开单个文件时也可能出问题。让我们改一下 API（当然，还是先改测试），让它可以返回 `error`。

```go
func TestNewBlogPosts(t *testing.T) {
	fs := fstest.MapFS{
		"hello world.md":  {Data: []byte("hi")},
		"hello-world2.md": {Data: []byte("hola")},
	}

	posts, err := blogposts.NewPostsFromFS(fs)

	if err != nil {
		t.Fatal(err)
	}

	if len(posts) != len(fs) {
		t.Errorf("got %d posts, wanted %d posts", len(posts), len(fs))
	}
}
```

跑一下测试：它应该会抱怨返回值的个数不对。代码改起来很直接。

```go
func NewPostsFromFS(fileSystem fs.FS) ([]Post, error) {
	dir, err := fs.ReadDir(fileSystem, ".")
	if err != nil {
		return nil, err
	}
	var posts []Post
	for range dir {
		posts = append(posts, Post{})
	}
	return posts, nil
}
```

测试这就过了。在写下把 `fs.ReadDir` 的错误传播出去的代码之前，我们并没有先看到失败的测试，你内心的 TDD 实践者也许会有点恼火。要做得“规矩”，我们得再写一个新测试，注入一个总是失败的 `fs.FS` 测试替身，让 `fs.ReadDir` 返回 `error`。

```go
type StubFailingFS struct {
}

func (s StubFailingFS) Open(name string) (fs.File, error) {
	return nil, errors.New("oh no, i always fail")
}
```

```go
// 稍后
_, err := blogposts.NewPostsFromFS(StubFailingFS{})
```

这应该能让你对我们的方法更有信心。我们用的接口只有一个方法，这让创建测试替身来测试不同场景变得轻而易举。

有些时候，测试错误处理是务实的做法；但在我们的例子里，我们对这个错误没做任何*有意思的*处理，只是把它传播出去，所以不值得费劲再写一个新测试。

按逻辑，接下来的迭代将围绕扩充 `Post` 类型展开，让它装上一些有用的数据。

## 先写测试

我们从拟定的博客文章格式的第一行开始：title 字段。

我们需要把测试文件的内容改成与规格一致，然后就可以断言它被正确解析了。

```go
func TestNewBlogPosts(t *testing.T) {
	fs := fstest.MapFS{
		"hello world.md":  {Data: []byte("Title: Post 1")},
		"hello-world2.md": {Data: []byte("Title: Post 2")},
	}

	// 其余测试代码从略
	got := posts[0]
	want := blogposts.Post{Title: "Post 1"}

	if !reflect.DeepEqual(got, want) {
		t.Errorf("got %+v, want %+v", got, want)
	}
}
```

## 试着运行测试

```
./blogpost_test.go:58:26: unknown field 'Title' in struct literal of type blogposts.Post
```

## 写最少的代码让测试能跑起来，并确认失败的测试输出

给 `Post` 类型加上新字段，让测试能跑起来。

```go
type Post struct {
	Title string
}
```

重跑测试，你应该会看到一次清晰的失败

```
=== RUN   TestNewBlogPosts
=== RUN   TestNewBlogPosts/parses_the_post
    blogpost_test.go:61: got {Title:}, want {Title:Post 1}
```

## 写足够的代码让测试通过

我们需要打开每个文件，然后提取出标题。

```go
func NewPostsFromFS(fileSystem fs.FS) ([]Post, error) {
	dir, err := fs.ReadDir(fileSystem, ".")
	if err != nil {
		return nil, err
	}
	var posts []Post
	for _, f := range dir {
		post, err := getPost(fileSystem, f)
		if err != nil {
			return nil, err // todo：这里需要再想想，一个文件失败时应该整体失败，还是直接忽略？
		}
		posts = append(posts, post)
	}
	return posts, nil
}

func getPost(fileSystem fs.FS, f fs.DirEntry) (Post, error) {
	postFile, err := fileSystem.Open(f.Name())
	if err != nil {
		return Post{}, err
	}
	defer postFile.Close()

	postData, err := io.ReadAll(postFile)
	if err != nil {
		return Post{}, err
	}

	post := Post{Title: string(postData)[7:]}
	return post, nil
}
```

记住，此时我们的重点不是写出优雅的代码，而是到达“有能用的软件”这一步。

尽管感觉只是前进了一小步，它还是让我们写了相当多的代码，并在错误处理上做了一些假设。这种时候你就该找同事聊聊，一起定下最合适的做法。

迭代式的方法给了我们快速的反馈：我们对需求的理解还不完整。

`fs.FS` 提供了用 `Open` 方法按名字打开其中某个文件的方式。接着我们从文件里读出数据；眼下不需要任何复杂的解析，用字符串切片把 `Title:` 那段文字切掉就行。

## 重构

把“打开文件的代码”和“解析文件内容的代码”分开，代码会更容易理解、更好上手。

```go
func getPost(fileSystem fs.FS, f fs.DirEntry) (Post, error) {
	postFile, err := fileSystem.Open(f.Name())
	if err != nil {
		return Post{}, err
	}
	defer postFile.Close()
	return newPost(postFile)
}

func newPost(postFile fs.File) (Post, error) {
	postData, err := io.ReadAll(postFile)
	if err != nil {
		return Post{}, err
	}

	post := Post{Title: string(postData)[7:]}
	return post, nil
}
```

提炼出新函数或新方法时，用心想想参数。你是在做设计，而且测试都绿着，尽可以深入思考什么才是合适的。想想耦合与内聚。就眼下的例子，你该问问自己：

> `newPost` 一定要耦合在 `fs.File` 上吗？这个类型的方法和数据我们都用上了吗？我们*真正*需要的到底是什么？

在我们的例子里，`fs.File` 只是被当作参数传给了 `io.ReadAll`，而后者需要的是一个 `io.Reader`。所以我们应当放松函数里的耦合，转而要求一个 `io.Reader`。

```go
func newPost(postFile io.Reader) (Post, error) {
	postData, err := io.ReadAll(postFile)
	if err != nil {
		return Post{}, err
	}

	post := Post{Title: string(postData)[7:]}
	return post, nil
}
```

对 `getPost` 函数也可以做类似的论证：它接收一个 `fs.DirEntry` 参数，却只是调用 `Name()` 拿个文件名。我们不需要那么多；跟这个类型解耦，直接把文件名作为 string 传进来吧。下面是完全重构后的代码：

```go
func NewPostsFromFS(fileSystem fs.FS) ([]Post, error) {
	dir, err := fs.ReadDir(fileSystem, ".")
	if err != nil {
		return nil, err
	}
	var posts []Post
	for _, f := range dir {
		post, err := getPost(fileSystem, f.Name())
		if err != nil {
			return nil, err // todo：这里需要再想想，一个文件失败时应该整体失败，还是直接忽略？
		}
		posts = append(posts, post)
	}
	return posts, nil
}

func getPost(fileSystem fs.FS, fileName string) (Post, error) {
	postFile, err := fileSystem.Open(fileName)
	if err != nil {
		return Post{}, err
	}
	defer postFile.Close()
	return newPost(postFile)
}

func newPost(postFile io.Reader) (Post, error) {
	postData, err := io.ReadAll(postFile)
	if err != nil {
		return Post{}, err
	}

	post := Post{Title: string(postData)[7:]}
	return post, nil
}
```

从现在起，我们的大部分工作都能干净利落地收在 `newPost` 里。打开和遍历文件这些事已经了结，接下来可以专心为 `Post` 类型提取数据了。虽然技术上并非必须，但文件是把相关内容按逻辑归组的好办法，所以我顺手把 `Post` 类型和 `newPost` 挪进了新建的 `post.go` 文件。

### 测试辅助函数

我们也该照顾好自己的测试。接下来我们会频繁地对 `Post` 做断言，所以该写点代码来搭把手：

```go
func assertPost(t *testing.T, got blogposts.Post, want blogposts.Post) {
	t.Helper()
	if !reflect.DeepEqual(got, want) {
		t.Errorf("got %+v, want %+v", got, want)
	}
}
```

```go
assertPost(t, posts[0], blogposts.Post{Title: "Post 1"})
```

## 先写测试

我们继续扩展测试，提取文件里的下一行：description。把测试推到通过为止的这整套流程，你现在应该已经轻车熟路了。

```go
func TestNewBlogPosts(t *testing.T) {
	const (
		firstBody = `Title: Post 1
Description: Description 1`
		secondBody = `Title: Post 2
Description: Description 2`
	)

	fs := fstest.MapFS{
		"hello world.md":  {Data: []byte(firstBody)},
		"hello-world2.md": {Data: []byte(secondBody)},
	}

	// 其余测试代码从略
	assertPost(t, posts[0], blogposts.Post{
		Title:       "Post 1",
		Description: "Description 1",
	})

}
```

## 试着运行测试

```
./blogpost_test.go:47:58: unknown field 'Description' in struct literal of type blogposts.Post
```

## 写最少的代码让测试能跑起来，并确认失败的测试输出

给 `Post` 加上新字段。

```go
type Post struct {
	Title       string
	Description string
}
```

测试现在应该能编译了，然后失败。

```
=== RUN   TestNewBlogPosts
    blogpost_test.go:47: got {Title:Post 1
        Description: Description 1 Description:}, want {Title:Post 1 Description:Description 1}
```

## 写足够的代码让测试通过

标准库里有个顺手的库，能帮你把数据一行一行地扫过去：[`bufio.Scanner`](https://golang.org/pkg/bufio/#Scanner)。

> Scanner 提供了一个便捷的接口，用来读取数据，比如按换行分隔的一行行文本组成的文件。

```go
func newPost(postFile io.Reader) (Post, error) {
	scanner := bufio.NewScanner(postFile)

	scanner.Scan()
	titleLine := scanner.Text()

	scanner.Scan()
	descriptionLine := scanner.Text()

	return Post{Title: titleLine[7:], Description: descriptionLine[13:]}, nil
}
```

方便的是，它读取的同样是一个 `io.Reader`（再次感谢松耦合），我们的函数参数一个都不用改。

调用 `Scan` 读取一行，然后用 `Text` 提取数据。

这个函数永远不可能返回 `error`。这时候把它从返回类型里去掉是挺诱人，但我们知道之后还得处理非法的文件结构，所以不妨先留着。

## 重构

“扫描一行、然后读出文本”这里有重复。我们知道这个操作至少还要再来一次，把它 DRY 掉（DRY：Don't Repeat Yourself，消除重复）是个简单的重构，就从这儿开始。

```go
func newPost(postFile io.Reader) (Post, error) {
	scanner := bufio.NewScanner(postFile)

	readLine := func() string {
		scanner.Scan()
		return scanner.Text()
	}

	title := readLine()[7:]
	description := readLine()[13:]

	return Post{Title: title, Description: description}, nil
}
```

这几乎没省下几行代码，但省行数很少是重构的重点。我在这里想做的，只是把读行的*做什么*和*怎么做*分开，让代码对读者来说更有声明式的味道。

7 和 13 这两个魔法数字虽然能干活，却实在没什么表现力。

```go
const (
	titleSeparator       = "Title: "
	descriptionSeparator = "Description: "
)

func newPost(postFile io.Reader) (Post, error) {
	scanner := bufio.NewScanner(postFile)

	readLine := func() string {
		scanner.Scan()
		return scanner.Text()
	}

	title := readLine()[len(titleSeparator):]
	description := readLine()[len(descriptionSeparator):]

	return Post{Title: title, Description: description}, nil
}
```

现在，带着充满创意的重构之眼盯着这段代码，我想试试让 readLine 函数顺便把标签去掉。另外还有个更可读的办法可以从字符串里去掉前缀，就是 `strings.TrimPrefix` 函数。

```go
func newPost(postBody io.Reader) (Post, error) {
	scanner := bufio.NewScanner(postBody)

	readMetaLine := func(tagName string) string {
		scanner.Scan()
		return strings.TrimPrefix(scanner.Text(), tagName)
	}

	return Post{
		Title:       readMetaLine(titleSeparator),
		Description: readMetaLine(descriptionSeparator),
	}, nil
}
```

这个主意你可能喜欢，也可能不喜欢，反正我喜欢。重点在于：处于重构阶段时，我们可以随意把玩内部细节，并且一直重跑测试确认行为依然正确。不满意的话，随时可以退回之前的状态。TDD 方法给了我们这张许可证，让我们可以频繁试验各种想法，从而有更多机会写出优秀的代码。

下一个需求是提取文章的 tags。如果你在跟着做，我建议先自己动手实现，再往下读。你现在应该已经找到了不错的迭代节奏，有信心提取下一行并解析出数据。

为节省篇幅，TDD 的步骤我就不逐一走过了，直接给出加了 tags 的测试。

```go
func TestNewBlogPosts(t *testing.T) {
	const (
		firstBody = `Title: Post 1
Description: Description 1
Tags: tdd, go`
		secondBody = `Title: Post 2
Description: Description 2
Tags: rust, borrow-checker`
	)

	// 其余测试代码从略
	assertPost(t, posts[0], blogposts.Post{
		Title:       "Post 1",
		Description: "Description 1",
		Tags:        []string{"tdd", "go"},
	})
}
```

如果只是复制粘贴我写的代码，那你骗的只是你自己。为了确保我们想的一样，下面是我的代码，包含提取 tags 的部分。

```go
const (
	titleSeparator       = "Title: "
	descriptionSeparator = "Description: "
	tagsSeparator        = "Tags: "
)

func newPost(postBody io.Reader) (Post, error) {
	scanner := bufio.NewScanner(postBody)

	readMetaLine := func(tagName string) string {
		scanner.Scan()
		return strings.TrimPrefix(scanner.Text(), tagName)
	}

	return Post{
		Title:       readMetaLine(titleSeparator),
		Description: readMetaLine(descriptionSeparator),
		Tags:        strings.Split(readMetaLine(tagsSeparator), ", "),
	}, nil
}
```

希望这里没什么意外。我们复用了 `readMetaLine` 拿到 tags 那一行，然后用 `strings.Split` 把它拆开。

正常路径上的最后一次迭代，是提取正文。

回顾一下拟定的文件格式。

```markdown
Title: Hello, TDD world!
Description: First post on our wonderful blog
Tags: tdd, go
---
Hello world!

The body of posts starts after the `---`
```

前 3 行已经读过了。接下来再读一行，把它丢掉，文件剩下的部分就是文章正文。

## 先写测试

修改测试数据：加上分隔符，正文里放几个换行，检查我们能拿到全部内容。

```go
	const (
		firstBody = `Title: Post 1
Description: Description 1
Tags: tdd, go
---
Hello
World`
		secondBody = `Title: Post 2
Description: Description 2
Tags: rust, borrow-checker
---
B
L
M`
	)
```

像之前那样给断言加上内容

```go
	assertPost(t, posts[0], blogposts.Post{
		Title:       "Post 1",
		Description: "Description 1",
		Tags:        []string{"tdd", "go"},
		Body: `Hello
World`,
	})
```

## 试着运行测试

```
./blogpost_test.go:60:3: unknown field 'Body' in struct literal of type blogposts.Post
```

跟预期一样。

## 写最少的代码让测试能跑起来，并确认失败的测试输出

给 `Post` 加上 `Body`，测试应该会失败。

```
=== RUN   TestNewBlogPosts
    blogposts_test.go:38: got {Title:Post 1 Description:Description 1 Tags:[tdd go] Body:}, want {Title:Post 1 Description:Description 1 Tags:[tdd go] Body:Hello
        World}
```

## 写足够的代码让测试通过

1. 扫过下一行，忽略 `---` 分隔符。
2. 持续扫描，直到没有内容可扫。

```go
func newPost(postBody io.Reader) (Post, error) {
	scanner := bufio.NewScanner(postBody)

	readMetaLine := func(tagName string) string {
		scanner.Scan()
		return strings.TrimPrefix(scanner.Text(), tagName)
	}

	title := readMetaLine(titleSeparator)
	description := readMetaLine(descriptionSeparator)
	tags := strings.Split(readMetaLine(tagsSeparator), ", ")

	scanner.Scan() // 忽略掉一行

	var b strings.Builder
	for scanner.Scan() {
		fmt.Fprintln(&b, scanner.Text())
	}
	body := strings.TrimSuffix(b.String(), "\n")

	return Post{
		Title:       title,
		Description: description,
		Tags:        tags,
		Body:        body,
	}, nil
}
```

* `scanner.Scan()` 返回一个 `bool`，表示是否还有数据可扫，所以我们可以拿它配合 `for` 循环，把数据一路读到末尾。
* 每次 `Scan()` 之后，我们用 `fmt.Fprintln` 把数据写进缓冲区。选带换行的那个版本，是因为 scanner 会把每行末尾的换行剥掉，而我们需要保留它们。
* 由于上面的原因，最后得把末尾的换行 trim 掉，免得正文结尾多出一个换行。

## 重构

把“取剩余数据”这件事封装成一个函数，未来的读者就能迅速看懂 `newPost` 里*发生了什么*，而不必纠缠于具体的实现细节。

```go
func newPost(postBody io.Reader) (Post, error) {
	scanner := bufio.NewScanner(postBody)

	readMetaLine := func(tagName string) string {
		scanner.Scan()
		return strings.TrimPrefix(scanner.Text(), tagName)
	}

	return Post{
		Title:       readMetaLine(titleSeparator),
		Description: readMetaLine(descriptionSeparator),
		Tags:        strings.Split(readMetaLine(tagsSeparator), ", "),
		Body:        readBody(scanner),
	}, nil
}

func readBody(scanner *bufio.Scanner) string {
	scanner.Scan() // 忽略掉一行
	var b strings.Builder
	for scanner.Scan() {
		fmt.Fprintln(&b, scanner.Text())
	}
	return strings.TrimSuffix(b.String(), "\n")
}
```

## 继续迭代

我们已经拧出了功能的“主钢缆”（steel thread）——沿着最短的路线打通了正常路径——但离生产可用显然还有一段路。

我们还没处理：

* 文件格式不对的情况
* 文件不是 `.md` 的情况
* 元数据字段的顺序不一样怎么办？这应该被允许吗？我们应该能处理它吗？

但至关重要的是：我们有了能工作的软件，也定义好了接口。上面这些都只是后续迭代，再多写一些测试来驱动行为而已。要支持其中任何一条，我们都不应该需要改动*设计*，只需要调整实现细节。

盯紧目标意味着：我们做的是重要的决策，并用期望的行为验证了它们，而不是一头栽进那些根本影响不了整体设计的琐事里。

## 总结

`fs.FS` 以及 Go 1.16 的其他变化，给了我们一些优雅的方式来从文件系统读取数据，并简单地对它们进行测试。

如果你想“来真的”跑一跑这些代码：

* 在项目里建一个 `cmd` 文件夹，添加一个 `main.go` 文件
* 加入以下代码

```go
import (
	blogposts "github.com/quii/fstest-spike"
	"log"
	"os"
)

func main() {
	posts, err := blogposts.NewPostsFromFS(os.DirFS("posts"))
	if err != nil {
		log.Fatal(err)
	}
	log.Println(posts)
}
```

* 往 `posts` 文件夹里放几个 markdown 文件，然后运行程序！

注意生产代码

```go
posts, err := blogposts.NewPostsFromFS(os.DirFS("posts"))
```

和测试代码

```go
posts, err := blogposts.NewPostsFromFS(fs)
```

之间的对称性。

这正是使用者驱动、自顶向下的 TDD *让人感觉对了*的时刻。

包的使用者看看我们的测试，就能很快上手：知道它该做什么、该怎么用。作为维护者，我们则可以*确信自己的测试是有用的，因为它们出自使用者的视角*。我们没有测试实现细节或其他偶然细节，因此可以相当有把握：重构时，测试会帮到我们，而不是拖我们的后腿。

依靠[**依赖注入**](./dependency-injection.md)这类良好的软件工程实践，我们的代码既容易测试，也容易复用。

创建包的时候，哪怕它只在项目内部使用，也请优先采用自顶向下、使用者驱动的方式。这能防止你把设计想象得过于复杂、造出可能根本用不上的抽象，也能帮你确保写出的测试真正有用。

迭代式方法让每一步都很小，持续的反馈帮我们发现了那些模糊不清的需求，甚至可能比其他更随意的做法更早。

### 写文件呢？

要注意：这些新特性只提供了*读取*文件的操作。如果你的工作需要写文件，就得另找办法。记住随时想想标准库目前已经提供了什么——如果要写数据，你大概应该考虑利用现有的接口，比如 `io.Writer`，让自己的代码保持松耦合、可复用。

### 延伸阅读

* 本章只是对 `io/fs` 的粗浅介绍。[Ben Congdon 写过一篇非常出色的文章](https://benjamincongdon.me/blog/2021/01/21/A-Tour-of-Go-116s-iofs-package/)，对本章的写作帮助很大。
* [关于文件系统接口的讨论](https://github.com/golang/go/issues/41190)
