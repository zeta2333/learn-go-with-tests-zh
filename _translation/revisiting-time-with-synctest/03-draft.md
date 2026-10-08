# 用 `testing/synctest` 重访时间

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/synctest)**

在[Time 一章](time.md)里，我们用 `time.AfterFunc` 让扑克 CLI 学会了调度"盲注上涨"提醒。但要测它却不太容易：`time.AfterFunc` 要等一段真实时长流逝之后，才会在自己的 goroutine 里运行回调，而 Go 里又没法比较函数，所以我们很难看清究竟调度了些什么。

我们的解法是一个熟面孔：依赖注入。定义一个 `BlindAlerter` 接口，测试里再把真正的实现换成一个 spy——它只负责记下"别人让它调度什么"，大致长这样：

```go
type BlindAlerter interface {
	ScheduleAlertAt(duration time.Duration, amount int)
}

type SpyBlindAlerter struct {
	Alerts []struct {
		At     time.Duration
		Amount int
	}
}

func (s *SpyBlindAlerter) ScheduleAlertAt(at time.Duration, amount int) {
	s.Alerts = append(s.Alerts, struct {
		At     time.Duration
		Amount int
	}{at, amount})
}
```

这是个好设计，它撑起来的测试又快又稳。但凑近看看，这些测试实际覆盖的是什么？它们断言的无非是"`ScheduleAlertAt` 被以 `10 * time.Minute` 和 `200` 调用过"。它们从没让*真正的* alerter 跑起来。真正调用 `time.AfterFunc`、真正往外打印的那段代码——真正可能藏 bug 的部分——从未被任何测试执行过。

这不是疏忽，是权衡。要认真测试一个基于 `time.AfterFunc` 的真 alerter，要么让测试干等真实的几分钟，要么把时长缩到毫秒级，再祈祷跑测试的机器忙得没那么厉害、还跟得上。两条路都不讨人喜欢。所以一直以来，我们的选择是：不测。

