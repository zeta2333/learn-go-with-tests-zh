# 数组和切片

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/arrays)**

数组（array）让你可以在一个变量里按特定的顺序存储多个相同类型的元素。

用上数组之后，有一件事非常常见：遍历它们。那就用[刚学到的 `for` 知识](iteration.md)来写一个 `Sum` 函数吧。`Sum` 接收一个数字数组，返回它们的总和。

拿出我们的 TDD 功力吧

## 先写测试

新建一个文件夹作为工作目录。在里面新建一个名为 `sum_test.go` 的文件，写入以下代码：

```go
package main

import "testing"

func TestSum(t *testing.T) {

	numbers := [5]int{1, 2, 3, 4, 5}

	got := Sum(numbers)
	want := 15

	if got != want {
		t.Errorf("got %d want %d given, %v", got, want, numbers)
	}
}
```


数组有_固定的容量_（fixed capacity），你在声明变量时就得把它定下来。我们有两种初始化数组的方式：

* [N]type{value1, value2, ..., valueN} 例如 `numbers := [5]int{1, 2, 3, 4, 5}`
* [...]type{value1, value2, ..., valueN} 例如 `numbers := [...]int{1, 2, 3, 4, 5}`

有时在错误信息里把传给函数的输入也一并打印出来会很有用。这里我们用 `%v` 占位符以"默认"格式打印，它对数组效果很好。

