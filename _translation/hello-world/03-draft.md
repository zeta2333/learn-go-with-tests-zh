# Hello, World

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/hello-world)**

按照惯例，学一门新语言写的第一个程序都是 [Hello, World](https://en.m.wikipedia.org/wiki/%22Hello,_World!%22_program)。

- 随便在哪儿建一个文件夹
- 在里面新建一个名为 `hello.go` 的文件，写入以下代码

```go
package main

import "fmt"

func main() {
	fmt.Println("Hello, world")
}
```

运行它，输入 `go run hello.go` 即可。

## 工作原理

用 Go 写程序时，你需要定义一个 `main` 包，里面再放一个 `main` 函数。包（package）是把相关的 Go 代码归拢到一起的方式。

`func` 关键字用来定义函数，包括函数名和函数体。

`import "fmt"` 则是导入一个包，我们要用来打印输出的 `Println` 函数就在其中。

## 如何测试

这段代码要怎么测试呢？一个良好习惯是把「领域」代码与外部世界（副作用）隔离开。`fmt.Println` 是一个副作用（往标准输出打印），而我们传给它的字符串才是我们的领域逻辑。

那就把这两件事拆开，测试起来就轻松了

```go
package main

import "fmt"

func Hello() string {
	return "Hello, world"
}

func main() {
	fmt.Println(Hello())
}
```

我们又用 `func` 创建了一个新函数，不过这次在定义里多了一个 `string` 关键字，意思是这个函数会返回一个 `string`。

接着新建一个名为 `hello_test.go` 的文件，我们要在这里给 `Hello` 函数写测试

```go
package main

import "testing"

func TestHello(t *testing.T) {
	got := Hello()
	want := "Hello, world"

	if got != want {
		t.Errorf("got %q want %q", got, want)
	}
}
```

## Go modules？

下一步是跑测试。在终端里输入 `go test`。如果你的 Go 版本比较老，测试会直接通过。但如果你用的是 Go 1.16 或更高版本，测试大概率跑不起来，终端里会报这样一个错：

```shell
$ go test
go: cannot find main module; see 'go help modules'
```

问题出在哪儿？一个词：[模块（modules）](https://blog.golang.org/go116-module-changes)。好在解决办法很简单。在终端输入 `go mod init example.com/hello`，它会创建一个内容如下的新文件：

```
module example.com/hello

go 1.16
```

这个文件向 `go` 工具链描述了你的代码的一些关键信息。如果你打算发布自己的应用，还要在这里写明代码的下载地址以及依赖信息。模块名 example\.com\/hello 通常就是能找到并下载这个模块的 URL。为了兼容我们后面会用到的工具，请确保模块名里带个点，比如 example\.com/hello 里 .com 的那个点。眼下你的模块文件保持这个最小样子就挺好。想深入了解模块，可以查阅 [Golang 文档中的参考章节](https://golang.org/doc/modules/gomod-ref)。现在测试应该能跑了（哪怕在 Go 1.16 上），我们可以回到测试和学习 Go 本身了。

在后面的章节里，每到一个新文件夹，你都需要先运行 `go mod init SOMENAME`，然后才能执行 `go test` 或 `go build` 之类的命令。

有一点值得说清楚：模块名 `SOMENAME` 跟 `package main` 毫无关系（本书目前每个 `.go` 文件顶部都声明了 `package main`）。模块名只是整个项目的标识符——不必叫 `main`，你起什么名字都行，只要在同一个文件夹里运行，`go run`、`go test` 和 `go build` 都能正常工作。

## 回到测试

在终端里跑一次 `go test`。应该通过了！为了验证，你可以故意把 `want` 字符串改掉，让测试挂掉试试。

注意到了吗？你完全不用在各种测试框架里挑来挑去，再研究怎么安装。你需要的一切都内置在语言里，而且语法跟你写的其他代码一模一样。

### 编写测试

写测试跟写普通函数差不多，只有几条规矩

* 文件名得长成 `xxx_test.go` 这样
* 测试函数必须以 `Test` 这个词开头
* 测试函数只接收一个参数 `t *testing.T`
* 要使用 `*testing.T` 类型，需要 `import "testing"`，就像前面在另一个文件里导入 `fmt` 一样

现阶段你只需要知道：这个 `*testing.T` 类型的 `t` 是你接入测试框架的「钩子」，想让测试失败时可以调用 `t.Fail()` 之类的方法。

上面出现了几个新话题：

#### `if`
Go 的 if 语句跟其他编程语言非常像。

#### 声明变量

我们用 `varName := value` 的语法声明变量，把测试里用到的值存起来，方便复用、提高可读性。

#### `t.Errorf`

我们调用了 `t` 上的 `Errorf` *方法*，它会打印一条消息并让测试失败。`f` 代表 format（格式化），可以把值填进 `%q` 这样的占位符来拼出字符串。等你故意把测试弄失败的时候，就能直观看到它的效果。

占位符的更多细节可以看 [fmt 文档](https://pkg.go.dev/fmt#hdr-Printing)。写测试时 `%q` 特别好用，因为它会自动给你的值套上双引号。

方法和函数的区别，我们后面会专门讨论。

### Go 的文档

Go 还有一个提升幸福感的设计：文档。刚才我们在官方包查看网站上看了 fmt 包的文档，Go 同样提供了离线快速查文档的办法。

Go 内置了 `doc` 工具，可以查看系统上任何已安装的包，或者你手头正在开发的模块。想看刚才那段 Printing 动词（verbs）的文档，输入：

```
$ go doc fmt
package fmt // import "fmt"

Package fmt implements formatted I/O with functions analogous to C's printf and
scanf. The format 'verbs' are derived from C's but are simpler.

# Printing

The verbs:

General:

    %v	the value in a default format
    	when printing structs, the plus flag (%+v) adds field names
    %#v	a Go-syntax representation of the value
    %T	a Go-syntax representation of the type of the value
    %%	a literal percent sign; consumes no value
...
```

Go 查文档的第二个工具是 `pkgsite` 命令，Go 官方包查看网站背后跑的就是它。用 `go install golang.org/x/pkgsite/cmd/pkgsite@latest` 安装 pkgsite，然后用 `pkgsite -open .` 启动。`go install` 会从对应仓库下载源码并编译成可执行文件；默认安装的 Go 会把可执行文件放在 Linux 和 macOS 的 `$HOME/go/bin`，Windows 则是 `%USERPROFILE%\go\bin`。如果你还没把这些路径加进 `$PATH` 环境变量，建议加一下，以后运行 go 安装的命令会方便很多。

标准库的绝大多数包都有出色的文档和示例。启动 pkgsite 后访问 [http://localhost:8080/testing](http://localhost:8080/testing)，看看都有什么可用的，绝对值得。

### Hello, YOU

有了测试，我们就能放心地迭代软件了。

上一节我们是在代码写完**之后**才补的测试，为的是先让你看看怎么写测试、怎么声明函数。从现在开始，我们要**先写测试**。

下一个需求：让我们能指定问候的对象。

还是先把需求写进测试里。这就是最基本的测试驱动开发，它能确保我们的测试是在真正测我们想测的东西。事后补测试是有风险的——代码就算没按预期工作，测试也可能照样通过。

```go
package main

import "testing"

func TestHello(t *testing.T) {
	got := Hello("Chris")
	want := "Hello, Chris"

	if got != want {
		t.Errorf("got %q want %q", got, want)
	}
}
```

现在运行 `go test`，你应该会看到一个编译错误

```text
./hello_test.go:6:18: too many arguments in call to Hello
    have (string)
    want ()
```

用 Go 这样的静态类型语言，很重要的一点是*听编译器的话*。编译器清楚你的代码该怎么拼装、怎么运作，你不用全靠自己。

这里编译器就是在告诉你下一步该做什么：把 `Hello` 函数改成接收一个参数。

修改 `Hello` 函数，让它接收一个 string 类型的参数

```go
func Hello(name string) string {
	return "Hello, world"
}
```

这时再跑测试，`hello.go` 会编译失败，因为你没有传参数。传入 "world" 让它编译通过。

```go
func main() {
	fmt.Println(Hello("world"))
}
```

现在再跑测试，你应该会看到类似这样的输出

```text
hello_test.go:10: got 'Hello, world' want 'Hello, Chris''
```

程序终于能编译了，可是按测试的说法，它还没满足需求。

那就用上 name 参数，把它跟 `Hello,` 拼在一起，让测试通过

```go
func Hello(name string) string {
	return "Hello, " + name
}
```

跑一下测试，现在应该全过了。按照 TDD 循环，接下来通常就该*重构*了。

### 顺便聊聊版本控制

到了这一步，如果你在用版本控制（你应该用！），我会把代码原样 `commit` 下来：我们有了能工作的软件，背后还有测试撑腰。

不过我*不会* push 到 main，因为接下来我要重构了。这个时候先 commit 一下很值——万一重构搞砸了，随时能回到能工作的版本。

这里没什么好重构的，但我们可以趁机引入另一个语言特性：*常量*。

### 常量

常量这样定义

```go
const englishHelloPrefix = "Hello, "
```

现在可以重构我们的代码了

```go
const englishHelloPrefix = "Hello, "

func Hello(name string) string {
	return englishHelloPrefix + name
}
```

重构完，重跑一遍测试，确认没弄坏任何东西。

用常量来体现值的含义，是值得养成习惯的做法，有时还能带来性能上的好处。

## Hello, world……再来一次

下一个需求：当函数收到空字符串时，默认输出 "Hello, World"，而不是 "Hello, "。

先写一个新的失败测试

```go
func TestHello(t *testing.T) {
	t.Run("saying hello to people", func(t *testing.T) {
		got := Hello("Chris")
		want := "Hello, Chris"

		if got != want {
			t.Errorf("got %q want %q", got, want)
		}
	})
	t.Run("say 'Hello, World' when an empty string is supplied", func(t *testing.T) {
		got := Hello("")
		want := "Hello, World"

		if got != want {
			t.Errorf("got %q want %q", got, want)
		}
	})
}
```

这里我们往测试武器库里又添了一件工具：子测试（subtests）。有时候，把测试围绕某个「对象」分组、再用子测试描述各个场景，会很有用。

这种做法的一个好处是，你可以在外层准备共享代码，供各个子测试使用。

趁测试还挂着，我们用 `if` 把代码修好。

```go
const englishHelloPrefix = "Hello, "

func Hello(name string) string {
	if name == "" {
		name = "World"
	}
	return englishHelloPrefix + name
}
```

跑一下测试，应该能看到新需求满足了，而且其他功能也没被顺手弄坏。

有一点很重要：你的测试必须是代码该做什么的*清晰规约*。但是现在，校验消息是否符合预期这件事出现了重复代码。

重构可不只是生产代码的专利！

测试既然全过了，我们就可以、也应该重构测试本身。

```go
func TestHello(t *testing.T) {
	t.Run("saying hello to people", func(t *testing.T) {
		got := Hello("Chris")
		want := "Hello, Chris"
		assertCorrectMessage(t, got, want)
	})

	t.Run("empty string defaults to 'world'", func(t *testing.T) {
		got := Hello("")
		want := "Hello, World"
		assertCorrectMessage(t, got, want)
	})

}

func assertCorrectMessage(t testing.TB, got, want string) {
	t.Helper()
	if got != want {
		t.Errorf("got %q want %q", got, want)
	}
}
```

我们刚才做了什么？

我们把断言重构进了一个新函数。这减少了重复，也让测试更好读。之所以要传入 `t *testing.T`，是为了在需要的时候能让测试失败。

写辅助函数时，接收 `testing.TB` 是个好主意：它是一个接口（interface），`*testing.T` 和 `*testing.B` 都满足它，这样既能在测试里调用辅助函数，也能在基准测试里调用。（如果「接口」这类词现在听着还陌生，别担心，后面会讲到。）

`t.Helper()` 的作用是告诉测试套件：这个方法是辅助函数。这样一来，测试失败时报告的行号会指向我们*调用它的那一行*，而不是辅助函数内部，其他开发者排查问题会容易得多。如果你还是不理解，就把这行注释掉，让一个测试失败，观察测试输出有什么不同。注释是给代码补充额外信息的好办法，在这里它还有个妙用：快速让编译器忽略某一行。在行首加上两个斜杠 `//` 就能注释掉 `t.Helper()` 这行代码。你会看到那一行变灰，或者变成跟其余代码不同的颜色，说明它已经被注释掉了。

当多个参数的类型相同（比如这里的两个 string），不必写 `(got string, want string)`，可以简写成 `(got, want string)`。

### 回到版本控制

对代码满意之后，我会 amend 之前的那个 commit，这样仓库里就只留下这份带着测试的漂亮代码。

### 纪律

再把整个循环过一遍

* 写一个测试
* 让编译通过
* 运行测试，看到它失败，并确认错误信息是有意义的
* 写刚好够让测试通过的代码
* 重构

表面上看这套流程有点繁琐，但严格守住这个反馈循环非常重要。

它不仅保证你写出的测试*切中要害*，还让你能在测试的保护下放心重构，从而*设计出更好的软件*。

亲眼看到测试失败是一项重要的检查：你顺便确认了错误信息长什么样。作为开发者，如果失败的测试说不清问题出在哪，这样的代码库用起来会非常痛苦。

保证测试*跑得快*，再把工具配置得让跑测试足够简单，你就能在写代码时进入*心流*状态。

反过来，不写测试，就等于承诺以后每次都靠手动运行软件来检查代码，心流就此打断。这省不了时间——从长远看尤其如此。

## 继续前进！还有新需求

好家伙，需求又来了。现在要支持第二个参数，指定问候语的语言。如果传入了我们不认识的语言，就默认用英语。

有了 TDD，我们应该有信心轻松把这个功能做出来！

先写一个传入西班牙语的测试，加到现有的测试组里。

```go
	t.Run("in Spanish", func(t *testing.T) {
		got := Hello("Elodie", "Spanish")
		want := "Hola, Elodie"
		assertCorrectMessage(t, got, want)
	})
```

记住，别作弊！*先写测试*。运行测试时，编译器*应该*会抱怨，因为你用两个参数调用了 `Hello`，而它只接收一个。

```text
./hello_test.go:27:19: too many arguments in call to Hello
    have (string, string)
    want (string)
```

给 `Hello` 再加一个 string 参数，修好编译错误

```go
func Hello(name string, language string) string {
	if name == "" {
		name = "World"
	}
	return englishHelloPrefix + name
}
```

这时再跑测试，它又会抱怨其他测试和 `hello.go` 里调用 `Hello` 时参数不够

```text
./hello.go:15:19: not enough arguments in call to Hello
    have (string)
    want (string, string)
```

传空字符串修好它们。现在除了新场景，你所有的测试应该都能编译*并且*通过

```text
hello_test.go:29: got 'Hello, Elodie' want 'Hola, Elodie'
```

可以用 `if` 判断语言是不是 "Spanish"，是的话换一条消息

```go
func Hello(name string, language string) string {
	if name == "" {
		name = "World"
	}

	if language == "Spanish" {
		return "Hola, " + name
	}
	return englishHelloPrefix + name
}
```

测试现在应该全过了。

到了*重构*时间。你应该能看出代码里的一些问题：「魔法」字符串，有些还重复出现。自己动手重构试试吧，记住每改一次都要重跑测试，确保重构没有弄坏任何东西。

```go
	const spanish = "Spanish"
	const englishHelloPrefix = "Hello, "
	const spanishHelloPrefix = "Hola, "

	func Hello(name string, language string) string {
		if name == "" {
			name = "World"
		}

		if language == spanish {
			return spanishHelloPrefix + name
		}
		return englishHelloPrefix + name
	}
```

### 法语

* 写一个测试：传入 `"French"` 时，返回 `"Bonjour, "` 开头的问候
* 看它失败，确认错误信息容易读懂
* 在代码里做最小的合理改动

你可能写出了大致这样的东西

```go
func Hello(name string, language string) string {
	if name == "" {
		name = "World"
	}

	if language == spanish {
		return spanishHelloPrefix + name
	}
	if language == french {
		return frenchHelloPrefix + name
	}
	return englishHelloPrefix + name
}
```

## `switch`

当一长串 `if` 都在检查同一个值时，惯例是改用 `switch` 语句。我们用 `switch` 重构代码，可读性更好；以后想支持更多语言，扩展起来也更容易

```go
func Hello(name string, language string) string {
	if name == "" {
		name = "World"
	}

	prefix := englishHelloPrefix

	switch language {
	case spanish:
		prefix = spanishHelloPrefix
	case french:
		prefix = frenchHelloPrefix
	}

	return prefix + name
}
```

注意：`prefix` 只在第一次用了 `:=`（声明一个新变量并赋初值），之后所有改值的地方用的都是普通的 `=`，包括上面对 `name` 的赋值和 `switch` 里的 `prefix`。`:=` 是 Go 的[短变量声明](https://go.dev/ref/spec#Short_variable_declarations)——它创建一个新变量；`=` 是普通的[赋值](https://go.dev/ref/spec#Assignment_statements)——它改变一个已存在变量的值（`name` 作为参数已经存在，而 `prefix` 两行之前刚用 `:=` 声明过）。对同一作用域里已经存在的变量用 `:=`，或者对还不存在的变量用 `=`，都是编译错误。

再写一个测试，加上你喜欢的语言的问候语，你就能看到扩展我们这个*了不起的*函数有多简单。

### 最后一次……重构？

要是有人嫌我们的函数变得有点大了呢？最简单的重构就是把一部分功能抽到另一个函数里。

```go

const (
	spanish = "Spanish"
	french  = "French"

	englishHelloPrefix = "Hello, "
	spanishHelloPrefix = "Hola, "
	frenchHelloPrefix  = "Bonjour, "
)

func Hello(name string, language string) string {
	if name == "" {
		name = "World"
	}

	return greetingPrefix(language) + name
}

func greetingPrefix(language string) (prefix string) {
	switch language {
	case french:
		prefix = frenchHelloPrefix
	case spanish:
		prefix = spanishHelloPrefix
	default:
		prefix = englishHelloPrefix
	}
	return
}
```

这里有几个新概念：

* 在函数签名里，我们用了*具名返回值* `(prefix string)`。
* 它会在你的函数里创建一个名为 `prefix` 的变量。
  * 它会被赋上「零值」。零值由类型决定，比如 `int` 是 0，`string` 是 `""`。
    * 只写 `return` 而不用写 `return prefix`，就能返回它当前的值。
  * 它会显示在这个函数的 Go Doc 里，让代码的意图更清晰。
* `switch` 里的 `default` 分支，会在其他所有 `case` 都不匹配时执行。
* 这个函数名以小写字母开头。在 Go 里，公开函数以大写字母开头，私有函数以小写字母开头。我们不想把算法的内部细节暴露给外界，所以把这个函数设成了私有。
* 另外，常量可以放进一个块里统一声明，不必一行一行单独写。为了可读性，相关的几组常量之间用空行隔开是好习惯。

## 总结

谁能想到一个 `Hello, world` 能学出这么多东西？

到这里，你应该已经初步了解：

### 一部分 Go 语法

* 编写测试
* 声明函数，包括参数和返回类型
* `if`、`const` 和 `switch`
* 声明变量和常量

### TDD 流程，以及*为什么*每个步骤都重要

* *先写失败的测试并看到它失败*，这样我们才知道自己写了一个*切中需求*的测试，并且亲眼看到了它给出的失败描述*易于理解*
* 写最少的代码让测试通过，这样我们才知道软件确实能跑
* *然后*再重构，在测试的保护下，确保代码精心打磨、易于维护

在本章里，我们从 `Hello()` 走到 `Hello("name")`，再到 `Hello("name", "French")`，每一步都很小、很好懂。

当然，跟「真实世界」的软件相比，这不过是雕虫小技，但道理是相通的。TDD 是一门需要练习才能掌握的技能，不过只要学会把问题拆成一个个可测试的小块，你写软件的日子会好过得多。
