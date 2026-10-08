# Context-aware Reader

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/q-and-a/context-aware-reader)**

本章演示如何用 TDD 一步步开发一个支持 context 的 `io.Reader`，思路出自 Mat Ryer 和 David Hernandez 发表在 [The Pace Dev Blog](https://pace.dev/blog/2020/02/03/context-aware-ioreader-for-golang-by-mat-ryer) 上的文章。

## 支持 context 的 Reader？

先花一分钟快速复习一下 `io.Reader`。

如果你读过本书的其他章节，那其实已经不止一次见过 `io.Reader` 了：打开文件、编码 JSON 以及其他各种常见任务，背后都是它。它是一个简单的抽象，抽象的正是"从*某个东西*里读出数据"这件事

```go
type Reader interface {
	Read(p []byte) (n int, err error)
}
```

借助 `io.Reader`，你能大量复用标准库的现成能力；它是一个非常常用的抽象（与它配套的还有 `io.Writer`）

### 何谓"支持 context"？

在[前面的一章](context.md)里我们讲过，如何用 `context` 来提供取消能力。如果你要执行的任务可能非常吃计算资源、又希望能随时叫停，context 就格外有用。

用 `io.Reader` 的时候，速度是没有任何保证的：它可能 1 纳秒就完事，也可能要跑上几百个小时。要是能在自己的应用里取消这类任务，往往会很有用——这正是 Mat 和 David 那篇文章讨论的问题。

他们把两个简单的抽象（`context.Context` 和 `io.Reader`）组合起来解决这个问题。

下面我们就用 TDD 来做出这样一个功能：把一个 `io.Reader` 包装起来，让它可以被取消。

怎么测试它，倒是个有意思的挑战。平时用 `io.Reader`，通常都是把它交给别的函数去用，比如 `json.NewDecoder` 或 `io.ReadAll`，你并不用操心背后的细节。

我们想验证的行为大致是这样

> 假如有一个内容为 "ABCDEF" 的 `io.Reader`，当我在读到一半时发出取消信号，之后再继续读就读不到任何东西了，最终拿到的只有 "ABC"

再看一眼这个接口。

```go
type Reader interface {
	Read(p []byte) (n int, err error)
}
```

`Reader` 的 `Read` 方法会把它手里的内容读进我们提供的 `[]byte`。

所以我们不必一口气读完，完全可以这样：

 - 提供一个装不下全部内容的定长字节数组
 - 发出取消信号
 - 再试着读一次，这时应当返回一个错误，且读到的字节数为 0

眼下我们先只写一个"正常路径"（happy path）的测试，其中没有任何取消发生——这样能先熟悉一下问题本身，暂时还不用写任何生产代码。

```go
func TestContextAwareReader(t *testing.T) {
	t.Run("lets just see how a normal reader works", func(t *testing.T) {
		rdr := strings.NewReader("123456")
		got := make([]byte, 3)
		_, err := rdr.Read(got)

		if err != nil {
			t.Fatal(err)
		}

		assertBufferHas(t, got, "123")

		_, err = rdr.Read(got)

		if err != nil {
			t.Fatal(err)
		}

		assertBufferHas(t, got, "456")
	})
}

func assertBufferHas(t testing.TB, buf []byte, want string) {
	t.Helper()
	got := string(buf)
	if got != want {
		t.Errorf("got %q, want %q", got, want)
	}
}
```

- 用一段带数据的字符串造出一个 `io.Reader`
- 准备一个字节数组用来读入，它比 reader 里的内容要小
- 调用 Read，检查读到的内容，如此往复。

由此不难想象：只要在第二次读之前发个取消信号，就能改变它的行为。

看过它是怎么工作的之后，剩下的功能我们就用 TDD 来做。

## 先写测试

我们想要的是：把一个 `io.Reader` 和一个 `context.Context` 组合起来。

用 TDD 时，最好的起点是先设想你期望的 API 长什么样，然后为它写一个测试。

接下来，就交给编译器和失败的测试输出，让它们指引我们找到答案

```go
t.Run("behaves like a normal reader", func(t *testing.T) {
	rdr := NewCancellableReader(strings.NewReader("123456"))
	got := make([]byte, 3)
	_, err := rdr.Read(got)

	if err != nil {
		t.Fatal(err)
	}

	assertBufferHas(t, got, "123")

	_, err = rdr.Read(got)

	if err != nil {
		t.Fatal(err)
	}

	assertBufferHas(t, got, "456")
})
```

## 试着运行测试

```
./cancel_readers_test.go:12:10: undefined: NewCancellableReader
```
## 写最少的代码让测试先跑起来，并查看失败的测试输出

我们得把这个函数定义出来，它应当返回一个 `io.Reader`

```go
func NewCancellableReader(rdr io.Reader) io.Reader {
	return nil
}
```

现在试着运行一下

```
=== RUN   TestCancelReaders
=== RUN   TestCancelReaders/behaves_like_a_normal_reader
panic: runtime error: invalid memory address or nil pointer dereference [recovered]
	panic: runtime error: invalid memory address or nil pointer dereference
[signal SIGSEGV: segmentation violation code=0x1 addr=0x0 pc=0x10f8fb5]
```

不出所料

## 写足够的代码让测试通过

这一步我们先偷个懒，把传进来的 `io.Reader` 原样返回

```go
func NewCancellableReader(rdr io.Reader) io.Reader {
	return rdr
}
```

测试现在应该通过了。

我知道，我知道，这一步看起来又傻又较真。但在一头扎进那些花活之前，重要的是我们至少得有*某种*验证，确认 `io.Reader` 的"正常"行为没有被弄坏；往后推进的过程中，这个测试会给我们底气。

## 先写测试

接下来试试取消。

```go
t.Run("stops reading when cancelled", func(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	rdr := NewCancellableReader(ctx, strings.NewReader("123456"))
	got := make([]byte, 3)
	_, err := rdr.Read(got)

	if err != nil {
		t.Fatal(err)
	}

	assertBufferHas(t, got, "123")

	cancel()

	n, err := rdr.Read(got)

	if err == nil {
		t.Error("expected an error after cancellation but didn't get one")
	}

	if n > 0 {
		t.Errorf("expected 0 bytes to be read after cancellation but %d were read", n)
	}
})
```

这个测试基本上是把第一个测试复制了过来，但现在多了几件事：
- 创建一个带取消能力的 `context.Context`，这样在第一次读之后就能调用 `cancel`
- 要让代码工作，我们得把 `ctx` 传进自己的函数
- 然后断言：`cancel` 之后什么也读不到了

## 试着运行测试

```
./cancel_readers_test.go:33:30: too many arguments in call to NewCancellableReader
	have (context.Context, *strings.Reader)
	want (io.Reader)
```

## 写最少的代码让测试先跑起来，并查看失败的测试输出

编译器在告诉我们该干什么：更新函数签名，让它接收一个 context

```go
func NewCancellableReader(ctx context.Context, rdr io.Reader) io.Reader {
	return rdr
}
```

（记得把第一个测试也改一下，传入 `context.Background`。）

现在你应该能看到一段非常清晰的失败输出

```
=== RUN   TestCancelReaders
=== RUN   TestCancelReaders/stops_reading_when_cancelled
--- FAIL: TestCancelReaders (0.00s)
    --- FAIL: TestCancelReaders/stops_reading_when_cancelled (0.00s)
        cancel_readers_test.go:48: expected an error but didn't get one
        cancel_readers_test.go:52: expected 0 bytes to be read after cancellation but 3 were read
```

## 写足够的代码让测试通过

到了这一步，接下来的代码基本上可以从 Mat 和 David 的原帖里照搬，不过我们还是慢慢来，一小步一小步地迭代。

我们已经知道，需要一个类型，把真正读数据的那个 `io.Reader` 和 `context.Context` 封装在一起。那就把它创建出来，然后试着让函数返回它，而不是原来的 `io.Reader`

```go
func NewCancellableReader(ctx context.Context, rdr io.Reader) io.Reader {
	return &readerCtx{
		ctx:      ctx,
		delegate: rdr,
	}
}

type readerCtx struct {
	ctx      context.Context
	delegate io.Reader
}
```

正如本书反复强调的：慢慢来，让编译器帮你

```
./cancel_readers_test.go:60:3: cannot use &readerCtx literal (type *readerCtx) as type io.Reader in return argument:
	*readerCtx does not implement io.Reader (missing Read method)
```

这个抽象感觉没问题，但它还没有实现我们需要的接口（`io.Reader`），那就把方法加上。

```go
func (r *readerCtx) Read(p []byte) (n int, err error) {
	panic("implement me")
}
```

跑一下测试，应该能*编译通过*，但会 panic。这同样是进展。

先让第一个测试通过：把调用直接*委托*（delegate）给底层的 `io.Reader` 就行

```go
func (r readerCtx) Read(p []byte) (n int, err error) {
	return r.delegate.Read(p)
}
```

到这里，正常路径的测试又绿了，整套东西抽象得也挺漂亮

要让第二个测试通过，需要检查一下 `context.Context`，看它是否已经被取消。

```go
func (r readerCtx) Read(p []byte) (n int, err error) {
	if err := r.ctx.Err(); err != nil {
		return 0, err
	}
	return r.delegate.Read(p)
}
```

现在所有测试都应该通过了。注意我们是怎么把 `context.Context` 里的 error 原样返回的：这样一来，调用方就能进一步查清取消发生的各种原因。原帖对这一点有更详细的讨论。

## 总结

- 小接口是好事，而且易于组合
- 当你想用一样东西去增强另一样东西时（比如给 `io.Reader` 添能力），通常该伸手去拿的就是[委托模式](https://en.wikipedia.org/wiki/Delegation_pattern)

> 在软件工程中，委托模式是一种面向对象的设计模式，它让对象组合得以实现与继承相同的代码复用效果。

- 开展这类工作有个简单的切入点：先把 delegate（被委托的对象）包起来，写一个测试断言它的行为和 delegate 平时一模一样，然后才开始组合其他部分去改变行为。这样在你朝着目标编码的路上，一切都能保持正常工作