[了解更多关于格式化字符串的内容](https://golang.org/pkg/fmt/)

## 试着运行测试

如果你初始化 go mod 时用的是 `go mod init main`，就会看到这样一个报错 `_testmain.go:13:2: cannot import "main"`。这是因为按照惯例，package main 只应该包含对其他包的整合，而不是可被单元测试的代码，所以 Go 不允许你导入名为 `main` 的包。

要解决这个问题，你可以把 `go.mod` 里声明的主模块名改成任何别的名字。

上面的错误修好之后，再去运行 `go test`，编译器会报出那个熟悉的错 `./sum_test.go:10:15: undefined: Sum`。现在我们可以动手编写真正要测试的函数了。

## 写最少的代码让测试能运行，并检查失败的测试输出

在 `sum.go` 里

```go
package main

func Sum(numbers [5]int) int {
	return 0
}
```


现在你的测试应该会失败，并给出_一条清晰的错误信息_

`sum_test.go:13: got 0 want 15 given, [1 2 3 4 5]`

## 写足够的代码让测试通过

```go
func Sum(numbers [5]int) int {
	sum := 0
	for i := 0; i < 5; i++ {
		sum += numbers[i]
	}
	return sum
}
```


想取出数组中特定索引（index）上的值，用 `array[index]` 语法就行。这里我们用 `for` 循环 5 次，遍历整个数组，把每个元素累加到 `sum` 上。

## 重构

我们来引入 [`range`](https://gobyexample.com/range)，帮我们把代码收拾干净

```go
func Sum(numbers [5]int) int {
	sum := 0
	for _, number := range numbers {
		sum += number
	}
	return sum
}
```


`range` 让你可以遍历数组。每次迭代它会返回两个值——索引和值。我们选择用 `_`（[空白标识符](https://golang.org/doc/effective_go.html#blank)）忽略索引值。

### 数组与类型

数组有个有趣的性质：大小被编码在了它的类型里。如果你试图把一个 `[4]int` 传给一个期望 `[5]int` 的函数，代码是编译不过的。它们是不同的类型，这就跟把 `string` 传给一个想要 `int` 的函数是一回事。

你可能会想：数组的长度是固定的，用起来真麻烦，而且大多数时候你八成根本用不到它！

Go 有_切片_（slice），它不把集合的大小编码进类型，想要多大都可以。

下一个需求：对大小不一的集合求和。

## 先写测试

我们现在要用上[切片类型][slice]了，它让我们可以拥有任意大小的集合。语法跟数组非常像，声明时省略大小就行

`mySlice := []int{1,2,3}` 而不是 `myArray := [3]int{1,2,3}`

```go
func TestSum(t *testing.T) {

	t.Run("collection of 5 numbers", func(t *testing.T) {
		numbers := [5]int{1, 2, 3, 4, 5}

		got := Sum(numbers)
		want := 15

		if got != want {
			t.Errorf("got %d want %d given, %v", got, want, numbers)
		}
	})

	t.Run("collection of any size", func(t *testing.T) {
		numbers := []int{1, 2, 3}

		got := Sum(numbers)
		want := 6

		if got != want {
			t.Errorf("got %d want %d given, %v", got, want, numbers)
		}
	})

}
```


## 试着运行测试

这段代码编译不过

`./sum_test.go:22:13: cannot use numbers (type []int) as type [5]int in argument to Sum`

## 写最少的代码让测试能运行，并检查失败的测试输出

这里的问题在于，我们可以二选一

* 破坏现有 API：把 `Sum` 的参数从数组改成切片。这么做的话，弄不好就会毁了别人的一天，因为我们_另外_那个测试将无法编译！
* 新建一个函数

在我们这个例子里，没有别人在用这个函数，所以与其维护两个函数，不如只要一个。

```go
func Sum(numbers []int) int {
	sum := 0
	for _, number := range numbers {
		sum += number
	}
	return sum
}
```


此时去跑测试，它们仍然编译不过，你得把第一个测试改成传入切片而不是数组。

## 写足够的代码让测试通过

结果发现，修好编译错误就大功告成了，测试全部通过！

## 重构

`Sum` 我们已经重构过了——刚才做的就是把数组换成切片，所以不需要额外改动。记住，重构阶段也不可以忽视测试代码——我们的 `Sum` 测试还能再改进。

```go
func TestSum(t *testing.T) {

	t.Run("collection of 5 numbers", func(t *testing.T) {
		numbers := []int{1, 2, 3, 4, 5}

		got := Sum(numbers)
		want := 15

		if got != want {
			t.Errorf("got %d want %d given, %v", got, want, numbers)
		}
	})

	t.Run("collection of any size", func(t *testing.T) {
		numbers := []int{1, 2, 3}

		got := Sum(numbers)
		want := 6

		if got != want {
			t.Errorf("got %d want %d given, %v", got, want, numbers)
		}
	})

}
```


质疑自己测试的价值很重要。目标不应该是测试越多越好，而是对你的代码库有尽可能多的_信心_。测试太多真的会变成实实在在的麻烦，白白增加维护负担。**每个测试都有成本**。

就我们这个例子来说，可以看出给这个函数写两个测试是多余的。如果它对某一种大小的切片有效，那它多半对任何大小的切片都有效（在合理范围内）。

Go 内置的测试工具箱自带一个[覆盖率工具](https://blog.golang.org/cover)。虽然一味追求 100% 的覆盖率（coverage）不该是你的终极目标，但覆盖率工具可以帮你找出代码里测试没有覆盖到的地方。如果你一直严格执行 TDD，覆盖率多半本来就会接近 100%。

试着运行

`go test -cover`

你应该会看到

```bash
PASS
coverage: 100.0% of statements
```


现在删掉其中一个测试，再检查一遍覆盖率。

现在，我们已经有了一个测试充分的函数，够让人满意了。在迎接下一个挑战之前，先把你这份漂亮的成果 commit 下来吧。

我们需要一个叫 `SumAll` 的新函数：它接收数量不定的切片，返回一个新切片，其中包含传入的每个切片各自的总和。

比如

`SumAll([]int{1,2}, []int{0,9})` 会返回 `[]int{3, 9}`

或者

`SumAll([]int{1,1,1})` 会返回 `[]int{3}`

## 先写测试

```go
func TestSumAll(t *testing.T) {

	got := SumAll([]int{1, 2}, []int{0, 9})
	want := []int{3, 9}

	if got != want {
		t.Errorf("got %v want %v", got, want)
	}
}
```


## 试着运行测试

`./sum_test.go:23:9: undefined: SumAll`

## 写最少的代码让测试能运行，并检查失败的测试输出

我们要按照测试的期望来定义 `SumAll`。

Go 允许你编写[_可变参数函数_](https://gobyexample.com/variadic-functions)（variadic functions），它可以接收个数不定的参数。

```go
func SumAll(numbersToSum ...[]int) []int {
	return nil
}
```


这样写是合法的，但我们的测试还是编译不过！

`./sum_test.go:26:9: invalid operation: got != want (slice can only be compared to nil)`

Go 不允许对切片使用相等运算符。你_当然可以_自己写一个函数，遍历 `got` 和 `want` 两个切片，逐个检查它们的值，但如果有一个更方便的办法呢？

从 Go 1.21 开始，标准库提供了 [slices](https://pkg.go.dev/slices#pkg-overview) 包，其中的 [slices.Equal](https://pkg.go.dev/slices#Equal) 函数可以对切片做一次简单的浅比较（shallow compare），像上面那样自己写循环逐个比较的活儿就不用干了。注意，这个函数要求元素是[可比较的](https://pkg.go.dev/builtin#comparable)（comparable），所以它不能用于元素不可比较的切片，比如二维切片。

那我们就把它用起来！

```go
func TestSumAll(t *testing.T) {

	got := SumAll([]int{1, 2}, []int{0, 9})
	want := []int{3, 9}

	if !slices.Equal(got, want) {
		t.Errorf("got %v want %v", got, want)
	}
}
```


你应该会看到类似这样的测试输出：

`sum_test.go:30: got [] want [3 9]`

## 写足够的代码让测试通过

我们要做的是：遍历这些可变参数（varargs），用现有的 `Sum` 函数算出各自的和，然后把它加进我们要返回的切片里

```go
func SumAll(numbersToSum ...[]int) []int {
	lengthOfNumbers := len(numbersToSum)
	sums := make([]int, lengthOfNumbers)

	for i, numbers := range numbersToSum {
		sums[i] = Sum(numbers)
	}

	return sums
}
```


又有好多新东西要学！

创建切片有了一种新方式。`make` 允许你创建一个切片，初始容量为 `numbersToSum` 的 `len`——也就是我们要逐个处理的那些切片的数量。切片的_长度_（length）指它当前持有的元素个数，用 `len(mySlice)` 获取；_容量_（capacity）则指它的底层数组能容纳多少个元素，用 `cap(mySlice)` 获取。比如 `make([]int, 0, 5)` 会创建一个长度为 0、容量为 5 的切片。

跟数组一样，你可以用 `mySlice[N]` 索引切片取出值，或者用 `=` 给它赋新值

现在测试应该能通过了。

## 重构

前面提到过，切片是有容量的。如果你有一个容量为 2 的切片，却尝试执行 `mySlice[10] = 1`，就会得到一个_运行时_（runtime）错误。

不过，你可以使用 `append` 函数：它接收一个切片和一个新值，然后返回一个装着所有元素的新切片。

```go
func SumAll(numbersToSum ...[]int) []int {
	var sums []int
	for _, numbers := range numbersToSum {
		sums = append(sums, Sum(numbers))
	}

	return sums
}
```


在这个实现里，我们基本不用为容量操心。我们从一个空切片 `sums` 开始，在处理可变参数的过程中，把 `Sum` 的结果逐个 append 进去。

下一个需求：把 `SumAll` 改成 `SumAllTails`，让它计算每个切片"尾部"（tail）的总和。集合的尾部是集合中除第一个元素（"头部"，head）之外的所有元素。

## 先写测试

```go
func TestSumAllTails(t *testing.T) {
	got := SumAllTails([]int{1, 2}, []int{0, 9})
	want := []int{2, 9}

	if !slices.Equal(got, want) {
		t.Errorf("got %v want %v", got, want)
	}
}
```


## 试着运行测试

`./sum_test.go:26:9: undefined: SumAllTails`

## 写最少的代码让测试能运行，并检查失败的测试输出

把函数重命名为 `SumAllTails`，再跑一遍测试

`sum_test.go:30: got [3 9] want [2 9]`

## 写足够的代码让测试通过

```go
func SumAllTails(numbersToSum ...[]int) []int {
	var sums []int
	for _, numbers := range numbersToSum {
		tail := numbers[1:]
		sums = append(sums, Sum(tail))
	}

	return sums
}
```


切片还可以再切片！语法是 `slice[low:high]`。如果省略 `:` 某一侧的值，它会取那一侧的所有内容。在我们的例子里，`numbers[1:]` 说的就是"从 1 取到末尾"。你不妨花点时间多写一些围绕切片的测试，摆弄摆弄切片操作符，跟它混熟一些。

## 重构

这次没什么可重构的。

你觉得，如果往我们的函数里传入一个空切片，会发生什么？空切片的"尾部"是什么？当你让 Go 从 `myEmptySlice[1:]` 获取所有元素时，会发生什么？

## 先写测试

```go
func TestSumAllTails(t *testing.T) {

	t.Run("make the sums of some slices", func(t *testing.T) {
		got := SumAllTails([]int{1, 2}, []int{0, 9})
		want := []int{2, 9}

		if !slices.Equal(got, want) {
			t.Errorf("got %v want %v", got, want)
		}
	})

	t.Run("safely sum empty slices", func(t *testing.T) {
		got := SumAllTails([]int{}, []int{3, 4, 5})
		want := []int{0, 9}

		if !slices.Equal(got, want) {
			t.Errorf("got %v want %v", got, want)
		}
	})

}
```


## 试着运行测试

```text
panic: runtime error: slice bounds out of range [recovered]
    panic: runtime error: slice bounds out of range
```


糟糕！值得注意的是：测试_编译通过了_，但它_有一个运行时错误_。

编译期错误是我们的朋友，因为它帮我们写出能正常工作的软件；运行时错误是我们的敌人，因为它坑的是我们的用户。

## 写足够的代码让测试通过

```go
func SumAllTails(numbersToSum ...[]int) []int {
	var sums []int
	for _, numbers := range numbersToSum {
		if len(numbers) == 0 {
			sums = append(sums, 0)
		} else {
			tail := numbers[1:]
			sums = append(sums, Sum(tail))
		}
	}

	return sums
}
```


## 重构

我们的测试里断言部分的代码又出现了重复，这次把它们提取到一个函数里。

```go
func TestSumAllTails(t *testing.T) {

	checkSums := func(t *testing.T, got, want []int) {
		t.Helper()
		if !slices.Equal(got, want) {
			t.Errorf("got %v want %v", got, want)
		}
	}

	t.Run("make the sums of tails of", func(t *testing.T) {
		got := SumAllTails([]int{1, 2}, []int{0, 9})
		want := []int{2, 9}
		checkSums(t, got, want)
	})

	t.Run("safely sum empty slices", func(t *testing.T) {
		got := SumAllTails([]int{}, []int{3, 4, 5})
		want := []int{0, 9}
		checkSums(t, got, want)
	})

}
```


我们本可以像往常一样新建一个 `checkSums` 函数，但这次我们展示一种新技术：把函数赋值给变量。它看上去可能有点怪，但这跟把一个 `string` 或 `int` 赋给变量没什么两样——函数其实也是值。

这里没有演示，但当你想把函数绑定到"作用域"（scope）内的其他局部变量上时（比如某对 `{}` 之间），这项技术会派上用场。它还能帮你缩小 API 的暴露面。

把函数定义在测试内部，本包中的其他函数就无法使用它。把不需要导出（exported）的变量和函数隐藏起来，是一个重要的设计考量。

这样做还有一个顺带的好处：它为我们的代码增添了一点类型安全（type-safety）。如果有开发者不小心在新测试里写成了 `checkSums(t, got, "dave")`，编译器会当场把他们拦下来。

```bash
$ go test
./sum_test.go:52:21: cannot use "dave" (type string) as type []int in argument to checkSums
```


## 总结

本章覆盖了

* 数组
* 切片
  * 创建它们的种种方式
  * 它们有_固定_的容量，但你可以用 `append` 从旧切片创建新切片
  * 如何给切片再切片！
* `len`，用来获取数组或切片的长度
* 测试覆盖率工具
* `slices.Equal`，以及为什么需要用它来替代常规的相等运算符

本章我们只用整数演示了切片和数组，但它们对其他任何类型同样适用，包括数组/切片本身。所以需要的话，你完全可以声明一个 `[][]string` 类型的变量。

想深入了解切片，可以[读一读 Go 博客上关于切片的那篇文章][blog-slice]。读完之后多写几个测试，把学到的知识巩固住。

除了写测试，另一个试验 Go 的顺手工具是 Go Playground。大多数东西都可以在上面试，需要提问时也能轻松分享你的代码。[我做了一个带切片的 Go Playground，供你随意试验。](https://play.golang.org/p/ICCWcRGIO68)

[这个例子](https://play.golang.org/p/bTrRmYfNYCp)演示了对数组做切片后，修改切片会如何影响原数组；而切片的"副本"则不会影响原数组。[另一个例子](https://play.golang.org/p/Poth8JS28sc)说明了为什么对一个非常大的切片做切片之后，最好再复制一份。

[for]: ../iteration.md#
[blog-slice]: https://blog.golang.org/go-slices-usage-and-internals
[deepEqual]: https://golang.org/pkg/reflect/#DeepEqual
[slice]: https://golang.org/doc/effective_go.html#slices
