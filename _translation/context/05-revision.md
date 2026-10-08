# Context

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/context)**

软件经常需要启动一些长时间运行、很吃资源的进程（往往放在 goroutine 里）。如果触发这些进程的那个动作被取消（cancellation）了，或者出于某种原因失败了，你就需要在整个应用中以一致的方式把这些进程停下来。

要是放任不管，你那引以为傲、响应飞快的 Go 应用，可能就会开始出现难以排查的性能问题。

本章我们会用 `context` 包来帮助我们管理长时间运行的进程。

从一个经典的例子开始：一个 web server，每次被请求命中，都会启动一个可能耗时很长的进程去取一些数据，取到后再放进响应里返回。

我们要演练这样一个场景：用户在数据取回之前取消了请求，我们要确保那个进程收到通知、放弃手头的工作。

我已经在正常路径（happy path）上备好了一些代码，让我们有个起点。下面是 server 的代码：

```go
func Server(store Store) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprint(w, store.Fetch())
	}
}
```

`Server` 函数接收一个 `Store`，返回给我们一个 `http.HandlerFunc`。Store 的定义如下：

```go
type Store interface {
	Fetch() string
}
```

返回的那个函数会调用 `store` 的 `Fetch` 方法拿到数据，然后把它写进响应。

我们还有一个与之对应的 spy，会在测试里用到它：

```go
type SpyStore struct {
	response string
}

func (s *SpyStore) Fetch() string {
	return s.response
}

func TestServer(t *testing.T) {
	data := "hello, world"
	svr := Server(&SpyStore{data})

	request := httptest.NewRequest(http.MethodGet, "/", nil)
	response := httptest.NewRecorder()

	svr.ServeHTTP(response, request)

	if response.Body.String() != data {
		t.Errorf(`got "%s", want "%s"`, response.Body.String(), data)
	}
}
```

正常路径有了，接下来我们构造一个更现实的场景：用户取消了请求，而 `Store` 没能完成 `Fetch`。

## 先写测试

我们的 handler 需要有办法告诉 `Store` 取消手头的工作，所以先更新接口：

```go
type Store interface {
	Fetch() string
	Cancel()
}
```

接着要调整 spy：让它在返回 `data` 之前先花掉一点时间，并且提供一种途径让我们知道它被要求取消过。为了实现 `Store` 接口，它还必须把 `Cancel` 加为方法。

```go
type SpyStore struct {
	response  string
	cancelled bool
}

func (s *SpyStore) Fetch() string {
	time.Sleep(100 * time.Millisecond)
	return s.response
}

func (s *SpyStore) Cancel() {
	s.cancelled = true
}
```

我们来加一个新测试：在 100 毫秒之内取消请求，然后检查 store 有没有被取消。

```go
t.Run("tells store to cancel work if request is cancelled", func(t *testing.T) {
	data := "hello, world"
	store := &SpyStore{response: data}
	svr := Server(store)

	request := httptest.NewRequest(http.MethodGet, "/", nil)

	cancellingCtx, cancel := context.WithCancel(request.Context())
	time.AfterFunc(5*time.Millisecond, cancel)
	request = request.WithContext(cancellingCtx)

	response := httptest.NewRecorder()

	svr.ServeHTTP(response, request)

	if !store.cancelled {
		t.Error("store was not told to cancel")
	}
})
```

