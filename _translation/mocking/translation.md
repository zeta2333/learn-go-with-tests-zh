# Mocking

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/mocking)**

有人给你提了个需求：写一个从 3 开始倒数的程序，每个数字单独占一行打印（中间停顿 1 秒），数到零时打印 "Go!" 然后退出。

```
3
2
1
Go!
```

我们的思路是先写一个名为 `Countdown` 的函数，然后再把它装进一个 `main` 程序里，大致像这样：

```go
package main

func main() {
	Countdown()
}
```

这个程序虽然简单得不能再简单，但要把它测得彻彻底底，我们还是得一如既往地走*迭代式*、*测试驱动*的路子。

什么叫迭代式？就是说我们每一步都尽可能迈得小，同时保证手里始终有*有用的软件*。

我们可不想在一堆"再折腾折腾理论上就能跑"的代码上耗掉大把时间——开发者掉进兔子洞（越陷越深），往往就是这么开始的。**把需求切得越小越好，好让自己尽快拿到*能跑的软件*，这是一项很重要的功力。**

我们可以照下面这样划分工作、逐步迭代：

- 打印 3
- 打印 3、2、1 和 Go!
- 每行之间等 1 秒

## 先写测试

我们的软件需要打印到标准输出，而在讲 DI 的那一章里，我们已经见识过怎么用依赖注入（DI）来方便这类测试。

```go
func TestCountdown(t *testing.T) {
	buffer := &bytes.Buffer{}

	Countdown(buffer)

	got := buffer.String()
	want := "3"

	if got != want {
		t.Errorf("got %q want %q", got, want)
	}
}
```

如果 `buffer` 这类东西你还没什么印象，请回看[上一章](dependency-injection.md)。

我们已经清楚要让 `Countdown` 往某个地方写数据，而想把这件事抽象成接口，Go 里事实上的标准就是 `io.Writer`。

- 在 `main` 里我们传 `os.Stdout`，让用户看到倒计时打印在终端上。
- 在测试里我们传 `bytes.Buffer`，让测试能捕获正在生成的数据。

## 试着运行测试

`./countdown_test.go:11:2: undefined: Countdown`

## 写最少量的代码让测试跑起来，并检查失败的测试输出

定义 `Countdown`

```go
func Countdown() {}
```

再试一次

```
./countdown_test.go:11:11: too many arguments in call to Countdown
    have (*bytes.Buffer)
    want ()
```

编译器在告诉你函数签名可以长什么样，照它说的改就行。

```go
func Countdown(out *bytes.Buffer) {}
```

`countdown_test.go:17: got '' want '3'`

完美！

## 写足够的代码让它通过

```go
func Countdown(out *bytes.Buffer) {
	fmt.Fprint(out, "3")
}
```

这里用的是 `fmt.Fprint`，它接收一个 `io.Writer`（比如 `*bytes.Buffer`），并把一个 `string` 写进去。测试应该能通过了。

## 重构

我们知道 `*bytes.Buffer` 虽然能用，但换成通用的接口会更好。

```go
func Countdown(out io.Writer) {
	fmt.Fprint(out, "3")
}
```

重跑一遍测试，应该全过。

最后收个尾：把这个函数接进一个 `main`，这样我们就有一点能跑的软件了，也好让自己确信确实在前进。

```go
package main

import (
	"fmt"
	"io"
	"os"
)

func Countdown(out io.Writer) {
	fmt.Fprint(out, "3")
}

func main() {
	Countdown(os.Stdout)
}
```

运行一下程序，为自己的手艺惊叹吧。

是的，这看起来微不足道，但我推荐任何项目都用这个套路。**切下一小片功能，让它端到端跑通，背后有测试撑腰。**

接下来让它打印 2、1，然后是 "Go!"。

## 先写测试

花力气把整体管线搭对之后，我们就能安心、轻松地迭代方案了。所有逻辑都有测试把关，我们不用再停下来手动运行程序去确认它能工作。

```go
func TestCountdown(t *testing.T) {
	buffer := &bytes.Buffer{}

	Countdown(buffer)

	got := buffer.String()
	want := `3
2
1
Go!`

	if got != want {
		t.Errorf("got %q want %q", got, want)
	}
}
```

反引号语法是创建 `string` 的另一种方式，好处是能直接写进换行符这样的东西，正适合我们这个测试。

## 试着运行测试

```
countdown_test.go:21: got '3' want '3
        2
        1
        Go!'
```

## 写足够的代码让它通过

