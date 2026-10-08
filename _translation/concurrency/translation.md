# 并发

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/concurrency)**

先交代一下背景：一位同事写了一个函数 `CheckWebsites`，用来检查一批 URL 的状态。

```go
package concurrency

type WebsiteChecker func(string) bool

func CheckWebsites(wc WebsiteChecker, urls []string) map[string]bool {
	results := make(map[string]bool)

	for _, url := range urls {
		results[url] = wc(url)
	}

	return results
}
```

它返回一个 map，把检查过的每个 URL 映射到对应的布尔值：响应正常是 `true`，响应异常是 `false`。

调用时还得传入一个 `WebsiteChecker`，后者接收单个 URL 并返回布尔值，函数就是靠它来检查所有网站的。

多亏用了[依赖注入][DI]，他们不用发起真正的 HTTP 调用就能测试这个函数，测试因而可靠又快速。

他们写的测试是这样的：

```go
package concurrency

import (
	"reflect"
	"testing"
)

func mockWebsiteChecker(url string) bool {
	return url != "waat://furhurterwe.geds"
}

func TestCheckWebsites(t *testing.T) {
	websites := []string{
		"http://google.com",
		"http://blog.gypsydave5.com",
		"waat://furhurterwe.geds",
	}

	want := map[string]bool{
		"http://google.com":          true,
		"http://blog.gypsydave5.com": true,
		"waat://furhurterwe.geds":    false,
	}

	got := CheckWebsites(mockWebsiteChecker, websites)

	if !reflect.DeepEqual(want, got) {
		t.Fatalf("wanted %v, got %v", want, got)
	}
}
```

这个函数已经投入生产，用来检查几百个网站。但同事开始收到投诉，说它太慢了，于是找你来帮忙提速。

## 编写测试

我们用基准测试来测一测 `CheckWebsites` 的速度，这样就能看到改动带来的效果。

```go
package concurrency

import (
	"testing"
	"time"
)

func slowStubWebsiteChecker(_ string) bool {
	time.Sleep(20 * time.Millisecond)
	return true
}

func BenchmarkCheckWebsites(b *testing.B) {
	urls := make([]string, 100)
	for i := 0; i < len(urls); i++ {
		urls[i] = "a url"
	}

	for b.Loop() {
		CheckWebsites(slowStubWebsiteChecker, urls)
	}
}
```

这个基准测试用一个包含一百个 URL 的切片来测 `CheckWebsites`，还用到了一个新的 fake 实现 `WebsiteChecker`。`slowStubWebsiteChecker` 是故意做慢的：它用 `time.Sleep` 精确地等上二十毫秒，然后返回 true。

用 `go test -bench=.` 运行基准测试（如果你在 Windows Powershell 里，命令是 `go test -bench="."`）：

```sh
pkg: github.com/gypsydave5/learn-go-with-tests/concurrency/v0
BenchmarkCheckWebsites-4               1        2249228637 ns/op
PASS
ok      github.com/gypsydave5/learn-go-with-tests/concurrency/v0        2.268s
```

`CheckWebsites` 测得的成绩是 2249228637 纳秒——大约 2.25 秒。

来试试让它变快吧。

### 写足够的代码让它通过

现在，我们终于可以聊聊并发了。就本章而言，并发的意思是“同时有不止一件事情在进行”。这本来就是我们每天自然而然在做的事。

比如今天早上，我给自己泡了杯茶。我把水壶烧上，然后趁等水开的工夫，从冰箱里拿出牛奶，从橱柜里把茶拿出来，找出我最喜欢的马克杯，把茶包放进杯子；等水烧开，再把热水冲进杯子。

我*没有*做的，是把水壶烧上，然后直勾勾地站在那儿盯着水壶，一直盯到水开，等水烧开了才去干其余的事。

如果你能明白为什么第一种泡茶方式更快，那你就能明白我们打算怎么让 `CheckWebsites` 变快：不等一个网站响应完才给下一个网站发请求，而是让电脑在等待的同时把下一个请求发出去。

在 Go 里，我们调用函数 `doSomething()` 时，通常要等它返回（即使它没有值可返回，我们也得等它执行完）。我们说这种操作是*阻塞*（blocking）的——它让我们等它结束。而在 Go 中不阻塞的操作，会运行在一个独立的*流程*（process）里，这种流程叫作 *goroutine*。不妨把流程想象成从上到下读一页 Go 代码：遇到函数调用，就“钻进去”读一读它做了什么。当一个新的流程启动时，就好像另一位读者开始从函数内部读起，而原来的那位读者继续往下读自己的那一页。

要让 Go 启动一个新的 goroutine，只需在函数调用前加上关键字 `go`，把它变成一条 `go` 语句：`go doSomething()`。

