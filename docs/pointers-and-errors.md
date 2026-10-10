# 指针与错误

[**本章的所有代码都可以在这里找到**](https://github.com/quii/learn-go-with-tests/tree/main/pointers)

上一节我们学习了结构体，它能把围绕同一个概念的一组值聚合到一起。

总有一天，你或许会想用结构体来管理状态：对外暴露一些方法，让用户以你能控制的方式去修改状态。

**金融科技圈爱死 Go 了**，还有，呃……比特币？那就让我们展示一下，我们能搞出一套多么了不起的银行系统吧。

我们来创建一个 `Wallet` 结构体，让它可以存入 `Bitcoin`。

## 先写测试

```go
func TestWallet(t *testing.T) {

	wallet := Wallet{}

	wallet.Deposit(10)

	got := wallet.Balance()
	want := 10

	if got != want {
		t.Errorf("got %d want %d", got, want)
	}
}
```

在[上一章的例子里](structs-methods-and-interfaces.md)，我们是直接用字段名访问字段的；但在我们这个*固若金汤的钱包*里，可不想把内部状态暴露给外面的世界，我们想通过方法来控制访问。

## 试着运行测试

`./wallet_test.go:7:12: undefined: Wallet`

## 写最少量的代码让测试得以运行，并查看失败的输出

编译器还不知道 `Wallet` 是什么，那我们就来告诉它。

```go
type Wallet struct{}
```

现在钱包已经建好，再试着运行一下测试

```
./wallet_test.go:9:8: wallet.Deposit undefined (type Wallet has no field or method Deposit)
./wallet_test.go:11:15: wallet.Balance undefined (type Wallet has no field or method Balance)
```

我们需要把这两个方法定义出来。

记住，只写刚好够让测试跑起来的代码。我们要确保测试能正确地失败，并给出清晰易读的错误信息。

```go
func (w Wallet) Deposit(amount int) {

}

func (w Wallet) Balance() int {
	return 0
}
```

如果这个语法让你觉得眼生，请回过头去读一读结构体那一节。

现在测试应该能编译并运行了

`wallet_test.go:15: got 0 want 10`

## 写足够的代码让测试通过

我们需要在结构体里放一个 *balance* 之类的变量来存储状态

```go
type Wallet struct {
	balance int
}
```

在 Go 里，如果一个符号（变量、类型、函数等等）以小写字母开头，那它在*定义它的包之外*就是私有的。

就我们的场景而言，我们希望只有自己的方法能操作这个值，其他人都不能。

记住，我们可以用“接收者”变量来访问结构体内部的 `balance` 字段。

```go
func (w Wallet) Deposit(amount int) {
	w.balance += amount
}

func (w Wallet) Balance() int {
	return w.balance
}
```

如此一来，我们的金融科技职业前程算是稳了，跑一下测试套件，尽情沐浴在测试通过的喜悦里吧

`wallet_test.go:15: got 0 want 10`

### 好像不太对劲

这就让人摸不着头脑了：我们的代码看起来应该没问题才对。我们把新数额加到了余额上，然后 balance 方法理应返回它的当前状态。

在 Go 里，**调用函数或方法时，实参都会为**_**复制**_。

调用 `func (w Wallet) Deposit(amount int)` 时，这个 `w` 只是调用方那个对象的一份副本。

不扯太多计算机科学的细节：当你创建一个值——比如一个钱包——它会被存放在内存中的某个位置。用 `&myVal` 就能查到那块内存的*地址*。

往代码里加些打印语句，做个实验

```go
func TestWallet(t *testing.T) {

	wallet := Wallet{}

	wallet.Deposit(10)

	got := wallet.Balance()

	fmt.Printf("address of balance in test is %p \n", &wallet.balance)

	want := 10

	if got != want {
		t.Errorf("got %d want %d", got, want)
	}
}
```

```go
func (w Wallet) Deposit(amount int) {
	fmt.Printf("address of balance in Deposit is %p \n", &w.balance)
	w.balance += amount
}
```

`%p` 占位符会以 16 进制、带 `0x` 前缀的形式打印内存地址，转义字符则会打印一个换行。注意，只要在符号的开头放一个 `&` 字符，就能取到它的指针（内存地址）。

现在重新运行测试

```
address of balance in Deposit is 0xc420012268
address of balance in test is 0xc420012260
```

可以看到，两个余额的地址并不相同。也就是说，当我们在代码里修改余额时，操作的只是从测试传来的那份副本。因此测试里的余额纹丝不动。

我们可以用*指针*（pointer）来解决这个问题。[指针](https://gobyexample.com/pointers)让我们得以*指向*某个值并修改它。所以，与其复制整个 Wallet，不如拿到一个指向这个钱包的指针，这样就能修改它内部原本的值。

```go
func (w *Wallet) Deposit(amount int) {
	w.balance += amount
}

func (w *Wallet) Balance() int {
	return w.balance
}
```

区别在于接收者类型是 `*Wallet` 而不是 `Wallet`，你可以把它读作“一个指向 wallet 的指针”。

再跑一次测试，应该就通过了。

你可能纳闷：它们怎么就通过了？我们并没有在函数里解引用（dereference）这个指针，比如写成这样：

```go
func (w *Wallet) Balance() int {
	return (*w).balance
}
```

似乎就直接访问到对象本身了。事实上，上面用 `(*w)` 的写法完全合法。不过 Go 的设计者嫌这种记法太笨重，于是语言允许我们直接写 `w.balance`，无需显式解引用。这种指向结构体的指针甚至有个自己的名字：*结构体指针*（struct pointers），而且会被[自动解引用](https://golang.org/ref/spec#Method_values)。

严格来说，`Balance` 不必改成指针接收者，复制一份余额并没有什么问题。不过按惯例，为了保持一致，方法接收者的类型应该统一起来。

## 重构

我们说要做的是比特币钱包，可到现在还只字未提比特币。我们一直在用 `int`，因为它数数非常好使！

为此专门创建一个 `struct` 似乎有点杀鸡用牛刀。`int` 从工作方式上讲没问题，就是不够达意。

Go 允许你基于已有类型创建新类型。

语法是 `type MyName OriginalType`

```go
type Bitcoin int

type Wallet struct {
	balance Bitcoin
}

func (w *Wallet) Deposit(amount Bitcoin) {
	w.balance += amount
}

func (w *Wallet) Balance() Bitcoin {
	return w.balance
}
```

```go
func TestWallet(t *testing.T) {

	wallet := Wallet{}

	wallet.Deposit(Bitcoin(10))

	got := wallet.Balance()

	want := Bitcoin(10)

	if got != want {
		t.Errorf("got %d want %d", got, want)
	}
}
```

想要一个 `Bitcoin`，用 `Bitcoin(999)` 这样的语法就行。

这样做之后，我们就拥有了一个新类型，还可以在它上面声明*方法*。当你想在已有类型之上添加一些领域特定的功能时，这一招非常好用。

我们来为 `Bitcoin` 实现 [Stringer](https://golang.org/pkg/fmt/#Stringer)

```go
type Stringer interface {
	String() string
}
```

这个接口定义在 `fmt` 包里，它能让你定义自己的类型在打印中配合 `%s` 格式化字符串时的输出形式。

```go
func (b Bitcoin) String() string {
	return fmt.Sprintf("%d BTC", b)
}
```

可以看到，在类型声明上定义方法的语法，跟在结构体上是一样的。

这里我们没守住纪律：没先写测试就加了个方法。没关系，我们总不能时时刻刻都当圣人，但也不能放任不管。跑一下 `go test -cover` 会发现 `String` 没有被覆盖，这正好提醒我们回头想想：值不值得给它补个测试。我们不该为了凑数而追求 100% 的覆盖率，但在这个例子里，`String` 自带逻辑（`fmt.Sprintf`），值得固定下来，那就来补一个测试吧。

```go
t.Run("Bitcoin String", func(t *testing.T) {
	btc := Bitcoin(10)
	got := btc.String()
	want := "10 BTC"

	if got != want {
		t.Errorf("got %s want %s", got, want)
	}
})
```

接下来要更新测试里的格式化字符串，让它们改用 `String()`。

```go
if got != want {
	t.Errorf("got %s want %s", got, want)
}
```

为了看看实际效果，故意把测试弄失败，就能看到

`wallet_test.go:18: got 10 BTC want 20 BTC`

这下测试里发生了什么就清楚多了。

下一个需求是一个 `Withdraw` 函数。

## 先写测试

基本上就是 `Deposit()` 的反操作

```go
func TestWallet(t *testing.T) {

	t.Run("deposit", func(t *testing.T) {
		wallet := Wallet{}

		wallet.Deposit(Bitcoin(10))

		got := wallet.Balance()

		want := Bitcoin(10)

		if got != want {
			t.Errorf("got %s want %s", got, want)
		}
	})

	t.Run("withdraw", func(t *testing.T) {
		wallet := Wallet{balance: Bitcoin(20)}

		wallet.Withdraw(Bitcoin(10))

		got := wallet.Balance()

		want := Bitcoin(10)

		if got != want {
			t.Errorf("got %s want %s", got, want)
		}
	})
}
```

## 试着运行测试

`./wallet_test.go:26:9: wallet.Withdraw undefined (type Wallet has no field or method Withdraw)`

## 写最少量的代码让测试得以运行，并查看失败的输出

```go
func (w *Wallet) Withdraw(amount Bitcoin) {

}
```

`wallet_test.go:33: got 20 BTC want 10 BTC`

## 写足够的代码让测试通过

```go
func (w *Wallet) Withdraw(amount Bitcoin) {
	w.balance -= amount
}
```

## 重构

我们的测试里有些重复，来把它重构掉。

```go
func TestWallet(t *testing.T) {

	assertBalance := func(t testing.TB, wallet Wallet, want Bitcoin) {
		t.Helper()
		got := wallet.Balance()

		if got != want {
			t.Errorf("got %s want %s", got, want)
		}
	}

	t.Run("deposit", func(t *testing.T) {
		wallet := Wallet{}
		wallet.Deposit(Bitcoin(10))
		assertBalance(t, wallet, Bitcoin(10))
	})

	t.Run("withdraw", func(t *testing.T) {
		wallet := Wallet{balance: Bitcoin(20)}
		wallet.Withdraw(Bitcoin(10))
		assertBalance(t, wallet, Bitcoin(10))
	})

}
```

如果你试图 `Withdraw` 的钱超过了账户余额，应该发生什么？眼下我们的需求是：假设没有透支功能。

那么在使用 `Withdraw` 时，该如何表示出了问题呢？

在 Go 里，如果想表示出错，惯用做法是让你的函数返回一个 `err`，由调用者检查并采取行动。

我们在测试里试试看。

## 先写测试

```go
t.Run("withdraw insufficient funds", func(t *testing.T) {
	startingBalance := Bitcoin(20)
	wallet := Wallet{startingBalance}
	err := wallet.Withdraw(Bitcoin(100))

	assertBalance(t, wallet, startingBalance)

	if err == nil {
		t.Error("wanted an error but didn't get one")
	}
})
```

我们希望 `Withdraw` 在你试图取出超过余额的钱*时*返回一个错误，并且余额应保持不变。

接着我们检查确实返回了错误：如果它是 `nil`，就让测试失败。

`nil` 相当于其他编程语言里的 `null`。错误可以是 `nil`，因为 `Withdraw` 的返回类型会是 `error`，而 `error` 是一个接口。如果你看到某个函数的参数或返回值是接口类型，那它们就是 nillable（可为 nil）的。

跟 `null` 一样，如果你试图访问一个值为 `nil` 的东西，就会抛出**运行时 panic**。这可不是好事！你务必确保自己检查过 nil。

## 试着运行测试

`./wallet_test.go:31:25: wallet.Withdraw(Bitcoin(100)) used as value`

这条报错的措辞也许有点让人费解，但我们之前对 `Withdraw` 的设想只是调用它而已，它从不返回值。要让代码通过编译，我们得把它改成有返回类型。

## 写最少量的代码让测试得以运行，并查看失败的输出

```go
func (w *Wallet) Withdraw(amount Bitcoin) error {
	w.balance -= amount
	return nil
}
```

再说一次，只写刚好满足编译器的代码非常重要。我们把 `Withdraw` 方法改成返回 `error`，而现在总得返回*点什么*，那就先返回 `nil` 吧。

## 写足够的代码让测试通过

```go
func (w *Wallet) Withdraw(amount Bitcoin) error {

	if amount > w.balance {
		return errors.New("oh no")
	}

	w.balance -= amount
	return nil
}
```

记得在代码里导入 `errors`。

`errors.New` 会创建一个新的 `error`，消息由你指定。

## 重构

我们来快速写一个检查错误的测试辅助函数，提升测试的可读性

```go
assertError := func(t testing.TB, err error) {
	t.Helper()
	if err == nil {
		t.Error("wanted an error but didn't get one")
	}
}
```

然后在我们的测试里

```go
t.Run("withdraw insufficient funds", func(t *testing.T) {
	startingBalance := Bitcoin(20)
	wallet := Wallet{startingBalance}
	err := wallet.Withdraw(Bitcoin(100))

	assertError(t, err)
	assertBalance(t, wallet, startingBalance)
})
```

返回 “oh no” 这个错误时，你心里可能已经在想：我们*多半*还会对它继续迭代，因为这么返回似乎没什么用处。

假设这个错误最终会被返回给用户，那我们就更新一下测试：不再只断言有错误存在，而是对某种具体的错误信息做断言。

## 先写测试

更新我们的辅助函数，让它接收一个用于比较的 `string`。

```go
assertError := func(t testing.TB, got error, want string) {
	t.Helper()

	if got == nil {
		t.Fatal("didn't get an error but wanted one")
	}

	if got.Error() != want {
		t.Errorf("got %q, want %q", got, want)
	}
}
```

可以看到，`Error` 可以用 `.Error()` 方法转换成字符串，我们借此把它与期望的字符串作比较。我们还确保了错误不是 `nil`，以免对 `nil` 调用 `.Error()`。

然后更新调用方

```go
t.Run("withdraw insufficient funds", func(t *testing.T) {
	startingBalance := Bitcoin(20)
	wallet := Wallet{startingBalance}
	err := wallet.Withdraw(Bitcoin(100))

	assertError(t, err, "cannot withdraw, insufficient funds")
	assertBalance(t, wallet, startingBalance)
})
```

这里我们引入了 `t.Fatal`，它一旦被调用就会让测试停止。因为如果压根没有错误，我们就不想再对“返回的错误”做更多断言了。没有这一步，测试会继续执行下一步，并因为空指针而 panic。

## 试着运行测试

`wallet_test.go:61: got err 'oh no' want 'cannot withdraw, insufficient funds'`

## 写足够的代码让测试通过

```go
func (w *Wallet) Withdraw(amount Bitcoin) error {

	if amount > w.balance {
		return errors.New("cannot withdraw, insufficient funds")
	}

	w.balance -= amount
	return nil
}
```

## 重构

错误信息在测试代码和 `Withdraw` 代码里重复出现了。

如果有人想改改错误的措辞，测试就跟着挂，那也太烦人了；而且这对我们的测试来说实在是过于细节。我们*并不*真的在乎确切的措辞，只在乎在特定条件下会返回某种与取款相关的、有意义的错误。

在 Go 里，错误也是值，所以我们可以把它重构成一个变量，让这条信息有唯一的事实来源。

```go
var ErrInsufficientFunds = errors.New("cannot withdraw, insufficient funds")

func (w *Wallet) Withdraw(amount Bitcoin) error {

	if amount > w.balance {
		return ErrInsufficientFunds
	}

	w.balance -= amount
	return nil
}
```

`var` 关键字让我们可以定义包内全局的值。

这本身就是个好改动，因为现在我们的 `Withdraw` 函数看起来非常清晰。

接下来可以重构测试代码，用这个值代替具体的字符串。

```go
func TestWallet(t *testing.T) {

	t.Run("deposit", func(t *testing.T) {
		wallet := Wallet{}
		wallet.Deposit(Bitcoin(10))
		assertBalance(t, wallet, Bitcoin(10))
	})

	t.Run("withdraw with funds", func(t *testing.T) {
		wallet := Wallet{Bitcoin(20)}
		wallet.Withdraw(Bitcoin(10))
		assertBalance(t, wallet, Bitcoin(10))
	})

	t.Run("withdraw insufficient funds", func(t *testing.T) {
		wallet := Wallet{Bitcoin(20)}
		err := wallet.Withdraw(Bitcoin(100))

		assertError(t, err, ErrInsufficientFunds)
		assertBalance(t, wallet, Bitcoin(20))
	})
}

func assertBalance(t testing.TB, wallet Wallet, want Bitcoin) {
	t.Helper()
	got := wallet.Balance()

	if got != want {
		t.Errorf("got %q want %q", got, want)
	}
}

func assertError(t testing.TB, got, want error) {
	t.Helper()
	if got == nil {
		t.Fatal("didn't get an error but wanted one")
	}

	if got != want {
		t.Errorf("got %q, want %q", got, want)
	}
}
```

现在测试也更容易读懂了。

我把这些辅助函数移出了主测试函数，这样别人一打开文件，先读到的就是我们的断言，而不是一堆辅助函数。

测试还有一个有用的性质：它帮我们理解代码的*真实*用法，从而写出对使用者更体贴的代码。这里可以看到，开发者只需调用我们的代码，跟 `ErrInsufficientFunds` 做个相等比较，就能据此做出相应处理。

### 未检查的错误

尽管 Go 编译器已经能帮上很多忙，有些事情你仍然可能漏掉，而且错误处理有时也挺棘手。

有一个场景我们还没测到。要把它揪出来，在终端里运行以下命令，安装 `errcheck`——Go 可用的众多 linter（静态检查工具）之一。

`go install github.com/kisielk/errcheck@latest`

然后，在你代码所在的目录里运行 `errcheck .`

你应该会看到类似这样的输出

`wallet_test.go:17:18: wallet.Withdraw(Bitcoin(10))`

它在告诉我们：那一行代码返回的错误，我们没有检查。在我机器上，这行代码对应的是正常取款的场景，因为我们没有检查 `Withdraw` 成功时*不会*返回错误这一点。

下面是把这种情况也考虑进去的最终测试代码。

```go
func TestWallet(t *testing.T) {

	t.Run("deposit", func(t *testing.T) {
		wallet := Wallet{}
		wallet.Deposit(Bitcoin(10))

		assertBalance(t, wallet, Bitcoin(10))
	})

	t.Run("withdraw with funds", func(t *testing.T) {
		wallet := Wallet{Bitcoin(20)}
		err := wallet.Withdraw(Bitcoin(10))

		assertNoError(t, err)
		assertBalance(t, wallet, Bitcoin(10))
	})

	t.Run("withdraw insufficient funds", func(t *testing.T) {
		wallet := Wallet{Bitcoin(20)}
		err := wallet.Withdraw(Bitcoin(100))

		assertError(t, err, ErrInsufficientFunds)
		assertBalance(t, wallet, Bitcoin(20))
	})
}

func assertBalance(t testing.TB, wallet Wallet, want Bitcoin) {
	t.Helper()
	got := wallet.Balance()

	if got != want {
		t.Errorf("got %s want %s", got, want)
	}
}

func assertNoError(t testing.TB, got error) {
	t.Helper()
	if got != nil {
		t.Fatal("got an error but didn't want one")
	}
}

func assertError(t testing.TB, got error, want error) {
	t.Helper()
	if got == nil {
		t.Fatal("didn't get an error but wanted one")
	}

	if got != want {
		t.Errorf("got %s, want %s", got, want)
	}
}
```

## 用错误包装添加上下文

把 `err` 与 `ErrInsufficientFunds` 直接比较，在这里效果很好，因为能产生它的只有 `Withdraw`。但真实的程序是分层的——一个 `Wallet` 可能被某个 `Bank` 使用，`Bank` 又被某个 HTTP handler 使用，诸如此类。如果每一层都原样返回收到的错误，那么隔了好几层的调用者永远只能看到 `insufficient funds`，根本不知道究竟是哪个账户、哪个操作出了问题。

假设我们有一个函数，为指定账户处理取款：

```go
func ProcessWithdrawal(wallet *Wallet, accountID string, amount Bitcoin) error {
	if err := wallet.Withdraw(amount); err != nil {
		return fmt.Errorf("processing withdrawal for account %s: %w", accountID, err)
	}
	return nil
}
```

`%w` 这个格式化动词（Go 1.13 引入）在把 `err` 的字符串填进来这一点上跟 `%v` 一样，但它还做了 `%v` 做不到的事：它会把 `err` *包装*进 `fmt.Errorf` 返回的新错误里，而不只是把它的消息拷贝成一个新的、互不相干的字符串。试试看：

```go
wallet := Wallet{Bitcoin(10)}
err := ProcessWithdrawal(&wallet, "acc-123", Bitcoin(100))
fmt.Println(err)
// processing withdrawal for account acc-123: cannot withdraw, insufficient funds
```

我们保住了有用的上下文（“哪个账户、哪个操作”），同时也没有弄丢底层实际出了什么问题的细节。

### 检查被包装的错误

既然 `ProcessWithdrawal` 返回的错误值与 `ErrInsufficientFunds` *并不相同*，再用 `==`（或上面的 `assertError` 辅助函数）来比较就会失败，尽管底层原因其实是同一个。这正是 [`errors.Is`](https://pkg.go.dev/errors#Is) 要解决的问题——它检查的是一整条被包装的错误链，而不只是最外层的那个：

```go
if errors.Is(err, ErrInsufficientFunds) {
	// 仍然为 true，尽管 err 的消息现在还会提到账户
}
```

`errors.Is` 的工作方式是对 `err` 反复调用 [`errors.Unwrap`](https://pkg.go.dev/errors#Unwrap)（它知道怎么把被包装的错误取出来，因为 `fmt.Errorf` 配合 `%w` 产生的值带有 `Unwrap() error` 方法），直到找到匹配项，或者再也没有错误可解包为止。正因如此，在 [Maps](maps.md) 一章的 `assertError` 辅助函数里，你还会看到我们用 `errors.Is` 而不是 `==`——它是个安全的默认选择，对从未被包装过的错误也同样有效。

如果你需要从一条被包装的错误链里提取*特定类型*的错误（而不是与 `ErrInsufficientFunds` 这样的哨兵值做比较），也有一个对应的函数：[`errors.As`](https://pkg.go.dev/errors#As)。[error types](error-types.md) 一章会更深入地讨论这个话题。

## 总结

### 指针

* 把值传给函数/方法时，Go 会复制它们，所以如果你写的函数需要修改状态，就得让它接收一个指针，指向你想修改的那个东西。
* Go 复制值这件事大多数时候都正合心意，但有时你并不想让自己的系统复制某样东西，这时就需要传引用。比如引用非常庞大的数据结构，或者那些只需要一个实例的东西（比如数据库连接池）。

### nil

* 指针可以是 nil
* 当函数返回指向某个东西的指针时，务必检查它是不是 nil，否则可能触发运行时异常——这种事编译器可帮不了你。
* 当你想表达“某个值可能缺失”时，它很有用

### 错误

* 错误用来表示调用函数/方法时的失败。
* 倾听测试的反馈后我们得出结论：在错误里检查字符串会让测试变得 flaky（不稳定）。于是我们重构实现，改用一个有意义的值，这让代码更容易测试；我们由此也可断定，对我们 API 的使用者来说它同样省心。
* 错误处理的故事远没有结束，你还可以玩出更复杂的花样，这里只是入门。后面的章节会介绍更多策略。
* [别只顾着检查错误，要优雅地处理它们](https://dave.cheney.net/2016/04/27/dont-just-check-errors-handle-them-gracefully)

### 从已有类型创建新类型

* 适合为值赋予更多领域特定的含义
* 可以让你实现接口

指针和错误是写 Go 绕不开的重头戏，你必须把它们用得得心应手。好在只要你做错了什么，编译器*通常*都会出手相助——放慢节奏，仔细读读错误信息就好。