到了 Go 1.25，有了第三个选择：[`testing/synctest`](https://pkg.go.dev/testing/synctest)。它让我们可以在一个对时间拥有完全控制权的测试里，运行使用 `time.Sleep`、`time.AfterFunc` 之类工具的真实代码、原封不动的代码：不用干等，不会时灵时不灵，也不必缩小时长然后碰运气。

本章我们就从零把这个真 alerter 写出来，再用 `synctest` 测它。不过得先吃点苦头——先看清楚它究竟把我们从什么坑里捞出来，这甜头才算挣来的。

## 关于 `testing/synctest`，知道这些就够了

`testing/synctest` 会在一个隔离的**气泡（bubble）**里运行一个函数。在这个气泡里：

* `time` 包使用的是虚拟时钟（fake clock）。它从 2000 年 1 月 1 日 UTC 午夜开始，只会向前走。
* 只有当气泡里的每一个 goroutine 都处于**持久阻塞（durably blocked）**状态——也就是那种只有同一气泡里的另一个 goroutine 才能解除的阻塞——虚拟时间才会前进。`time.Sleep`、对气泡内创建的 channel 的阻塞接收、`sync.Cond.Wait`、`sync.WaitGroup.Wait` 都算数；锁 `sync.Mutex` 不算，因为互斥锁通常只会被短暂持有。
* `synctest.Test(t, f)` 在一个新气泡里运行 `f`，直到里面派生的所有 goroutine 都退出才返回。如果气泡最终陷入无法推进的持久阻塞，它会以死锁（deadlock）为由让测试失败，而不是永远挂着。
* `synctest.Wait()` 会阻塞调用它的 goroutine，直到气泡里所有*其他* goroutine 都持久阻塞，然后才返回。想让后台工作尘埃落定再做断言，用的就是它。

起步，这些就够了。路上我们还会碰到几处更锋利的棱角。

## 先写测试

在请出 `synctest` 之前，先从最直白的做法开始：一个 `BlindAlerter`，给它一段时长和一个金额，它等够这段时长，然后把一条消息写到某个地方——用真实时间来测。

```go
package poker

import (
	"bytes"
	"testing"
	"time"
)

func TestStdOutAlerter(t *testing.T) {
	out := &bytes.Buffer{}
	alerter := StdOutAlerter(out)

	alerter.ScheduleAlertAt(5*time.Second, 100)

	time.Sleep(6 * time.Second)

	want := "Blind is now 100"
	if out.String() != want {
		t.Errorf("got %q, want %q", out.String(), want)
	}
}
```

我们睡得比安排的提醒稍久一点（是 6 秒，不是 5 秒），好让 `time.AfterFunc` 派生出来的那只 goroutine 在我们检查之前来得及真正跑一跑。

## 试着运行测试

生产代码还一行没写，编译过不去：

```
./blind_alerter_test.go:11:13: undefined: StdOutAlerter
```

## 写足够的代码让测试通过

```go
package poker

import (
	"fmt"
	"io"
	"time"
)

// BlindAlerter 为盲注金额安排提醒。
type BlindAlerter interface {
	ScheduleAlertAt(duration time.Duration, amount int)
}

// BlindAlerterFunc 让你用一个函数就能实现 BlindAlerter。
type BlindAlerterFunc func(duration time.Duration, amount int)

// ScheduleAlertAt 是 BlindAlerterFunc 对 BlindAlerter 的实现。
func (a BlindAlerterFunc) ScheduleAlertAt(duration time.Duration, amount int) {
	a(duration, amount)
}

// StdOutAlerter 返回一个 BlindAlerterFunc，它负责调度提醒并把消息打印到 out。
func StdOutAlerter(out io.Writer) BlindAlerterFunc {
	return func(duration time.Duration, amount int) {
		time.AfterFunc(duration, func() {
			fmt.Fprintf(out, "Blind is now %d", amount)
		})
	}
}
```

运行：

```
=== RUN   TestStdOutAlerter
--- PASS: TestStdOutAlerter (6.00s)
PASS
ok  	github.com/quii/learn-go-with-tests/synctest/v1	6.191s
```

测试过了。但为了一个提醒，它花了实打实的 6 秒。真实的游戏要调度 11 个提醒，相邻最远的两个能隔上 1 小时 40 分钟。没人愿意每跑一次测试都干等这个，所以实际上，这个测试要么被跳过，要么用不真实的小时长来写，跟真实场景只有点形似。这正是 `synctest` 存在要解决的问题。

## 初识 synctest

我们把同一个测试包进气泡里，看看要是对"虚拟时钟"能耐的期望乐观过了头，会发生什么：

```go
func TestStdOutAlerter(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		out := &bytes.Buffer{}
		alerter := StdOutAlerter(out)

		alerter.ScheduleAlertAt(5*time.Second, 100)

		want := "Blind is now 100"
		if out.String() != want {
			t.Errorf("got %q, want %q", out.String(), want)
		}
	})
}
```

我们把 sleep 整个删掉了：虚拟时钟现在总该替我们把这件事办了吧？并没有：

```
=== RUN   TestStdOutAlerter
    blind_alerter_test.go:19: got "", want "Blind is now 100"
--- FAIL: TestStdOutAlerter (0.00s)
FAIL
```

气泡的虚拟时钟不会自己定着表往前走，只有气泡里有东西持久阻塞、在等它前进时，它才走。要等什么，仍然得我们自己说；只是再也不必用真实的秒数来买单了。把 sleep 加回来：

```go
func TestStdOutAlerter(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		out := &bytes.Buffer{}
		alerter := StdOutAlerter(out)

		alerter.ScheduleAlertAt(5*time.Second, 100)

		time.Sleep(6 * time.Second)

		want := "Blind is now 100"
		if out.String() != want {
			t.Errorf("got %q, want %q", out.String(), want)
		}
	})
}
```

```
=== RUN   TestStdOutAlerter
--- PASS: TestStdOutAlerter (0.00s)
PASS
ok  	github.com/quii/learn-go-with-tests/synctest/v2	0.133s
```

通过了，而且是瞬间：气泡里的 `time.Sleep(6 * time.Second)` 不花一点真实时间。看上去完事了。习惯使然，我们再用 `-race` 复核一下它到底站不站得住：

```
go test -race ./...
```

```
==================
WARNING: DATA RACE
Read at 0x00c00010e630 by goroutine 9:
  bytes.(*Buffer).String()
      /usr/local/go/src/bytes/buffer.go:77 +0x174
  github.com/quii/learn-go-with-tests/synctest/v2.TestStdOutAlerter.func1()
      blind_alerter_test.go:20 +0x15c
  testing.tRunner()
      /usr/local/go/src/testing/testing.go:1934 +0x164

Previous write at 0x00c00010e630 by goroutine 11:
  bytes.(*Buffer).grow()
      /usr/local/go/src/bytes/buffer.go:143 +0x354
  bytes.(*Buffer).Write()
      /usr/local/go/src/bytes/buffer.go:185 +0xb4
  fmt.Fprintf()
      /usr/local/go/src/fmt/print.go:225 +0x94
  github.com/quii/learn-go-with-tests/synctest/v2.TestStdOutAlerter.func1.BlindAlerterFunc.ScheduleAlertAt.TestStdOutAlerter.func1.StdOutAlerter.1.2()
      blind_alerter.go:26 +0x6c

Goroutine 11 (finished) created at:
  time.goFunc()
      /usr/local/go/src/time/sleep.go:215 +0x40
==================
--- FAIL: TestStdOutAlerter (0.00s)
    testing.go:1617: race detected during execution of test
FAIL
```

哎哟。注意"Goroutine 11 (finished)"：写确实发生在读之前，我们每跑一次都是如此。从功能上讲，这个测试的断言永远不可能真的失败。但竞态检测器问的不是"这一次出了事吗"，而是"有没有什么*保证*它出不了事"。我们这个 goroutine 上的 `time.Sleep`，跟 `time.AfterFunc` 回调所在的 goroutine，不过是两只各自独立调度的 goroutine。"我睡了一会儿"这句话，担保不了另一只 goroutine 已经碰完共享内存——睡得再慷慨也不行。睡久一点解决不了问题，多久都一样；它只是让测试在 `-race` 之外失败得不那么频繁罢了。

值得在这儿停一秒细品：这场竞态从一开始就潜伏在我们最早的、朴素的真实时间版本里，那个带着货真价实的 `time.Sleep` 的版本。我们只是从没想过要查：谁会对一个跑一次就要 6 秒的测试，一遍又一遍地跑 `-race` 呢？

## 先写测试

我们需要的是一个真正的同步点：不是让写*大概*先发生，而是实打实地确立它已经先发生。这正是 `synctest.Wait()` 的用武之地：

```go
func TestStdOutAlerter(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		out := &bytes.Buffer{}
		alerter := StdOutAlerter(out)

		alerter.ScheduleAlertAt(5*time.Second, 100)

		time.Sleep(6 * time.Second)
		synctest.Wait()

		want := "Blind is now 100"
		if out.String() != want {
			t.Errorf("got %q, want %q", out.String(), want)
		}
	})
}
```

## 重构

生产代码没什么要改的，但我们要确认这个版本在 `-race` 下反复跑都站得住：

```
ok  	github.com/quii/learn-go-with-tests/synctest/v3	1.153s
ok  	github.com/quii/learn-go-with-tests/synctest/v3	1.143s
ok  	github.com/quii/learn-go-with-tests/synctest/v3	1.148s
ok  	github.com/quii/learn-go-with-tests/synctest/v3	1.147s
ok  	github.com/quii/learn-go-with-tests/synctest/v3	1.143s
```

每一次都干干净净。非常好。

## 先写测试

还有一件事值得一测：什么都不该发生。用真实时间，这意味着猜一个睡眠时长——得长到让人放心，又不能长到把测试拖垮。synctest 不用猜：

```go
func TestStdOutAlerter(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		out := &bytes.Buffer{}
		alerter := StdOutAlerter(out)

		alerter.ScheduleAlertAt(5*time.Second, 100)

		synctest.Wait()
		if out.String() != "" {
			t.Errorf("did not expect anything to be printed yet, got %q", out.String())
		}

		time.Sleep(5 * time.Second)
		synctest.Wait()

		want := "Blind is now 100"
		if out.String() != want {
			t.Errorf("got %q, want %q", out.String(), want)
		}
	})
}
```

我们调度提醒的那一刻，气泡里没有别的任何东西在干活，所以 `Wait()` 应该立刻返回：眼下还没有什么可*等*的，`out` 应该还是空的。运行：

```
=== RUN   TestStdOutAlerter
--- PASS: TestStdOutAlerter (0.00s)
PASS
```

过了。再用 `-race` 验一下——现在我们知道该验了：

```
==================
WARNING: DATA RACE
Write at 0x00c00011c630 by goroutine 11:
  bytes.(*Buffer).grow()
      /usr/local/go/src/bytes/buffer.go:143 +0x354
  bytes.(*Buffer).Write()
      /usr/local/go/src/bytes/buffer.go:185 +0xb4
  fmt.Fprintf()
      /usr/local/go/src/fmt/print.go:225 +0x94
  github.com/quii/learn-go-with-tests/synctest/v4.TestStdOutAlerter.func1.BlindAlerterFunc.ScheduleAlertAt.TestStdOutAlerter.func1.StdOutAlerter.1.2()
      blind_alerter.go:26 +0x6c

Previous read at 0x00c00011c630 by goroutine 9:
  bytes.(*Buffer).String()
      /usr/local/go/src/bytes/buffer.go:77 +0x164
  github.com/quii/learn-go-with-tests/synctest/v4.TestStdOutAlerter.func1()
      blind_alerter_test.go:18 +0x14c
  testing.tRunner()
      /usr/local/go/src/testing/testing.go:1934 +0x164

Goroutine 11 (running) created at:
  time.goFunc()
      /usr/local/go/src/time/sleep.go:215 +0x40
==================
--- FAIL: TestStdOutAlerter (0.00s)
    testing.go:1617: race detected during execution of test
FAIL
```

竞态在第 18 行：正是我们的第一处检查——那个我们满怀信心的检查，理由是"还没有什么可等的"。每一次运行，稳稳复现。

问题在于，单凭 `Wait()` 自己，没有任何东西限定它愿意让虚拟时钟走多远。那一刻气泡里没有别的 goroutine，也没有什么*即将到来*的截止时间可供我们等待。剩下的只有那个 5 秒提醒的定时器，躺在运行时的定时器堆里。于是运行时做了它唯一能做的有用的事：把定时器触发，好让一切有所进展——派生 goroutine 11 去跑我们的回调，而此时 `Wait()` 还在盘算要不要返回。goroutine 11 是实打实地跟我们的检查并发运行，而不是赶在它前面。有时那个写先完成，有时不是。我们俩都在碰的 `bytes.Buffer` 没有锁，所以无论哪种时序，都没有什么能兜底。

这本可以按修任何数据竞争的老办法来修：给 `out` 套一把 `sync.Mutex`，或者更轻量一点，用上 `sync/atomic` 的 `atomic.Pointer[T]`。但看看 `StdOutAlerter` 实际被要求做的事：既决定消息内容，*又*执行打印这个副作用。安排扑克盲注提醒这件事，按理说完全不需要知道 `io.Writer` 的存在；那是调用方的事。本书反复回到的正是这种张力：[如果你的测试让你痛苦，请倾听这个信号，思考你的代码设计](http-handlers-revisited.md)。让 alerter 到点只管把消息生产出来，拿它怎么办，交给调用方决定。

## 重构

跨越 goroutine 边界，正是 channel 的本行。Go 谚语说得好：[不要靠共享内存来通信，而要靠通信来共享内存](https://go.dev/blog/codelab-share)。我们的 alerter 不必往共享的 `out` 里写，可以把写好的消息顺着 channel 发出去：

```go
func NewAlerter() (BlindAlerterFunc, <-chan string) {
	alerts := make(chan string)

	scheduleAlertAt := func(duration time.Duration, amount int) {
		time.AfterFunc(duration, func() {
			alerts <- fmt.Sprintf("Blind is now %d", amount)
		})
	}

	return scheduleAlertAt, alerts
}
```

`BlindAlerter` 和 `BlindAlerterFunc` 原封不动。只有 `StdOutAlerter` 没了——很能说明问题的是，它早就跟 stdout 没什么关系了——取而代之的 `NewAlerter` 会把 alerter 和一个可供接收的 channel 一并交回来。谁想把这些提醒打印出来（比如 `main`），谁就去 range 那个 channel 自行打印；这不再是这个包的事了。

测试也跟着变简单了：

```go
func TestNewAlerter(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		alerter, alerts := NewAlerter()

		alerter.ScheduleAlertAt(5*time.Second, 100)

		select {
		case got := <-alerts:
			t.Fatalf("did not expect an alert yet, got %q", got)
		default:
		}

		got := <-alerts
		want := "Blind is now 100"
		if got != want {
			t.Errorf("got %q, want %q", got, want)
		}
	})
}
```

注意一下消失了什么：哪儿都没有 `synctest.Wait()`，没有守护共享值的自定义类型，也根本没有 `time.Sleep`。这些统统不再需要。

带 `default` 分支的 `select`，[Select 一章](select.md)里讲过，从不阻塞：要么取走一个就绪的分支，要么立刻落到 `default`。此刻虚拟时间还停在零点，离提醒还整整差 5（虚拟）秒，根本无物可同步：当然什么都没到。而 `got := <-alerts` 也不需要谁推一把：它就是个普通的阻塞接收，于是气泡恰好做了它被设计出来要做的事——既然气泡里大家唯一在等的就是那个定时器，虚拟时间就直接跳到它触发的时刻，唤醒 `time.AfterFunc` 的 goroutine，把我们的接收解开。

用 `-race` 反复跑它。它一直是绿的：已经没有共享内存可供竞争了。

把它跟前一章的 `SpyBlindAlerter` 路子比一比。干另一份活儿时，spy 仍然是一把好手：它检查的是*调度了什么*（给定玩家人数，各金额是不是在正确的偏移处被调度？），完全不关心真实时序（当你测的是算术而非计时时，这很有用）。`synctest` 没有取代这个需求；它补上的是纯粹的"我被要求做什么"式 spy 永远会留下的覆盖缺口：调度机制本身到底灵不灵？

## 总结

### 本章所学

* `synctest.Test`，以及气泡的想法：一个带着隔离虚拟时钟的小世界，时钟只在有东西持久阻塞时才前进，自己不会走。
* "持久阻塞"：虚拟时间得以前进的条件，以及 `sync.Mutex` 为何被刻意排除在外（channel 接收却算数）。
* 睡"够久"不等于同步：哪怕一个慷慨的、实践中从来没错的睡眠，只要没有什么强制保证先后次序，它就仍然是一场真实的数据竞争。
* `synctest.Wait()` 能为单次检查解决这一问题，但如果气泡里没有别的东西替它兜底，调用它就可能让虚拟时钟跑得比你想的更远——测"什么都不该发生"时我们正是这样栽的。
* 测试不光揪出 bug，还暴露了设计问题；我们的对策是改设计，而不是顺手抓把锁。

### 要留心的坑

* 如果气泡的根函数返回时，气泡里还有 goroutine 处于持久阻塞，`synctest.Test` 会以死锁为由让测试失败，而不是一直挂着；务必确保后台 goroutine 真正跑完。
* channel、timer、ticker 都绑在创建它们的气泡上；拿到气泡外面用会 panic。
* 真实的网络和文件 I/O 不属于持久阻塞，没法直接靠 `synctest` 的虚拟时钟驱动；需要内存里的替身时，可以求诸 `net.Pipe` 之类的工具。
* `time.AfterFunc` 的回调在自己的 goroutine 里运行，享受不到 channel 提供的任何同步保证。如果它必须直接碰共享状态，这个状态就得自己上锁，跟其他并发代码一样。

### 延伸材料

* [Go blog: Testing concurrent code with testing/synctest](https://go.dev/blog/synctest)
* [`testing/synctest` 包文档](https://pkg.go.dev/testing/synctest)
* [Go 1.25 发行说明](https://go.dev/doc/go1.25)

### 关于本章的写作方式

这是本书第一章借助 AI（Claude）写成的章节。我想开诚布公地承认这一点，也想说清楚这里的"借助"到底是什么意思——它可不是"描述一下章节，就收获一个章节"。

这套流程跟本书一路传授的 TDD 循环像极了：去钻研真实的 `testing/synctest` 文档和源码，而不是凭感觉猜；在写下正文第一个字之前，先拿用完即弃的小程序（spike）验证各种说法；把文档里的每一条论断，都当作"要靠真实跑一遍 `go test -race` 来验证"的东西，而不是照单全收。本章的好几个坑——`Wait()` 与竞态检测器的相互作用首当其冲——之所以能写进这里，是因为测试真的以意料之外的方式失败过，反复实跑了好几轮，而且必须把原因挖个水落石出，才谈得上决定写什么。

设计本身中途也变了样。初稿让 `StdOutAlerter` 直接往一个 `io.Writer` 里写——每当测试开始折磨人时，本书一贯抵制的正是这种做法：[如果你的测试让你痛苦，请倾听这个信号，思考你的代码设计](http-handlers-revisited.md)。于是我们照做了，最终得到上面这个基于 channel 的版本，本章也因此更短、更好。

这里的每一样东西都经过审阅和编辑，而且不止一次被打回重写：语气听着不对时；某一节膨胀得超出了实际教学所需时；明明展示一次真实的测试失败更有说服力、解释却往术语堆里钻时。如果读到这里还有什么别扭的地方，那是我的问题，不是工具的。