```go
package concurrency

type WebsiteChecker func(string) bool

func CheckWebsites(wc WebsiteChecker, urls []string) map[string]bool {
	results := make(map[string]bool)

	for _, url := range urls {
		go func() {
			results[url] = wc(url)
		}()
	}

	return results
}
```

由于启动 goroutine 的唯一方式就是在函数调用前加 `go`，我们想启动 goroutine 时，常常会用*匿名函数*（anonymous function）。匿名函数字面量看起来跟普通函数声明一模一样，只是没有名字（这倒不出奇）。上面 `for` 循环的循环体里就有一个。

匿名函数有不少好用的特性，上面就用到了两个。第一，它们可以在声明的同时被执行——匿名函数末尾的那个 `()` 做的就是这件事。第二，它们能持续访问自己定义时所在的词法作用域（lexical scope）——声明匿名函数的那一刻能看到的全部变量，在函数体内同样能看到。

上面这个匿名函数的函数体，跟之前的循环体一模一样。唯一的区别是：循环的每一轮都会启动一个新的 goroutine，与当前流程（也就是 `WebsiteChecker` 函数）并发地运行。每个 goroutine 都会把自己的结果写进 results map。

可是运行 `go test` 时：

```sh
--- FAIL: TestCheckWebsites (0.00s)
        CheckWebsites_test.go:31: Wanted map[http://google.com:true http://blog.gypsydave5.com:true waat://furhurterwe.geds:false], got map[]
FAIL
exit status 1
FAIL    github.com/gypsydave5/learn-go-with-tests/concurrency/v1        0.010s

```

### 岔开一句，去并发的宇宙里逛逛……

你跑出来的结果可能不是上面这个。你可能会看到一条 panic 信息——我们过一会儿就会讲到它。看到也不用慌，多跑几次测试，直到你*真的*看到上面的结果为止。或者就当自己看到了，随你便。欢迎来到并发的世界：如果处理不当，你很难预测会发生什么。别担心——这正是我们写测试的原因，它能帮我们确认自己对并发的处理是可预测的。

### ……好了，我们回来了。

我们被最初那个 `CheckWebsites` 的测试抓了个正着：函数现在返回的是一个空 map。哪里出了问题？

`for` 循环启动的那些 goroutine，没有一个来得及把自己的结果写进 `results` map；`CheckWebsites` 对它们来说跑得太快了，map 还空着就被返回了。

要解决这个问题，我们只要等所有 goroutine 干完活再返回就行了。等两秒应该就够了，对吧？

```go
package concurrency

import "time"

type WebsiteChecker func(string) bool

func CheckWebsites(wc WebsiteChecker, urls []string) map[string]bool {
	results := make(map[string]bool)

	for _, url := range urls {
		go func() {
			results[url] = wc(url)
		}()
	}

	time.Sleep(2 * time.Second)

	return results
}
```

运气好的话，你会得到：

```sh
PASS
ok      github.com/gypsydave5/learn-go-with-tests/concurrency/v1        2.012s
```

但如果运气不好（和基准测试一起跑时更容易撞上，因为尝试的次数更多），你会看到：

```sh
fatal error: concurrent map writes

goroutine 8 [running]:
runtime.throw(0x12c5895, 0x15)
        /usr/local/Cellar/go/1.9.3/libexec/src/runtime/panic.go:605 +0x95 fp=0xc420037700 sp=0xc4200376e0 pc=0x102d395
runtime.mapassign_faststr(0x1271d80, 0xc42007acf0, 0x12c6634, 0x17, 0x0)
        /usr/local/Cellar/go/1.9.3/libexec/src/runtime/hashmap_fast.go:783 +0x4f5 fp=0xc420037780 sp=0xc420037700 pc=0x100eb65
github.com/gypsydave5/learn-go-with-tests/concurrency/v3.WebsiteChecker.func1(0xc42007acf0, 0x12d3938, 0x12c6634, 0x17)
        /Users/gypsydave5/go/src/github.com/gypsydave5/learn-go-with-tests/concurrency/v3/websiteChecker.go:12 +0x71 fp=0xc4200377c0 sp=0xc420037780 pc=0x12308f1
runtime.goexit()
        /usr/local/Cellar/go/1.9.3/libexec/src/runtime/asm_amd64.s:2337 +0x1 fp=0xc4200377c8 sp=0xc4200377c0 pc=0x105cf01
created by github.com/gypsydave5/learn-go-with-tests/concurrency/v3.WebsiteChecker
        /Users/gypsydave5/go/src/github.com/gypsydave5/learn-go-with-tests/concurrency/v3/websiteChecker.go:11 +0xa1

        ... many more scary lines of text ...
```

这一大段又长又吓人，但我们要做的只是深吸一口气，去读堆栈跟踪（stacktrace）：`fatal error: concurrent map writes`。有时候我们跑测试，两个 goroutine 会恰好在同一时刻往 results map 里写数据。Go 的 map 不喜欢同时有多个东西往里写，于是就有了 `fatal error`。

