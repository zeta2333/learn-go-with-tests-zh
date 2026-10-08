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
- 遍历集合，把某种操作（或函数）作用到结果和切片中的下一个元素上，为结果设一个新值
- 返回结果。

函数式编程圈子里经常谈论这个想法，通常叫它 "reduce" 或 [fold（折叠）](https://en.wikipedia.org/wiki/Fold_(higher-order_function))。

> 在函数式编程中，fold（也称 reduce、accumulate、aggregate、compress 或 inject）指的是一族分析递归数据结构的高阶函数：它们通过给定的组合操作，把递归处理各组成部分所得到的结果重新组合起来，构建出一个返回值。通常，使用 fold 时会提供一个组合函数、数据结构的顶层节点，以及在特定条件下可能用到的一些默认值。随后，fold 会有条不紊地运用这个函数，逐层组合数据结构层级中的各个元素。

Go 一直都有高阶函数（higher-order function），而到了 1.18 版本，它又拥有了[泛型](./generics.md)，所以我们现在完全可以把前面讨论过的这类函数自己定义出来。把头埋进沙子里逃避是没有意义的，这是 Go 生态之外非常常见的一种抽象，理解它对你大有好处。

现在，我知道你们当中有些人看到这里已经在皱眉头了。

> Go 不是号称简单吗

**别把"容易"和"简单"混为一谈**。写循环、复制粘贴代码很容易，但未必简单。想深入了解简单与容易之别，去看看 [Rich Hickey 的杰作级演讲 - Simple Made Easy](https://www.youtube.com/watch?v=SxdOUGdseq4)。

**别把"陌生"和"复杂"混为一谈**。Fold/reduce 一开始听着可能挺吓人，一股计算机科学的学究气，但它其实只是对一个极其常见的操作做的抽象：拿一个集合，把它组合成一个值。退后一步想想，你会发现自己八成_经常_在干这件事。

## 一次泛型重构

人们面对闪亮的新语言特性常犯的一个错误，是还没弄清具体用例就开始上手，全凭臆测和瞎猜来指导方向。

好在我们的"有用"函数已经写好，测试也都围着它们，所以在 TDD 的重构阶段，我们大可以放手试验各种想法，并且心里有数：不管试的是什么，它的价值都有单元测试替我们验证。

在重构这一步把泛型当作简化代码的工具来用，更有可能引导你做出真正有用的改进，而不是搞出过早的抽象。

放心大胆地试，重跑测试；喜欢这个改动就 commit，不喜欢就 revert 掉。这种放手试验的空间，正是 TDD 真正巨大的价值之一。

[上一章](generics.md)你已经见识过泛型的语法了，试着写出你自己的 `Reduce` 函数，把它用到 `Sum` 和 `SumAllTails` 里面吧。

### 提示

先想清楚函数要接收哪些参数，可行的解法立刻就只剩很小的一撮了
  - 你想 reduce 的那个数组
  - 某种组合函数

"Reduce" 是一个文档齐全得不可思议的模式，没必要重新发明轮子。[去读读那个 wiki 页面，尤其是 lists 那一节](https://en.wikipedia.org/wiki/Fold_(higher-order_function))，它会提醒你还差一个参数。

> 在实践中，提供一个初始值是方便且自然的做法

### 我的 `Reduce` 初版

```go
func Reduce[A any](collection []A, f func(A, A) A, initialValue A) A {
	var result = initialValue
	for _, x := range collection {
		result = f(result, x)
	}
	return result
}
```

`Reduce` 捕捉到了这个模式的_精髓_：它接收一个集合、一个累加函数和一个初始值，返回单个值。没有任何围绕具体类型的杂乱干扰。

只要你懂泛型的语法，看懂这个函数在做什么应该不成问题。用了 `Reduce` 这个公认的术语，其他语言的程序员也能明白其中的意图。

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

`Sum` 和 `SumAllTails` 现在把各自计算的行为，交给了各自第一行声明的那个函数去描述；在集合上真正执行计算这件事，则被抽象进了 `Reduce`。

## reduce 的更多应用

借助测试，我们可以把 reduce 函数摆弄一番，看看它到底有多可复用。我已经把上一章的那些泛型断言函数复制了过来。

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

在乘法的例子里，我们看到了为什么要给 `Reduce` 传一个默认值参数。如果我们依赖 Go 给 `int` 规定的零值 0，就得拿初始值去乘 0，再乘上后面的元素，结果永远只会是 0。把它设成 1，切片的第一个元素就能保持原样，再逐个乘上后面的元素。

如果你想在极客朋友面前显得有学问，可以管它叫[单位元（identity element）](https://en.wikipedia.org/wiki/Identity_element)。

> 在数学中，作用于某个集合的二元运算的单位元（也称中性元素，neutral element），是指集合中的这样一个元素：把该运算作用到它身上时，集合中的每个元素都保持不变。

拿加法来说，单位元是 0。

`1 + 0 = 1`

乘法的单位元则是 1。

`1 * 1 = 1`

## 如果我们想 reduce 成 `A` 以外的类型怎么办？

假设我们有一组交易 `Transaction`，想要一个函数：传入这些交易和一个名字，就能算出此人的银行余额。

我们按 TDD 的流程来。

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

类型和函数都还没有，先把它们加上，让测试能跑起来。

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

此时运行测试，应该会看到：

```
=== RUN   TestBadBank
    bad_bank_test.go:19: got 0, want 100
    bad_bank_test.go:20: got 0, want -75
    bad_bank_test.go:21: got 0, want -25
--- FAIL: TestBadBank (0.00s)
```

## 写足够的代码让测试通过

我们先假装还没有 `Reduce` 函数，把代码写出来。

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

到了这一步，拿出点版本控制的纪律，把成果 commit 下来。我们有了能工作的软件，随时可以向 Monzo、Barclays 这些银行发起挑战了。

代码已经 commit，我们可以放开手脚摆弄它，在重构阶段尝试一些不同的想法。平心而论，眼下的代码并不算差，但为了这个练习，我想用 `Reduce` 把同样的代码再演示一遍。

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

但这编译不过。

```
./bad_bank.go:19:35: type func(acc float64, t Transaction) float64 of adjustBalance does not match inferred type func(Transaction, Transaction) Transaction for func(A, A) A
```

原因在于，我们想 reduce 出的目标类型跟集合元素的类型_不同_。这听着吓人，其实只需要调整一下 `Reduce` 的类型签名就能解决。函数体一行不用改，现有的调用方也一个都不用动。

```go
func Reduce[A, B any](collection []A, f func(B, A) B, initialValue B) B {
	var result = initialValue
	for _, x := range collection {
		result = f(result, x)
	}
	return result
}
```

我们添加了第二个类型约束，从而放宽了对 `Reduce` 的限制。现在大家可以 `Reduce` 一个 `A` 类型的集合，得到一个 `B`。在我们的例子里，就是从 `Transaction` 到 `float64`。

这让 `Reduce` 更通用、更可复用，同时依然是类型安全的。再跑一遍测试，应该能编译通过，而且全部通过。

## 扩展银行

为了好玩，我想把银行代码的易用性再改进一下。为了节省篇幅，TDD 过程就省略了。

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

下面是更新后的代码

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

我觉得这个例子真正展示了 `Reduce` 这类概念的力量。`NewBalanceFor` 显得更加_声明式_：它描述的是_发生什么_，而不是_怎么发生_。我们读代码的时候，经常是在一大堆文件之间来回穿梭，想知道的是_发生了什么_，而不是_怎么实现的_，这种代码风格恰好成全了这一点。

想深挖细节随时可以：`applyTransaction` 的_业务逻辑_一目了然，不必操心循环和状态变更；那些事 `Reduce` 单独打理。

### Fold/reduce 相当通用

有了 `Reduce`（或 `Fold`），可能性是无穷无尽的™️。这个模式如此常见是有原因的，它能干的可远不止算术或字符串拼接。再多试几种应用吧。

- 为什么不试着把一组 `color.RGBA` 混合成一种颜色？
- 统计一次投票的总票数，或者购物篮里的商品总数。
- 几乎任何涉及处理列表的事情，都算得上。

## Find

Go 有了泛型之后，再把它们跟高阶函数组合起来，我们就能在项目里削减大量样板代码，让系统更容易理解和管理。

你再也不必为每种想搜索的集合专门写一个 `Find` 函数了，直接复用一个，或者自己写一个 `Find` 就行。如果你看懂了上面的 `Reduce` 函数，写一个 `Find` 函数不过是小菜一碟。

先看测试

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

再看实现

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

同理，因为它接收的是泛型，我们可以在很多场景复用它

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

如你所见，这段代码无懈可击。

## 总结

用得有品味的话，这类高阶函数会让你的代码更易读、更好维护，但记住这条经验法则：

用 TDD 流程先逼出你真正需要的、具体的行为；到了重构阶段，你_或许_会发现一些有用的抽象，帮代码收拾得更整洁。

练习把 TDD 和良好的版本控制习惯结合起来。在测试通过后就 commit 你的成果，_然后_才去尝试重构。这样就算搞砸了，也能轻松回到能工作的状态。

### 命名很重要

花点功夫到 Go 以外的世界做做调研，免得把那些早已存在、名字早已约定俗成的模式重新发明一遍。

要写一个接收 `A` 集合、把它们转换成 `B` 的函数？别叫它 `Convert`，它的名字叫 [`Map`](https://en.wikipedia.org/wiki/Map_(higher-order_function))。给这些东西用上"正规"名字，能减轻别人的认知负担，想继续学习时搜索引擎也更友好。

### 这样写不够惯用？

试着保持开放的心态。

虽然 Go 的惯用法不会、也不应该因为泛型的发布就_彻底_改变，但惯用法_终将_改变——因为语言本身在变！这一点不该有任何争议。

只甩下一句

> 这不惯用

却不附任何细节，这话既没法付诸行动，也没什么用，尤其是在讨论新语言特性的时候。

跟同事讨论模式和代码风格时，要看它们本身好不好，而不是抱着教条不放。只要你拥有设计良好的测试，随着你逐渐弄清什么对你和你的团队行之有效，你随时都能继续重构、继续调整。

### 参考资料

Fold 算是计算机科学里真正的基石之一。想继续深挖的话，这里有一些有意思的资料：
- [Wikipedia: Fold](https://en.wikipedia.org/wiki/Fold)
- [A tutorial on the universality and expressiveness of fold](http://www.cs.nott.ac.uk/~pszgmh/fold.pdf)
