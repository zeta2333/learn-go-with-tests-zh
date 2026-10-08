# 迭代

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/for)**

想在 Go 里重复地做某件事，你需要 `for`。Go 没有 `while`、`do`、`until` 这些关键字，你只能用 `for`。这可是件好事！

我们来写一个测试，测的是一个把字符重复 5 次的函数。

到这里还没有任何新东西，所以自己动手写一写，就当练手。

## 先写测试

```go
package iteration

import "testing"

func TestRepeat(t *testing.T) {
	repeated := Repeat("a")
	expected := "aaaaa"

	if repeated != expected {
		t.Errorf("expected %q but got %q", expected, repeated)
	}
}
```

## 试着运行测试

`./repeat_test.go:6:14: undefined: Repeat`

## 写出让测试能运行的最少代码，并检查失败测试的输出

_保持纪律！_ 现在还不需要学任何新东西，就足够让测试正确地失败了。

眼下要做的只是让代码编译通过，这样你就能确认自己的测试写得没问题。

```go
package iteration

func Repeat(character string) string {
	return ""
}
```

你已经掌握的 Go 知识就够给一些基础问题写测试了，这不挺好的吗？这也意味着，从现在起你可以随便折腾生产代码，并且心里有底：它的行为正如你所愿。

`repeat_test.go:10: expected 'aaaaa' but got ''`

## 写足够的代码让测试通过

`for` 的语法毫无出奇之处，跟大多数类 C 语言一个样。

```go
func Repeat(character string) string {
	var repeated string
	for i := 0; i < 5; i++ {
		repeated = repeated + character
	}
	return repeated
}
```

跟 C、Java 或 JavaScript 这些语言不同，for 语句的三个组成部分外面没有括号，而且花括号 `{ }` 是必须写的。你可能会好奇下面这一行是在干什么

```go
	var repeated string
```

毕竟到目前为止，我们声明并初始化变量用的都是 `:=`。其实 `:=` 只不过是把这两步合起来写的[简写](https://gobyexample.com/variables)。这里我们只是声明一个 `string` 变量，并不初始化，所以才要用显式写法。后面还会看到，`var` 也可以用来声明函数。

跑一下测试，应该就通过了。

for 循环的其他变体在[这里](https://gobyexample.com/for)有介绍。

## 重构

又到了重构时间，这次顺便引入另一个新构造：`+=` 赋值运算符。

```go
const repeatCount = 5

func Repeat(character string) string {
	var repeated string
	for i := 0; i < repeatCount; i++ {
		repeated += character
	}
	return repeated
}
```

`+=` 名叫 _“Add AND 赋值运算符”_，它把右边的操作数加到左边的操作数上，再把结果赋给左边的操作数。整数之类的其他类型也能用。

### 基准测试

在 Go 里编写[基准测试](https://golang.org/pkg/testing/#hdr-Benchmarks)是这门语言提供的又一项一等公民特性，写起来跟写测试非常像。

```go
func BenchmarkRepeat(b *testing.B) {
	for b.Loop() {
		Repeat("a")
	}
}
```

可以看到，这段代码跟测试长得非常像。

`testing.B` 让你可以用上 loop 函数。只要基准测试还该继续跑，`Loop()` 就会返回 true。

基准测试代码执行时，框架会测量它耗时多久。等 `Loop()` 返回 false，`b.N` 里保存的就是实际运行的总迭代次数。

代码要跑多少次不用你操心，框架会定出一个“合适”的次数，好让你得到像样的结果。

运行基准测试用 `go test -bench=.`（如果你在 Windows Powershell 里，则是 `go test -bench="."`）

```text
goos: darwin
goarch: amd64
pkg: github.com/quii/learn-go-with-tests/for/v4
10000000           136 ns/op
PASS
```

`136 ns/op` 的意思是：我们的函数平均跑一次要花 136 纳秒（在我的电脑上）。相当不错了！为了测出这个数字，它把函数跑了 10000000 遍。

**注意：** 默认情况下，基准测试是串行运行的。

只有循环体才会被计时；准备和清理代码会自动排除在基准测试计时之外。一个典型的基准测试长这样：

```go
func Benchmark(b *testing.B) {
	//... 准备工作 ...
	for b.Loop() {
		//... 要测量的代码 ...
	}
	//... 清理工作 ...
}
```

Go 的字符串是不可变的（immutable），也就是说每一次拼接——比如我们 `Repeat` 函数里的那种——都要拷贝内存来容纳新字符串。这会影响性能，大量拼接字符串时尤其明显。

标准库提供了 [`strings.Builder`](https://pkg.go.dev/strings#Builder) 类型，它能尽量减少内存拷贝。它实现了 `WriteString` 方法，我们可以用它来拼接字符串：

```go
const repeatCount = 5

func Repeat(character string) string {
	var repeated strings.Builder
	for i := 0; i < repeatCount; i++ {
		repeated.WriteString(character)
	}
	return repeated.String()
}
```

**注意**：必须调用 `String` 方法才能拿到最终结果。

我们可以用 `BenchmarkRepeat` 来确认 `strings.Builder` 确实让性能有了显著提升。运行 `go test -bench=. -benchmem`：

```text
goos: darwin
goarch: amd64
pkg: github.com/quii/learn-go-with-tests/for/v4
10000000           25.70 ns/op           8 B/op           1 allocs/op
PASS
```

`-benchmem` 标志会报告内存分配的相关信息：

* `B/op`：每次迭代分配的字节数
* `allocs/op`：每次迭代执行的内存分配次数

## 练习

* 修改测试，让调用方可以指定字符重复的次数，然后把代码修好
* 写一个 `ExampleRepeat`，为你的函数写文档
* 翻一翻 [strings](https://golang.org/pkg/strings) 包。挑出你觉得有用的函数，像本章这样写测试来实验它们。花时间学习标准库，假以时日回报会非常大。

## 总结

* 更多 TDD 练习
* 学会了 `for`
* 学会了怎么写基准测试