这就是一次*数据竞争*（data race）：当两个或更多 goroutine 并发地访问同一块内存，而其中至少有一个访问是写操作时，就会出现这种 bug。由于我们无法精确控制每个 goroutine 何时执行，多个 goroutine 就有可能恰好在同一时刻往 `results` map 里写。Go 的 map 并不支持安全的并发写入，所以运行时会抛出致命错误，以防内存被破坏。

Go 内置的[*竞态检测器*（race detector）][godoc_race_detector]能帮我们发现竞态条件（race condition）。要启用这个功能，运行测试时加上 `race` 标志：`go test -race`。

你应该会看到类似这样的输出：

```sh
==================
WARNING: DATA RACE
Write at 0x00c420084d20 by goroutine 8:
  runtime.mapassign_faststr()
      /usr/local/Cellar/go/1.9.3/libexec/src/runtime/hashmap_fast.go:774 +0x0
  github.com/gypsydave5/learn-go-with-tests/concurrency/v3.WebsiteChecker.func1()
      /Users/gypsydave5/go/src/github.com/gypsydave5/learn-go-with-tests/concurrency/v3/websiteChecker.go:12 +0x82

Previous write at 0x00c420084d20 by goroutine 7:
  runtime.mapassign_faststr()
      /usr/local/Cellar/go/1.9.3/libexec/src/runtime/hashmap_fast.go:774 +0x0
  github.com/gypsydave5/learn-go-with-tests/concurrency/v3.WebsiteChecker.func1()
      /Users/gypsydave5/go/src/github.com/gypsydave5/learn-go-with-tests/concurrency/v3/websiteChecker.go:12 +0x82

Goroutine 8 (running) created at:
  github.com/gypsydave5/learn-go-with-tests/concurrency/v3.WebsiteChecker()
      /Users/gypsydave5/go/src/github.com/gypsydave5/learn-go-with-tests/concurrency/v3/websiteChecker.go:11 +0xc4
  github.com/gypsydave5/learn-go-with-tests/concurrency/v3.TestWebsiteChecker()
      /Users/gypsydave5/go/src/github.com/gypsydave5/learn-go-with-tests/concurrency/v3/websiteChecker_test.go:27 +0xad
  testing.tRunner()
      /usr/local/Cellar/go/1.9.3/libexec/src/testing/testing.go:746 +0x16c

Goroutine 7 (finished) created at:
  github.com/gypsydave5/learn-go-with-tests/concurrency/v3.WebsiteChecker()
      /Users/gypsydave5/go/src/github.com/gypsydave5/learn-go-with-tests/concurrency/v3/websiteChecker.go:11 +0xc4
  github.com/gypsydave5/learn-go-with-tests/concurrency/v3.TestWebsiteChecker()
      /Users/gypsydave5/go/src/github.com/gypsydave5/learn-go-with-tests/concurrency/v3/websiteChecker_test.go:27 +0xad
  testing.tRunner()
      /usr/local/Cellar/go/1.9.3/libexec/src/testing/testing.go:746 +0x16c
==================
```

这些细节依然不好读——但 `WARNING: DATA RACE` 已经说得足够明白。细读错误的正文，可以看到两个不同的 goroutine 在对同一个 map 执行写操作：

`Write at 0x00c420084d20 by goroutine 8:`

写入的正是同一块内存，也就是

`Previous write at 0x00c420084d20 by goroutine 7:`

除此之外，我们还能看到写操作发生在哪一行代码：

`/Users/gypsydave5/go/src/github.com/gypsydave5/learn-go-with-tests/concurrency/v3/websiteChecker.go:12`

以及 goroutine 7 和 8 是在哪一行启动的：

`/Users/gypsydave5/go/src/github.com/gypsydave5/learn-go-with-tests/concurrency/v3/websiteChecker.go:11`

你需要知道的一切都打印在终端里了——你要做的，就是耐着性子把它读完。

### Channels

我们可以用 *channel*（通道）来协调各个 goroutine，从而解决这个数据竞争。channel 是一种 Go 数据结构，既可以接收值，也可以发送值。正是这些操作及其细节，让不同的流程之间得以通信。

在这个例子里，我们要关注的是父流程和它派去干活的各个 goroutine 之间的通信——这些 goroutine 负责拿着 url 去运行 `WebsiteChecker` 函数。

```go
package concurrency

type WebsiteChecker func(string) bool
type result struct {
	string
	bool
}

func CheckWebsites(wc WebsiteChecker, urls []string) map[string]bool {
	results := make(map[string]bool)
	resultChannel := make(chan result)

	for _, url := range urls {
		go func() {
			resultChannel <- result{url, wc(url)}
		}()
	}

	for i := 0; i < len(urls); i++ {
		r := <-resultChannel
		results[r.string] = r.bool
	}

	return results
}
```

