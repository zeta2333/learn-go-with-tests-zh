# 验收测试入门

在 `$WORK`，我们的服务最近总绕不开一个需求："优雅关停"（graceful shutdown）。优雅关停确保你的系统在被终止之前，把手头的工作妥妥当当地收尾。打个现实中的比方：就像通话的人会把电话好好讲完、体面收尾，再去赶下一个会，而不是话说到一半就直接挂断。

本章会以 HTTP 服务器为语境介绍优雅关停，并讲讲如何编写"验收测试"，让你对自己代码的行为更有底气。

读完本章，你会知道如何带着出色的测试分享包、如何减少维护投入、如何对自己工作的质量更有信心。

## 关于 Kubernetes，知道这么多就够了

我们的软件跑在 [Kubernetes](https://kubernetes.io/)（K8s）上。K8s 会出于各种原因终止 "Pod"（实践中就是我们的软件），最常见的一种就是推了新代码要部署。

我们对照 [DORA 指标](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance)给自己立了很高的标准，因此我们的工作方式是：每天多次向生产环境部署小的、渐进式的改进和功能。

当 k8s 想终止一个 Pod 时，它会启动一个["终止生命周期"](https://cloud.google.com/blog/products/containers-kubernetes/kubernetes-best-practices-terminating-with-grace)，其中一环就是向我们的软件发送 SIGTERM 信号。这是 k8s 在对我们的代码说：

> 你得把自己关停，手头在做的活儿都收好尾，因为"宽限期"（grace period）一过，我就会送上 `SIGKILL`，到时候你就熄灯走人了。

一旦收到 `SIGKILL`，你的程序正在做的任何工作都会被立即叫停。

## 如果不留体面

取决于你软件的性质，如果无视 `SIGTERM`，就可能碰上麻烦。

我们碰到的具体问题出在还在处理中的 HTTP 请求上。自动化测试正在调用我们的 API 时，如果 k8s 决定停掉 Pod，服务器就会死掉，测试收不到服务器的响应，于是测试失败。

这会在我们的事故告警频道里触发一条告警，得有位开发者放下手头的活儿去处理问题。这种时有时无的失败既烦人又让人分心，对团队是个不小的干扰。

这些问题并不只困扰我们的测试。如果用户向你的系统发了一个请求，进程却在半路被终止，用户迎面撞上的多半是一个 5xx HTTP 错误——这可不是你想交付的用户体验。

## 留足体面的时候

我们想要做的是监听 `SIGTERM`，不去立刻杀掉服务器，而是：

- 不再接收任何新请求
- 让在途的请求跑完
- *然后*再终止进程

## 如何做到体面

庆幸的是，Go 早就内置了优雅关停服务器的机制：[net/http/Server.Shutdown](https://pkg.go.dev/net/http#Server.Shutdown)。

> Shutdown 会优雅地关停服务器，且不打断任何活动连接。它的工作方式是：先关闭所有打开的监听器，再关闭所有空闲连接，然后无限期地等待各条连接回到空闲状态并将其关闭。如果提供的 context 在关停完成前到期，Shutdown 会返回 context 的错误；否则返回关闭 Server 底层 Listener 时返回的错误。

要处理 `SIGTERM`，可以用 [os/signal.Notify](https://pkg.go.dev/os/signal#Notify)，它会把收到的信号发送到我们提供的 channel。

有了标准库的这两个功能，你就能监听 `SIGTERM` 并优雅地关停。

## 优雅关停包

为此，我写了 [https://pkg.go.dev/github.com/quii/go-graceful-shutdown](https://pkg.go.dev/github.com/quii/go-graceful-shutdown)。它为 `*http.Server` 提供了一个装饰器函数（decorator），在检测到 `SIGTERM` 信号时调用其 `Shutdown` 方法：

```go
func main() {
	var (
		ctx        = context.Background()
		httpServer = &http.Server{Addr: ":8080", Handler: http.HandlerFunc(acceptancetests.SlowHandler)}
		server     = gracefulshutdown.NewServer(httpServer)
	)

	if err := server.ListenAndServe(ctx); err != nil {
		// 通常是因为 ctx 截止前响应没来得及写完才会走到这里，没什么能做的
		log.Fatalf("uh oh, didn't shutdown gracefully, some responses may have been lost %v", err)
	}

	// 希望你看到的永远是下面这条
	log.Println("shutdown gracefully! all responses were sent")
}
```

代码的细节对本次阅读来说不太重要，不过继续往下之前，值得把代码快速过上一眼。

## 测试与反馈循环

写 `gracefulshutdown` 包的时候，我们有单元测试证明它行为正确，这给了我们大胆重构的底气。然而，要说它**真的**能行，我们心里还是没那么"有底"。

我们加了一个 `cmd` 包，写了一个真正的程序来使用这个正在开发中的包。手动把它跑起来，向它发一个 HTTP 请求，然后送一个 `SIGTERM`，看看会发生什么。

**你内心的工程师应该已经对手动测试感到不自在了**。
它无聊、无法规模化、不准确，而且浪费。如果你在写一个打算分享出去的包，同时又想让它保持简单、改动起来便宜，手动测试根本撑不住场面。

## 验收测试

如果你已经读过本书的其他章节，你写的基本都是"单元测试"。单元测试是一件极好的工具：让重构无所畏惧、驱动出良好的模块化设计、防止回归、带来快速反馈。

顾名思义，它们只测系统中很小的局部。通常，只靠单元测试是*不够的*，不足以构成一套有效的测试策略。别忘了，我们要让系统**随时可发布**。手动测试靠不住，所以我们需要另一种测试：**验收测试**。

### 什么是验收测试？

验收测试是一种"黑盒测试"（black-box test），有时也被称作"功能测试"（functional tests）。它们应当像系统的一个用户那样去行使系统。

"黑盒"的意思是：测试代码接触不到系统的内部构造，只能使用它的公开接口，并对观察到的行为做断言。这意味着它们只能把系统当作一个整体来测。

这是一个优点，因为这意味着测试和真实用户以完全相同的方式行使系统，它没法走什么特殊捷径让测试通过，却证明不了你真正要证明的东西。这跟另一条原则异曲同工：单元测试文件最好放在独立的外部测试包里，比如 `package mypkg_test` 而不是 `package mypkg`。

### 验收测试的好处

- 它们通过时，你就知道整个系统的行为符合你的预期。
- 比手动测试更精确、更快、更省力。
- 写得好的话，它们就是一份精确且经过验证的系统文档。它不会掉进"文档与系统真实行为渐行渐远"的陷阱。
- 不用 mock！一切都是真的。

### 与单元测试相比的潜在缺点

- 编写成本高。
- 运行时间更长。
- 受系统设计的制约。
- 失败时通常不告诉你根因（root cause），调试起来可能很费劲。
- 它们不提供关于系统内部质量的反馈。哪怕你写的是一坨垃圾，验收测试照样能通过。
- 由于黑盒的天性，并非所有场景都能实际覆盖到。

正因如此，只依赖验收测试是不明智的。它们不具备单元测试的许多优点，一个堆满验收测试的系统，往往会在维护成本和前置时间（lead time）上吃尽苦头。

#### 前置时间（lead time）？

前置时间指的是从一次 commit 合入主干，到部署进生产环境需要多久。这个数字因团队而异，有的要几周甚至几个月，有的只要几分钟。再说一次，`$WORK` 很看重 DORA 的研究结论，我们要把前置时间控制在 10 分钟以内。

想让系统可靠、前置时间漂亮，需要一套均衡的测试策略，人们通常用[测试金字塔](https://martinfowler.com/articles/practical-test-pyramid.html)（Test Pyramid）来描述它。

## 如何编写基本的验收测试

这些跟最初的问题有什么关系？我们这里刚写了一个包，而且它完全可以做单元测试。

正如我所说，单元测试给不了我们所需的全部信心。我们想*真正*确信：这个包与一个真实运行的程序集成之后也能正常工作。我们手动做的那些检查，理应能够自动化。

来看看这个测试用的程序：

```go
func main() {
	var (
		ctx        = context.Background()
		httpServer = &http.Server{Addr: ":8080", Handler: http.HandlerFunc(acceptancetests.SlowHandler)}
		server     = gracefulshutdown.NewServer(httpServer)
	)

	if err := server.ListenAndServe(ctx); err != nil {
		// 通常是因为 ctx 截止前响应没来得及写完才会走到这里，没什么能做的
		log.Fatalf("uh oh, didn't shutdown gracefully, some responses may have been lost %v", err)
	}

	// 希望你看到的永远是下面这条
	log.Println("shutdown gracefully! all responses were sent")
}
```

你可能已经猜到了，`SlowHandler` 里有一个 `time.Sleep` 用来拖延响应，好让我有时间送出 `SIGTERM`、看看会发生什么。剩下的都是些样板代码：

- 创建一个 `net/http/Server`；
- 用库把它包一层（参见：[装饰器模式](https://en.wikipedia.org/wiki/Decorator_pattern)）；
- 用包装后的版本去 `ListenAndServe`。

### 验收测试的高层次步骤

- 编译程序
- 运行它（并等它监听上 `8080` 端口）
- 向服务器发送一个 HTTP 请求
- 趁服务器还没来得及发回 HTTP 响应，送出 `SIGTERM`
- 看看我们是否还能收到响应

### 编译并运行程序

```go
package acceptancetests

import (
	"fmt"
	"math/rand"
	"net"
	"os"
	"os/exec"
	"path/filepath"
	"syscall"
	"time"
)

const (
	baseBinName = "temp-testbinary"
)

func LaunchTestProgram(port string) (cleanup func(), sendInterrupt func() error, err error) {
	binName, err := buildBinary()
	if err != nil {
		return nil, nil, err
	}

	sendInterrupt, kill, err := runServer(binName, port)

	cleanup = func() {
		if kill != nil {
			kill()
		}
		os.Remove(binName)
	}

	if err != nil {
		cleanup() // 即便没能正常监听，程序可能仍在运行
		return nil, nil, err
	}

	return cleanup, sendInterrupt, nil
}

func buildBinary() (string, error) {
	binName := randomString(10) + "-" + baseBinName

	build := exec.Command("go", "build", "-o", binName)

	if err := build.Run(); err != nil {
		return "", fmt.Errorf("cannot build tool %s: %s", binName, err)
	}
	return binName, nil
}

func runServer(binName string, port string) (sendInterrupt func() error, kill func(), err error) {
	dir, err := os.Getwd()
	if err != nil {
		return nil, nil, err
	}

	cmdPath := filepath.Join(dir, binName)

	cmd := exec.Command(cmdPath)

	if err := cmd.Start(); err != nil {
		return nil, nil, fmt.Errorf("cannot run temp converter: %s", err)
	}

	kill = func() {
		_ = cmd.Process.Kill()
	}

	sendInterrupt = func() error {
		return cmd.Process.Signal(syscall.SIGTERM)
	}

	err = waitForServerListening(port)

	return
}

func waitForServerListening(port string) error {
	for i := 0; i < 30; i++ {
		conn, _ := net.Dial("tcp", net.JoinHostPort("localhost", port))
		if conn != nil {
			conn.Close()
			return nil
		}
		time.Sleep(100 * time.Millisecond)
	}
	return fmt.Errorf("nothing seems to be listening on localhost:%s", port)
}

func randomString(n int) string {
	var letters = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

	s := make([]rune, n)
	for i := range s {
		s[i] = letters[rand.Intn(len(letters))]
	}
	return string(s)
}
```

`LaunchTestProgram` 负责这些事：

- 编译程序
- 启动程序
- 等它监听上 `8080` 端口
- 提供一个 `cleanup` 函数，用来杀掉程序并把它删除，确保测试结束时留下一个干净的环境
- 提供一个 `interrupt` 函数，用来向程序发送 `SIGTERM`，让我们能测试目标行为

平心而论，这段代码算不上世界上最好看的代码，但你只需要关注导出函数 `LaunchTestProgram`，它调用的那些非导出函数都是乏味的样板代码。

如前所述，验收测试的搭建往往更麻烦。而这段代码确实让*测试*代码本身易读了许多；况且验收测试常常是这样：仪式性的代码一旦写完，就完事了，你尽可以把它忘掉。

### 验收测试（们）

我们想给两个程序各写一个验收测试：一个有优雅关停，一个没有，这样我们自己（还有读者）就能看到二者行为的差别。有了 `LaunchTestProgram` 负责编译和运行程序，给两者写验收测试都相当简单，一些辅助函数还让我们享受到了复用的好处。

下面是*有*优雅关停的服务器的测试，[没有的那个可以到 GitHub 上找](https://github.com/quii/go-graceful-shutdown/blob/main/acceptancetests/withoutgracefulshutdown/main_test.go)。

```go
package main

import (
	"testing"
	"time"

	"github.com/quii/go-graceful-shutdown/acceptancetests"
	"github.com/quii/go-graceful-shutdown/assert"
)

const (
	port = "8080"
	url  = "<http://localhost:" + port
)

func TestGracefulShutdown(t *testing.T) {
	cleanup, sendInterrupt, err := acceptancetests.LaunchTestProgram(port)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(cleanup)

	// 先确认一下，关停之前服务器是好使的
	assert.CanGet(t, url)

	// 发出一个请求，趁它还没来得及响应就发送 SIGTERM。
	time.AfterFunc(50*time.Millisecond, func() {
		assert.NoError(t, sendInterrupt())
	})
	// 若没有优雅关停，这里会失败
	assert.CanGet(t, url)

	// 中断之后，服务器应当已经关停，再发请求就不行了
	assert.CantGet(t, url)
}
```

搭建过程封装好之后，这些测试就既全面、又能描述行为，读起来也相对轻松。

`assert.CanGet/CantGet` 是我为这套测试写的辅助函数，用来让这个常见断言不重复（DRY）。

```go
func CanGet(t testing.TB, url string) {
	errChan := make(chan error)

	go func() {
		res, err := http.Get(url)
		if err != nil {
			errChan <- err
			return
		}
		res.Body.Close()
		errChan <- nil
	}()

	select {
	case err := <-errChan:
		NoError(t, err)
	case <-time.After(3 * time.Second):
		t.Errorf("timed out waiting for request to %q", url)
	}
}
```

它会在一个 goroutine 上向 URL 发出一个 `GET`，如果在 3 秒内无错误地收到响应，测试就不会失败。`CantGet` 为省篇幅略去不贴，[你可以在这里到 GitHub 上查看](https://github.com/quii/go-graceful-shutdown/blob/main/assert/assert.go#L61)。

再强调一次很重要的一点：编写验收测试所需的一切工具，Go 都开箱即用。你*不必*借助任何特殊框架来搭建验收测试。

### 小投入，大回报

有了这些测试，读者看到示例程序时就能相信这个示例*确实*能跑起来，进而对这个包所宣称的能力有信心。

更重要的是，作为作者，我们获得了**快速反馈**和**巨大的信心**：这个包在真实场景下是好使的。

```shell
go test -count=1 ./...
ok  	github.com/quii/go-graceful-shutdown	0.196s
?   	github.com/quii/go-graceful-shutdown/acceptancetests	[no test files]
ok  	github.com/quii/go-graceful-shutdown/acceptancetests/withgracefulshutdown	4.785s
ok  	github.com/quii/go-graceful-shutdown/acceptancetests/withoutgracefulshutdown	2.914s
?   	github.com/quii/go-graceful-shutdown/assert	[no test files]
```

## 总结

本章把验收测试装进了你的测试工具箱。当你开始构建真实的系统时，它们弥足珍贵，也是单元测试的重要补充。

*如何*编写验收测试，取决于你在构建什么样的系统，但原则始终不变：把你的系统当成一个"黑盒"。如果你在做网站，测试就应当像个用户那样行动，你会需要 Selenium 这样的无头浏览器，去点链接、填表单等等。如果是 RESTful API，就用客户端发送 HTTP 请求。

### 在更复杂的系统上更进一步

不那么简单的系统，通常不是我们讨论的这种单进程应用。一般来说，你会依赖其他系统，比如数据库。对这些场景，你需要把本地测试环境的搭建自动化。像 [docker-compose](https://docs.docker.com/compose/) 这样的工具，很适合在本地把你运行系统所需的环境起成一个个容器。

### 下一章

在这一篇里，验收测试是事后补写的。而在 [Growing Object-Oriented Software](http://www.growing-object-oriented-software.com) 中，作者们展示了另一条路：以测试驱动的方式使用验收测试，让它充当指引我们工作的"北极星"。

随着系统越来越复杂，编写和维护验收测试的成本可能迅速失控。开发团队被昂贵的验收测试套件拖得举步维艰的故事，数不胜数。

下一章将介绍如何用验收测试来引导我们的设计，以及管理验收测试成本的原则和技巧。

### 提升开源项目的质量

如果你在写打算分享出去的包，我鼓励你写一些简单的示例程序来展示你的包能做什么，并花点时间配上一目了然的验收测试，给自己、也给未来使用你作品的人一份信心。

就像[可测试示例](https://go.dev/blog/examples)一样，在开发者体验上多花的这点小心思，对建立他人对你工作的信任大有帮助，也能降低你自己的维护成本。

## 替 `$WORK` 打个招聘广告

如果你想在一个大家伙一起解决有趣问题的环境里工作，住在伦敦或波尔图附近或周边，又喜欢本章和本书的内容——欢迎[来 Twitter 上找我](https://twitter.com/quii)，说不定我们很快就能共事了！