```go
func Countdown(out io.Writer) {
	for i := 3; i > 0; i-- {
		fmt.Fprintln(out, i)
	}
	fmt.Fprint(out, "Go!")
}
```

用 `for` 循环配合 `i--` 倒着数，用 `fmt.Fprintln` 往 `out` 打印数字，数字后面跟一个换行符。最后用 `fmt.Fprint` 把 "Go!" 发出去。

## 重构

没什么可重构的，顶多把几个魔法值提炼成具名常量。

```go
const finalWord = "Go!"
const countdownStart = 3

func Countdown(out io.Writer) {
	for i := countdownStart; i > 0; i-- {
		fmt.Fprintln(out, i)
	}
	fmt.Fprint(out, finalWord)
}
```

现在运行程序，输出应该是对的了，但它还不是那种带 1 秒停顿、有戏剧感的倒计时。

在 Go 里，用 `time.Sleep` 就能做到。试着把它加进我们的代码。

```go
func Countdown(out io.Writer) {
	for i := countdownStart; i > 0; i-- {
		fmt.Fprintln(out, i)
		time.Sleep(1 * time.Second)
	}

	fmt.Fprint(out, finalWord)
}
```

再运行程序，一切如我们所愿。

## 该谈谈 Mocking 了

测试依然全过，软件也按预期工作，但问题来了：

- 我们的测试要跑 3 秒。
    - 每一篇有前瞻性的软件开发文章，都在强调快速反馈循环的重要性。
    - **慢测试毁掉开发者的生产力**。
    - 想象一下需求变得越来越复杂、需要更多测试的时候。`Countdown` 每多一个新测试，测试运行就要多上 3 秒，我们乐意吗？
- 我们还没测到函数的一个重要性质。

我们对 `Sleep` 有依赖，得把它抽出来，才能在测试里掌控它。

如果能 _mock_ 掉 `time.Sleep`，我们就可以用*依赖注入*让代码用它来代替"真正的" `time.Sleep`，然后 **spy 住这些调用**，对它们做断言。

## 先写测试

我们把这个依赖定义成一个接口。这样在 `main` 里可以用*真正的* Sleeper，在测试里用 *spy sleeper*。用了接口，`Countdown` 函数对这一切毫不知情，调用方还多了一些灵活性。

```go
type Sleeper interface {
	Sleep()
}
```

我做了个设计决定：睡多久，不归 `Countdown` 函数管。这至少眼下能让代码简单一点，也意味着函数的使用者想怎么配置这份"瞌睡"都行。

现在我们需要为它做一个 _mock_，供测试使用。

```go
type SpySleeper struct {
	Calls int
}

func (s *SpySleeper) Sleep() {
	s.Calls++
}
```

_Spy_ 是 _mock_ 的一种，它能记录一个依赖是怎么被使用的：传进去的参数、被调用的次数等等都可以记。在我们这儿，就是记下 `Sleep()` 被调用了几次，好在测试里检查。

更新测试，把我们的 Spy 当作依赖注入进去，并断言 sleep 被调用了 3 次。

```go
func TestCountdown(t *testing.T) {
	buffer := &bytes.Buffer{}
	spySleeper := &SpySleeper{}

	Countdown(buffer, spySleeper)

	got := buffer.String()
	want := `3
2
1
Go!`

	if got != want {
		t.Errorf("got %q want %q", got, want)
	}

	if spySleeper.Calls != 3 {
		t.Errorf("not enough calls to sleeper, want 3 got %d", spySleeper.Calls)
	}
}
```

## 试着运行测试

```
too many arguments in call to Countdown
    have (*bytes.Buffer, *SpySleeper)
    want (io.Writer)
```

## 写最少量的代码让测试跑起来，并检查失败的测试输出

我们得让 `Countdown` 接收我们的 `Sleeper`

```go
func Countdown(out io.Writer, sleeper Sleeper) {
	for i := countdownStart; i > 0; i-- {
		fmt.Fprintln(out, i)
		time.Sleep(1 * time.Second)
	}

	fmt.Fprint(out, finalWord)
}
```

再试一次的话，你的 `main` 会因为同样的原因编译不过了

```
./main.go:26:11: not enough arguments in call to Countdown
    have (*os.File)
    want (io.Writer, Sleeper)
```

我们来写一个*真正的* sleeper，它实现我们需要的接口

```go
type DefaultSleeper struct{}

func (d *DefaultSleeper) Sleep() {
	time.Sleep(1 * time.Second)
}
```

然后就可以在真实的应用里这样用它

```go
func main() {
	sleeper := &DefaultSleeper{}
	Countdown(os.Stdout, sleeper)
}
```

