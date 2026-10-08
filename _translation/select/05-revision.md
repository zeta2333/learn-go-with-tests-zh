# Select

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/select)**

这次你的任务是写一个叫 `WebsiteRacer` 的函数：接收两个 URL，让它们“竞速”——各发一个 HTTP GET，返回先返回结果的那个 URL。如果 10 秒内两个都没有返回，就返回一个 `error`。

为此我们会用到：

- `net/http`，用来发起 HTTP 调用
- `net/http/httptest`，帮我们测试这些调用
- goroutine（Go 的轻量级并发单元）
- `select`，用来同步各个流程

## 先写测试

先从一个朴素的版本起步，跑通再说。

```go
func TestRacer(t *testing.T) {
	slowURL := "http://www.facebook.com"
	fastURL := "http://www.quii.dev"

	want := fastURL
	got := Racer(slowURL, fastURL)

	if got != want {
		t.Errorf("got %q, want %q", got, want)
	}
}
```

我们知道它并不完美，也有不少问题，但这是个开始。重要的是别一上来就执着于一步到位。

## 试着运行测试

`./racer_test.go:14:9: undefined: Racer`

## 写最少的代码让测试能运行，并检查失败的测试输出

```go
func Racer(a, b string) (winner string) {
	return
}
```

`racer_test.go:25: got '', want 'http://www.quii.dev'`

## 写足够的代码让测试通过

```go
func Racer(a, b string) (winner string) {
	startA := time.Now()
	resp, err := http.Get(a)
	if err == nil {
		resp.Body.Close()
	}
	aDuration := time.Since(startA)

	startB := time.Now()
	resp, err = http.Get(b)
	if err == nil {
		resp.Body.Close()
	}
	bDuration := time.Since(startB)

	if aDuration < bDuration {
		return a
	}

	return b
}
```

对每个 URL：

