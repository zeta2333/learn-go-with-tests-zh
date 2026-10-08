# 用泛型重访数组与切片

**[本章的所有代码承接着《数组和切片》，可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/arrays)**

先看看我们在[数组和切片](arrays-and-slices.md)一章里写过的 `SumAll` 和 `SumAllTails`。如果你手头没有自己的版本，请把[数组和切片](arrays-and-slices.md)一章的代码连同测试一起复制过来。

```go
// Sum 计算一个数字切片的总和。
func Sum(numbers []int) int {
	var sum int
	for _, number := range numbers {
		sum += number
	}
	return sum
}

// SumAllTails 给定一组切片，计算除第一个数字之外其余数字的总和。
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

看出一个反复出现的模式了吗？

- 先创建某种"初始"的结果值。
- 遍历集合，把某种操作（或函数）作用到结果和切片中的下一个元素上，为结果设置一个新值
- 返回结果。

函数式编程圈子里经常谈论这个想法，通常叫它 "reduce" 或 [fold](https://en.wikipedia.org/wiki/Fold_(higher-order_function))。

> 在函数式编程中，fold（也称 reduce、accumulate、aggregate、compress 或 inject）指的是一族分析递归数据结构的高阶函数：通过使用给定的组合操作，把递归处理其组成部分所得到的结果重新组合起来，构建出一个返回值。通常，fold 会得到一个组合函数、一个数据结构的顶层节点，以及在特定条件下可能用到的一些默认值。然后 fold 会有条不紊地使用这个函数，去组合数据结构层级中的各个元素。

Go 一直都有高阶函数，而到了 1.18 版本，它又拥有了[泛型](./generics.md)，所以现在我们完全可以自己定义一些前面讨论过的这类函数。把头埋进沙子里是没有意义的，这是 Go 生态之外非常常见的一种抽象，理解它会让你受益。

现在，我知道你们当中有些人看到这里大概已经开始畏缩了。

> Go 不是号称简单吗

**别把"容易"和"简单"混为一谈**。写循环、复制粘贴代码是容易的，但不一定简单。想深入了解简单与容易之别，可以去看 [Rich Hickey 的杰作级演讲 - Simple Made Easy](https://www.youtube.com/watch?v=SxdOUGdseq4)。

**别把"陌生"和"复杂"混为一谈**。Fold/reduce 一开始听起来可能很吓人，很有计算机科学的味道，但它实际上只是对一个极其常见的操作的抽象：取一个集合，把它组合成一个值。退后一步看，你会意识到你可能_经常_做这件事。

## 一次泛型重构

人们面对闪亮的新语言特性时经常犯的一个错误，是在还没有具体用例的情况下就开始使用它们。他们依靠臆测和猜测来指导自己的努力。

值得庆幸的是，我们已经写好了自己的"有用"函数，并且有测试围绕它们，所以现在我们可以在 TDD 的重构阶段自由地试验各种想法，并且知道无论我们尝试什么，它的价值都有我们的单元测试来验证。

通过重构这一步把泛型当作简化代码的工具来使用，更有可能引导你获得有用的改进，而不是过早的抽象。

我们可以放心地尝试，重新运行测试；如果我们喜欢这个改动，就可以 commit；如果不喜欢，把这个改动 revert 掉就行。这种自由试验的自由是 TDD 真正巨大的价值之一。

[从上一章](generics.md)你应该已经熟悉了泛型的语法，试着写出你自己的 `Reduce` 函数，并在 `Sum` 和 `SumAllTails` 里使用它。

### 提示

如果你先思考函数的参数，它会给你一个非常小的有效解集
  - 你想要 reduce 的数组
  - 某种组合函数

"Reduce" 是一个文档丰富得难以置信的模式，没有必要重新发明轮子。[阅读那个 wiki，特别是 lists 部分](https://en.wikipedia.org/wiki/Fold_(higher-order_function))，它应该会提示你需要的另一个参数。

> 在实践中，拥有一个初始值是方便且自然的

### 我的 `Reduce` 第一版

```go
func Reduce[A any](collection []A, f func(A, A) A, initialValue A) A {
	var result = initialValue
	for _, x := range collection {
		result = f(result, x)
	}
	return result
}
```

`Reduce` 捕捉到了这个模式的_精髓_，它是一个接收集合、累加函数、初始值并返回单个值的函数。没有围绕具体类型的混乱干扰。

如果你理解泛型语法，理解这个函数做什么应该没有问题。通过使用公认的术语 `Reduce`，来自其他语言的程序员也能理解其意图。

### 用法

```go
// Sum 计算一个数字切片的总和。
func Sum(numbers []int) int {
	add := func(acc, x int) int { return acc + x }
	return Reduce(numbers, add, 0)
}