## 写足够的代码让它通过

测试现在能编译了，但还是过不去，因为我们调用的仍然是 `time.Sleep`，而不是注入进来的依赖。来修一下。

```go
func Countdown(out io.Writer, sleeper Sleeper) {
	for i := countdownStart; i > 0; i-- {
		fmt.Fprintln(out, i)
		sleeper.Sleep()
	}

	fmt.Fprint(out, finalWord)
}
```

测试应该能通过，而且不再耗时 3 秒。

### 还有问题

还有一个重要性质我们没有测到。

`Countdown` 应该在打印下一条内容之前先 sleep，比如：

- `Print N`
- `Sleep`
- `Print N-1`
- `Sleep`
- `Print Go!`
- 等等

我们刚才的改动只断言了它睡了 3 次，但这些 sleep 完全可能不按顺序发生。

写测试的时候，如果你对"测试是否给了你足够的信心"没那么有信心，那就故意把代码弄坏！（当然，先确保你已经把改动 commit 到版本控制里了。）把代码改成下面这样

```go
func Countdown(out io.Writer, sleeper Sleeper) {
	for i := countdownStart; i > 0; i-- {
		sleeper.Sleep()
	}

	for i := countdownStart; i > 0; i-- {
		fmt.Fprintln(out, i)
	}

	fmt.Fprint(out, finalWord)
}
```

跑一下测试，你会发现尽管实现是错的，测试居然还是全过。

我们再用 spy 写一个新测试，检查操作的顺序是否正确。

我们有两个不同的依赖，想把它们的操作都记录到同一个列表里。所以我们为它们俩做_一个 spy_。

```go
type SpyCountdownOperations struct {
	Calls []string
}

func (s *SpyCountdownOperations) Sleep() {
	s.Calls = append(s.Calls, sleep)
}

func (s *SpyCountdownOperations) Write(p []byte) (n int, err error) {
	s.Calls = append(s.Calls, write)
	return
}

const write = "write"
const sleep = "sleep"
```

我们的 `SpyCountdownOperations` 同时实现了 `io.Writer` 和 `Sleeper`，把每一次调用都记进一个切片。这个测试只关心操作的顺序，所以把操作按名字记成一张列表就足够了。

现在可以在测试套件里加一个子测试，验证 sleep 和 print 按我们期望的顺序进行

```go
t.Run("sleep before every print", func(t *testing.T) {
	spySleepPrinter := &SpyCountdownOperations{}
	Countdown(spySleepPrinter, spySleepPrinter)

	want := []string{
		write,
		sleep,
		write,
		sleep,
		write,
		sleep,
		write,
	}

	if !reflect.DeepEqual(want, spySleepPrinter.Calls) {
		t.Errorf("wanted calls %v got %v", want, spySleepPrinter.Calls)
	}
})
```

这个测试现在应该会失败。把 `Countdown` 恢复原样，测试就修好了。

现在有两个测试都在 spy `Sleeper`，我们可以重构测试了：一个测打印出来的内容，另一个确保打印之间有 sleep。最后，第一个 spy 已经没用了，可以删掉。

```go
func TestCountdown(t *testing.T) {

	t.Run("prints 3 to Go!", func(t *testing.T) {
		buffer := &bytes.Buffer{}
		Countdown(buffer, &SpyCountdownOperations{})

		got := buffer.String()
		want := `3
2
1
Go!`

		if got != want {
			t.Errorf("got %q want %q", got, want)
		}
	})

	t.Run("sleep before every print", func(t *testing.T) {
		spySleepPrinter := &SpyCountdownOperations{}
		Countdown(spySleepPrinter, spySleepPrinter)

		want := []string{
			write,
			sleep,
			write,
			sleep,
			write,
			sleep,
			write,
		}

		if !reflect.DeepEqual(want, spySleepPrinter.Calls) {
			t.Errorf("wanted calls %v got %v", want, spySleepPrinter.Calls)
		}
	})
}
```

至此，函数和它的两个重要性质都得到了妥当的测试。

## 让 Sleeper 变得可配置

有个不错的改进是让 `Sleeper` 可配置。这样我们就能在主程序里调整睡眠时长。

### 先写测试

先创建一个新类型 `ConfigurableSleeper`，它接收我们做配置和测试所需要的东西。

```go
type ConfigurableSleeper struct {
	duration time.Duration
	sleep    func(time.Duration)
}
```