1. 我们用 `time.Now()` 在尝试获取 `URL` 之前记下当前时间。
1. 然后用 [`http.Get`](https://golang.org/pkg/net/http/#Client.Get) 尝试对这个 `URL` 发起 HTTP `GET` 请求。这个函数会返回一个 [`http.Response`](https://golang.org/pkg/net/http/#Response) 和一个 `error`。我们要关闭响应体，避免泄漏文件描述符（file descriptor）——不关的话，每个请求都会留下一个一直开着的连接。
1. `time.Since` 接收起始时间，返回一个表示两者之差的 `time.Duration`。

都测完之后，比较一下两段耗时，看谁最快就清楚了。

### 问题

这个测试你跑起来可能过，也可能不过。问题在于：为了测试我们自己的逻辑，我们却去访问了真实的网站。

测试会用到 HTTP 的代码太常见了，所以 Go 在标准库里就准备了帮你测试它的工具。

在 mock 和依赖注入那几章里我们讲过：理想情况下，我们不应该依赖外部服务来测试自己的代码，因为它们可能

- 很慢
- 不稳定（flaky）
- 没法测边界情况

标准库里有一个叫 [`net/http/httptest`](https://golang.org/pkg/net/http/httptest/) 的包，能让你轻松创建 mock HTTP 服务器。

我们把测试改成用 mock，这样就有一批可靠、可控的服务器可以用来测试了。

```go
func TestRacer(t *testing.T) {

	slowServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(20 * time.Millisecond)
		w.WriteHeader(http.StatusOK)
	}))

	fastServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))

	slowURL := slowServer.URL
	fastURL := fastServer.URL

	want := fastURL
	got := Racer(slowURL, fastURL)

	if got != want {
		t.Errorf("got %q, want %q", got, want)
	}

	slowServer.Close()
	fastServer.Close()
}
```

这段语法看着可能有点密，慢慢来就好。

`httptest.NewServer` 接收一个 `http.HandlerFunc`，我们这里用*匿名函数*（anonymous function）把它传进去。

`http.HandlerFunc` 是这样一个类型：`type HandlerFunc func(ResponseWriter, *Request)`。

说白了，它要的就是一个接收 `ResponseWriter` 和 `Request` 的函数——对一个 HTTP 服务器来说，这没什么好意外的。

其实这里压根没有额外的魔法，**用 Go 写一个*真正的* HTTP 服务器也是这么写的**。唯一的区别是我们把它包在了 `httptest.NewServer` 里，这让它在测试中更好用：它会自动找一个空闲端口来监听，测试完你随手关掉就行。

在这两个服务器的处理函数里，我们让慢的那个在收到请求时先 `time.Sleep` 一小段时间，好让它比另一个慢。随后两个服务器都用 `w.WriteHeader(http.StatusOK)` 给调用方写回一个 `OK` 响应。

现在再跑测试，肯定能通过，而且应该更快了。动手改改这些 sleep 的时长，故意把测试弄挂看看。

## 重构

生产代码和测试代码里都有一些重复。

```go
func Racer(a, b string) (winner string) {
	aDuration := measureResponseTime(a)
	bDuration := measureResponseTime(b)

	if aDuration < bDuration {
		return a
	}

	return b
}

func measureResponseTime(url string) time.Duration {
	start := time.Now()
	resp, err := http.Get(url)
	if err == nil {
		resp.Body.Close()
	}
	return time.Since(start)
}
```

这一番 DRY（消除重复）下来，`Racer` 的代码好读多了。

```go
func TestRacer(t *testing.T) {

	slowServer := makeDelayedServer(20 * time.Millisecond)
	fastServer := makeDelayedServer(0 * time.Millisecond)

	defer slowServer.Close()
	defer fastServer.Close()

	slowURL := slowServer.URL
	fastURL := fastServer.URL

	want := fastURL
	got := Racer(slowURL, fastURL)

	if got != want {
		t.Errorf("got %q, want %q", got, want)
	}
}

func makeDelayedServer(delay time.Duration) *httptest.Server {
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(delay)
		w.WriteHeader(http.StatusOK)
	}))
}
```

我们把创建 fake 服务器的代码重构成了一个叫 `makeDelayedServer` 的函数，把测试里那些无趣的代码挪出去，顺便减少重复。

### `defer`

在函数调用前面加上 `defer`，这个调用就会推迟到*外层函数结束的时刻*才执行。

有时你需要清理资源，比如关闭文件，或者像我们这里这样关掉服务器，免得它继续占着端口监听。

你希望这个操作在函数末尾才执行，但又想让这行代码留在创建服务器的地方，方便以后读代码的人。

就目前学过的 Go 特性而言，我们的重构已经算是一种改进、一个合理的方案了，但我们还能让方案更简单。

### 同步流程

- Go 明明这么擅长并发，为什么还要一个接一个地测网站速度？我们应该能同时测两个。
- 我们其实并不在乎请求*具体的响应时间*，只想知道哪个先回来。

为此，我们要引入一个新的语法结构 `select`，它能帮我们非常简单、清晰地同步各个流程。

```go
func Racer(a, b string) (winner string) {
	select {
	case <-ping(a):
		return a
	case <-ping(b):
		return b
	}
}

func ping(url string) chan struct{} {
	ch := make(chan struct{})
	go func() {
		resp, err := http.Get(url)
		if err == nil {
			resp.Body.Close()
		}
		close(ch)
	}()
	return ch
}
```

#### `ping`

我们定义了一个 `ping` 函数，它创建一个 `chan struct{}` 并返回。

在这个场景里，我们*不在乎*往 channel（通道）里发的是什么类型，*只想发出“我做完了”的信号*，而关闭 channel 恰好能完美地做到这一点！

为什么用 `struct{}` 而不是 `bool` 之类的其他类型？这么说吧，从内存的角度看，`chan struct{}` 用的是最小的数据类型，相比 `bool` 不会带来任何内存分配。既然我们只是关闭 channel、不在上面发送任何东西，又何必分配内存呢？

在同一个函数里，我们启动一个 goroutine，等 `http.Get(url)` 一完成它就往 channel 里发信号。响应体会被立刻关闭——我们只关心请求有没有完成，不关心响应内容，而让响应体一直开着会泄漏文件描述符。

##### 一定要用 `make` 创建 channel

注意，创建 channel 必须用 `make`，而不是写成 `var ch chan struct{}`。用 `var` 声明的变量会被初始化为该类型的“零值”：`string` 是 `""`，`int` 是 0，等等。

channel 的零值是 `nil`，如果你试图用 `<-` 向它发送数据，它会永远阻塞下去，因为你无法向 `nil` channel 发送数据

[你可以在 The Go Playground 里看到这个效果](https://play.golang.org/p/IIbeAox5jKA)

#### `select`

你应该还记得并发那一章讲过：可以用 `myVar := <-ch` 等待值被发送到 channel。这是一个*阻塞*（blocking）调用，因为你在等一个值。

`select` 让你可以同时等待*多个* channel。第一个发来值的 channel 就“获胜”了，它对应的 `case` 下面的代码就会执行。

我们在 `select` 里用 `ping` 建起两个 channel，每个 `URL` 一个。谁先往自己的 channel 里写入，`select` 就执行谁的那段代码，返回的就是它的 `URL`（赢的就是它）。

经过这些改动，代码背后的意图一目了然，实现反倒更简单了。

### 超时

我们的最后一个需求是：如果 `Racer` 耗时超过 10 秒，就返回一个 error。

## 先写测试

```go
func TestRacer(t *testing.T) {
	t.Run("compares speeds of servers, returning the url of the fastest one", func(t *testing.T) {
		slowServer := makeDelayedServer(20 * time.Millisecond)
		fastServer := makeDelayedServer(0 * time.Millisecond)

		defer slowServer.Close()
		defer fastServer.Close()

		slowURL := slowServer.URL
		fastURL := fastServer.URL

		want := fastURL
		got, _ := Racer(slowURL, fastURL)

		if got != want {
			t.Errorf("got %q, want %q", got, want)
		}
	})

	t.Run("returns an error if a server doesn't respond within 10s", func(t *testing.T) {
		serverA := makeDelayedServer(11 * time.Second)
		serverB := makeDelayedServer(12 * time.Second)

		defer serverA.Close()
		defer serverB.Close()

		_, err := Racer(serverA.URL, serverB.URL)

		if err == nil {
			t.Error("expected an error but didn't get one")
		}
	})
}
```

我们让测试服务器花超过 10 秒才返回，就是为了演练这个场景；现在我们期望 `Racer` 返回两个值：获胜的 URL（在这个测试里用 `_` 忽略掉）和一个 `error`。

注意，我们在原本那个测试里也处理了 error 返回值——眼下先用 `_` 接住，保证测试能跑起来。

## 试着运行测试

`./racer_test.go:37:10: assignment mismatch: 2 variables but Racer returns 1 value`

## 写最少的代码让测试能运行，并检查失败的测试输出

```go
func Racer(a, b string) (winner string, error error) {
	select {
	case <-ping(a):
		return a, nil
	case <-ping(b):
		return b, nil
	}
}
```

把 `Racer` 的签名改成返回获胜者和一个 `error`。正常情况（happy case）下返回 `nil`。

现在运行的话，等上 11 秒它就会失败。

```
--- FAIL: TestRacer (12.00s)
    --- FAIL: TestRacer/returns_an_error_if_a_server_doesn't_respond_within_10s (12.00s)
        racer_test.go:40: expected an error but didn't get one
```

## 写足够的代码让测试通过

```go
func Racer(a, b string) (winner string, error error) {
	select {
	case <-ping(a):
		return a, nil
	case <-ping(b):
		return b, nil
	case <-time.After(10 * time.Second):
		return "", fmt.Errorf("timed out waiting for %s and %s", a, b)
	}
}
```

用 `select` 的时候，`time.After` 是个非常顺手的函数。虽然我们这个场景没碰上，但你完全可能写出这样的代码：监听的 channel 一直没有值传来，程序就永远阻塞下去。`time.After` 会返回一个 `chan`（就像 `ping` 那样），并在你设定的时间过去之后往里面发一个信号。

对我们来说这正合适：如果 `a` 或 `b` 先返回了，它们获胜；但如果拖到了 10 秒，`time.After` 就会发出信号，我们随即返回一个 `error`。

### 慢测试

现在的问题是这个测试要跑 10 秒钟。就这么一点简单的逻辑，这个代价让人不太舒服。

一个办法是让超时时间可配置。这样测试里可以用一个很短的超时，等代码真正用到真实环境里，再设成 10 秒。

```go
func Racer(a, b string, timeout time.Duration) (winner string, error error) {
	select {
	case <-ping(a):
		return a, nil
	case <-ping(b):
		return b, nil
	case <-time.After(timeout):
		return "", fmt.Errorf("timed out waiting for %s and %s", a, b)
	}
}
```

现在测试编译不过了，因为我们没有传超时参数。

先别急着冲过去给两个测试都补上默认值，我们先来*听听测试怎么说*。

- “happy” 那个测试真的在乎超时吗？
- 需求里对超时可是写得明明白白的。

想清楚这些，我们来做一点小重构，既体贴测试，也体贴使用我们代码的人。

```go
var tenSecondTimeout = 10 * time.Second

func Racer(a, b string) (winner string, error error) {
	return ConfigurableRacer(a, b, tenSecondTimeout)
}

func ConfigurableRacer(a, b string, timeout time.Duration) (winner string, error error) {
	select {
	case <-ping(a):
		return a, nil
	case <-ping(b):
		return b, nil
	case <-time.After(timeout):
		return "", fmt.Errorf("timed out waiting for %s and %s", a, b)
	}
}
```

用户和第一个测试可以继续用 `Racer`（它在底层调用 `ConfigurableRacer`），异常路径（sad path）的测试则用 `ConfigurableRacer`。

```go
func TestRacer(t *testing.T) {

	t.Run("compares speeds of servers, returning the url of the fastest one", func(t *testing.T) {
		slowServer := makeDelayedServer(20 * time.Millisecond)
		fastServer := makeDelayedServer(0 * time.Millisecond)

		defer slowServer.Close()
		defer fastServer.Close()

		slowURL := slowServer.URL
		fastURL := fastServer.URL

		want := fastURL
		got, err := Racer(slowURL, fastURL)

		if err != nil {
			t.Fatalf("did not expect an error but got one %v", err)
		}

		if got != want {
			t.Errorf("got %q, want %q", got, want)
		}
	})

	t.Run("returns an error if a server doesn't respond within the specified time", func(t *testing.T) {
		server := makeDelayedServer(25 * time.Millisecond)

		defer server.Close()

		_, err := ConfigurableRacer(server.URL, server.URL, 20*time.Millisecond)

		if err == nil {
			t.Error("expected an error but didn't get one")
		}
	})
}
```

我在第一个测试里加了最后一道检查，确认不会拿到 `error`。

## 总结

### `select`

- 帮你同时等待多个 channel。
- 有时你需要在某个 `case` 里加上 `time.After`，以免系统永远阻塞下去。

### `httptest`

- 一种创建测试服务器的便捷方式，让你拥有可靠、可控的测试。
- 与“真正的” `net/http` 服务器共用同一套接口，既保持一致，你要学的东西也更少。
