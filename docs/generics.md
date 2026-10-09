# 泛型

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/generics)**

本章将带你入门泛型（generics），打消你可能对它的种种顾虑，并让你对今后如何简化一部分代码心里有数。读完本章，你将学会编写：

- 接收泛型参数的函数
- 泛型数据结构

## 我们自己的测试辅助函数（`AssertEqual`、`AssertNotEqual`）

为了探索泛型，我们先来写一些测试辅助函数。

### 断言整数

从一个基础的版本开始，一步步朝目标迭代

```go
import "testing"

func TestAssertFunctions(t *testing.T) {
	t.Run("asserting on integers", func(t *testing.T) {
		AssertEqual(t, 1, 1)
		AssertNotEqual(t, 1, 2)
	})
}

func AssertEqual(t *testing.T, got, want int) {
	t.Helper()
	if got != want {
		t.Errorf("got %d, want %d", got, want)
	}
}

func AssertNotEqual(t *testing.T, got, want int) {
	t.Helper()
	if got == want {
		t.Errorf("didn't want %d", got)
	}
}
```

### 断言字符串

能对整数做相等断言当然很好，可要是想对 `string` 做断言呢？

```go
t.Run("asserting on strings", func(t *testing.T) {
	AssertEqual(t, "hello", "hello")
	AssertNotEqual(t, "hello", "Grace")
})
```

你会得到一个错误

```
# github.com/quii/learn-go-with-tests/generics [github.com/quii/learn-go-with-tests/generics.test]
./generics_test.go:12:18: cannot use "hello" (untyped string constant) as int value in argument to AssertEqual
./generics_test.go:13:21: cannot use "hello" (untyped string constant) as int value in argument to AssertNotEqual
./generics_test.go:13:30: cannot use "Grace" (untyped string constant) as int value in argument to AssertNotEqual
```

静下心来读一读这条错误，你会发现编译器在抱怨：我们正试图把一个 `string` 传给期望 `integer` 的函数。

#### 回顾一下类型安全

如果你读过本书前面的章节，或者用过静态类型语言，这应该不会让你意外。Go 编译器要求你在编写函数、结构体等等东西时，描述清楚自己想处理哪些类型。

你不能把 `string` 传给期望 `integer` 的函数。

虽然这有时显得像繁文缛节，但它其实极有帮助。把这些约束（constraint）描述清楚，你就能：

- 让函数实现更简单。向编译器说明你处理哪些类型，就等于**限制了可能存在的合法实现的数量**。你不能把 `Person` 和 `BankAccount` "相加"，也不能把一个 `integer` "变成大写"。在软件行业，约束往往极其有用。
- 避免一不小心把数据传给你并不想传的函数。

Go 也提供了一种让类型更抽象的方式——[接口](./structs-methods-and-interfaces.md)：你可以把函数设计成不接收具体类型，而是接收任何能提供你所需行为的类型。这样既获得了一些灵活性，又不失类型安全。

### 一个既接收字符串又接收整数的函数？（其实，别的类型也行）

Go 还有一招能让你的函数更灵活：把参数的类型声明为 `interface{}`，意思是"任何东西"。

试着把函数签名改成用这个类型。

```go
func AssertEqual(got, want interface{})

func AssertNotEqual(got, want interface{})

```

测试现在应该能编译并通过了。如果你故意让它们失败，会看到输出有点不伦不类，因为我们打印消息用的还是整数的 `%d` 格式化字符串；把它们换成通用的 `%+v` 格式，任何类型的值都能有更好的输出效果。

### `interface{}` 的问题