> **关于 goroutine 里的 `url`。** 循环的每一轮都会启动一个引用了 `url` 的新 goroutine，并没有把它显式传进去。从 Go 1.22 开始，这样写是安全的：语言规范已经修改，`url` 在每一轮循环里都是全新的变量，因此每个 goroutine 捕获到的都是自己那一份副本。
>
> 如果项目 `go.mod` 里声明的 `go` 版本*旧于* `1.22`，你看到的就是老行为：`url` 是一个由每一轮循环共享复用的变量，等 goroutine 真正跑起来时，它们看到的很可能是同一个（多半是最后一轮的）`url` 值。这个问题特别容易坑人，因为你的 Go *工具链*可以是新的，而 `go.mod` 的 `go` 指令却是旧的——工具链遵循的是所声明版本对应的循环变量语义。在旧的 `go.mod` 上，修法是把 `url` 显式传进 goroutine：`go func(url string) { ... }(url)`。

现在除了 `results` map，我们还有了一个 `resultChannel`，它同样是用 `make` 创建的。`chan result` 就是这个 channel 的类型——一个装着 `result` 的 channel。新类型 `result` 的用途，是把 `WebsiteChecker` 的返回值和被检查的 url 关联起来——它是一个由 `string` 和 `bool` 组成的结构体。由于我们不需要给这两个值起名字，它们在结构体里都是匿名的；当你不知道该给某个值起什么名字时，这个办法会很好用。

现在遍历这些 url 时，我们不再直接往 `map` 里写，而是每次调用 `wc`，就把一个 `result` 结构体用*发送语句*（send statement）发送到 `resultChannel`。它用的也是 `<-` 操作符，左边是 channel，右边是值：

```go
// Send statement
resultChannel <- result{url, wc(url)}
```

接下来的 `for` 循环，对每个 url 各迭代一次。循环体里用的是*接收表达式*（receive expression），它把从 channel 接收到的值赋给一个变量。它用的同样是 `<-` 操作符，只不过两个操作数的位置对调了：channel 在右边，被赋值的变量在左边：

```go
// Receive expression
r := <-resultChannel
```

然后用接收到的 `result` 去更新 map。

把结果发送进 channel，我们就能控制每次写入 results map 的时机，确保写入一次只发生一个。尽管每次对 `wc` 的调用、每次向 result channel 的发送，都在各自的流程里并发地进行，但随着我们用接收表达式从 result channel 取值，每个结果都是被逐个处理的。

我们只对想提速的那部分代码用上了并发，同时确保无法同时发生的那部分依然线性地执行。我们还借助 channel，让其中涉及的多个流程实现了相互通信。

跑一下基准测试：

```sh
pkg: github.com/gypsydave5/learn-go-with-tests/concurrency/v2
BenchmarkCheckWebsites-8             100          23406615 ns/op
PASS
ok      github.com/gypsydave5/learn-go-with-tests/concurrency/v2        2.377s
```

23406615 纳秒——0.023 秒，速度大约是原来那个函数的一百倍。大获成功。

## 总结

这个练习对 TDD 的着墨比平时少了些。从某种角度看，我们其实一直在对 `CheckWebsites` 函数进行一场漫长的重构：输入和输出从未改变，只是变快了。而手头已有的测试，加上我们写下的基准测试，让我们既能放心地重构 `CheckWebsites`，保持对软件仍然正常工作的信心，又能证明它确实变快了。

在让它变快的过程中，我们学到了

- *goroutine*：Go 中并发的基本单元，让我们能同时应付不止一个网站检查请求。
- *匿名函数*：我们用它启动每一个检查网站的并发流程。
- *channel*：帮助组织和控制不同流程之间的通信，让我们避开了*竞态条件*这种 bug。
- *竞态检测器*：帮我们调试并发代码的问题

### 让它变快

有一种关于敏捷软件开发方式的说法，常被误认为是 Kent Beck 提出的：

> [先让它能跑，再让它对，最后让它快][wrf]

其中“能跑”是让测试通过，“对”是重构代码，“快”是优化代码，比如让它运行得更快。只有先让它能跑、让它对，我们才能去“让它快”。我们很幸运，拿到的代码已经被证明能跑，也不需要重构。但在那两步完成之前，绝不该急着“让它快”，因为

> [过早优化是万恶之源][popt]
> -- Donald Knuth

[DI]: dependency-injection.md
[wrf]: http://wiki.c2.com/?MakeItWorkMakeItRightMakeItFast
[godoc_race_detector]: https://blog.golang.org/race-detector
[popt]: http://wiki.c2.com/?PrematureOptimization
