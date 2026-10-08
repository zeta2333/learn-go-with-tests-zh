# 依赖注入

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/di)**

本章假定你已经读过[结构体一章](./structs-methods-and-interfaces.md)，因为接下来会用到一些接口方面的知识。

程序员圈子里对依赖注入（DI）的误解*多得很*。希望这份指南能让你看到：

* 你不需要什么框架
* 它不会把你的设计搞复杂
* 它让测试变得容易
* 它让你能写出漂亮、通用的函数。

我们想写一个向某人打招呼的函数，就像我们在 hello-world 章里做的那样，只不过这一次，我们要测试的是*实际的打印动作*。

先简单回顾一下，这个函数大概长这样

```go
func Greet(name string) {
	fmt.Printf("Hello, %s", name)
}
```

可这要怎么测试呢？调用 `fmt.Printf` 会打印到标准输出，而用测试框架去捕获它相当困难。

我们要做的，是能够**注入**（说白了就是"传个参数"，只是叫法高级了点）打印这项依赖。

**我们的函数不需要关心打印发生在*哪里*、*如何*发生，所以我们应该接受一个*接口*，而不是某个具体类型（concrete type）。**

这样做之后，我们就可以把实现改成打印到某个我们可控的东西上，从而能够测试它。在"真实世界"里，你会注入一个写到标准输出的东西。