摘自 [Go 博客：Context](https://blog.golang.org/context)

> `context` 包提供了一些函数，可以从现有的 Context 值派生（derive）出新的 Context 值。这些值构成一棵树：当一个 Context 被取消时，由它派生的所有 Context 也都会被取消。

很重要的一点是，你的 context 都应当通过派生来创建，这样取消才能沿着相应请求的整个调用栈一路传播下去。

我们的做法是：从 `request` 派生出一个新的 `cancellingCtx`，同时得到一个 `cancel` 函数；然后用 `time.AfterFunc` 安排这个函数在 5 毫秒后被调用；最后调用 `request.WithContext`，把这个新的 context 用到请求上。

## 试着运行测试

测试如预期那样失败了。

```
--- FAIL: TestServer (0.00s)
    --- FAIL: TestServer/tells_store_to_cancel_work_if_request_is_cancelled (0.00s)
    	context_test.go:62: store was not told to cancel
```

## 写足够的代码让测试通过

记得守住 TDD 的纪律：只写*最少量的*代码让测试通过。

```go
func Server(store Store) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		store.Cancel()
		fmt.Fprint(w, store.Fetch())
	}
}
```

这样测试是过了，可总觉得不对劲，对吧？我们肯定不应该在*每一个请求*上都先调用 `Cancel()` 再去取数据。

正因为守了纪律，才暴露出我们测试里的一个缺陷，这是好事！

我们得更新正常路径的测试，断言 store *不会*被取消。

```go
t.Run("returns data from store", func(t *testing.T) {
	data := "hello, world"
	store := &SpyStore{response: data}
	svr := Server(store)

	request := httptest.NewRequest(http.MethodGet, "/", nil)
	response := httptest.NewRecorder()

	svr.ServeHTTP(response, request)

	if response.Body.String() != data {
		t.Errorf(`got "%s", want "%s"`, response.Body.String(), data)
	}

	if store.cancelled {
		t.Error("it should not have cancelled the store")
	}
})
```

把两个测试都跑一遍，这次正常路径的测试应该挂掉了，这下我们就被迫写出一个更合理的实现。

```go
func Server(store Store) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		ctx := r.Context()

		data := make(chan string, 1)

		go func() {
			data <- store.Fetch()
		}()

		select {
		case d := <-data:
			fmt.Fprint(w, d)
		case <-ctx.Done():
			store.Cancel()
		}
	}
}
```

我们在这里做了什么？

`context` 有一个 `Done()` 方法，它返回一个 channel，当 context "结束"（done）或者被"取消"（cancelled）时，这个 channel 会收到一个信号。我们要监听这个信号，一收到就调用 `store.Cancel`；但如果 `Store` 抢在信号之前完成了 `Fetch`，那就要无视它。

为了做到这一点，我们把 `Fetch` 放到一个 goroutine 里运行，它会把结果写进一个新的 channel `data`。然后我们用 `select`，实际上是让这两个异步过程赛跑，最终要么写出响应，要么调用 `Cancel`。

## 重构

我们可以把测试代码重构一下，把断言做成 spy 上的方法：

```go
type SpyStore struct {
	response  string
	cancelled bool
	t         *testing.T
}

func (s *SpyStore) assertWasCancelled() {
	s.t.Helper()
	if !s.cancelled {
		s.t.Error("store was not told to cancel")
	}
}

func (s *SpyStore) assertWasNotCancelled() {
	s.t.Helper()
	if s.cancelled {
		s.t.Error("store was told to cancel")
	}
}
```

记得创建 spy 时要把 `*testing.T` 传进去。

```go
func TestServer(t *testing.T) {
	data := "hello, world"

	t.Run("returns data from store", func(t *testing.T) {
		store := &SpyStore{response: data, t: t}
		svr := Server(store)

		request := httptest.NewRequest(http.MethodGet, "/", nil)
		response := httptest.NewRecorder()

		svr.ServeHTTP(response, request)

		if response.Body.String() != data {
			t.Errorf(`got "%s", want "%s"`, response.Body.String(), data)
		}

		store.assertWasNotCancelled()
	})

	t.Run("tells store to cancel work if request is cancelled", func(t *testing.T) {
		store := &SpyStore{response: data, t: t}
		svr := Server(store)

		request := httptest.NewRequest(http.MethodGet, "/", nil)

		cancellingCtx, cancel := context.WithCancel(request.Context())
		time.AfterFunc(5*time.Millisecond, cancel)
		request = request.WithContext(cancellingCtx)

		response := httptest.NewRecorder()

		svr.ServeHTTP(response, request)

		store.assertWasCancelled()
	})
}
```

这种做法没问题，但它符合 Go 的惯用法（idiomatic）吗？

让我们的 web server 负责手动取消 `Store`，这说得通吗？万一 `Store` 自己也恰好依赖其他一些跑得很慢的进程呢？那我们就得保证 `Store.Cancel` 能把取消正确地传播给它的所有依赖方。

`context` 的主要意义之一就在于：它提供了一种一致的取消方式。

摘自 [go doc](https://golang.org/pkg/context/)

> 服务器收到的请求应当创建一个 Context，向外发出的调用应当接收一个 Context。两者之间的函数调用链必须把这个 Context 传播下去，也可以视情况把它替换为用 WithCancel、WithDeadline（截止时间 deadline）、WithTimeout（超时）或 WithValue 创建的派生 Context。当一个 Context 被取消时，由它派生的所有 Context 也都会被取消。

再引一段 [Go 博客：Context](https://blog.golang.org/context)：

> 在 Google，我们要求 Go 程序员把 Context 参数作为第一个参数，传给入站请求与出站请求之间调用路径上的每一个函数。这样一来，由许多不同团队开发的 Go 代码就能良好地互操作。它让我们能简单地控制超时和取消，并确保安全凭证这类关键值能在 Go 程序中正确地传递。

（不妨停下来想一想：如果每个函数都得传入一个 context，会带来什么样的连锁影响，用起来又是什么体验。）

是不是有点不安？很好。不过我们还是试着遵循这套做法：把 `context` 传递给 `Store`，让它自己负责取消。这样一来，它也可以把 `context` 继续传给它自己的依赖方，让它们同样负责把自己停下来。

## 先写测试

现有测试的职责变了，测试也得跟着改。现在 handler 唯一的职责是：确保把一个 context 传递给下游的 `Store`，并处理 `Store` 被取消时返回的那个 error。

我们来更新 `Store` 接口，体现新的职责：

```go
type Store interface {
	Fetch(ctx context.Context) (string, error)
}
```

先把 handler 里的代码删掉：

```go
func Server(store Store) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
	}
}
```

更新我们的 `SpyStore`：

```go
type SpyStore struct {
	response string
	t        *testing.T
}

func (s *SpyStore) Fetch(ctx context.Context) (string, error) {
	data := make(chan string, 1)

	go func() {
		var result string
		for _, c := range s.response {
			select {
			case <-ctx.Done():
				log.Println("spy store got cancelled")
				return
			default:
				time.Sleep(10 * time.Millisecond)
				result += string(c)
			}
		}
		data <- result
	}()

	select {
	case <-ctx.Done():
		return "", ctx.Err()
	case res := <-data:
		return res, nil
	}
}
```

我们得让 spy 表现得像一个真正能与 `context` 协作的方法。

我们在模拟一个很慢的过程：在一个 goroutine 里一个字符一个字符地拼接字符串，慢慢把结果攒出来。goroutine 干完活之后，就把字符串写进 `data` channel。这个 goroutine 同时监听着 `ctx.Done`，一旦那个 channel 里传来信号，就停止手头的工作。

最后，代码用另一个 `select` 来等待：要么等 goroutine 完成工作，要么等取消发生。

思路跟之前的做法类似：我们用 Go 的并发原语让两个异步过程赛跑，由胜负决定我们返回什么。

以后你写自己的、接收 `context` 的函数和方法时，多半也会采用类似的做法，所以请务必弄懂这里发生了什么。

最后我们可以更新测试了。先把取消那个测试注释掉，让我们先修好正常路径的测试。

```go
t.Run("returns data from store", func(t *testing.T) {
	data := "hello, world"
	store := &SpyStore{response: data, t: t}
	svr := Server(store)

	request := httptest.NewRequest(http.MethodGet, "/", nil)
	response := httptest.NewRecorder()

	svr.ServeHTTP(response, request)

	if response.Body.String() != data {
		t.Errorf(`got "%s", want "%s"`, response.Body.String(), data)
	}
})
```

## 试着运行测试

```
=== RUN   TestServer/returns_data_from_store
--- FAIL: TestServer (0.00s)
    --- FAIL: TestServer/returns_data_from_store (0.00s)
    	context_test.go:22: got "", want "hello, world"
```

## 写足够的代码让测试通过

```go
func Server(store Store) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		data, _ := store.Fetch(r.Context())
		fmt.Fprint(w, data)
	}
}
```

我们的正常路径这下应该……正常了。现在可以修另一个测试。

## 先写测试

我们需要测试：在出错的情形下，不写出任何形式的响应。遗憾的是，`httptest.ResponseRecorder` 没办法帮我们弄清楚这一点，所以我们得自己动手写一个 spy 来测它。

```go
type SpyResponseWriter struct {
	written bool
}

func (s *SpyResponseWriter) Header() http.Header {
	s.written = true
	return nil
}

func (s *SpyResponseWriter) Write([]byte) (int, error) {
	s.written = true
	return 0, errors.New("not implemented")
}

func (s *SpyResponseWriter) WriteHeader(statusCode int) {
	s.written = true
}
```

我们的 `SpyResponseWriter` 实现了 `http.ResponseWriter`，所以可以在测试里使用它。

```go
t.Run("tells store to cancel work if request is cancelled", func(t *testing.T) {
	data := "hello, world"
	store := &SpyStore{response: data, t: t}
	svr := Server(store)

	request := httptest.NewRequest(http.MethodGet, "/", nil)

	cancellingCtx, cancel := context.WithCancel(request.Context())
	time.AfterFunc(5*time.Millisecond, cancel)
	request = request.WithContext(cancellingCtx)

	response := &SpyResponseWriter{}

	svr.ServeHTTP(response, request)

	if response.written {
		t.Error("a response should not have been written")
	}
})
```

## 试着运行测试

```
=== RUN   TestServer
=== RUN   TestServer/tells_store_to_cancel_work_if_request_is_cancelled
--- FAIL: TestServer (0.01s)
    --- FAIL: TestServer/tells_store_to_cancel_work_if_request_is_cancelled (0.01s)
    	context_test.go:47: a response should not have been written
```

## 写足够的代码让测试通过

```go
func Server(store Store) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		data, err := store.Fetch(r.Context())

		if err != nil {
			return // todo: 按你喜欢的方式记录日志
		}

		fmt.Fprint(w, data)
	}
}
```

到这里可以看到，server 代码变得简单了：它不再显式负责取消，只是把 `context` 传递下去，由下游函数自己去响应可能发生的任何取消。

## 总结

### 本章我们都学了什么

- 如何测试一个请求被客户端取消的 HTTP handler。
- 如何使用 context 来管理取消。
- 如何编写接收 `context` 的函数，借助 goroutine、`select` 和 channel 利用它取消自身。
- 遵循 Google 的准则来管理取消：沿着你的调用栈传播请求范围的 context。
- 需要的话，如何为 `http.ResponseWriter` 造一个自己的 spy。

### 那 context.Value 呢？

[Michal Štrba](https://faiface.github.io/post/context-should-go-away-go2/) 和我的看法差不多。

> 要是在我这家（并不存在的）公司里用 ctx.Value，你会被开除

一些工程师主张通过 `context` 来传值，因为这*感觉很方便*。

方便，往往是坏代码的根源。

`context.Values` 的问题在于，它就是一个无类型的 map：你得不到任何类型安全，还得处理值实际上并不存在的情况。你还得让 map 的 key 在模块与模块之间制造耦合，一旦有人改动了什么，各种东西就开始坏掉。

简而言之，**如果一个函数需要某些值，就把它们写成有类型的参数，而不是试图从 `context.Value` 里取**。这样既有静态检查保驾护航，又自成文档，人人都看得见。

#### 但是……

另一方面，把一些与请求"正交"的信息放进 context 也确实有帮助，比如追踪 ID（trace id）。这类信息调用栈里的每个函数未必都用得上，可要是硬塞进函数签名，签名就会变得非常凌乱。

[Jack Lindamood 说 **Context.Value 应该用来提供信息，而不是用来实施控制**](https://medium.com/@cep21/how-to-correctly-use-context-context-in-go-1-7-8f2c0fafdf39)

> context.Value 里的内容是给维护者看的，不是给使用者用的。对于文档写明的或符合预期的结果来说，它绝不应该成为必需的输入。

### 延伸阅读

- 我特别喜欢 [Michal Štrba 的《Context should go away for Go 2》](https://faiface.github.io/post/context-should-go-away-go2/)。他的论点是：到处都得传 `context` 本身就是一种坏味道（smell），它指向的是这门语言在取消方面的能力欠缺。他认为这件事最好在语言层面解决，而不是在库的层面。在那一天到来之前，想管理长时间运行的进程，你还是离不开 `context`。
- [Go 博客进一步介绍了使用 `context` 的动机，还附有一些示例](https://blog.golang.org/context)