我们的 `AssertX` 函数相当简陋，但从概念上讲，它跟其他[流行库提供同类功能的方式](https://github.com/matryer/is/blob/master/is.go#L160)并没有太大区别

```go
func (is *I) Equal(a, b interface{})
```

那么问题出在哪儿呢？

一旦用了 `interface{}`，编译器就没法在写代码时帮到我们，因为我们没有告诉它任何有用的信息，说明传进函数的东西到底是什么类型。试着比较两个不同的类型。

```go
AssertEqual(1, "1")
```

这个例子侥幸过关：测试能编译，也如愿失败了，尽管错误消息 `got 1, want 1` 让人摸不着头脑。可是，我们真的想让字符串跟整数互相比较吗？拿 `Person` 跟 `Airport` 比呢？

编写接收 `interface{}` 的函数可能极具挑战性，还容易滋生 bug，因为我们*丢掉了*约束，而且编译期对我们在跟什么数据打交道毫无线索。

这意味着**编译器帮不了我们**，我们反而更可能遇上**运行时错误**，轻则影响用户、造成服务中断，重则更糟。

开发者常常不得不借助反射（reflection）来实现这些*咳咳*"泛型"函数，这样的代码读写起来都很费劲，还可能拖累程序的性能。

## 用泛型实现我们自己的测试辅助函数

理想情况是，我们不必为打交道的每一种类型都专门写一套 `AssertX` 函数。我们想要*一个*能配合*任何*类型使用的 `AssertEqual`，但它又不允许你[拿苹果跟橙子作比较](https://en.wikipedia.org/wiki/Apples_and_oranges)。

泛型给了我们一种做出抽象的手段（就像接口那样）：让我们能**描述自己的约束**。借助泛型，我们可以写出灵活程度跟 `interface{}` 相当的函数，同时保住类型安全，给调用者带来的开发体验也更好。

```go
func TestAssertFunctions(t *testing.T) {
	t.Run("asserting on integers", func(t *testing.T) {
		AssertEqual(t, 1, 1)
		AssertNotEqual(t, 1, 2)
	})

	t.Run("asserting on strings", func(t *testing.T) {
		AssertEqual(t, "hello", "hello")
		AssertNotEqual(t, "hello", "Grace")
	})

	// AssertEqual(t, 1, "1") // 取消注释看看编译器报什么错
}

func AssertEqual[T comparable](t *testing.T, got, want T) {
	t.Helper()
	if got != want {
		t.Errorf("got %v, want %v", got, want)
	}
}

func AssertNotEqual[T comparable](t *testing.T, got, want T) {
	t.Helper()
	if got == want {
		t.Errorf("didn't want %v", got)
	}
}
```

要在 Go 里写泛型函数，你需要提供"类型参数"（type parameters）——说得玄乎，其实就是"描述你的泛型类型，并给它起个标签"。

在我们的例子里，类型参数的约束是 `comparable`，标签是 `T`。有了这个标签，我们就能进一步描述函数参数的类型（`got, want T`）。

我们之所以用 `comparable`，是想告诉编译器：我们希望在函数里对 `T` 类型的值使用 `==` 和 `!=` 运算符——我们要做比较！如果你试着把约束改成 `any`，

```go
func AssertNotEqual[T any](got, want T)
```

你会得到这样的错误：

```
prog.go2:15:5: cannot compare got != want (operator != not defined for T)
```

这就非常合理了，因为你没法在每一种类型（也就是 `any`）上使用这些运算符。

### [`T any`](https://go.googlesource.com/proposal/+/refs/heads/master/design/go2draft-type-parameters.md#the-constraint) 的泛型函数，跟 `interface{}` 是一回事吗？

看两个函数

```go
func GenericFoo[T any](x, y T)
```

```go
func InterfaceyFoo(x, y interface{})
```

泛型在这里的意义何在？`any` 难道不是描述了……任何东西吗？

单论约束，`any` 确实表示"任何东西"，`interface{}` 也是。事实上，`any` 是 Go 1.18 才加入的，它*只是 `interface{}` 的一个别名（alias）*。

泛型版本的不同之处在于，*你描述的仍然是一个具体的类型*——这就意味着，我们仍然把这个函数限定为只能处理*一种*类型。

也就是说，你可以用任意类型组合去调用 `InterfaceyFoo`（比如 `InterfaceyFoo(apple, orange)`）。而 `GenericFoo` 仍然带着约束，因为我们说过它只支持*一种*类型 `T`。

合法：

- `GenericFoo(apple1, apple2)`
- `GenericFoo(orange1, orange2)`
- `GenericFoo(1, 2)`
- `GenericFoo("one", "two")`

不合法（编译不通过）：

- `GenericFoo(apple1, orange1)`
- `GenericFoo("1", 1)`

如果你的函数返回泛型类型，调用者还能按原样使用这个类型，而不必做类型断言（type assertion），因为函数返回 `interface{}` 时，编译器对它的类型做不出任何保证。

## 接下来：泛型数据类型

我们来创建一个[栈](https://en.wikipedia.org/wiki/Stack_(abstract_data_type))数据类型。单看需求，栈应该很好理解：它是一组元素的集合，你可以把元素 `Push`（压入）到"栈顶"，要取回元素就再从栈顶把元素 `Pop`（弹出）出来（LIFO——后进先出，last in, first out）。

为省篇幅，下面这份 `int` 栈和 `string` 栈的代码是怎么通过 TDD 得出的，我就略去不表了。

```go
type StackOfInts struct {
	values []int
}

func (s *StackOfInts) Push(value int) {
	s.values = append(s.values, value)
}

func (s *StackOfInts) IsEmpty() bool {
	return len(s.values) == 0
}

func (s *StackOfInts) Pop() (int, bool) {
	if s.IsEmpty() {
		return 0, false
	}

	index := len(s.values) - 1
	el := s.values[index]
	s.values = s.values[:index]
	return el, true
}

type StackOfStrings struct {
	values []string
}

func (s *StackOfStrings) Push(value string) {
	s.values = append(s.values, value)
}

func (s *StackOfStrings) IsEmpty() bool {
	return len(s.values) == 0
}

func (s *StackOfStrings) Pop() (string, bool) {
	if s.IsEmpty() {
		return "", false
	}

	index := len(s.values) - 1
	el := s.values[index]
	s.values = s.values[:index]
	return el, true
}
```

我还另外写了两个断言函数来帮忙

```go
func AssertTrue(t *testing.T, got bool) {
	t.Helper()
	if !got {
		t.Errorf("got %v, want true", got)
	}
}

func AssertFalse(t *testing.T, got bool) {
	t.Helper()
	if got {
		t.Errorf("got %v, want false", got)
	}
}
```

测试如下

```go
func TestStack(t *testing.T) {
	t.Run("integer stack", func(t *testing.T) {
		myStackOfInts := new(StackOfInts)

		// 检查栈是不是空的
		AssertTrue(t, myStackOfInts.IsEmpty())

		// 放一个元素进去，然后检查栈不为空
		myStackOfInts.Push(123)
		AssertFalse(t, myStackOfInts.IsEmpty())

		// 再放一个元素，然后把它弹出来
		myStackOfInts.Push(456)
		value, _ := myStackOfInts.Pop()
		AssertEqual(t, value, 456)
		value, _ = myStackOfInts.Pop()
		AssertEqual(t, value, 123)
		AssertTrue(t, myStackOfInts.IsEmpty())
	})

	t.Run("string stack", func(t *testing.T) {
		myStackOfStrings := new(StackOfStrings)

		// 检查栈是不是空的
		AssertTrue(t, myStackOfStrings.IsEmpty())

		// 放一个元素进去，然后检查栈不为空
		myStackOfStrings.Push("123")
		AssertFalse(t, myStackOfStrings.IsEmpty())

		// 再放一个元素，然后把它弹出来
		myStackOfStrings.Push("456")
		value, _ := myStackOfStrings.Pop()
		AssertEqual(t, value, "456")
		value, _ = myStackOfStrings.Pop()
		AssertEqual(t, value, "123")
		AssertTrue(t, myStackOfStrings.IsEmpty())
	})
}
```

### 问题

- `StackOfStrings` 和 `StackOfInts` 的代码几乎一模一样。重复代码虽然未必是世界末日，但终究意味着更多的代码要读、要写、要维护。
- 同一套逻辑在两个类型间重复了，测试也就不得不跟着重复一份。

我们真正想要的，是把栈这个*概念*收进一个类型里，再用一套测试覆盖它就够了。此刻我们应该戴上"重构"的帽子：也就是说，不该去改测试，因为我们要保持行为不变。

如果不用泛型，我们*可以*这么做

```go
type StackOfInts = Stack
type StackOfStrings = Stack

type Stack struct {
	values []interface{}
}

func (s *Stack) Push(value interface{}) {
	s.values = append(s.values, value)
}

func (s *Stack) IsEmpty() bool {
	return len(s.values) == 0
}

func (s *Stack) Pop() (interface{}, bool) {
	if s.IsEmpty() {
		var zero interface{}
		return zero, false
	}

	index := len(s.values) - 1
	el := s.values[index]
	s.values = s.values[:index]
	return el, true
}
```

- 我们给之前的 `StackOfInts` 和 `StackOfStrings` 实现起了别名，统一指向新的类型 `Stack`
- 我们让 `values` 成为 `interface{}` 的[切片](https://github.com/quii/learn-go-with-tests/blob/main/arrays-and-slices.md)，`Stack` 也就失去了类型安全

想试试这段代码，你得先把断言函数上的类型约束去掉：

```go
func AssertEqual(t *testing.T, got, want interface{})
```

这么一改，我们的测试照样全过。还要泛型干什么？

### 抛弃类型安全的代价

第一个问题跟 `AssertEquals` 那里如出一辙——我们丢掉了类型安全。现在我可以往橙子栈里 `Push` 苹果了。

就算我们有足够的自律、绝不这么干，这样的代码用起来依然难受，因为方法一旦**返回 `interface{}`，用起来就格外恶心**。

加上下面这个测试，

```go
t.Run("interface stack DX is horrid", func(t *testing.T) {
	myStackOfInts := new(StackOfInts)

	myStackOfInts.Push(1)
	myStackOfInts.Push(2)
	firstNum, _ := myStackOfInts.Pop()
	secondNum, _ := myStackOfInts.Pop()
	AssertEqual(t, firstNum+secondNum, 3)
})
```

你会得到一个编译错误，它正好暴露了丢失类型安全的软肋：

```
invalid operation: operator + not defined on firstNum (variable of type interface{})
```

`Pop` 返回 `interface{}`，意味着编译器对这份数据一无所知，我们能做的事因此大受限制。它不知道这应该是个整数，也就不允许我们使用 `+` 运算符。

为了绕开这个问题，调用者得对每个值做一次[类型断言](https://golang.org/ref/spec#Type_assertions)。

```go
t.Run("interface stack dx is horrid", func(t *testing.T) {
	myStackOfInts := new(StackOfInts)

	myStackOfInts.Push(1)
	myStackOfInts.Push(2)
	firstNum, _ := myStackOfInts.Pop()
	secondNum, _ := myStackOfInts.Pop()

	// 从 interface{} 里把 int 取出来
	reallyFirstNum, ok := firstNum.(int)
	AssertTrue(t, ok) // 得确认我们确实从 interface{} 里拿到了 int

	reallySecondNum, ok := secondNum.(int)
	AssertTrue(t, ok) // 这里也一样！

	AssertEqual(t, reallyFirstNum+reallySecondNum, 3)
})
```

这段测试散发出的难受劲儿，`Stack` 实现的每一个潜在用户都得原样再受一遍。真恶心。

### 泛型数据结构来救场

就像函数可以定义泛型参数一样，数据结构也可以定义成泛型的。

下面是我们新的 `Stack` 实现，带上了泛型数据类型。

```go
type Stack[T any] struct {
	values []T
}

func (s *Stack[T]) Push(value T) {
	s.values = append(s.values, value)
}

func (s *Stack[T]) IsEmpty() bool {
	return len(s.values) == 0
}

func (s *Stack[T]) Pop() (T, bool) {
	if s.IsEmpty() {
		var zero T
		return zero, false
	}

	index := len(s.values) - 1
	el := s.values[index]
	s.values = s.values[:index]
	return el, true
}
```

测试如下，可以看到它们完全按我们的期望工作，享有完整的类型安全。

```go
func TestStack(t *testing.T) {
	t.Run("integer stack", func(t *testing.T) {
		myStackOfInts := new(Stack[int])

		// 检查栈是不是空的
		AssertTrue(t, myStackOfInts.IsEmpty())

		// 放一个元素进去，然后检查栈不为空
		myStackOfInts.Push(123)
		AssertFalse(t, myStackOfInts.IsEmpty())

		// 再放一个元素，然后把它弹出来
		myStackOfInts.Push(456)
		value, _ := myStackOfInts.Pop()
		AssertEqual(t, value, 456)
		value, _ = myStackOfInts.Pop()
		AssertEqual(t, value, 123)
		AssertTrue(t, myStackOfInts.IsEmpty())

		// 取出来的就是我们放进去的数字，而不是无类型的 interface{}
		myStackOfInts.Push(1)
		myStackOfInts.Push(2)
		firstNum, _ := myStackOfInts.Pop()
		secondNum, _ := myStackOfInts.Pop()
		AssertEqual(t, firstNum+secondNum, 3)
	})
}
```

你会注意到，定义泛型数据结构的语法跟给函数定义泛型参数的语法是一致的。

```go
type Stack[T any] struct {
	values []T
}
```

它跟之前*几乎*一样，不同的只是：**栈的类型约束了你能处理什么类型的值**。

一旦你创建了 `Stack[Orange]` 或 `Stack[Apple]`——也就是用具体类型把泛型实例化（instantiation）——栈上定义的方法就只允许你传入、也只会返回你所用的那个栈的具体类型：

```go
func (s *Stack[T]) Pop() (T, bool)
```

你不妨想象这些实现是按需替你生成好的——你创建什么类型的栈，就生成哪一版：

```go
func (s *Stack[Orange]) Pop() (Orange, bool)
```

```go
func (s *Stack[Apple]) Pop() (Apple, bool)
```

完成这次重构之后，我们就可以放心删掉 `string` 栈的测试了，因为没必要把同样的逻辑证明一遍又一遍。

注意，到目前为止的示例里，调用泛型函数时我们都不需要指定泛型类型。例如调用 `AssertEqual[T]` 时，不必指明类型 `T` 是什么，因为编译器能根据参数把它推断出来（type inference，类型推断）。而当泛型类型无法被推断时，就需要在调用函数时显式指定类型，语法与定义函数时相同：在参数前的方括号里写上类型。


```go
func NewStack[T any]() *Stack[T] {
	return new(Stack[T])
}
```
要用这个构造函数创建一个 `int` 栈和一个 `string` 栈，可以这样调用：
```go
myStackOfInts := NewStack[int]()
myStackOfStrings := NewStack[string]()
```

下面是加上构造函数之后的 `Stack` 实现和测试。

```go
type Stack[T any] struct {
	values []T
}

func NewStack[T any]() *Stack[T] {
	return new(Stack[T])
}

func (s *Stack[T]) Push(value T) {
	s.values = append(s.values, value)
}

func (s *Stack[T]) IsEmpty() bool {
	return len(s.values) == 0
}

func (s *Stack[T]) Pop() (T, bool) {
	if s.IsEmpty() {
		var zero T
		return zero, false
	}

	index := len(s.values) - 1
	el := s.values[index]
	s.values = s.values[:index]
	return el, true
}
```

```go
func TestStack(t *testing.T) {
	t.Run("integer stack", func(t *testing.T) {
		myStackOfInts := NewStack[int]()

		// 检查栈是不是空的
		AssertTrue(t, myStackOfInts.IsEmpty())

		// 放一个元素进去，然后检查栈不为空
		myStackOfInts.Push(123)
		AssertFalse(t, myStackOfInts.IsEmpty())

		// 再放一个元素，然后把它弹出来
		myStackOfInts.Push(456)
		value, _ := myStackOfInts.Pop()
		AssertEqual(t, value, 456)
		value, _ = myStackOfInts.Pop()
		AssertEqual(t, value, 123)
		AssertTrue(t, myStackOfInts.IsEmpty())

		// 取出来的就是我们放进去的数字，而不是无类型的 interface{}
		myStackOfInts.Push(1)
		myStackOfInts.Push(2)
		firstNum, _ := myStackOfInts.Pop()
		secondNum, _ := myStackOfInts.Pop()
		AssertEqual(t, firstNum+secondNum, 3)
	})
}
```

用上泛型数据类型，我们做到了：

- 减少了重要逻辑的重复。
- 让 `Pop` 返回 `T`，这样创建 `Stack[int]` 后，`Pop` 实际返回的就是 `int`；现在可以直接用 `+`，不必再耍类型断言的杂技。
- 在编译期就防住了误用。你没法往苹果栈里 `Push` 橙子。

## 总结

本章应该让你初尝了泛型语法的滋味，也对"泛型为什么有用"有了一些想法。我们写了自己的 `Assert` 函数，以后可以放心地复用它去试验泛型的其他玩法；我们还实现了一个简单的数据结构，能以类型安全的方式存放我们想要的任何类型的数据。

### 大多数情况下，泛型比 `interface{}` 更简单

如果你对静态类型语言经验不多，泛型的意义可能不是一眼就能看出来的，但我希望本章的例子已经展示了 Go 语言在哪些地方表达力不如我们所愿。尤其是使用 `interface{}` 会让你的代码：

- 更不安全（苹果橙子混着来），需要更多错误处理
- 表达力更弱，`interface{}` 对数据只字不提
- 更依赖[反射](https://github.com/quii/learn-go-with-tests/blob/main/reflection.md)、类型断言等手段，代码更难处理、更容易出错，因为它把检查从编译期推到了运行期

使用静态类型语言，本质上是描述约束的过程。做得好，你写出的代码不仅安全易用，编写起来也更简单，因为可能的解空间变小了。

泛型给了我们在代码中表达约束的新方式。正如前面所展示的，有了它，我们才能合并并简化代码——在 Go 1.18 之前这是做不到的。

### 泛型会把 Go 变成 Java 吗？

- 不会。

Go 社区里有不少[关于泛型的 FUD（fear, uncertainty and doubt，恐惧、不确定与怀疑）](https://en.wikipedia.org/wiki/Fear,_uncertainty,_and_doubt)，生怕泛型带来噩梦般的抽象和令人费解的代码库。这种论调通常还要补一句"必须小心使用"。

这话没错，但算不上什么特别有用的建议，因为任何语言特性都是如此。

没多少人抱怨我们能定义接口这件事，而接口跟泛型一样，也是在代码中描述约束的一种方式。定义接口时，你就是在做一个*可能很糟糕的*设计决策；能把代码搞得令人困惑、用着闹心的，并不只有泛型。

### 你其实已经在用泛型了

想一想：只要你用过数组、切片或 map，你就*早已是泛型代码的使用者*。

```
var myApples []Apple
// You can't do this!
append(myApples, Orange{})
```

### 抽象不是贬义词

嘲讽 [AbstractSingletonProxyFactoryBean](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/aop/framework/AbstractSingletonProxyFactoryBean.html) 很容易，但也别假装毫无抽象的代码库就没什么不好。你的职责是在合适的时机*归拢*相关概念，让系统更易于理解和修改；而不是任由代码沦为一堆界限不清、各不相干的函数和类型。

### [先让它跑起来，再把它做对，再让它变快](https://wiki.c2.com/?MakeItWorkMakeItRightMakeItFast#:~:text=%22Make%20it%20work%2C%20make%20it,to%20DesignForPerformance%20ahead%20of%20time.)

人们在信息还不足以做出好的设计决策时就急着抽象，这时泛型就会带来麻烦。

红、绿、重构的 TDD 循环意味着，对于要交付的行为*真正需要*哪些代码，你会有更多的依据，**而不是凭空预先想象抽象**；但你仍然需要小心。

这里没有硬性规定，但在看清自己手里确实有一个有用的泛化之前，请忍住别把东西泛型化。我们创建各个 `Stack` 实现时，关键的一点是从*具体的*行为起步，比如有测试撑腰的 `StackOfStrings` 和 `StackOfInts`。从*真实的*代码中，我们才能看出真实的模式；有测试保驾护航，我们才敢放手重构，探索更通用的方案。

人们常常建议：同一段代码见过三次再考虑泛化。这听起来是个不错的经验法则起点。

我在其他编程语言里走过的一条常见路径是：

- 一个 TDD 循环驱动出某个行为
- 再来一个 TDD 循环，覆盖另外一些相关场景

> 嗯，这几样东西看起来挺像——不过，一点点重复总好过耦合到一个糟糕的抽象上

- 睡一觉，先放一放
- 再来一个 TDD 循环

> 好，我想试试能不能把这东西泛化。多亏我又聪明又英俊，还用着 TDD：想什么时候重构就什么时候重构，而且整个过程帮我在过度设计之前就弄明白了真正需要的行为。

- 这个抽象感觉真不错！测试照样全过，代码也更简单了
- 现在我可以删掉一批测试了——我已经抓住了行为的*本质*，去掉了不必要的细节。
