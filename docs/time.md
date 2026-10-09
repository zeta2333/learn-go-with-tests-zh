# Time

[**本章的所有代码都可以在这里找到**](https://github.com/quii/learn-go-with-tests/tree/main/time)

产品负责人想让我们扩展命令行应用的功能：帮一群人玩德州扑克（Texas Hold'em）。

## 关于扑克，知道这些就够了

关于扑克你不需要懂太多，只要知道：每隔一段时间，都得把一个不断上涨的“盲注”（blind）金额告诉所有玩家。

我们的应用会帮忙记住盲注什么时候该涨、该涨到多少。

* 游戏开始时，它会问有多少玩家。这决定了“盲注”上涨之前的时间长短。
  * 基础时长是 5 分钟。
  * 每有一个玩家，加 1 分钟。
  * 比如 6 个玩家，盲注就是 11 分钟涨一次。
* 盲注时间到期后，游戏应该提醒玩家新一轮盲注的金额。
* 盲注从 100 筹码起步，然后是 200、400、600、1000、2000，接着一直翻倍涨下去，直到游戏结束（我们之前做的 “Ruth wins” 功能应该仍然能结束游戏）

## 回顾一下现有代码

上一章我们着手开发了这个命令行应用，它已经能接受 `{name} wins` 这样的命令。下面是当前 `CLI` 代码的样子，不过动手之前，也请务必把其他代码熟悉一遍。

```go
type CLI struct {
	playerStore PlayerStore
	in          *bufio.Scanner
}

func NewCLI(store PlayerStore, in io.Reader) *CLI {
	return &CLI{
		playerStore: store,
		in:          bufio.NewScanner(in),
	}
}

func (cli *CLI) PlayPoker() {
	userInput := cli.readLine()
	cli.playerStore.RecordWin(extractWinner(userInput))
}

func extractWinner(userInput string) string {
	return strings.Replace(userInput, " wins", "", 1)
}

func (cli *CLI) readLine() string {
	cli.in.Scan()
	return cli.in.Text()
}
```

### `time.AfterFunc`

我们想要的是：安排程序在特定的时间间隔后打印盲注金额，间隔取决于玩家人数。

为了收窄范围，我们先不管玩家人数这部分，直接假设有 5 个玩家，这样我们要测的就是：*每隔 10 分钟打印新的盲注金额*。

照例，标准库早已为我们备好了工具：[`func AfterFunc(d Duration, f func()) *Timer`](https://golang.org/pkg/time/#AfterFunc)

> `AfterFunc` 会等待一段时间（duration）流逝，然后在它自己的 goroutine 里调用 f。它返回一个 `Timer`，可以用它的 Stop 方法取消这次调用。

### [`time.Duration`](https://golang.org/pkg/time/#Duration)

> Duration 表示两个时刻之间经过的时间，以 int64 纳秒数计。

time 库提供了不少常量，让你把这些纳秒乘出更好读一些的值，正适合我们接下来要遇到的场景

```
5 * time.Second
```

调用 `PlayPoker` 时，我们会把所有盲注提醒都安排好。

不过测试起来可能有点棘手。我们想验证每个时间段都调度了正确的盲注金额，但看看 `time.AfterFunc` 的签名：它的第二个参数是将要执行的函数。Go 里无法比较函数，所以我们无从测出传进去的是什么函数。因此，我们需要给 `time.AfterFunc` 包上一层，让它接收“什么时间执行”和“打印什么金额”，这样我们才能 spy 住它。

## 先写测试

往测试套件里加一个新测试

```go
t.Run("it schedules printing of blind values", func(t *testing.T) {
	in := strings.NewReader("Chris wins\n")
	playerStore := &poker.StubPlayerStore{}
	blindAlerter := &SpyBlindAlerter{}

	cli := poker.NewCLI(playerStore, in, blindAlerter)
	cli.PlayPoker()

	if len(blindAlerter.alerts) != 1 {
		t.Fatal("expected a blind alert to be scheduled")
	}
})
```

你会注意到我们造了一个 `SpyBlindAlerter`，试图把它注入 `CLI`，然后检查调用 `PlayPoker` 之后有一个提醒被调度了。

（记住，我们先从最简单的场景做起，然后再迭代。）

下面是 `SpyBlindAlerter` 的定义

```go
type SpyBlindAlerter struct {
	alerts []struct {
		scheduledAt time.Duration
		amount      int
	}
}

func (s *SpyBlindAlerter) ScheduleAlertAt(duration time.Duration, amount int) {
	s.alerts = append(s.alerts, struct {
		scheduledAt time.Duration
		amount      int
	}{duration, amount})
}
```

## 试着运行测试

```
./CLI_test.go:32:27: too many arguments in call to poker.NewCLI
	have (*poker.StubPlayerStore, *strings.Reader, *SpyBlindAlerter)
	want (poker.PlayerStore, io.Reader)
```

## 写最少的代码让测试能运行，并检查失败的测试输出

我们新增了一个参数，编译器在抱怨。*严格来说*，最少的代码是让 `NewCLI` 接收一个 `*SpyBlindAlerter`，不过咱们稍微耍个滑头，直接把这个依赖定义成一个接口。

```go
type BlindAlerter interface {
	ScheduleAlertAt(duration time.Duration, amount int)
}
```

然后把它加进构造函数

```go
func NewCLI(store PlayerStore, in io.Reader, alerter BlindAlerter) *CLI
```

现在你的其他测试会失败，因为它们没有往 `NewCLI` 里传 `BlindAlerter`。

对其他测试来说，spy BlindAlerter 没有什么意义，所以在测试文件里加上

```go
var dummySpyAlerter = &SpyBlindAlerter{}
```

然后在其他测试里用它，修好编译问题。给它标上 “dummy”（哑对象），测试的读者一眼就能看出它无关紧要。

[> dummy 对象到处传递，却从来不会被真正用上；通常只是拿来凑参数列表的。](https://martinfowler.com/articles/mocksArentStubs.html)

现在测试应该能编译了，而我们的新测试会失败。

```
=== RUN   TestCLI
=== RUN   TestCLI/it_schedules_printing_of_blind_values
--- FAIL: TestCLI (0.00s)
    --- FAIL: TestCLI/it_schedules_printing_of_blind_values (0.00s)
    	CLI_test.go:38: expected a blind alert to be scheduled
```

## 写足够的代码让测试通过

我们需要把 `BlindAlerter` 加成 `CLI` 的一个字段，这样在 `PlayPoker` 方法里才能引用它。

```go
type CLI struct {
	playerStore PlayerStore
	in          *bufio.Scanner
	alerter     BlindAlerter
}

func NewCLI(store PlayerStore, in io.Reader, alerter BlindAlerter) *CLI {
	return &CLI{
		playerStore: store,
		in:          bufio.NewScanner(in),
		alerter:     alerter,
	}
}
```

为了让测试通过，我们可以给 `BlindAlerter` 随便传点什么

```go
func (cli *CLI) PlayPoker() {
	cli.alerter.ScheduleAlertAt(5*time.Second, 100)
	userInput := cli.readLine()
	cli.playerStore.RecordWin(extractWinner(userInput))
}
```

接下来，我们要检查它是否把 5 人局该有的所有提醒都调度了出来

## 先写测试

```go
	t.Run("it schedules printing of blind values", func(t *testing.T) {
		in := strings.NewReader("Chris wins\n")
		playerStore := &poker.StubPlayerStore{}
		blindAlerter := &SpyBlindAlerter{}

		cli := poker.NewCLI(playerStore, in, blindAlerter)
		cli.PlayPoker()

		cases := []struct {
			expectedScheduleTime time.Duration
			expectedAmount       int
		}{
			{0 * time.Second, 100},
			{10 * time.Minute, 200},
			{20 * time.Minute, 300},
			{30 * time.Minute, 400},
			{40 * time.Minute, 500},
			{50 * time.Minute, 600},
			{60 * time.Minute, 800},
			{70 * time.Minute, 1000},
			{80 * time.Minute, 2000},
			{90 * time.Minute, 4000},
			{100 * time.Minute, 8000},
		}

		for i, c := range cases {
			t.Run(fmt.Sprintf("%d scheduled for %v", c.expectedAmount, c.expectedScheduleTime), func(t *testing.T) {

				if len(blindAlerter.alerts) <= i {
					t.Fatalf("alert %d was not scheduled %v", i, blindAlerter.alerts)
				}

				alert := blindAlerter.alerts[i]

				amountGot := alert.amount
				if amountGot != c.expectedAmount {
					t.Errorf("got amount %d, want %d", amountGot, c.expectedAmount)
				}

				gotScheduledTime := alert.scheduledAt
				if gotScheduledTime != c.expectedScheduleTime {
					t.Errorf("got scheduled time of %v, want %v", gotScheduledTime, c.expectedScheduleTime)
				}
			})
		}
	})
```

表驱动测试在这里很合适，它清楚地展示了我们的需求是什么。我们遍历这个表，检查 `SpyBlindAlerter`，看提醒是否以正确的值被调度。

## 试着运行测试

你应该会看到一大堆类似这样的失败

```
=== RUN   TestCLI
--- FAIL: TestCLI (0.00s)
=== RUN   TestCLI/it_schedules_printing_of_blind_values
    --- FAIL: TestCLI/it_schedules_printing_of_blind_values (0.00s)
=== RUN   TestCLI/it_schedules_printing_of_blind_values/100_scheduled_for_0s
        --- FAIL: TestCLI/it_schedules_printing_of_blind_values/100_scheduled_for_0s (0.00s)
        	CLI_test.go:71: got scheduled time of 5s, want 0s
=== RUN   TestCLI/it_schedules_printing_of_blind_values/200_scheduled_for_10m0s
        --- FAIL: TestCLI/it_schedules_printing_of_blind_values/200_scheduled_for_10m0s (0.00s)
        	CLI_test.go:59: alert 1 was not scheduled [{5000000000 100}]
```

## 写足够的代码让测试通过

```go
func (cli *CLI) PlayPoker() {

	blinds := []int{100, 200, 300, 400, 500, 600, 800, 1000, 2000, 4000, 8000}
	blindTime := 0 * time.Second
	for _, blind := range blinds {
		cli.alerter.ScheduleAlertAt(blindTime, blind)
		blindTime = blindTime + 10*time.Minute
	}

	userInput := cli.readLine()
	cli.playerStore.RecordWin(extractWinner(userInput))
}
```

这比我们已有的代码复杂不了多少。现在只是遍历一个 `blinds` 数组，在递增的 `blindTime` 上调用调度器

## 重构

我们可以把调度提醒封装成一个方法，让 `PlayPoker` 读起来更清楚一点。

```go
func (cli *CLI) PlayPoker() {
	cli.scheduleBlindAlerts()
	userInput := cli.readLine()
	cli.playerStore.RecordWin(extractWinner(userInput))
}

func (cli *CLI) scheduleBlindAlerts() {
	blinds := []int{100, 200, 300, 400, 500, 600, 800, 1000, 2000, 4000, 8000}
	blindTime := 0 * time.Second
	for _, blind := range blinds {
		cli.alerter.ScheduleAlertAt(blindTime, blind)
		blindTime = blindTime + 10*time.Minute
	}
}
```

最后，我们的测试看起来有点笨拙。两个匿名结构体表示的其实是同一样东西——一个 `ScheduledAlert`。把它重构成一个新类型，再写几个辅助函数来比较它们吧。

```go
type scheduledAlert struct {
	at     time.Duration
	amount int
}

func (s scheduledAlert) String() string {
	return fmt.Sprintf("%d chips at %v", s.amount, s.at)
}

type SpyBlindAlerter struct {
	alerts []scheduledAlert
}

func (s *SpyBlindAlerter) ScheduleAlertAt(at time.Duration, amount int) {
	s.alerts = append(s.alerts, scheduledAlert{at, amount})
}
```

我们给这个类型加了一个 `String()` 方法，这样测试失败时能打印得好看些

更新我们的测试，用上新类型

```go
t.Run("it schedules printing of blind values", func(t *testing.T) {
	in := strings.NewReader("Chris wins\n")
	playerStore := &poker.StubPlayerStore{}
	blindAlerter := &SpyBlindAlerter{}

	cli := poker.NewCLI(playerStore, in, blindAlerter)
	cli.PlayPoker()

	cases := []scheduledAlert{
		{0 * time.Second, 100},
		{10 * time.Minute, 200},
		{20 * time.Minute, 300},
		{30 * time.Minute, 400},
		{40 * time.Minute, 500},
		{50 * time.Minute, 600},
		{60 * time.Minute, 800},
		{70 * time.Minute, 1000},
		{80 * time.Minute, 2000},
		{90 * time.Minute, 4000},
		{100 * time.Minute, 8000},
	}

	for i, want := range cases {
		t.Run(fmt.Sprint(want), func(t *testing.T) {

			if len(blindAlerter.alerts) <= i {
				t.Fatalf("alert %d was not scheduled %v", i, blindAlerter.alerts)
			}

			got := blindAlerter.alerts[i]
			assertScheduledAlert(t, got, want)
		})
	}
})
```

`assertScheduledAlert` 就留给你自己实现。

我们在这里花了相当多时间写测试，一直没跟应用本体集成，多少有点不听话。在继续堆需求之前，先把这件事解决掉。

试着运行应用，它编译不过，会抱怨 `NewCLI` 的参数不够。

我们来创建一个能在应用里用的 `BlindAlerter` 实现。

新建 `blind_alerter.go`，把 `BlindAlerter` 接口挪进去，再把下面的新东西加上

```go
package poker

import (
	"fmt"
	"os"
	"time"
)

type BlindAlerter interface {
	ScheduleAlertAt(duration time.Duration, amount int)
}

type BlindAlerterFunc func(duration time.Duration, amount int)

func (a BlindAlerterFunc) ScheduleAlertAt(duration time.Duration, amount int) {
	a(duration, amount)
}

func StdOutAlerter(duration time.Duration, amount int) {
	time.AfterFunc(duration, func() {
		fmt.Fprintf(os.Stdout, "Blind is now %d\n", amount)
	})
}
```

记住，任何*类型*都能实现接口，不只是 `struct`。如果你在写一个库，暴露的接口只定义了一个函数，那么顺带暴露一个 `MyInterfaceFunc` 类型是常见的惯用法。

这个类型本身是一个 `func`，同时实现了你的接口。这样，接口的使用者就可以只用一个函数实现你的接口，而不必创建一个空的 `struct` 类型。

接着我们创建 `StdOutAlerter` 函数，它的签名与该函数类型一致，然后直接用 `time.AfterFunc` 安排它打印到 `os.Stdout`。

更新 `main` 里创建 `NewCLI` 的地方，看看实际效果

```go
poker.NewCLI(store, os.Stdin, poker.BlindAlerterFunc(poker.StdOutAlerter)).PlayPoker()
```

运行之前，你或许想把 `CLI` 里 `blindTime` 的增量从 10 分钟改成 10 秒，好亲眼看看效果。

你应该能看到盲注金额像我们期望的那样每 10 秒打印一次。注意，你仍然可以在 CLI 里输入 `Shaun wins`，程序照样会像我们期望的那样停下来。

一局扑克可不会总凑 5 个人玩，所以我们需要在游戏开始前提示用户输入人数。

## 先写测试

要检查我们有没有提示输入人数，就得记录写到 StdOut 里的内容。这招我们已经用过几次了：`os.Stdout` 是个 `io.Writer`，所以只要用依赖注入在测试里传一个 `bytes.Buffer` 进去，就能看到我们的代码往里写了什么。

这个测试暂时不关心其他协作者，所以我们在测试文件里造了几个 dummy。

这里我们得多留个心眼：`CLI` 现在有 4 个依赖了，感觉它承担的职责可能开始有点过多。先忍一忍，看看加这个新功能的过程中会不会自然浮现出一次重构。

```go
var dummyBlindAlerter = &SpyBlindAlerter{}
var dummyPlayerStore = &poker.StubPlayerStore{}
var dummyStdIn = &bytes.Buffer{}
var dummyStdOut = &bytes.Buffer{}
```

下面是我们的新测试

```go
t.Run("it prompts the user to enter the number of players", func(t *testing.T) {
	stdout := &bytes.Buffer{}
	cli := poker.NewCLI(dummyPlayerStore, dummyStdIn, stdout, dummyBlindAlerter)
	cli.PlayPoker()

	got := stdout.String()
	want := "Please enter the number of players: "

	if got != want {
		t.Errorf("got %q, want %q", got, want)
	}
})
```

我们把将来在 `main` 里会作为 `os.Stdout` 的东西传进去，看看写了什么。

## 试着运行测试

```
./CLI_test.go:38:27: too many arguments in call to poker.NewCLI
	have (*poker.StubPlayerStore, *bytes.Buffer, *bytes.Buffer, *SpyBlindAlerter)
	want (poker.PlayerStore, io.Reader, poker.BlindAlerter)
```

## 写最少的代码让测试能运行，并检查失败的测试输出

多了一个新依赖，我们得更新 `NewCLI`

```go
func NewCLI(store PlayerStore, in io.Reader, out io.Writer, alerter BlindAlerter) *CLI
```

现在*其他*测试编译不过了，因为它们没有往 `NewCLI` 里传 `io.Writer`。

给其他测试加上 `dummyStdOut`。

新测试会像这样失败

```
=== RUN   TestCLI
--- FAIL: TestCLI (0.00s)
=== RUN   TestCLI/it_prompts_the_user_to_enter_the_number_of_players
    --- FAIL: TestCLI/it_prompts_the_user_to_enter_the_number_of_players (0.00s)
    	CLI_test.go:46: got '', want 'Please enter the number of players: '
FAIL
```

## 写足够的代码让测试通过

我们要把新依赖加到 `CLI` 上，好在 `PlayPoker` 里引用它

```go
type CLI struct {
	playerStore PlayerStore
	in          *bufio.Scanner
	out         io.Writer
	alerter     BlindAlerter
}

func NewCLI(store PlayerStore, in io.Reader, out io.Writer, alerter BlindAlerter) *CLI {
	return &CLI{
		playerStore: store,
		in:          bufio.NewScanner(in),
		out:         out,
		alerter:     alerter,
	}
}
```

然后终于可以在游戏开始时把提示语写上了

```go
func (cli *CLI) PlayPoker() {
	fmt.Fprint(cli.out, "Please enter the number of players: ")
	cli.scheduleBlindAlerts()
	userInput := cli.readLine()
	cli.playerStore.RecordWin(extractWinner(userInput))
}
```

## 重构

提示语字符串重复了，应该提取成一个常量

```go
const PlayerPrompt = "Please enter the number of players: "
```

测试代码和 `CLI` 里都用上它。

现在我们需要传入一个数字并把它提取出来。要知道有没有达到预期效果，唯一的办法就是看调度了哪些盲注提醒。

## 先写测试

```go
t.Run("it prompts the user to enter the number of players", func(t *testing.T) {
	stdout := &bytes.Buffer{}
	in := strings.NewReader("7\n")
	blindAlerter := &SpyBlindAlerter{}

	cli := poker.NewCLI(dummyPlayerStore, in, stdout, blindAlerter)
	cli.PlayPoker()

	got := stdout.String()
	want := poker.PlayerPrompt

	if got != want {
		t.Errorf("got %q, want %q", got, want)
	}

	cases := []scheduledAlert{
		{0 * time.Second, 100},
		{12 * time.Minute, 200},
		{24 * time.Minute, 300},
		{36 * time.Minute, 400},
	}

	for i, want := range cases {
		t.Run(fmt.Sprint(want), func(t *testing.T) {

			if len(blindAlerter.alerts) <= i {
				t.Fatalf("alert %d was not scheduled %v", i, blindAlerter.alerts)
			}

			got := blindAlerter.alerts[i]
			assertScheduledAlert(t, got, want)
		})
	}
})
```

哎哟！改动不少。

* 我们把 StdIn 的 dummy 撤掉，换成一个 mock 版的输入，扮演输入了 7 的用户
* 我们也把盲注提醒器上的 dummy 撤掉，这样才能看出人数对调度产生了影响
* 我们测试调度了哪些提醒

## 试着运行测试

测试应该仍能编译并失败，报告调度时间不对，因为我们把游戏硬编码成了按 5 人局来算

```
=== RUN   TestCLI
--- FAIL: TestCLI (0.00s)
=== RUN   TestCLI/it_prompts_the_user_to_enter_the_number_of_players
    --- FAIL: TestCLI/it_prompts_the_user_to_enter_the_number_of_players (0.00s)
=== RUN   TestCLI/it_prompts_the_user_to_enter_the_number_of_players/100_chips_at_0s
        --- PASS: TestCLI/it_prompts_the_user_to_enter_the_number_of_players/100_chips_at_0s (0.00s)
=== RUN   TestCLI/it_prompts_the_user_to_enter_the_number_of_players/200_chips_at_12m0s
```

## 写足够的代码让测试通过

记住，为了让它先跑起来，犯什么样的“罪行”都随我们。等有了能工作的软件，再来收拾我们即将造出的烂摊子！

```go
func (cli *CLI) PlayPoker() {
	fmt.Fprint(cli.out, PlayerPrompt)

	numberOfPlayers, _ := strconv.Atoi(cli.readLine())

	cli.scheduleBlindAlerts(numberOfPlayers)

	userInput := cli.readLine()
	cli.playerStore.RecordWin(extractWinner(userInput))
}

func (cli *CLI) scheduleBlindAlerts(numberOfPlayers int) {
	blindIncrement := time.Duration(5+numberOfPlayers) * time.Minute

	blinds := []int{100, 200, 300, 400, 500, 600, 800, 1000, 2000, 4000, 8000}
	blindTime := 0 * time.Second
	for _, blind := range blinds {
		cli.alerter.ScheduleAlertAt(blindTime, blind)
		blindTime = blindTime + blindIncrement
	}
}
```

* 我们把 `numberOfPlayersInput` 读进一个字符串
* 我们用 `cli.readLine()` 从用户那里拿到输入，然后调用 `Atoi` 把它转成整数——错误场景一概不管。那个场景我们之后得补个测试。
* 接着我们让 `scheduleBlindAlerts` 接收玩家人数。遍历盲注金额时，算出一个 `blindIncrement` 时间间隔，加到 `blindTime` 上

新测试是修好了，可一大堆其他测试挂了，因为现在我们的系统只有在游戏以“用户输入一个数字”开场时才能工作。你需要修改测试里的用户输入，加上“数字 + 换行”来把它们修好（这又暴露了当前做法的更多缺陷）。

## 重构

这一切是不是感觉有点糟糕？来**听测试的话**。

* 为了测试调度了一些提醒，我们摆弄了 4 个不同的依赖。系统里一个*东西*的依赖一多，往往说明它管得太宽了。这一点从测试有多乱就能直观地看出来。
* 在我看来，这意味着**我们需要在“读取用户输入”和“想做的业务逻辑”之间，做一层更干净的抽象**
* 更好的测试应该是：*给定这样的用户输入，我们是否用正确的人数调用了一个新类型 `Game`*。
* 然后把调度相关的测试抽到新 `Game` 的测试里去。

我们可以先朝 `Game` 重构，测试应该会继续保持通过。等结构调整到位，再来考虑如何重构测试，让它们体现新的关注点分离

记住，重构时的每一步改动都要尽量小，并且不断重跑测试。

自己先试试。想想 `Game` 该提供的能力边界在哪里，`CLI` 又该做什么。

眼下**不要**改 `NewCLI` 的对外接口——同时改测试代码和客户端代码太难两头兼顾，最后很可能把东西弄坏。

这是我想出来的：

```go
// game.go
type Game struct {
	alerter BlindAlerter
	store   PlayerStore
}

func (p *Game) Start(numberOfPlayers int) {
	blindIncrement := time.Duration(5+numberOfPlayers) * time.Minute

	blinds := []int{100, 200, 300, 400, 500, 600, 800, 1000, 2000, 4000, 8000}
	blindTime := 0 * time.Second
	for _, blind := range blinds {
		p.alerter.ScheduleAlertAt(blindTime, blind)
		blindTime = blindTime + blindIncrement
	}
}

func (p *Game) Finish(winner string) {
	p.store.RecordWin(winner)
}

// cli.go
type CLI struct {
	in   *bufio.Scanner
	out  io.Writer
	game *Game
}

func NewCLI(store PlayerStore, in io.Reader, out io.Writer, alerter BlindAlerter) *CLI {
	return &CLI{
		in:  bufio.NewScanner(in),
		out: out,
		game: &Game{
			alerter: alerter,
			store:   store,
		},
	}
}

const PlayerPrompt = "Please enter the number of players: "

func (cli *CLI) PlayPoker() {
	fmt.Fprint(cli.out, PlayerPrompt)

	numberOfPlayersInput := cli.readLine()
	numberOfPlayers, _ := strconv.Atoi(strings.Trim(numberOfPlayersInput, "\n"))

	cli.game.Start(numberOfPlayers)

	winnerInput := cli.readLine()
	winner := extractWinner(winnerInput)

	cli.game.Finish(winner)
}

func extractWinner(userInput string) string {
	return strings.Replace(userInput, " wins\n", "", 1)
}

func (cli *CLI) readLine() string {
	cli.in.Scan()
	return cli.in.Text()
}
```

从“领域”的视角看：

* 我们想 `Start` 一局 `Game`，告诉它有多少人参与
* 我们想 `Finish` 一局 `Game`，宣布获胜者

新的 `Game` 类型为我们封装了这些。

经过这次改动，`BlindAlerter` 和 `PlayerStore` 都交给了 `Game`，因为提醒和保存结果现在是它的职责。

我们的 `CLI` 现在只关心：

* 用它已有的依赖构造 `Game`（这一点接下来我们会重构）
* 把用户输入解释成对 `Game` 的方法调用

我们要尽量避免做那种让测试长时间处于失败状态的“大”重构，那会加大犯错的概率。（如果你在大型/分布式团队里工作，这一点格外重要。）

我们要做的第一件事是重构 `Game`，把它注入 `CLI`。先在测试里做最小的改动来配合，然后再看怎么把测试按“解析用户输入”和“游戏管理”两个主题拆开。

眼下要做的只是改 `NewCLI`

```go
func NewCLI(in io.Reader, out io.Writer, game *Game) *CLI {
	return &CLI{
		in:   bufio.NewScanner(in),
		out:  out,
		game: game,
	}
}
```

这感觉已经是一种进步了。依赖更少了，而且*我们的依赖清单正反映着整体设计目标*：CLI 只管输入/输出，游戏特有的动作交给 `Game`。

尝试编译会出问题。你应该能自己修好。现在先别想着给 `Game` 做 mock，直接初始化*真正的* `Game`，让一切编译通过、测试变绿就行。

为此你需要写一个构造函数

```go
func NewGame(alerter BlindAlerter, store PlayerStore) *Game {
	return &Game{
		alerter: alerter,
		store:   store,
	}
}
```

下面是其中一个测试修好后的初始化代码

```go
stdout := &bytes.Buffer{}
in := strings.NewReader("7\n")
blindAlerter := &SpyBlindAlerter{}
game := poker.NewGame(blindAlerter, dummyPlayerStore)

cli := poker.NewCLI(in, stdout, game)
cli.PlayPoker()
```

把测试修好、回到绿色应该费不了多少劲（重点就在这儿！），但进入下一阶段前，记得把 `main.go` 也修好。

```go
// main.go
game := poker.NewGame(poker.BlindAlerterFunc(poker.StdOutAlerter), store)
cli := poker.NewCLI(os.Stdin, os.Stdout, game)
cli.PlayPoker()
```

既然已经抽出了 `Game`，就该把游戏特有的断言挪进独立于 CLI 的测试里。

这就是一道把 `CLI` 测试复制一份、依赖更少的练习题

```go
func TestGame_Start(t *testing.T) {
	t.Run("schedules alerts on game start for 5 players", func(t *testing.T) {
		blindAlerter := &poker.SpyBlindAlerter{}
		game := poker.NewGame(blindAlerter, dummyPlayerStore)

		game.Start(5)

		cases := []poker.ScheduledAlert{
			{At: 0 * time.Second, Amount: 100},
			{At: 10 * time.Minute, Amount: 200},
			{At: 20 * time.Minute, Amount: 300},
			{At: 30 * time.Minute, Amount: 400},
			{At: 40 * time.Minute, Amount: 500},
			{At: 50 * time.Minute, Amount: 600},
			{At: 60 * time.Minute, Amount: 800},
			{At: 70 * time.Minute, Amount: 1000},
			{At: 80 * time.Minute, Amount: 2000},
			{At: 90 * time.Minute, Amount: 4000},
			{At: 100 * time.Minute, Amount: 8000},
		}

		checkSchedulingCases(cases, t, blindAlerter)
	})

	t.Run("schedules alerts on game start for 7 players", func(t *testing.T) {
		blindAlerter := &poker.SpyBlindAlerter{}
		game := poker.NewGame(blindAlerter, dummyPlayerStore)

		game.Start(7)

		cases := []poker.ScheduledAlert{
			{At: 0 * time.Second, Amount: 100},
			{At: 12 * time.Minute, Amount: 200},
			{At: 24 * time.Minute, Amount: 300},
			{At: 36 * time.Minute, Amount: 400},
		}

		checkSchedulingCases(cases, t, blindAlerter)
	})

}

func TestGame_Finish(t *testing.T) {
	store := &poker.StubPlayerStore{}
	game := poker.NewGame(dummyBlindAlerter, store)
	winner := "Ruth"

	game.Finish(winner)
	poker.AssertPlayerWin(t, store, winner)
}
```

一局扑克开始时会发生什么，背后的意图现在清晰多了。

记得把游戏结束时的测试也一并搬过去。

确认游戏逻辑的测试都搬妥之后，我们就可以简化 CLI 测试，让它们更清楚地反映我们想要的职责

* 处理用户输入，并在合适的时机调用 `Game` 的方法
* 发送输出
* 至关重要的是，它完全不知道游戏内部是怎么运作的

为此，我们得让 `CLI` 不再依赖具体的 `Game` 类型，而是接收一个带 `Start(numberOfPlayers)` 和 `Finish(winner)` 的接口。然后我们就能创建一个该类型的 spy，验证正确的调用确实发生了。

也是在这里我们体会到，起名有时真让人别扭。把 `Game` 改名为 `TexasHoldem`（这才是我们在玩的*那种*游戏），新的接口则叫 `Game`。这样恰好忠于我们的初衷：CLI 对实际在玩什么游戏、`Start` 和 `Finish` 之后发生什么一无所知。

```go
type Game interface {
	Start(numberOfPlayers int)
	Finish(winner string)
}
```

把 `CLI` 里所有引用 `*Game` 的地方替换成 `Game`（我们的新接口）。老规矩，重构期间不断重跑测试，确保一切保持绿色。

现在 `CLI` 与 `TexasHoldem` 解耦了，我们可以用 spy 检查 `Start` 和 `Finish` 是否在我们期望的时机、以正确的参数被调用。

创建一个实现了 `Game` 的 spy

```go
type GameSpy struct {
	StartedWith  int
	FinishedWith string
}

func (g *GameSpy) Start(numberOfPlayers int) {
	g.StartedWith = numberOfPlayers
}

func (g *GameSpy) Finish(winner string) {
	g.FinishedWith = winner
}
```

把 `CLI` 测试里所有在测游戏特有逻辑的地方，替换成对我们 `GameSpy` 调用情况的检查。这样测试就能清楚地反映 CLI 的职责。

下面是一个修好的测试示例；剩下的自己动手，卡住了就翻翻源代码。

```go
	t.Run("it prompts the user to enter the number of players and starts the game", func(t *testing.T) {
		stdout := &bytes.Buffer{}
		in := strings.NewReader("7\n")
		game := &GameSpy{}

		cli := poker.NewCLI(in, stdout, game)
		cli.PlayPoker()

		gotPrompt := stdout.String()
		wantPrompt := poker.PlayerPrompt

		if gotPrompt != wantPrompt {
			t.Errorf("got %q, want %q", gotPrompt, wantPrompt)
		}

		if game.StartedWith != 7 {
			t.Errorf("wanted Start called with 7 but got %d", game.StartedWith)
		}
	})
```

关注点已经分离得干干净净，再来检查 `CLI` 里围绕 IO 的边界场景应该就轻松多了。

我们需要处理这种情况：提示输入人数时，用户输入了非数字：

我们的代码不应该开始游戏，而应该给用户打印一条有用的错误信息，然后退出。

## 先写测试

我们先确保游戏不会开始

```go
t.Run("it prints an error when a non numeric value is entered and does not start the game", func(t *testing.T) {
	stdout := &bytes.Buffer{}
	in := strings.NewReader("Pies\n")
	game := &GameSpy{}

	cli := poker.NewCLI(in, stdout, game)
	cli.PlayPoker()

	if game.StartCalled {
		t.Errorf("game should not have started")
	}
})
```

你需要给 `GameSpy` 加一个字段 `StartCalled`，只有 `Start` 被调用时才会置位

## 试着运行测试

```
=== RUN   TestCLI/it_prints_an_error_when_a_non_numeric_value_is_entered_and_does_not_start_the_game
    --- FAIL: TestCLI/it_prints_an_error_when_a_non_numeric_value_is_entered_and_does_not_start_the_game (0.00s)
        CLI_test.go:62: game should not have started
```

## 写足够的代码让测试通过

在调用 `Atoi` 的地方，我们只需要检查一下错误

```go
numberOfPlayers, err := strconv.Atoi(cli.readLine())

if err != nil {
	return
}
```

接下来要把“你哪里做错了”告知用户，所以我们对打印到 `stdout` 的内容做断言。

## 先写测试

之前我们已经对打印到 `stdout` 的内容做过断言，所以暂时可以照搬那段代码

```go
gotPrompt := stdout.String()

wantPrompt := poker.PlayerPrompt + "you're so silly"

if gotPrompt != wantPrompt {
	t.Errorf("got %q, want %q", gotPrompt, wantPrompt)
}
```

写到 stdout 的*所有*内容我们都有存，所以仍然期望有 `poker.PlayerPrompt`。然后我们只是额外检查又打印了点东西。具体措辞先不纠结，重构的时候再处理。

## 试着运行测试

```
=== RUN   TestCLI/it_prints_an_error_when_a_non_numeric_value_is_entered_and_does_not_start_the_game
    --- FAIL: TestCLI/it_prints_an_error_when_a_non_numeric_value_is_entered_and_does_not_start_the_game (0.00s)
        CLI_test.go:70: got 'Please enter the number of players: ', want 'Please enter the number of players: you're so silly'
```

## 写足够的代码让测试通过

修改错误处理代码

```go
if err != nil {
	fmt.Fprint(cli.out, "you're so silly")
	return
}
```

## 重构

现在把这个消息重构成常量，就像 `PlayerPrompt` 那样

```go
wantPrompt := poker.PlayerPrompt + poker.BadPlayerInputErrMsg
```

再换上一条更合适的消息

```go
const BadPlayerInputErrMsg = "Bad value received for number of players, please try again with a number"
```

最后，我们围绕“发送到 `stdout` 的内容”的测试相当啰嗦，写个断言函数来清爽一下。

```go
func assertMessagesSentToUser(t testing.TB, stdout *bytes.Buffer, messages ...string) {
	t.Helper()
	want := strings.Join(messages, "")
	got := stdout.String()
	if got != want {
		t.Errorf("got %q sent to stdout but expected %+v", got, messages)
	}
}
```

这里用可变参数（vararg）语法（`...string`）正合适，因为我们要断言的消息数量不定。

两个对“发给用户的消息”做断言的测试都用上这个辅助函数。

还有不少测试可以借一些 `assertX` 函数改善一下，练习练习重构，把测试收拾得读起来舒服。

花点时间想想，我们一路逼出来的这些测试哪些真正有价值。记住，测试不是越多越好——你能不能重构/删掉其中一些，*同时依然对一切正常工作充满信心*？

这是我想出来的

```go
func TestCLI(t *testing.T) {

	t.Run("start game with 3 players and finish game with 'Chris' as winner", func(t *testing.T) {
		game := &GameSpy{}
		stdout := &bytes.Buffer{}

		in := userSends("3", "Chris wins")
		cli := poker.NewCLI(in, stdout, game)

		cli.PlayPoker()

		assertMessagesSentToUser(t, stdout, poker.PlayerPrompt)
		assertGameStartedWith(t, game, 3)
		assertFinishCalledWith(t, game, "Chris")
	})

	t.Run("start game with 8 players and record 'Cleo' as winner", func(t *testing.T) {
		game := &GameSpy{}

		in := userSends("8", "Cleo wins")
		cli := poker.NewCLI(in, dummyStdOut, game)

		cli.PlayPoker()

		assertGameStartedWith(t, game, 8)
		assertFinishCalledWith(t, game, "Cleo")
	})

	t.Run("it prints an error when a non numeric value is entered and does not start the game", func(t *testing.T) {
		game := &GameSpy{}

		stdout := &bytes.Buffer{}
		in := userSends("pies")

		cli := poker.NewCLI(in, stdout, game)
		cli.PlayPoker()

		assertGameNotStarted(t, game)
		assertMessagesSentToUser(t, stdout, poker.PlayerPrompt, poker.BadPlayerInputErrMsg)
	})
}
```

现在这些测试反映了 CLI 的主要能力：读懂用户输入里有几个人在玩、谁赢了，并处理人数输入非法的情况。这样读者不但清楚 `CLI` 做什么，也清楚它不做什么。

如果用户没有输入 `Ruth wins`，而是输入 `Lloyd is a killer`，会发生什么？

给这个场景写个测试并让它通过，给本章收个尾。

## 总结

### 项目快速回顾

过去 5 章，我们用 TDD 慢慢磨出了不少代码

* 我们有两个应用：一个命令行应用和一个 web 服务器。
* 两个应用都靠一个 `PlayerStore` 来记录获胜者
* web 服务器还能展示联盟排行榜，看看谁赢的场次最多
* 命令行应用则通过追踪当前盲注金额，帮玩家玩一局扑克。

### time.AfterFunc

在指定时长之后安排一次函数调用——这是个非常称手的工具。很值得花点时间[读读 `time` 包的文档](https://golang.org/pkg/time/)，里面有很多帮你省时间的函数和方法，随取随用。

我最喜欢的几个是

* `time.After(duration)` 在时长到期后返回一个 `chan Time`。如果你想*在*某个特定时间之后做点事，它能帮上忙。
* `time.NewTicker(duration)` 返回一个 `Ticker`，跟上面类似也返回 channel，但它是每隔一个 duration “滴答”一次，而不是只来一次。想每隔 `N duration` 执行一段代码时，它非常好用。

### 关注点分离的更多例子

*总的来说*，把处理用户输入和响应的职责从领域代码里分离出去，是好的实践。我们的命令行应用和 web 服务器都体现了这一点。

我们的测试一度变得乱糟糟：断言太多（检查这个输入、调度那些提醒，等等），依赖也太多。乱不乱，肉眼可见；**听测试的话实在太重要了**。

* 如果你的测试看起来很乱，试着重构它们。
* 如果重构之后还是一团糟，那很可能是在指出你设计上的缺陷
* 这正是测试真正的力量之一。

尽管测试和生产代码都有点乱，但有测试撑腰，我们依然可以放心重构。

记住，遇到这种局面时，永远小步走，每改一次就重跑测试。

同时重构测试代码*和*生产代码是危险的，所以我们先重构生产代码（在当时的状况下，测试也改进不了多少），并且不动它的接口，这样在改动的同时能最大限度地仰仗我们的测试。*然后*，等设计变好了，再重构测试。

重构之后，依赖清单反映了我们的设计目标。这是 DI 的又一个好处：它常常起到“记录意图”的作用。一旦依赖全局变量，职责就变得非常模糊。

## 用函数实现接口的例子

当你定义的接口里只有一个方法时，可以考虑配套定义一个 `MyInterfaceFunc` 类型，让用户只用一个函数就能实现你的接口。

```go
type BlindAlerter interface {
	ScheduleAlertAt(duration time.Duration, amount int)
}

// BlindAlerterFunc 允许你用一个函数来实现 BlindAlerter
type BlindAlerterFunc func(duration time.Duration, amount int)

// ScheduleAlertAt 是 BlindAlerterFunc 对 BlindAlerter 接口的实现
func (a BlindAlerterFunc) ScheduleAlertAt(duration time.Duration, amount int) {
	a(duration, amount)
}
```

这样一来，用你这个库的人只用一个函数就能实现你的接口。他们可以用[类型转换（Type Conversion）](https://go.dev/tour/basics/13)把自己的函数转成 `BlindAlerterFunc`，然后当作 BlindAlerter 来用（因为 `BlindAlerterFunc` 实现了 `BlindAlerter`）。

```go
game := poker.NewTexasHoldem(poker.BlindAlerterFunc(poker.StdOutAlerter), store)
```

往大了说，在 Go 里你可以给*类型*添加方法，而不只是结构体。这个特性非常强大，你可以用它以更顺手的方式实现接口。

想想看：你不仅可以基于函数定义类型，还可以围绕其他类型定义类型，从而给它们添加方法。

```go
type Blog map[string]string

func (b Blog) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, b[r.URL.Path])
}
```

这里我们创建了一个 HTTP handler，实现了一个非常简单的“博客”：它拿 URL 路径当键，去 map 里查对应的文章。
