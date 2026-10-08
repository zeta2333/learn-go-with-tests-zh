# Sync

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/sync)**

我们想做一个可以并发安全地使用的计数器。

先从一个不安全的计数器开始，验证它在单线程环境下行为正常。

然后写一个测试，让多个 goroutine 同时抢着使用这个计数器，把它的不安全暴露出来，再修好它。

## 先写测试

我们希望 API 提供两个方法：一个用来增加计数，另一个用来读取计数器的值。

```go
func TestCounter(t *testing.T) {
	t.Run("incrementing the counter 3 times leaves it at 3", func(t *testing.T) {
		counter := Counter{}
		counter.Inc()
		counter.Inc()
		counter.Inc()

		if counter.Value() != 3 {
			t.Errorf("got %d, want %d", counter.Value(), 3)
		}
	})
}
```

## 试着运行测试

```
./sync_test.go:9:14: undefined: Counter
```

## 写最少的代码让测试能运行，并检查失败的测试输出

先来定义 `Counter`。

```go
type Counter struct {
}
```

再跑一次，测试会报如下错误

```
./sync_test.go:14:10: counter.Inc undefined (type Counter has no field or method Inc)
./sync_test.go:18:13: counter.Value undefined (type Counter has no field or method Value)
```

所以，为了让测试终于能跑起来，我们把这两个方法定义出来

```go
func (c *Counter) Inc() {

}

func (c *Counter) Value() int {
	return 0
}
```

现在测试应该能运行，并且会失败

```
=== RUN   TestCounter
=== RUN   TestCounter/incrementing_the_counter_3_times_leaves_it_at_3
--- FAIL: TestCounter (0.00s)
    --- FAIL: TestCounter/incrementing_the_counter_3_times_leaves_it_at_3 (0.00s)
    	sync_test.go:27: got 0, want 3
```

## 写足够的代码让测试通过

对我们这样的 Go 专家来说，这应该是小菜一碟。我们需要在自己的类型里保存计数器的状态，然后每次调用 `Inc` 时都把它加一

```go
type Counter struct {
	value int
}

func (c *Counter) Inc() {
	c.value++
}

func (c *Counter) Value() int {
	return c.value
}
```

## 重构

没多少可重构的，不过接下来我们还要围绕 `Counter` 写更多测试，所以先写一个小的断言函数 `assertCounter`，让测试读起来更清楚。

```go
t.Run("incrementing the counter 3 times leaves it at 3", func(t *testing.T) {
	counter := Counter{}
	counter.Inc()
	counter.Inc()
	counter.Inc()

	assertCounter(t, counter, 3)
})
```
```go
func assertCounter(t testing.TB, got Counter, want int) {
	t.Helper()
	if got.Value() != want {
		t.Errorf("got %d, want %d", got.Value(), want)
	}
}
```

## 下一步

这一步相当轻松，但现在我们多了一条需求：它必须能在并发环境下安全使用。我们需要写一个会失败的测试来把这个问题暴露出来。

## 先写测试

```go
t.Run("it runs safely concurrently", func(t *testing.T) {
	wantedCount := 1000
	counter := Counter{}

	var wg sync.WaitGroup
	wg.Add(wantedCount)

	for i := 0; i < wantedCount; i++ {
		go func() {
			counter.Inc()
			wg.Done()
		}()
	}
	wg.Wait()

	assertCounter(t, counter, wantedCount)
})
```

这段代码会循环 `wantedCount` 次，每次启动一个 goroutine 去调用 `counter.Inc()`。