`duration` 用来配置睡眠时长，`sleep` 则是传入 sleep 函数的途径。`sleep` 的签名跟 `time.Sleep` 一致，这样真实实现里可以用 `time.Sleep`，测试里可以用下面这个 spy：

```go
type SpyTime struct {
	durationSlept time.Duration
}

func (s *SpyTime) SetDurationSlept(duration time.Duration) {
	s.durationSlept = duration
}
```

spy 准备就绪，就可以为可配置 sleeper 写一个新测试了。

```go
func TestConfigurableSleeper(t *testing.T) {
	sleepTime := 5 * time.Second

	spyTime := &SpyTime{}
	sleeper := ConfigurableSleeper{sleepTime, spyTime.SetDurationSlept}
	sleeper.Sleep()

	if spyTime.durationSlept != sleepTime {
		t.Errorf("should have slept for %v but slept for %v", sleepTime, spyTime.durationSlept)
	}
}
```

这个测试应该不会有什么新东西，搭法和之前的 mock 测试非常像。

### 试着运行测试

```
sleeper.Sleep undefined (type ConfigurableSleeper has no field or method Sleep, but does have sleep)

```

你会看到一条非常清晰的错误信息：我们还没给 `ConfigurableSleeper` 创建 `Sleep` 方法。

### 写最少量的代码让测试跑起来，并检查失败的测试输出

```go
func (c *ConfigurableSleeper) Sleep() {
}
```

新的 `Sleep` 函数实现好之后，我们得到了一个失败的测试。

```
countdown_test.go:56: should have slept for 5s but slept for 0s
```

### 写足够的代码让它通过

现在要做的，就是为 `ConfigurableSleeper` 真正实现 `Sleep` 函数。

```go
func (c *ConfigurableSleeper) Sleep() {
	c.sleep(c.duration)
}
```

改完之后所有测试应该又都过了。你可能会纳闷：主程序根本没变，折腾这一圈图什么？看完下一节你应该就明白了。

### 清理与重构

最后一件事，是在 main 函数里真正用上我们的 `ConfigurableSleeper`。

```go
func main() {
	sleeper := &ConfigurableSleeper{1 * time.Second, time.Sleep}
	Countdown(os.Stdout, sleeper)
}
```

跑一遍测试，再手动运行一次程序，可以看到所有行为都和原来一样。