如果你去看看 [`fmt.Printf`](https://pkg.go.dev/fmt#Printf) 的源码，就能发现一个可以切入的点

```go
// 它返回写入的字节数，以及遇到的任何写入错误。
func Printf(format string, a ...interface{}) (n int, err error) {
	return Fprintf(os.Stdout, format, a...)
}
```

有意思！`Printf` 在底层其实只是调用了 `Fprintf`，并把 `os.Stdout` 传了进去。

`os.Stdout` 到底*是*个什么东西？`Fprintf` 又希望第一个参数传进来的是什么呢？

```go
func Fprintf(w io.Writer, format string, a ...interface{}) (n int, err error) {
	p := newPrinter()
	p.doPrintf(format, a)
	n, err = w.Write(p.buf)
	p.free()
	return
}
```

一个 `io.Writer`——`io` 包里定义的接口（interface）

```go
type Writer interface {
	Write(p []byte) (n int, err error)
}
```

由此我们可以推断：`os.Stdout` 实现了 `io.Writer`；`Printf` 把 `os.Stdout` 传给了 `Fprintf`，而 `Fprintf` 期望的正是一个 `io.Writer`。

随着你写的 Go 代码越来越多，你会发现这个接口频繁现身，因为它是一个极好的通用接口，专管"把这份数据放到某个地方去"。

于是我们知道，底层最终是在用 `Writer` 把问候语发送到某处。那就用上这个现成的抽象，让我们的代码可测试、更可复用吧。

## 先写测试

```go
func TestGreet(t *testing.T) {
	buffer := bytes.Buffer{}
	Greet(&buffer, "Chris")

	got := buffer.String()
	want := "Hello, Chris"

	if got != want {
		t.Errorf("got %q want %q", got, want)
	}
}
```

`bytes` 包里的 `Buffer` 类型实现了 `Writer` 接口，因为它拥有 `Write(p []byte) (n int, err error)` 这个方法。

所以我们在测试里就把它当作我们的 `Writer` 传进去，等调用完 `Greet` 之后，就能检查里面写入了什么

## 试着运行测试

测试编译不过

```text
./di_test.go:10:2: undefined: Greet
```

## 写最少量的代码让测试能跑起来，并检查失败的测试输出

*听编译器的话*，把问题修掉。

```go
func Greet(writer *bytes.Buffer, name string) {
	fmt.Printf("Hello, %s", name)
}
```

`Hello, Chris di_test.go:16: got '' want 'Hello, Chris'`

测试失败了。注意，name 是打印出来了，但它打到了标准输出上。

## 写足够的代码让它通过

用这个 writer 把问候语发到我们测试里的 buffer。记住，`fmt.Fprintf` 跟 `fmt.Printf` 很像，只不过它要多接收一个 `Writer` 来指定字符串的去处，而 `fmt.Printf` 默认写到标准输出。

```go
func Greet(writer *bytes.Buffer, name string) {
	fmt.Fprintf(writer, "Hello, %s", name)
}
```

测试现在通过了。

## 重构

刚才编译器让我们传入一个指向 `bytes.Buffer` 的指针。这在技术上没错，但用处不大。

为了说明这一点，试着把 `Greet` 函数接进一个 Go 应用，让它打印到标准输出。

```go
func main() {
	Greet(os.Stdout, "Elodie")
}
```

`./di.go:14:7: cannot use os.Stdout (type *os.File) as type *bytes.Buffer in argument to Greet`

正如前面讨论过的，`fmt.Fprintf` 允许你传入 `io.Writer`，而我们知道 `os.Stdout` 和 `bytes.Buffer` 都实现了它。

如果我们把代码改成使用这个更通用的接口，它现在就既能用在测试里，也能用在我们的应用程序里了。

```go
package main

import (
	"fmt"
	"io"
	"os"
)

func Greet(writer io.Writer, name string) {
	fmt.Fprintf(writer, "Hello, %s", name)
}

func main() {
	Greet(os.Stdout, "Elodie")
}
```

## 再聊聊 io.Writer

用 `io.Writer` 还能把数据写到哪些地方？我们的 `Greet` 函数到底有多通用？

### 互联网

运行下面的代码

```go
package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
)

func Greet(writer io.Writer, name string) {
	fmt.Fprintf(writer, "Hello, %s", name)
}

func MyGreeterHandler(w http.ResponseWriter, r *http.Request) {
	Greet(w, "world")
}

func main() {
	log.Fatal(http.ListenAndServe(":5001", http.HandlerFunc(MyGreeterHandler)))
}
```

运行程序，然后访问 [http://localhost:5001](http://localhost:5001)，你会看到自己的问候函数派上了用场。

HTTP 服务器会在后面的章节里讲到，所以细节暂时不用太操心。

编写 HTTP handler 时，你会拿到一个 `http.ResponseWriter`，以及发起这次请求所用的 `http.Request`。实现服务器时，你正是用这个 writer 把响应*写*出去的。

你大概能猜到，`http.ResponseWriter` 同样实现了 `io.Writer`，这正是我们能在 handler 里复用 `Greet` 函数的原因。

## 总结

我们最初的那版代码不好测试，因为它把数据写到了一个我们无法控制的地方。

*在测试的驱动下*，我们重构了代码，通过**注入依赖**来控制数据写到*哪里*，这让我们可以：

* **测试我们的代码** 如果一个函数*不容易*测试，通常是因为依赖硬编码在函数里，*或者*用了全局状态。如果某个服务层用到了一个全局的数据库连接池，相关代码多半很难测，测试跑起来也慢。DI 会促使你注入数据库依赖（通过接口），然后在测试里用可控的东西把它 mock 掉。
* **分离关注点**，把*数据去哪儿*和*怎么生成数据*解耦。如果你觉得某个方法/函数职责太多了（既生成数据*又*写数据库？既处理 HTTP 请求*又*做领域逻辑？），DI 多半就是你需要的那个工具。
* **让代码能在不同环境中复用** 我们的代码能派上用场的第一个"新"环境就是测试。再往后，如果有人想拿你的函数试试新东西，他们可以注入自己的依赖。

### 那 mock 呢？听说搞 DI 得用它，而且它还很邪恶

mock 的细节会在后面的章节展开（它并不邪恶）。mock 的用途，是把你注入的真实依赖换成一个假装的版本，在测试里既能控制它又能检查它。不过在咱们这个例子里，标准库早就备好了现成的东西给我们用。

### Go 标准库真的很棒，值得花时间研究

正因为对 `io.Writer` 接口有了几分熟悉，我们才能在测试里用 `bytes.Buffer` 充当 `Writer`，也才能换用标准库里的其他 `Writer`，把我们的函数用在命令行应用或 web 服务器里。

你对标准库越熟悉，就越容易发现这些通用接口，进而在自己的代码里复用它们，让你的软件在多种场景下都能复用。

这个例子深受 [The Go Programming language](https://www.amazon.co.uk/Programming-Language-Addison-Wesley-Professional-Computing/dp/0134190440) 中某一章的启发，如果你喜欢这一章，就去买一本吧！