我们用到了 [`sync.WaitGroup`](https://golang.org/pkg/sync/#WaitGroup)（等待组），它是一种同步并发进程的便捷方式。

> 等待组会等待一组 goroutine 执行完毕。主 goroutine 调用 Add 来设置要等待的 goroutine 数量。随后每个 goroutine 开始运行，并在结束时调用 Done。与此同时，可以用 Wait 来阻塞，直到所有 goroutine 都执行完毕。

等到 `wg.Wait()` 结束之后再做断言，我们就能确定所有 goroutine 都已尝试对 `Counter` 执行过 `Inc`。

## 试着运行测试

```
=== RUN   TestCounter/it_runs_safely_concurrently
--- FAIL: TestCounter (0.00s)
    --- FAIL: TestCounter/it_runs_safely_concurrently (0.00s)
    	sync_test.go:26: got 939, want 1000
FAIL
```

测试*大概率*会失败，而且每次失败的数字还都不一样；但无论如何，它证明了当多个 goroutine 同时试图修改计数器的值时，这段代码是无法正常工作的。

### 为什么会这样？

`c.value++` 看起来是一个单一的、不可分割的操作，其实并不是，它大致相当于下面的操作：

```go
tmp := c.value // 1. 读取
tmp = tmp + 1  // 2. 自增
c.value = tmp  // 3. 写回
```

这三步里的每一步都是独立的操作，而 Go 运行时随时可以在它们之间的任何一个点上切换到另一个 goroutine。如果两个 goroutine 差不多同时调用 `Inc`，它们的步骤就可能交错进行，比如：

```
goroutine A: reads c.value (0)
goroutine B: reads c.value (0)
goroutine A: increments its copy to 1
goroutine B: increments its copy to 1
goroutine A: writes c.value = 1
goroutine B: writes c.value = 1
```

两个 goroutine 各调用了一次 `Inc`，我们自然希望 `c.value` 最终等于 `2`，结果却是 `1`。其中一次自增被悄无声息地弄丢了：因为两个 goroutine 都在对方写回结果之前读到了同一个初始值。这就叫*竞态条件*（race condition）。一千个 goroutine 同时抢着读、自增、写回，有一部分自增会丢失也就不足为奇了。

## 写足够的代码让测试通过

一个简单的办法是给 `Counter` 加一把锁，确保同一时刻只有一个 goroutine 能增加计数。Go 的 [`Mutex`](https://golang.org/pkg/sync/#Mutex)（互斥锁）提供的正是这样一种锁：

> Mutex 是一种互斥锁（mutual exclusion lock）。Mutex 的零值是一把未加锁的互斥锁。

```go
type Counter struct {
	mu    sync.Mutex
	value int
}

func (c *Counter) Inc() {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.value++
}
```

也就是说，最先调用 `Inc` 的那个 goroutine 会拿到 `Counter` 上的锁。其他所有 goroutine 都必须等它 `Unlock` 之后才能获得访问权。

现在重新跑测试，应该就能通过了，因为每个 goroutine 都得排到自己的轮次才能做修改。

## 我见过别的例子，把 `sync.Mutex` 嵌入到结构体里

你可能会见到这样的写法

```go
type Counter struct {
	sync.Mutex
	value int
}
```

有人会说这样能让代码更优雅一点。

```go
func (c *Counter) Inc() {
	c.Lock()
	defer c.Unlock()
	c.value++
}
```

这*看起来*不错，但哪怕编程是一门极其主观的学问，这么写也是**又糟又错**。

有时人们会忘记：嵌入一个类型，意味着那个类型的方法会变成*公开接口的一部分*；而这往往不是你想要的。记住，我们对公开 API 应当格外小心——从把某个东西公开的那一刻起，别的代码就可能把自己耦合到它上面。我们始终要避免不必要的耦合。

把 `Lock` 和 `Unlock` 暴露出去，往好了说是让人困惑，往坏了说，一旦使用你这个类型的人开始调用这些方法，可能给你的软件带来极大的危害。

![演示这个 API 的使用者如何错误地改变锁的状态](https://i.imgur.com/SWYNpwm.png)

*这看起来真是个馊主意*

## 拷贝互斥锁

我们的测试通过了，但代码还是有点危险

如果在代码上跑一下 `go vet`，你应该会看到类似下面这样的报错

```
sync/v2/sync_test.go:16: call of assertCounter copies lock value: v1.Counter contains sync.Mutex
sync/v2/sync_test.go:39: assertCounter passes lock by value: v1.Counter contains sync.Mutex
```

查一下 [`sync.Mutex`](https://golang.org/pkg/sync/#Mutex) 的文档，就知道原因了

> Mutex 在首次使用之后不可再拷贝。

当我们把 `Counter` 按值传给 `assertCounter` 时，它会试图创建一份互斥锁的拷贝。

要解决这个问题，我们应该改为传入指向 `Counter` 的指针，把 `assertCounter` 的签名改成这样

```go
func assertCounter(t testing.TB, got *Counter, want int)
```

这么一改，测试就编译不过了，因为我们传入的是 `Counter` 而不是 `*Counter`。对此我更倾向于创建一个构造函数（constructor），借此告诉 API 的读者：最好不要自己动手初始化这个类型。

```go
func NewCounter() *Counter {
	return &Counter{}
}
```

在测试里初始化 `Counter` 时就改用这个函数。

## 另一种选择：sync/atomic

`Mutex` 是一个通用工具——它可以保护任意多个字段以及字段之间的任意不变式（invariant），只要你记得在每次访问前后都 `Lock`/`Unlock`。但我们的 `Counter` 已经简单到共享状态的极限了：一个整数，多个 goroutine 并发地对它自增。恰恰针对这种场景，[`sync/atomic`](https://pkg.go.dev/sync/atomic) 包提供了 [`atomic.Int64`](https://pkg.go.dev/sync/atomic#Int64) 这样的类型，让你根本不需要额外的锁就能并发安全地访问单个值：

```go
type Counter struct {
	value atomic.Int64
}

func NewCounter() *Counter {
	return &Counter{}
}

func (c *Counter) Inc() {
	c.value.Add(1)
}

func (c *Counter) Value() int64 {
	return c.value.Load()
}
```

不需要 `Mutex`，不需要 `Lock`/`Unlock`，而且随便多少个 goroutine 同时调用 `Inc` 都是安全的——我们前面写的那个测试原封不动就能通过。它的底层用的是低级 CPU 指令，让自增这个操作本身具备原子性，在这种简单场景下通常比 `Mutex` 更快。`atomic.Int64`（还有它的兄弟们，比如 `atomic.Int32` 和 `atomic.Bool`）也堵上了旧版 Go 里裸写 `atomic.AddInt64(&x, 1)` 这类函数调用的误用空间——你不可能忘记传指针，也不可能绕过 `Load` 直接读到字段的值。

要保护的只是单个值，就用 `sync/atomic` 的类型；一旦需要让多个字段、或字段之间的某个不变式保持一致，就用 `Mutex`。

## 总结

这一章我们接触了 [sync 包](https://golang.org/pkg/sync/) 里的几样东西

- `Mutex` 让我们可以给数据加锁
- `WaitGroup` 是等待 goroutine 完成工作的一种手段
- `sync/atomic` 提供对单个值的安全无锁访问，当动用完整的 `Mutex` 未免杀鸡用牛刀时，值得一试

### 什么时候该用锁，而不是 channel 和 goroutine？

[我们在第一篇并发章节里已经介绍过 goroutine](concurrency.md)，它让我们能写出安全的并发代码，那为什么还要用锁呢？
[Go wiki 上有一个专门讨论这个话题的页面：Mutex Or Channel](https://go.dev/wiki/MutexOrChannel)

> Go 新手常犯的一个错误，是仅仅因为可以用、或者因为好玩，就过度使用 channel 和 goroutine。如果 sync.Mutex 最适合你的问题，别害怕用它。Go 很务实：它让你自由使用最能解决问题的工具，而不是强迫你套进某一种代码风格里。

概括一下：

- **传递数据的所有权时，用 channel**
- **管理状态时，用互斥锁**

### go vet

记得在构建脚本里用上 go vet，它能在代码里那些隐蔽的 bug 伤到你可怜的用户之前，就把它们揪出来提醒你。

### 别因为方便就用嵌入

- 想一想嵌入会对你的公开 API 产生什么影响。
- 你*真的*想把这些方法暴露出去，让别人把自己的代码耦合上来吗？
- 对互斥锁来说，这么做的潜在后果可能是灾难性的，而且出事的方式难以预测、无比诡异：想象某段居心不良的代码在不该解锁的时候解锁了互斥锁——它会带来一些非常奇怪的 bug，极难排查。