// SumAllTails 给定一组切片，计算除第一个数字之外其余数字的总和。
func SumAllTails(numbers ...[]int) []int {
	sumTail := func(acc, x []int) []int {
		if len(x) == 0 {
			return append(acc, 0)
		} else {
			tail := x[1:]
			return append(acc, Sum(tail))
		}
	}

	return Reduce(numbers, sumTail, []int{})
}
```

`Sum` 和 `SumAllTails` 现在分别在它们的第一行声明的函数中描述了它们计算的行为。在集合上运行计算的行为被抽象到了 `Reduce` 中。

## reduce 的更多应用

使用测试，我们可以把我们的 reduce 函数拿来玩一玩，看看它的可复用性如何。我已经从上一章复制了我们的泛型断言函数。

```go
func TestReduce(t *testing.T) {
	t.Run("multiplication of all elements", func(t *testing.T) {
		multiply := func(x, y int) int {
			return x * y
		}

		AssertEqual(t, Reduce([]int{1, 2, 3}, multiply, 1), 6)
	})

	t.Run("concatenate strings", func(t *testing.T) {
		concatenate := func(x, y string) string {
			return x + y
		}

		AssertEqual(t, Reduce([]string{"a", "b", "c"}, concatenate, ""), "abc")
	})
}
```

### 零值

在乘法的例子中，我们展示了把一个默认值作为参数传给 `Reduce` 的原因。如果我们依赖 Go 对 `int` 的默认值 0，我们会把初始值乘以 0，然后再乘以后面的那些，所以你只会得到 0。把它设置为 1，切片中的第一个元素将保持不变，其余的将乘以后面的元素。

如果你想在你的书呆子朋友面前显得聪明，你可以称之为[单位元](https://en.wikipedia.org/wiki/Identity_element)。

> 在数学中，作用于一个集合上的二元运算的单位元，或称中性元素，是该集合中的一个元素，当运算被应用时，它使该集合中的每个元素都保持不变。

另外，单位元对于加法是 0。

`1 + 0 = 1`

对于乘法，它是 1。

`1 * 1 = 1`

## 如果我们希望 reduce 成与 `A` 不同的类型怎么办？

假设我们有一个交易列表 `Transaction`，我们想要一个函数，接收它们外加一个名字，来算出他们的银行余额。

让我们遵循 TDD 流程。

## 先写测试

```go
func TestBadBank(t *testing.T) {
	transactions := []Transaction{
		{
			From: "Chris",
			To:   "Riya",
			Sum:  100,
		},
		{
			From: "Adil",
			To:   "Chris",
			Sum:  25,
		},
	}

	AssertEqual(t, BalanceFor(transactions, "Riya"), 100)
	AssertEqual(t, BalanceFor(transactions, "Chris"), -75)
	AssertEqual(t, BalanceFor(transactions, "Adil"), -25)
}
```

## 试着运行测试

```
# github.com/quii/learn-go-with-tests/arrays/v8 [github.com/quii/learn-go-with-tests/arrays/v8.test]
./bad_bank_test.go:6:20: undefined: Transaction
./bad_bank_test.go:18:14: undefined: BalanceFor
```

## 写最少的代码让测试能运行，并检查失败的测试输出

我们还没有我们的类型和函数，添加它们以使测试运行。

```go
type Transaction struct {
	From string
	To   string
	Sum  float64
}

