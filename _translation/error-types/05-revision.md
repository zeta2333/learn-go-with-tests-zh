# Error types

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/q-and-a/error-types)**

**为错误创建自己的类型，是一种十分优雅的做法：既能让代码更整洁，也更好用、更好测。**

Gopher Slack 上的 Pedro 问：

> 如果我创建的错误是 `fmt.Errorf("%s must be foo, got %s", bar, baz)` 这样的，有没有什么办法判断相等，而不必去比较字符串的值？

我们来现编一个函数，帮着把这个问题琢磨清楚。

```go
// DumbGetter 会在收到 200 时返回 url 的响应体字符串
func DumbGetter(url string) (string, error) {
	res, err := http.Get(url)

	if err != nil {
		return "", fmt.Errorf("problem fetching from %s, %v", url, err)
	}

	if res.StatusCode != http.StatusOK {
		return "", fmt.Errorf("did not get 200 from %s, got %d", url, res.StatusCode)
	}

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body) // 为简洁起见，忽略 err

	return string(body), nil
}
```

一个函数可能因为不同的原因而失败，这样的写法并不少见，而我们想确保每一种场景都得到了正确的处理。

正如 Pedro 所说，针对这类状态错误，我们*可以*像下面这样写一个测试。

```go
t.Run("when you don't get a 200 you get a status error", func(t *testing.T) {

	svr := httptest.NewServer(http.HandlerFunc(func(res http.ResponseWriter, req *http.Request) {
		res.WriteHeader(http.StatusTeapot)
	}))
	defer svr.Close()

	_, err := DumbGetter(svr.URL)

	if err == nil {
		t.Fatal("expected an error")
	}

	want := fmt.Sprintf("did not get 200 from %s, got %d", svr.URL, http.StatusTeapot)
	got := err.Error()

	if got != want {
		t.Errorf(`got "%v", want "%v"`, got, want)
	}
})
```

这个测试创建了一个永远返回 `StatusTeapot` 的服务器，然后把它的 URL 作为参数传给 `DumbGetter`，看看它能不能正确处理非 `200` 的响应。

## 这种测试方式的问题

本书一直强调*倾听测试的反馈*，而这个测试给人的*感觉*就不太对：

- 为了测试它，我们在测试里把生产代码要拼的字符串又拼了一遍
- 读起来、写起来都很烦人
- 我们*真正关心的*，真的是错误信息字符串一字不差吗？

这说明了什么？我们的测试用起来是什么手感，别的代码用起我们的代码来就是什么手感。

使用我们代码的人，要如何应对我们返回的特定种类的错误呢？他们能做的顶多是去看错误字符串——这种写法极易出错，而且写起来苦不堪言。

## 我们应该怎么做

有了 TDD，我们更容易进入这样一种思维模式：

> *我*会希望怎么来使用这段代码？

对 `DumbGetter` 来说，我们能做的是提供一种途径，让使用者借助类型系统（type system）弄清楚到底发生了哪种错误。

如果 `DumbGetter` 能返回这样一个东西呢：

```go
type BadStatusError struct {
	URL    string
	Status int
}
```

我们拿到的就不再是魔法字符串，而是实实在在可以操作的*数据*。

来改一下现有的测试，体现这个新需求：

```go
t.Run("when you don't get a 200 you get a status error", func(t *testing.T) {

	svr := httptest.NewServer(http.HandlerFunc(func(res http.ResponseWriter, req *http.Request) {
		res.WriteHeader(http.StatusTeapot)
	}))
	defer svr.Close()

	_, err := DumbGetter(svr.URL)

	if err == nil {
		t.Fatal("expected an error")
	}

	got, isStatusErr := err.(BadStatusError)

	if !isStatusErr {
		t.Fatalf("was not a BadStatusError, got %T", err)
	}

	want := BadStatusError{URL: svr.URL, Status: http.StatusTeapot}

	if got != want {
		t.Errorf("got %v, want %v", got, want)
	}
})
```

我们得让 `BadStatusError` 实现 `error` 接口。

```go
func (b BadStatusError) Error() string {
	return fmt.Sprintf("did not get 200 from %s, got %d", b.URL, b.Status)
}
```

### 这个测试做了什么？

我们不再检查错误的字符串是否一字不差，而是对错误做一次[类型断言](https://tour.golang.org/methods/15)（type assertion），看它是不是一个 `BadStatusError`。这更清晰地表达了我们想要的是哪一种错误。假如断言通过，我们再去检查这个错误的各个字段是否正确。

跑一下测试，它告诉我们：我们没有返回正确种类的错误

```
--- FAIL: TestDumbGetter (0.00s)
    --- FAIL: TestDumbGetter/when_you_dont_get_a_200_you_get_a_status_error (0.00s)
    	error-types_test.go:56: was not a BadStatusError, got *errors.errorString
```

我们来修好 `DumbGetter`，把错误处理的代码改成使用我们的类型：

```go
if res.StatusCode != http.StatusOK {
	return "", BadStatusError{URL: url, Status: res.StatusCode}
}
```

这次改动带来了一些*实实在在的好处*：

- `DumbGetter` 函数变得更简单了：它不再操心错误字符串里的种种细节，只管创建一个 `BadStatusError`。
- 我们的测试现在体现（同时也是一份文档）了代码的使用者*可以*怎么做——如果他们想做点比记日志更精细的错误处理的话。只消做一次类型断言，就能轻松拿到错误的各个字段。
- 它仍然"只是"一个 `error`，所以只要使用者愿意，照样可以像对待其他 `error` 一样，把它沿调用栈（call stack）往上传，或者记进日志。

## 总结

如果你发现自己要测试多种错误情形，别掉进比较错误信息的陷阱。

这会让测试变得 flaky（不稳定），又难读又难写；而且它也映照出你代码的使用者将会遇到的难处：一旦他们也需要根据发生的错误种类来区别对待，同样会举步维艰。

务必让你的测试始终体现*你*希望怎样使用自己的代码；就此而言，不妨考虑创建错误类型，把你的各种错误封装起来。这让使用你代码的人更容易处理不同种类的错误，也让你自己写错误处理代码时更简单、更易读。

## 补充

从 Go 1.13 开始，标准库提供了一些处理错误的新方式，[Go 官方博客](https://blog.golang.org/go1.13-errors)有专门的介绍：

```go
t.Run("when you don't get a 200 you get a status error", func(t *testing.T) {

	svr := httptest.NewServer(http.HandlerFunc(func(res http.ResponseWriter, req *http.Request) {
		res.WriteHeader(http.StatusTeapot)
	}))
	defer svr.Close()

	_, err := DumbGetter(svr.URL)

	if err == nil {
		t.Fatal("expected an error")
	}

	var got BadStatusError
	isBadStatusError := errors.As(err, &got)
	want := BadStatusError{URL: svr.URL, Status: http.StatusTeapot}

	if !isBadStatusError {
		t.Fatalf("was not a BadStatusError, got %T", err)
	}

	if got != want {
		t.Errorf("got %v, want %v", got, want)
	}
})
```

这里我们用 [`errors.As`](https://pkg.go.dev/errors#example-As) 尝试把错误提取到我们的自定义类型里。它会返回一个 `bool` 表示是否成功，并在成功时替我们把结果提取进 `got`。