既然已经用上了 `ConfigurableSleeper`，就可以放心删掉 `DefaultSleeper` 实现了。程序收尾更利落，Sleeper 也变得更[通用](https://stackoverflow.com/questions/19291776/whats-the-difference-between-abstraction-and-generalization)了——多长的倒计时都应付得来。

## 可 mock 不是邪恶的吗？

你可能听说过"mock 很邪恶"。跟软件开发里的任何东西一样，它确实能被用来作恶，[DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) 也一样。

人们把局面搞糟，通常是因为不_听测试的话_，并且_没把重构阶段当回事_。

如果你的 mock 代码越来越复杂，或者为了测一个东西你得 mock 掉一大堆，那就该_倾听_这种不安的感觉，好好想想你的代码。这通常意味着：

- 你要测的东西身兼了太多职责（所以要 mock 的依赖太多）
  - 把模块拆开，让它少干点
- 它的依赖粒度太细
  - 想想怎么把其中一些依赖合并成一个有意义的模块
- 你的测试过分关注实现细节
  - 测试要优先瞄准预期的行为，而不是实现

一般来说，mock 用得太多，指向的是代码里的_糟糕抽象_。

**大家在这里看到的是 TDD 的弱点，但它其实是优点**。糟糕的测试代码，多半是糟糕设计的结果；换个好听点的说法：设计良好的代码，很好测。

### 可 mock 和测试还是让我的日子很难过啊！

你遇到过这种情况吗？

- 你想重构一下
- 结果不得不改一大堆测试
- 于是你开始怀疑 TDD，并在 Medium 上发了一篇题为《Mocking considered harmful》（mock 有害论）的文章

这通常说明你测了太多的_实现细节_。尽量让测试去测_有用的行为_，除非实现本身对系统的运行方式真的至关重要。

到底该在_哪个层面_测，有时确实不好拿捏，下面是一些我努力遵循的思路和规矩：

- **重构的定义就是：代码变了，行为不变**。既然决定做重构，理论上你应该能在不改任何测试的情况下完成 commit。所以写测试的时候问问自己
  - 我测的是想要的行为，还是实现细节？
  - 如果重构这段代码，我是不是得大改测试？
- 虽然 Go 允许你测私有函数，但我建议别这么做：私有函数是为支撑公开行为而存在的实现细节，要测就测公开行为。Sandi Metz 说私有函数"不那么稳定"，你可不想让自己的测试跟它们绑在一起。
- 我觉得一个测试如果动用了**超过 3 个 mock，那就是个危险信号**——该重新想想设计了
- 用 spy 要谨慎。spy 能让你看到所写算法的内部，这非常有用，但也意味着测试代码和实现耦合得更紧。**如果你打算 spy 这些细节，先确认自己是真的在乎它们**

#### 我就不能用个 mock 框架吗？

mock 不需要什么魔法，而且相对简单；用框架反而会让 mock 显得比实际上复杂。这一章我们不用自动 mock，为的是收获：

- 更透彻地理解该怎么 mock
- 练习实现接口

在协作项目里，自动生成 mock 有它的价值。在团队中，mock 生成工具能把测试替身的一致性固化下来，避免测试替身写得五花八门——那会进一步导致测试写得五花八门。

你只应该使用针对接口生成测试替身的 mock 生成器。任何过分规定测试怎么写、或者满肚子"魔法"的工具，都请它直接滚进大海。

## 总结

### 再聊聊 TDD 方法

- 面对不那么简单的例子时，把问题拆成"细细的纵向切片"。尽早让_有测试撑腰的能跑软件_落地，免得掉进兔子洞，或者搞成"大爆炸"式的做法。
- 手里有了能跑的软件之后，_小步迭代_着走到你最终需要的软件，应该就容易多了。

> "什么时候该用迭代式开发？只在你希望成功的项目上，才用迭代式开发。"

Martin Fowler。

### Mocking

- **不 mock 的话，代码里很多重要的地方就没法测**。拿本章的例子来说，我们就无法测试"每次打印之间有停顿"这一点，而类似的例子数不胜数。要调用一个_可能_失败的服务？想让系统处在某个特定状态再测？不靠 mock，这些场景都很难测到。
- 不用 mock，你可能为了测一条简单的业务规则，就得搭数据库、备好各种第三方的东西。测试很可能因此变慢，形成**缓慢的反馈循环**。
- 为了测点东西就得拉起一个数据库或 web 服务的话，这类服务本身不可靠，你的测试也容易变得**脆弱**。

开发者一旦学会了 mock，就很容易走向过度测试——把系统的每个犄角旮旯都按它_怎么运作_来测，而不是_它做什么_。时刻留意**你的测试的价值**，以及它们将来会给重构带来什么影响。

在这篇讲 mock 的文章里，我们只介绍了 **Spy**，它只是 mock 的一种。而 mock 是"测试替身"（test double）的一种。

> [测试替身（Test Double）是一个通用术语，泛指一切为了测试目的而替换生产对象的做法。](https://martinfowler.com/bliki/TestDouble.html)

测试替身下面还细分好几种类型，比如 stub、spy，当然还有 mock！想深入了解，可以看 [Martin Fowler 的这篇文章](https://martinfowler.com/bliki/TestDouble.html)。

## 附加内容 —— Go 1.23 的迭代器示例

Go 1.23 [引入了迭代器](https://tip.golang.org/doc/go1.23)。迭代器的用法多种多样，在这里我们可以做一个 `countdownFrom` 迭代器，按倒序返回倒数要用的数字。

在讲怎么写自定义迭代器之前，先看看怎么用它。与其写一个看起来相当命令式的循环来倒数，不如去 `range` 我们自定义的 `countdownFrom` 迭代器，让这段代码更有表达力。

```go
func Countdown(out io.Writer, sleeper Sleeper) {
	for i := range countDownFrom(3) {
		fmt.Fprintln(out, i)
		sleeper.Sleep()
	}

	fmt.Fprint(out, finalWord)
}
```

要写一个像 `countDownFrom` 这样的迭代器，函数得按特定方式来写。文档是这么说的：

    The “range” clause in a “for-range” loop now accepts iterator functions of the following types
        func(func() bool)
        func(func(K) bool)
        func(func(K, V) bool)

（`K` 和 `V` 分别代表键和值的类型。）

在我们的场景里没有键，只有值。Go 还贴心地提供了 `iter.Seq[T]` 这个便捷类型，它是 `func(func(T) bool)` 的类型别名。

```go
func countDownFrom(from int) iter.Seq[int] {
	return func(yield func(int) bool) {
		for i := from; i > 0; i-- {
			if !yield(i) {
				return
			}
		}
	}
}
```

这是一个简单的迭代器，会从 `from` 开始倒序产出（yield）数字——正合我们的用例。