func BalanceFor(transactions []Transaction, name string) float64 {
	return 0.0
}
```

当你运行测试时，你应该看到以下内容：

```
=== RUN   TestBadBank
    bad_bank_test.go:19: got 0, want 100
    bad_bank_test.go:20: got 0, want -75
    bad_bank_test.go:21: got 0, want -25
--- FAIL: TestBadBank (0.00s)
```

## 写足够的代码让测试通过

让我们先假装我们没有 `Reduce` 函数来编写代码。

```go
func BalanceFor(transactions []Transaction, name string) float64 {
	var balance float64
	for _, t := range transactions {
		if t.From == name {
			balance -= t.Sum
		}
		if t.To == name {
			balance += t.Sum
		}
	}
	return balance
}
```

## 重构

在这一点上，保持一些源码控制的纪律，commit 你的工作。我们有了能工作的软件，准备好挑战 Monzo、Barclays 等了。

现在我们的工作已经 commit，我们可以自由地把玩它，并在重构阶段尝试一些不同的想法。公平地说，我们已有的代码并不算差，但为了这个练习的目的，我想用 `Reduce` 演示同样的代码。

```go
func BalanceFor(transactions []Transaction, name string) float64 {
	adjustBalance := func(currentBalance float64, t Transaction) float64 {
		if t.From == name {
			return currentBalance - t.Sum
		}
		if t.To == name {
			return currentBalance + t.Sum
		}
		return currentBalance
	}
	return Reduce(transactions, adjustBalance, 0.0)
}
```

但这将无法编译。

```
./bad_bank.go:19:35: type func(acc float64, t Transaction) float64 of adjustBalance does not match inferred type func(Transaction, Transaction) Transaction for func(A, A) A
```

原因是我们正试图 reduce 成与集合类型_不同_的一个类型。这听起来很吓人，但实际上只需要我们调整 `Reduce` 的类型签名就能让它工作。我们不必更改函数体，也不必更改任何现有的调用者。

```go
func Reduce[A, B any](collection []A, f func(B, A) B, initialValue B) B {
	var result = initialValue
	for _, x := range collection {
		result = f(result, x)
	}
	return result
}
```

我们添加了第二个类型约束，这使我们能够放宽对 `Reduce` 的约束。这使得人们可以把 `A` 的集合 `Reduce` 成一个 `B`。在我们的例子中，是从 `Transaction` 到 `float64`。

这使得 `Reduce` 更加通用和可复用，并且仍然是类型安全的。如果你尝试再次运行测试，它们应该可以编译并通过。

## 扩展银行

为了好玩，我想改进银行代码的人机工程学。为了简洁起见，我省略了 TDD 过程。

```go
func TestBadBank(t *testing.T) {
	var (
		riya  = Account{Name: "Riya", Balance: 100}
		chris = Account{Name: "Chris", Balance: 75}
		adil  = Account{Name: "Adil", Balance: 200}

		transactions = []Transaction{
			NewTransaction(chris, riya, 100),
			NewTransaction(adil, chris, 25),
		}
	)

	newBalanceFor := func(account Account) float64 {
		return NewBalanceFor(account, transactions).Balance
	}

	AssertEqual(t, newBalanceFor(riya), 200)
	AssertEqual(t, newBalanceFor(chris), 0)
	AssertEqual(t, newBalanceFor(adil), 175)
}
```

这是更新后的代码

```go
package main

type Transaction struct {
	From string
	To   string
	Sum  float64
}

func NewTransaction(from, to Account, sum float64) Transaction {
	return Transaction{From: from.Name, To: to.Name, Sum: sum}
}

type Account struct {
	Name    string
	Balance float64
}

func NewBalanceFor(account Account, transactions []Transaction) Account {
	return Reduce(
		transactions,
		applyTransaction,
		account,
	)
}

func applyTransaction(a Account, transaction Transaction) Account {
	if transaction.From == a.Name {
		a.Balance -= transaction.Sum
	}
	if transaction.To == a.Name {
		a.Balance += transaction.Sum
	}
	return a
}
```

我觉得这真正展示了使用 `Reduce` 这类概念的力量。`NewBalanceFor` 感觉更加_声明式_，描述_发生什么_而不是_如何发生_。通常当我们阅读代码时，我们在许多文件中飞快穿行，我们试图理解的是_发生了什么_而不是_如何发生_，而这种代码风格很好地促进了这一点。

如果我希望深入了解细节，我可以这样做，并且我可以看到 `applyTransaction` 的_业务逻辑_而无需担心循环和修改状态；`Reduce` 单独处理这些。

### Fold/reduce 相当通用

有了 `Reduce`（或 `Fold`），可能性是无穷的™️。它是一个常见模式是有原因的，它不仅仅用于算术或字符串拼接。尝试一些其他的应用。

- 为什么不把一些 `color.RGBA` 混合成单一颜色？
- 统计一次投票中的票数，或购物篮中的商品数量。
- 几乎任何涉及处理列表的事情。

## Find

既然 Go 有了泛型，将它们与高阶函数结合，我们可以减少项目内大量的样板代码，帮助我们的系统更容易理解和管理。

你不再需要为每种你想要搜索的集合类型编写特定的 `Find` 函数，而是复用或编写一个 `Find` 函数。如果你理解了上面的 `Reduce` 函数，编写一个 `Find` 函数将是轻而易举的。

这里有一个测试

```go
func TestFind(t *testing.T) {
	t.Run("find first even number", func(t *testing.T) {
		numbers := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

		firstEvenNumber, found := Find(numbers, func(x int) bool {
			return x%2 == 0
		})
		AssertTrue(t, found)
		AssertEqual(t, firstEvenNumber, 2)
	})
}
```

这是实现

```go
func Find[A any](items []A, predicate func(A) bool) (value A, found bool) {
	for _, v := range items {
		if predicate(v) {
			return v, true
		}
	}
	return
}
```

同样，因为它接收一个泛型类型，我们可以以多种方式复用它

```go
type Person struct {
	Name string
}

t.Run("Find the best programmer", func(t *testing.T) {
	people := []Person{
		Person{Name: "Kent Beck"},
		Person{Name: "Martin Fowler"},
		Person{Name: "Chris James"},
	}

	king, found := Find(people, func(p Person) bool {
		return strings.Contains(p.Name, "Chris")
	})

	AssertTrue(t, found)
	AssertEqual(t, king, Person{Name: "Chris James"})
})
```

如你所见，这段代码毫无缺陷。

## 总结

用得有品位时，像这样的高阶函数将使你的代码更易于阅读和维护，但请记住经验法则：

使用 TDD 流程来逼出你实际需要的真实的、具体的行为，在重构阶段你然后_可能_会发现一些有用的抽象来帮助整理代码。

练习将 TDD 与良好的源码控制习惯相结合。当你的测试通过时 commit 你的工作，_在_尝试重构_之前_。这样如果你搞得一团糟，你可以轻松地让自己回到能工作的状态。

### 命名很重要

努力在 Go 之外做一些研究，这样你就不会重新发明那些已经存在并已有既定名称的模式。

编写一个接收 `A` 的集合并将它们转换为 `B` 的函数？不要称它为 `Convert`，那是 [`Map`](https://en.wikipedia.org/wiki/Map_(higher-order_function))。为这些事物使用"正确"的名称将减少其他人的认知负担，并使其在搜索引擎上更容易学到更多。

### 这感觉不惯用？

试着拥有一个开放的心态。

虽然 Go 的惯用法不会、也不应该由于泛型的发布而_彻底_改变，但惯用法_将会_改变——由于语言在变化！这不应该是一个有争议的观点。

说

> 这不惯用

而不提供任何更多细节，不是一个可操作的或有用的说法，特别是在讨论新语言特性时。

与你的同事讨论模式和代码风格时基于它们的优点而不是教条。只要你拥有设计良好的测试，随着你理解什么对你和你的团队有效，你将始终能够重构和调整。

### 资源

Fold 是计算机科学中一个真正的基石。如果你想深入了解它，这里有一些有趣的资源：
- [Wikipedia: Fold](https://en.wikipedia.org/wiki/Fold)
- [A tutorial on the universality and expressiveness of fold](http://www.cs.nott.ac.uk/~pszgmh/fold.pdf)
