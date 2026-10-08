# 数学

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/math)**

现代计算机算起大数来快如闪电，可普通开发者的日常工作里几乎用不上什么数学。今天可不一样！我们要用数学解决一个*真实*问题。还不是那种无聊的数学——我们要用上三角函数、向量，还有一堆你发过誓"高中毕业就再也不碰"的玩意儿。

## 问题

你想画一个时钟的 SVG。不是数字时钟——不，那太容易了——要*模拟*时钟，带指针的那种。不求花哨，只要一个像样的函数：传入 `time` 包的 `Time`，吐出一幅时钟的 SVG，时针、分针、秒针全都指在正确的方向上。能有多难？

首先我们得有一幅 SVG 时钟来练手。SVG 是一种特别适合程序处理的图片格式：它就是用 XML 描述的一系列图形。比如这个时钟：

![一幅时钟的 SVG](assets/example_clock.svg)

是这样描述的：

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg"
     width="300"
     height="300"
     viewBox="0 0 300 300"
     version="2.0">

  <!-- bezel -->
  <circle cx="150" cy="150" r="100" style="fill:#fff;stroke:#000;stroke-width:5px;"/>

  <!-- hour hand -->
  <line x1="150" y1="150" x2="114.150000" y2="132.260000"
        style="fill:none;stroke:#000;stroke-width:7px;"/>

  <!-- minute hand -->
  <line x1="150" y1="150" x2="101.290000" y2="99.730000"
        style="fill:none;stroke:#000;stroke-width:7px;"/>

  <!-- second hand -->
  <line x1="150" y1="150" x2="77.190000" y2="202.900000"
        style="fill:none;stroke:#f00;stroke-width:3px;"/>
</svg>
```

它就是一个圆加上三条线段，每条线段都从圆心 (x=150, y=150) 出发，延伸到离圆心一段距离处。

我们要做的，就是想办法重建上面这幅图，但改变这些线段，让它们按照给定时间指向正确的方向。

## 验收测试

在一头扎进去之前，先想想验收测试（acceptance test）。

等等，你还不知道什么是验收测试。来，让我试着解释一下。

先问你一句：怎样才算赢了？我们怎么知道自己干完了活？TDD 提供了一个判断"完工"的好办法：测试通过的时候。有时候——其实几乎任何时候——写一个能告诉你"整个可用功能都写完了"的测试是件美事。它不只是告诉你某个函数在按你预期的方式工作，而是告诉你，你想做的整件事——整个"功能"——已经完成。

这类测试有时叫"验收测试"（acceptance test），有时叫"功能测试"（feature test）。思路是：先写一个非常高层级的测试来描述你想达成什么——比如"用户在网站上点一个按钮，就能看到自己捉到的全部宝可梦的完整列表"。有了这个测试之后，再写更多测试——单元测试——一步步搭出一个能通过验收测试的可运行系统。拿我们的例子来说，这些测试可能涉及渲染一个带按钮的网页、测试 web 服务器上的路由处理器、执行数据库查询等等。这些东西全都会用 TDD 一件件开发出来，而且全都在为最初那条验收测试的通过添砖加瓦。

类似 Nat Pryce 和 Steve Freeman 的这幅*经典*图示：

![TDD 由外向内的反馈循环](assets/TDD-outside-in.jpg)

不管怎样，来试着写下那条验收测试吧——它会告诉我们什么时候完工。

我们已经有了一幅示例时钟，那就想想哪些参数是关键的。

```
<line x1="150" y1="150" x2="114.150000" y2="132.260000"
        style="fill:none;stroke:#000;stroke-width:7px;"/>
```

时钟的中心（这条线的 `x1` 和 `y1` 属性）对每根指针来说都一样。每根指针需要变化的数字——也就是构建 SVG 时要传入的参数——是 `x2` 和 `y2` 属性。每根指针我们都需要一个 X 和一个 Y。

我*可以*考虑更多参数——表盘圆的半径、SVG 的尺寸、指针的颜色、形状等等……但更好的做法是先用一个简单、具体的方案解决一个简单、具体的问题，然后再逐步加参数，把它泛化。

那我们就定成这样

* 每个时钟的圆心都在 (150, 150)
* 时针长 50
* 分针长 80
* 秒针长 90。

关于 SVG 有一点要注意：它的原点——也就是 (0,0) 点——在*左上角*，而不是我们习惯的*左下角*。后面计算该往线段里填什么数字时，这一点非常重要。

最后，我暂时不定*怎么*构建 SVG——可以用 [`text/template`](https://golang.org/pkg/text/template/) 包的模板，也可以直接把字节写进 `bytes.Buffer` 或某个 writer。但我们知道肯定需要那些数字，所以先专注测试"生成这些数字"的东西。

### 先写测试

我的第一个测试长这样：

```go
package clockface_test

import (
	"projectpath/clockface"
	"testing"
	"time"
)

func TestSecondHandAtMidnight(t *testing.T) {
	tm := time.Date(1337, time.January, 1, 0, 0, 0, 0, time.UTC)

	want := clockface.Point{X: 150, Y: 150 - 90}
	got := clockface.SecondHand(tm)

	if got != want {
		t.Errorf("Got %v, wanted %v", got, want)
	}
}
```

这里的 `projectpath` 是个占位符——把它换成你自己模块的路径再加上 `/clockface`（比如你的 `go.mod` 写的是 `module example.com/learning-go`，这个 import 就应写成 `"example.com/learning-go/clockface"`）。这样做之所以可行，是因为我们把 `clockface_test.go` 放进了一个名为 `clockface` 的独立目录，与 `clockface.go`（下一节创建）并排。目录名与它所含的包名一致，Go 解析这个 import 时就不需要别名。同一目录下的 `package clockface_test` 则是 Go 允许的一个特例：外部测试包可以与 `package clockface` 的文件共处一个文件夹。

还记得 SVG 的坐标是从左上角开始画的吗？午夜时分，秒针在 X 轴上应该没有离开圆心——还是 150；Y 轴上则是从圆心"向上"伸出指针的长度：150 减 90。

### 试着运行测试

这会暴露出预期中的失败：函数和类型还没定义：

```
--- FAIL: TestSecondHandAtMidnight (0.00s)
./clockface_test.go:13:10: undefined: clockface.Point
./clockface_test.go:14:9: undefined: clockface.SecondHand
```

也就是说，需要一个 `Point` 表示秒针针尖该去的位置，再要一个函数把它算出来。

### 写最少的代码让测试能运行，并检查失败的测试输出

先把那些类型实现出来，让代码能编译：

```go
package clockface

import "time"

// Point 表示一个二维笛卡尔坐标
type Point struct {
	X float64
	Y float64
}

// SecondHand 是模拟时钟在时间 `t` 时秒针的单位向量，
// 以一个 Point 表示。
func SecondHand(t time.Time) Point {
	return Point{}
}
```

现在我们得到：

```
--- FAIL: TestSecondHandAtMidnight (0.00s)
    clockface_test.go:17: Got {0 0}, wanted {150 60}
FAIL
exit status 1
FAIL	learn-go-with-tests/math/clockface	0.006s
```

### 写足够的代码让测试通过

拿到预期中的失败后，就可以填上 `SecondHand` 的返回值了：

```go
// SecondHand 是模拟时钟在时间 `t` 时秒针的单位向量，
// 以一个 Point 表示。
func SecondHand(t time.Time) Point {
	return Point{150, 60}
}
```

且看，测试通过了。

```
PASS
ok  	    clockface	0.006s
```

### 重构

还没什么可重构的——代码都没几行！

### 为新需求重复以上步骤

我们大概得干点正事了，总不能每个时间都返回一个显示午夜的钟……

### 先写测试

```go
func TestSecondHandAt30Seconds(t *testing.T) {
	tm := time.Date(1337, time.January, 1, 0, 0, 30, 0, time.UTC)

	want := clockface.Point{X: 150, Y: 150 + 90}
	got := clockface.SecondHand(tm)

	if got != want {
		t.Errorf("Got %v, wanted %v", got, want)
	}
}
```

同样的思路，只是这次秒针指向*下方*，所以要把长度*加*到 Y 轴上。

这能编译过……可怎么让它通过呢？

## 思考时间

这个问题该怎么解决？

每一分钟，秒针都会经历同样的 60 个状态，指向 60 个不同的方向。0 秒时指向表盘顶部，30 秒时指向表盘底部。够简单。

那么，假如我想知道 37 秒时秒针指向哪个方向，我想要的就是 12 点方向与"绕圆 37/60 处"之间的夹角。用度数算是 `(360 / 60 ) * 37 = 222`，不过更省事的记法是：它就是一整圈的 `37/60`。

但角度只是故事的一半；我们还得知道秒针针尖所指的 X、Y 坐标。这可怎么算？

## 数学

想象围绕原点——坐标 `0, 0`——画一个半径为 1 的圆。

![单位圆示意图](assets/unit_circle.png)

它叫"单位圆"（unit circle），因为……呃，半径恰好是 1 个单位！

圆周是由网格上的点组成的——也就是更多的坐标。这些坐标的 x、y 分量构成一个个三角形，斜边恒为 1（也就是圆的半径）。

![单位圆示意图：在圆周上取一个点](assets/unit_circle_coords.png)

有了三角函数，只要知道每个三角形与原点连线所成的角度，我们就能算出它 X、Y 两边的长度。X 坐标是 cos(a)，Y 坐标是 sin(a)，其中 a 是这条线与（正）x 轴的夹角。

![单位圆示意图：射线的 x、y 分量分别为 cos(a) 与 sin(a)，a 是射线与 x 轴的夹角](assets/unit_circle_params-1.png)

（不信的话，[自己去翻维基百科……](https://en.wikipedia.org/wiki/Sine#Unit_circle_definition)）

最后还有个转折——因为我们要从 12 点方向而不是从 X 轴（3 点方向）量角度，所以得把轴调换一下：现在 x = sin(a)，y = cos(a)。

![单位圆示意图：从 y 轴起按角度定义的射线](assets/unit_circle_12_oclock.png)

至此我们知道了怎么求秒针的角度（每秒圆的 1/60）和 X、Y 坐标。`sin` 和 `cos` 两个函数我们都需要。

## `math` 包

好消息是 Go 的 `math` 包两个都有，只是有个小麻烦得先弄明白；看看 [`math.Cos`](https://golang.org/pkg/math/#Cos) 的文档描述：

> Cos 返回弧度参数 x 的余弦。

它要求角度用弧度（radian）表示。那弧度是什么？圆的一整圈不再由 360 度组成，而是定义为 2π 弧度。这么做有很好的理由，这里就不展开了。

读也读了、学也学了、想也想了，现在可以写下一个测试了。

### 先写测试

这堆数学又难又绕。我没把握说自己真的搞懂了——那就写个测试吧！我们不必一口气解决整个问题——先从"求出某个特定时刻秒针的正确弧度"下手。

在弄这些测试的时候，我会把之前写的验收测试*注释掉*——我可不想在让这个测试通过的路上被那条测试分心。

### 回顾一下包

眼下，我们的验收测试在 `clockface_test` 包里。测试可以放在 `clockface` 包之外——只要文件名以 `_test.go` 结尾，就能被运行。

弧度的测试我打算写在 `clockface` 包*内部*；这些函数可能永远不会导出，等我搞清楚状况后可能还会删掉（或挪走）。我会把验收测试文件重命名为 `clockface_acceptance_test.go`，这样就能新建一个名为 `clockface_test` 的*新*文件来测秒针的弧度。

```go
package clockface

import (
	"math"
	"testing"
	"time"
)

func TestSecondsInRadians(t *testing.T) {
	thirtySeconds := time.Date(312, time.October, 28, 0, 0, 30, 0, time.UTC)
	want := math.Pi
	got := secondsInRadians(thirtySeconds)

	if want != got {
		t.Fatalf("Wanted %v radians, but got %v", want, got)
	}
}
```

这里测的是：一分钟过 30 秒，秒针应该正好转到半圈。这也是我们第一次用上 `math` 包！既然一整圈是 2π 弧度，那半圈自然就是 π 弧度。`math.Pi` 为我们提供了 π 的值。

### 试着运行测试

```
./clockface_test.go:12:9: undefined: secondsInRadians
```

### 写最少的代码让测试能运行，并检查失败的测试输出

```go
func secondsInRadians(t time.Time) float64 {
	return 0
}
```

```
clockface_test.go:15: Wanted 3.141592653589793 radians, but got 0
```

### 写足够的代码让测试通过

```go
func secondsInRadians(t time.Time) float64 {
	return math.Pi
}
```

```
PASS
ok  	clockface	0.011s
```

### 重构

还没什么需要重构的

### 为新需求重复以上步骤

现在可以扩展测试，覆盖更多场景了。我打算往前跳一点，直接展示几段已经重构过的测试代码——我是怎么走到这一步的，应该足够一目了然。

```go
func TestSecondsInRadians(t *testing.T) {
	cases := []struct {
		time  time.Time
		angle float64
	}{
		{simpleTime(0, 0, 30), math.Pi},
		{simpleTime(0, 0, 0), 0},
		{simpleTime(0, 0, 45), (math.Pi / 2) * 3},
		{simpleTime(0, 0, 7), (math.Pi / 30) * 7},
	}

	for _, c := range cases {
		t.Run(testName(c.time), func(t *testing.T) {
			got := secondsInRadians(c.time)
			if got != c.angle {
				t.Fatalf("Wanted %v radians, but got %v", c.angle, got)
			}
		})
	}
}
```

我加了几个辅助函数，让这个表驱动测试写起来没那么枯燥。`testName` 把时间转成电子表格式（HH:MM:SS），`simpleTime` 只用我们真正关心的部分（还是时、分、秒）构造一个 `time.Time`。它们长这样：

```go
func simpleTime(hours, minutes, seconds int) time.Time {
	return time.Date(312, time.October, 28, hours, minutes, seconds, 0, time.UTC)
}

func testName(t time.Time) string {
	return t.Format("15:04:05")
}
```

这两个函数能让这些测试（以及将来的测试）更好写、也更好维护。

于是我们得到了一些不错的测试输出：

```
clockface_test.go:24: Wanted 0 radians, but got 3.141592653589793

clockface_test.go:24: Wanted 4.71238898038469 radians, but got 3.141592653589793
```

是时候把上面聊的那堆数学落实成代码了：

```go
func secondsInRadians(t time.Time) float64 {
	return float64(t.Second()) * (math.Pi / 30)
}
```

一秒是 (2π / 60) 弧度……约掉 2，得 π/30 弧度。乘上秒数（转成 `float64`），所有测试应该都能过了……

```
clockface_test.go:24: Wanted 3.141592653589793 radians, but got 3.1415926535897936
```

等等，什么情况？

### 浮点数真讨厌

浮点运算的[不精确是出了名的](https://0.30000000000000004.com/)。计算机真正能精确处理的只有整数，某种程度上还包括有理数。小数则开始变得不精确，尤其是像我们在 `secondsInRadians` 函数里这样来回乘除的时候。把 `math.Pi` 除以 30 再乘回 30，最后得到的竟是*一个不再等于 `math.Pi` 的数*。

有两条路可走：

1. 忍了
2. 重构等式，进而重构函数

选 (1) 看似不那么吸引人，但要让浮点数相等判断成立，它常常是唯一的办法。说真的，对画表盘而言，差那么一丝丝根本无所谓，所以我们完全可以写一个"差不多就算相等"的角度比较函数。不过有个简单的办法能把精度找回来：重排等式，让我们不必先除下去再乘上来，全程只做除法。

所以，不写

```
numberOfSeconds * π / 30
```

而写

```
π / (30 / numberOfSeconds)
```

两者等价。

用 Go 写就是：

```go
func secondsInRadians(t time.Time) float64 {
	return (math.Pi / (30 / (float64(t.Second()))))
}
```

然后就通过了。

```
PASS
ok      clockface     0.005s
```

整个代码[大致是这个样子](https://github.com/quii/learn-go-with-tests/tree/main/math/v3/clockface)。

### 关于除以零

计算机通常不喜欢除以零，因为无穷大这玩意儿有点怪。

在 Go 里，如果你显式地除以零，会得到一个编译错误。

```go
package main

import (
	"fmt"
)

func main() {
	fmt.Println(10.0 / 0.0) // 无法通过编译
}
```

当然，编译器不可能总能预测到你会除以零，比如除数来自我们的 `t.Second()` 时。

试试这个

```go
func main() {
	fmt.Println(10.0 / zero())
}

func zero() float64 {
	return 0.0
}
```

它会打印 `+Inf`（无穷大）。除以 +Inf 似乎会得到零，用下面的代码可以验证：

```go
package main

import (
	"fmt"
	"math"
)

func main() {
	fmt.Println(secondsinradians())
}

func zero() float64 {
	return 0.0
}

func secondsinradians() float64 {
	return (math.Pi / (30 / (float64(zero()))))
}
```

### 为新需求重复以上步骤

到这里第一部分搞定了——我们已经知道秒针指向的弧度了。现在来算坐标。

还是老规矩，尽量从简，只在*单位圆*上工作——半径为 1 的那个圆。这意味着所有指针的长度都是 1，不过好的一面是，这些数学就好消化多了。

### 先写测试

```go
func TestSecondHandPoint(t *testing.T) {
	cases := []struct {
		time  time.Time
		point Point
	}{
		{simpleTime(0, 0, 30), Point{0, -1}},
	}

	for _, c := range cases {
		t.Run(testName(c.time), func(t *testing.T) {
			got := secondHandPoint(c.time)
			if got != c.point {
				t.Fatalf("Wanted %v Point, but got %v", c.point, got)
			}
		})
	}
}
```

### 试着运行测试

```
./clockface_test.go:40:11: undefined: secondHandPoint
```

### 写最少的代码让测试能运行，并检查失败的测试输出

```go
func secondHandPoint(t time.Time) Point {
	return Point{}
}
```

```
clockface_test.go:42: Wanted {0 -1} Point, but got {0 0}
```

### 写足够的代码让测试通过

```go
func secondHandPoint(t time.Time) Point {
	return Point{0, -1}
}
```

```
PASS
ok  	clockface	0.007s
```

### 为新需求重复以上步骤

```go
func TestSecondHandPoint(t *testing.T) {
	cases := []struct {
		time  time.Time
		point Point
	}{
		{simpleTime(0, 0, 30), Point{0, -1}},
		{simpleTime(0, 0, 45), Point{-1, 0}},
	}

	for _, c := range cases {
		t.Run(testName(c.time), func(t *testing.T) {
			got := secondHandPoint(c.time)
			if got != c.point {
				t.Fatalf("Wanted %v Point, but got %v", c.point, got)
			}
		})
	}
}
```

### 试着运行测试

```
clockface_test.go:43: Wanted {-1 0} Point, but got {0 -1}
```

### 写足够的代码让测试通过

还记得单位圆那几张图吗？

![单位圆示意图：射线的 x、y 分量分别为 cos(a) 与 sin(a)，a 是射线与 x 轴的夹角](assets/unit_circle_params-1.png)

再回想一下，我们要从 12 点方向（Y 轴）量角度，而不是从 X 轴量秒针与 3 点方向的夹角。

![单位圆示意图：从 y 轴起按角度定义的射线](assets/unit_circle_12_oclock.png)

现在我们想要那个能算出 X 和 Y 的等式。先把它写进秒针的代码里：

```go
func secondHandPoint(t time.Time) Point {
	angle := secondsInRadians(t)
	x := math.Sin(angle)
	y := math.Cos(angle)

	return Point{x, y}
}
```

现在我们得到

```
clockface_test.go:43: Wanted {0 -1} Point, but got {1.2246467991473515e-16 -1}

clockface_test.go:43: Wanted {-1 0} Point, but got {-1 -1.8369701987210272e-16}
```

等等，（又来）？看来我们又一次被浮点数诅咒了——那两个意料之外的数其实都是*极小量*——小数点后第 16 位才见踪影。于是又到了二选一：要么设法提高精度，要么就认定它们"大致相等"，然后继续过日子。

想提高这些角度的精度，一个选项是用 `math/big` 包里的有理数类型 `Rat`。但既然我们的目标是画个 SVG，而不是登陆月球，我觉得带点模糊也无妨。

```go
func TestSecondHandPoint(t *testing.T) {
	cases := []struct {
		time  time.Time
		point Point
	}{
		{simpleTime(0, 0, 30), Point{0, -1}},
		{simpleTime(0, 0, 45), Point{-1, 0}},
	}

	for _, c := range cases {
		t.Run(testName(c.time), func(t *testing.T) {
			got := secondHandPoint(c.time)
			if !roughlyEqualPoint(got, c.point) {
				t.Fatalf("Wanted %v Point, but got %v", c.point, got)
			}
		})
	}
}

func roughlyEqualFloat64(a, b float64) bool {
	const equalityThreshold = 1e-7
	return math.Abs(a-b) < equalityThreshold
}

func roughlyEqualPoint(a, b Point) bool {
	return roughlyEqualFloat64(a.X, b.X) &&
		roughlyEqualFloat64(a.Y, b.Y)
}
```

我们定义了两个函数来判断两个 `Point` 是否近似相等——只要 X 和 Y 分量彼此相差不超过 0.0000001 就算相等。这已经相当精确了。

现在我们得到：

```
PASS
ok  	clockface	0.007s
```

### 重构

对这段代码我还挺满意。

[现在长这个样子](https://github.com/quii/learn-go-with-tests/tree/main/math/v4/clockface)

### 为新需求重复以上步骤

嗯，说*新*需求其实不太准确——现在真正能做的，是让那条验收测试通过！先回顾一下它长什么样：

```go
func TestSecondHandAt30Seconds(t *testing.T) {
	tm := time.Date(1337, time.January, 1, 0, 0, 30, 0, time.UTC)

	want := clockface.Point{X: 150, Y: 150 + 90}
	got := clockface.SecondHand(tm)

	if got != want {
		t.Errorf("Got %v, wanted %v", got, want)
	}
}
```

### 试着运行测试

```
clockface_acceptance_test.go:28: Got {150 60}, wanted {150 240}
```

### 写足够的代码让测试通过

要把单位向量（unit vector）换算成 SVG 上的一个点，需要做三件事：

1. 按指针长度缩放
2. 沿 X 轴翻转，以适应 SVG 原点在左上角的事实
3. 平移到正确的位置（让它从 (150,150) 这个原点出发）

多欢乐啊！

```go
// SecondHand 是模拟时钟在时间 `t` 时秒针的单位向量，
// 以一个 Point 表示。
func SecondHand(t time.Time) Point {
	p := secondHandPoint(t)
	p = Point{p.X * 90, p.Y * 90}   // 缩放
	p = Point{p.X, -p.Y}            // 翻转
	p = Point{p.X + 150, p.Y + 150} // 平移
	return p
}
```

缩放、翻转、平移，必须严格按照这个顺序。数学万岁！

```
PASS
ok  	clockface	0.007s
```

### 重构

这里有几个魔法数字（magic number）应该抽成常量，那就来吧

```go
const secondHandLength = 90
const clockCentreX = 150
const clockCentreY = 150

// SecondHand 是模拟时钟在时间 `t` 时秒针的单位向量，
// 以一个 Point 表示。
func SecondHand(t time.Time) Point {
	p := secondHandPoint(t)
	p = Point{p.X * secondHandLength, p.Y * secondHandLength}
	p = Point{p.X, -p.Y}
	p = Point{p.X + clockCentreX, p.Y + clockCentreY} //平移
	return p
}
```

## 画时钟

嗯……反正，先把秒针画出来……

干起来吧——世上最难受的事，莫过于价值明明已经躺在那里，等着闪亮登场惊艳世人，你却迟迟不把它交付出去。来画秒针！

我们要在主 `clockface` 包目录下再塞一个新目录，名字（相当容易混淆）还叫 `clockface`。里面放一个 `main` 包，它构建出的二进制文件会生成 SVG：

```
|-- clockface
|       |-- main.go
|-- clockface.go
|-- clockface_acceptance_test.go
|-- clockface_test.go
```

`main.go` 一开始可以照抄下面的代码，但要把 clockface 包的 import 改成指向你自己的版本：

```go
package main

import (
	"fmt"
	"io"
	"os"
	"time"

	"learn-go-with-tests/math/clockface" // 换成你自己的！
)

func main() {
	t := time.Now()
	sh := clockface.SecondHand(t)
	io.WriteString(os.Stdout, svgStart)
	io.WriteString(os.Stdout, bezel)
	io.WriteString(os.Stdout, secondHandTag(sh))
	io.WriteString(os.Stdout, svgEnd)
}

func secondHandTag(p clockface.Point) string {
	return fmt.Sprintf(`<line x1="150" y1="150" x2="%f" y2="%f" style="fill:none;stroke:#f00;stroke-width:3px;"/>`, p.X, p.Y)
}

const svgStart = `<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg"
     width="100%"
     height="100%"
     viewBox="0 0 300 300"
     version="2.0">`

const bezel = `<circle cx="150" cy="150" r="100" style="fill:#fff;stroke:#000;stroke-width:5px;"/>`

const svgEnd = `</svg>`
```

我的天，*这坨*代码是绝无可能拿"美丽代码奖"的——但活儿能干。它在把 SVG 往 `os.Stdout` 里写——一次一段字符串。

先编译

```
go build
```

再运行它，把输出重定向进一个文件

```
./clockface > clock.svg
```

应该能看到类似这样的东西

![只有秒针的时钟](assets/clock.svg)

代码[现在是这个样子](https://github.com/quii/learn-go-with-tests/tree/main/math/v6/clockface)。

### 重构

这味儿不太对。嗯，也没到*臭*不可闻的地步，但我就是不爽。

1. 整个 `SecondHand` 函数跟 SVG*深度*绑定……却又没提到 SVG，也没有真正产出 SVG……
2. ……与此同时，我的 SVG 代码一行都没测到。

是啊，我大概是搞砸了。感觉就是不对。试着用一个更以 SVG 为中心的测试挽回一下。

我们有什么选择？嗯，可以试着测一测 `SVGWriter` 吐出的字符里，是否包含某些看起来像"特定时间应有的 SVG 标签"的内容。比如：

```go
func TestSVGWriterAtMidnight(t *testing.T) {
	tm := time.Date(1337, time.January, 1, 0, 0, 0, 0, time.UTC)

	var b strings.Builder
	clockface.SVGWriter(&b, tm)
	got := b.String()

	want := `<line x1="150" y1="150" x2="150" y2="60"`

	if !strings.Contains(got, want) {
		t.Errorf("Expected to find the second hand %v, in the SVG output %v", want, got)
	}
}
```

但这真的是一种改进吗？

它不但会在我根本没产出合法 SVG 时照样通过（因为它只测"某个字符串出现在输出里"），还会在我对这个字符串做出最微小、最无关紧要的改动时挂掉——比如在属性之间多加一个空格。

*最大*的坏味道是：我在测一个数据结构——XML——却靠检查它作为一串字符的表示——字符串。这*从来*、*永远*都不是个好主意，它带来的正是上面那些问题：一个既太脆弱又不够敏感的测试。一个测错了对象的测试！

所以唯一的出路是把输出*当作 XML* 来测。要做到这一点，就得解析它。

## 解析 XML

[`encoding/xml`](https://pkg.go.dev/encoding/xml) 是 Go 里负责简单 XML 解析各项事务的包。

函数 [`xml.Unmarshal`](https://pkg.go.dev/encoding/xml#Unmarshal) 接收一段 `[]byte` 格式的 XML 数据，以及一个指向结构体的指针，解析结果会被反序列化（unmarshal）进这个结构体。

所以我们需要一个结构体来盛放解析出来的 XML。我们本可以花点时间琢磨各个节点和属性的正确名字、结构该怎么写，但好在有人写了一个程序 [`zek`](https://github.com/miku/zek)，能自动替我们包办这些苦差事。更妙的是，它还有在线版：[https://xml-to-go.github.io/](https://xml-to-go.github.io/)。把文件开头的那段 SVG 粘进输入框——砰——就蹦出了这么个东西：

```go
type Svg struct {
	XMLName xml.Name `xml:"svg"`
	Text    string   `xml:",chardata"`
	Xmlns   string   `xml:"xmlns,attr"`
	Width   string   `xml:"width,attr"`
	Height  string   `xml:"height,attr"`
	ViewBox string   `xml:"viewBox,attr"`
	Version string   `xml:"version,attr"`
	Circle  struct {
		Text  string `xml:",chardata"`
		Cx    string `xml:"cx,attr"`
		Cy    string `xml:"cy,attr"`
		R     string `xml:"r,attr"`
		Style string `xml:"style,attr"`
	} `xml:"circle"`
	Line []struct {
		Text  string `xml:",chardata"`
		X1    string `xml:"x1,attr"`
		Y1    string `xml:"y1,attr"`
		X2    string `xml:"x2,attr"`
		Y2    string `xml:"y2,attr"`
		Style string `xml:"style,attr"`
	} `xml:"line"`
}
```

需要的话我们可以再调整（比如把结构体改名为 `SVG`），但作为起点它绝对够用了。把这个结构体粘进 `clockface_acceptance_test` 文件，我们用它写个测试：

```go
func TestSVGWriterAtMidnight(t *testing.T) {
	tm := time.Date(1337, time.January, 1, 0, 0, 0, 0, time.UTC)

	b := bytes.Buffer{}
	clockface.SVGWriter(&b, tm)

	svg := Svg{}
	xml.Unmarshal(b.Bytes(), &svg)

	x2 := "150"
	y2 := "60"

	for _, line := range svg.Line {
		if line.X2 == x2 && line.Y2 == y2 {
			return
		}
	}

	t.Errorf("Expected to find the second hand with x2 of %+v and y2 of %+v, in the SVG output %v", x2, y2, b.String())
}
```

我们把 `clockface.SVGWriter` 的输出写进一个 `bytes.Buffer`，再把它 `Unmarshal` 进 `Svg`。然后逐条查看 `Svg` 里的 `Line`，看有没有哪条的 `X2` 和 `Y2` 值符合期望。匹配到了就提前 return（测试通过）；没匹配到，就带着一条（但愿）信息量足够的消息让测试失败。

```sh
./clockface_acceptance_test.go:41:2: undefined: clockface.SVGWriter
```

看来我们最好还是创建 `SVGWriter.go`……

```go
package clockface

import (
	"fmt"
	"io"
	"time"
)

const (
	secondHandLength = 90
	clockCentreX     = 150
	clockCentreY     = 150
)

// SVGWriter 把显示时间 t 的模拟时钟的 SVG 表示写入 writer w
func SVGWriter(w io.Writer, t time.Time) {
	io.WriteString(w, svgStart)
	io.WriteString(w, bezel)
	secondHand(w, t)
	io.WriteString(w, svgEnd)
}

func secondHand(w io.Writer, t time.Time) {
	p := secondHandPoint(t)
	p = Point{p.X * secondHandLength, p.Y * secondHandLength} // 缩放
	p = Point{p.X, -p.Y}                                      // 翻转
	p = Point{p.X + clockCentreX, p.Y + clockCentreY}         // 平移
	fmt.Fprintf(w, `<line x1="150" y1="150" x2="%f" y2="%f" style="fill:none;stroke:#f00;stroke-width:3px;"/>`, p.X, p.Y)
}

const svgStart = `<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg"
     width="100%"
     height="100%"
     viewBox="0 0 300 300"
     version="2.0">`

const bezel = `<circle cx="150" cy="150" r="100" style="fill:#fff;stroke:#000;stroke-width:5px;"/>`

const svgEnd = `</svg>`
```

世上最美的 SVG writer？并不是。但希望它能顶事儿……

```
clockface_acceptance_test.go:56: Expected to find the second hand with x2 of 150 and y2 of 60, in the SVG output <?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <svg xmlns="http://www.w3.org/2000/svg"
         width="100%"
         height="100%"
         viewBox="0 0 300 300"
         version="2.0"><circle cx="150" cy="150" r="100" style="fill:#fff;stroke:#000;stroke-width:5px;"/><line x1="150" y1="150" x2="150.000000" y2="60.000000" style="fill:none;stroke:#f00;stroke-width:3px;"/></svg>
```

哎呀！`%f` 这个格式化动词按默认精度打印我们的坐标——六位小数。坐标期望的精度应该由我们自己明说。就定三位小数吧。

```go
	fmt.Fprintf(w, `<line x1="150" y1="150" x2="%.3f" y2="%.3f" style="fill:none;stroke:#f00;stroke-width:3px;"/>`, p.X, p.Y)
```

再把测试里的期望值更新一下

```go
	x2 := "150.000"
	y2 := "60.000"
```

得到：

```
PASS
ok  	clockface	0.006s
```

现在可以把 `main` 函数精简为：

```go
package main

import (
	"os"
	"time"

	"learn-go-with-tests/math/clockface"
)

func main() {
	t := time.Now()
	clockface.SVGWriter(os.Stdout, t)
}
```

[现在一切应该长这个样子](https://github.com/quii/learn-go-with-tests/tree/main/math/v7b/clockface)。

照同样的模式，我们可以再为别的时刻写测试，但在这之前……

### 重构

有三处扎眼：

1. 我们其实没有测全需要确保存在的信息——比如 `x1` 的值呢？
2. 再说，`x1` 这些属性真的该是 `string` 吗？它们是数字啊！
3. 我真的在乎指针的 `style` 吗？又或者，`zak` 生成的那个空的 `Text` 节点呢？

我们能做得更好。来对 `Svg` 结构体和测试做几处调整，把一切打磨得更锋利。

```go
type SVG struct {
	XMLName xml.Name `xml:"svg"`
	Xmlns   string   `xml:"xmlns,attr"`
	Width   string   `xml:"width,attr"`
	Height  string   `xml:"height,attr"`
	ViewBox string   `xml:"viewBox,attr"`
	Version string   `xml:"version,attr"`
	Circle  Circle   `xml:"circle"`
	Line    []Line   `xml:"line"`
}

type Circle struct {
	Cx float64 `xml:"cx,attr"`
	Cy float64 `xml:"cy,attr"`
	R  float64 `xml:"r,attr"`
}

type Line struct {
	X1 float64 `xml:"x1,attr"`
	Y1 float64 `xml:"y1,attr"`
	X2 float64 `xml:"x2,attr"`
	Y2 float64 `xml:"y2,attr"`
}
```

这一版我做了这些事：

* 把结构体里重要的部分定义成具名类型——`Line` 和 `Circle`
* 把数字属性从 `string` 换成 `float64`。
* 删掉了 `Style`、`Text` 这类用不上的属性
* 把 `Svg` 改名为 `SVG`，因为*这就是该做的事*。

这样我们就能对要找的那条线做更精确的断言了：

```go
func TestSVGWriterAtMidnight(t *testing.T) {
	tm := time.Date(1337, time.January, 1, 0, 0, 0, 0, time.UTC)
	b := bytes.Buffer{}

	clockface.SVGWriter(&b, tm)

	svg := SVG{}

	xml.Unmarshal(b.Bytes(), &svg)

	want := Line{150, 150, 150, 60}

	for _, line := range svg.Line {
		if line == want {
			return
		}
	}

	t.Errorf("Expected to find the second hand line %+v, in the SVG lines %+v", want, svg.Line)
}
```

最后，我们可以从单元测试的表驱动里取取经，写一个辅助函数 `containsLine(line Line, lines []Line) bool`，让这些测试真正闪闪发光。`simpleTime` 和 `testName` 也想再用一次——但这个文件（`clockface_acceptance_test.go`）在 `package clockface_test` 里，与我们最初编写它们的 `clockface_test.go`（`package clockface`）不属于同一个包。这些函数没有导出，在声明它们的包之外不可见，所以这里需要自己的副本。

```go
func TestSVGWriterSecondHand(t *testing.T) {
	cases := []struct {
		time time.Time
		line Line
	}{
		{
			simpleTime(0, 0, 0),
			Line{150, 150, 150, 60},
		},
		{
			simpleTime(0, 0, 30),
			Line{150, 150, 150, 240},
		},
	}

	for _, c := range cases {
		t.Run(testName(c.time), func(t *testing.T) {
			b := bytes.Buffer{}
			clockface.SVGWriter(&b, c.time)

			svg := SVG{}
			xml.Unmarshal(b.Bytes(), &svg)

			if !containsLine(c.line, svg.Line) {
				t.Errorf("Expected to find the second hand line %+v, in the SVG lines %+v", c.line, svg.Line)
			}
		})
	}
}

func containsLine(l Line, ls []Line) bool {
	for _, line := range ls {
		if line == l {
			return true
		}
	}
	return false
}

func simpleTime(hours, minutes, seconds int) time.Time {
	return time.Date(312, time.October, 28, hours, minutes, seconds, 0, time.UTC)
}

func testName(t time.Time) string {
	return t.Format("15:04:05")
}
```

[现在长这个样子](https://github.com/quii/learn-go-with-tests/tree/main/math/v7c/clockface)

这*才*叫验收测试嘛！

### 先写测试

秒针到此完工。接下来开始搞分针。

```go
func TestSVGWriterMinuteHand(t *testing.T) {
	cases := []struct {
		time time.Time
		line Line
	}{
		{
			simpleTime(0, 0, 0),
			Line{150, 150, 150, 70},
		},
	}

	for _, c := range cases {
		t.Run(testName(c.time), func(t *testing.T) {
			b := bytes.Buffer{}
			clockface.SVGWriter(&b, c.time)

			svg := SVG{}
			xml.Unmarshal(b.Bytes(), &svg)

			if !containsLine(c.line, svg.Line) {
				t.Errorf("Expected to find the minute hand line %+v, in the SVG lines %+v", c.line, svg.Line)
			}
		})
	}
}
```

### 试着运行测试

```
clockface_acceptance_test.go:87: Expected to find the minute hand line {X1:150 Y1:150 X2:150 Y2:70}, in the SVG lines [{X1:150 Y1:150 X2:150 Y2:60}]
```

该着手造其他指针了。跟秒针测试的产出方式大同小异，我们可以迭代出下面这组测试。同样，在搞定之前先把验收测试注释掉：

```go
func TestMinutesInRadians(t *testing.T) {
	cases := []struct {
		time  time.Time
		angle float64
	}{
		{simpleTime(0, 30, 0), math.Pi},
	}

	for _, c := range cases {
		t.Run(testName(c.time), func(t *testing.T) {
			got := minutesInRadians(c.time)
			if got != c.angle {
				t.Fatalf("Wanted %v radians, but got %v", c.angle, got)
			}
		})
	}
}
```

### 试着运行测试

```
./clockface_test.go:59:11: undefined: minutesInRadians
```

### 写最少的代码让测试能运行，并检查失败的测试输出

```go
func minutesInRadians(t time.Time) float64 {
	return math.Pi
}
```

### 为新需求重复以上步骤

好，现在逼自己干点*真正的*活。我们可以把分针建模成每到整分钟才动一次——于是它从 30 分"跳"到 31 分，中间纹丝不动。但那样看上去有点寒碜。我们要的是它每一秒都挪动*一丁点儿*。

```go
func TestMinutesInRadians(t *testing.T) {
	cases := []struct {
		time  time.Time
		angle float64
	}{
		{simpleTime(0, 30, 0), math.Pi},
		{simpleTime(0, 0, 7), 7 * (math.Pi / (30 * 60))},
	}

	for _, c := range cases {
		t.Run(testName(c.time), func(t *testing.T) {
			got := minutesInRadians(c.time)
			if got != c.angle {
				t.Fatalf("Wanted %v radians, but got %v", c.angle, got)
			}
		})
	}
}
```

那一丁点儿到底是多少？是这样：

* 一分钟有 60 秒
* 半圈（`math.Pi` 弧度）里有 30 分钟
* 所以半圈是 `30 * 60` 秒。
* 如果时间是整点后 7 秒……
* ……我们期望分针位于 12 点起 `7 * (math.Pi / (30 * 60))` 弧度处。

### 试着运行测试

```
clockface_test.go:62: Wanted 0.012217304763960306 radians, but got 3.141592653589793
```

### 写足够的代码让测试通过

借用 Jennifer Aniston 的不朽名言：[科学环节到了](https://www.youtube.com/watch?v=29Im23SPNok)

```go
func minutesInRadians(t time.Time) float64 {
	return (secondsInRadians(t) / 60) +
		(math.Pi / (30 / float64(t.Minute())))
}
```

与其从头计算每一秒要把分针在表盘上推进多少，这里可以直接借用 `secondsInRadians` 函数。每一秒，分针移动秒针所移角度的 1/60。

```go
secondsInRadians(t) / 60
```

然后再加上分钟带来的移动——和秒针的移动方式类似。

```go
math.Pi / (30 / float64(t.Minute()))
```

然后……

```
PASS
ok  	clockface	0.007s
```

轻松愉快。现在[一切长这样](https://github.com/quii/learn-go-with-tests/tree/main/math/v8/clockface/clockface_acceptance_test.go)。

### 为新需求重复以上步骤

要不要再给 `minutesInRadians` 测试加几个用例？眼下只有两个。要加够多少个用例，才轮得到去测 `minuteHandPoint` 函数？

我最喜欢的 TDD 名言之一（常被认为出自 Kent Beck）：

> 把测试写到恐惧变成无聊为止。

坦白讲，那个函数我已经测烦了。我很确信自己知道它是怎么工作的。那就下一个。

### 先写测试

```go
func TestMinuteHandPoint(t *testing.T) {
	cases := []struct {
		time  time.Time
		point Point
	}{
		{simpleTime(0, 30, 0), Point{0, -1}},
	}

	for _, c := range cases {
		t.Run(testName(c.time), func(t *testing.T) {
			got := minuteHandPoint(c.time)
			if !roughlyEqualPoint(got, c.point) {
				t.Fatalf("Wanted %v Point, but got %v", c.point, got)
			}
		})
	}
}
```

### 试着运行测试

```
./clockface_test.go:79:11: undefined: minuteHandPoint
```

### 写最少的代码让测试能运行，并检查失败的测试输出

```go
func minuteHandPoint(t time.Time) Point {
	return Point{}
}
```

```
clockface_test.go:80: Wanted {0 -1} Point, but got {0 0}
```

### 写足够的代码让测试通过

```go
func minuteHandPoint(t time.Time) Point {
	return Point{0, -1}
}
```

```
PASS
ok  	clockface	0.007s
```

### 为新需求重复以上步骤

接下来来点真正的活

```go
func TestMinuteHandPoint(t *testing.T) {
	cases := []struct {
		time  time.Time
		point Point
	}{
		{simpleTime(0, 30, 0), Point{0, -1}},
		{simpleTime(0, 45, 0), Point{-1, 0}},
	}

	for _, c := range cases {
		t.Run(testName(c.time), func(t *testing.T) {
			got := minuteHandPoint(c.time)
			if !roughlyEqualPoint(got, c.point) {
				t.Fatalf("Wanted %v Point, but got %v", c.point, got)
			}
		})
	}
}
```

```
clockface_test.go:81: Wanted {-1 0} Point, but got {0 -1}
```

### 写足够的代码让测试通过

把 `secondHandPoint` 函数复制粘贴过来稍加修改，应该就够了……

```go
func minuteHandPoint(t time.Time) Point {
	angle := minutesInRadians(t)
	x := math.Sin(angle)
	y := math.Cos(angle)

	return Point{x, y}
}
```

```
PASS
ok  	clockface	0.009s
```

### 重构

`minuteHandPoint` 和 `secondHandPoint` 之间肯定有重复——我知道，因为我们刚刚就是把一个复制粘贴成另一个的。用一个函数把重复 DRY 掉。

```go
func angleToPoint(angle float64) Point {
	x := math.Sin(angle)
	y := math.Cos(angle)

	return Point{x, y}
}
```

这样 `minuteHandPoint` 和 `secondHandPoint` 就能重写成一行流：

```go
func minuteHandPoint(t time.Time) Point {
	return angleToPoint(minutesInRadians(t))
}
```

```go
func secondHandPoint(t time.Time) Point {
	return angleToPoint(secondsInRadians(t))
}
```

```
PASS
ok  	clockface	0.007s
```

现在可以取消验收测试的注释，开工画分针了。

### 写足够的代码让测试通过

`minuteHand` 函数就是 `secondHand` 的复制粘贴版，稍作调整，比如声明了 `minuteHandLength`：

```go
const minuteHandLength = 80

//...

func minuteHand(w io.Writer, t time.Time) {
	p := minuteHandPoint(t)
	p = Point{p.X * minuteHandLength, p.Y * minuteHandLength}
	p = Point{p.X, -p.Y}
	p = Point{p.X + clockCentreX, p.Y + clockCentreY}
	fmt.Fprintf(w, `<line x1="150" y1="150" x2="%.3f" y2="%.3f" style="fill:none;stroke:#000;stroke-width:3px;"/>`, p.X, p.Y)
}
```

再在 `SVGWriter` 函数里加一个对它的调用：

```go
func SVGWriter(w io.Writer, t time.Time) {
	io.WriteString(w, svgStart)
	io.WriteString(w, bezel)
	secondHand(w, t)
	minuteHand(w, t)
	io.WriteString(w, svgEnd)
}
```

现在应该能看到 `TestSVGWriterMinuteHand` 通过了：

```
PASS
ok  	clockface	0.006s
```

布丁好不好，得亲口尝尝——现在编译并运行我们的 `clockface` 程序，应该会看到类似这样的东西

![有时针和分针的时钟](assets/clock-1.svg)

### 重构

把 `secondHand` 和 `minuteHand` 里的重复清掉，把缩放、翻转、平移的逻辑全部收拢到一处。

```go
func secondHand(w io.Writer, t time.Time) {
	p := makeHand(secondHandPoint(t), secondHandLength)
	fmt.Fprintf(w, `<line x1="150" y1="150" x2="%.3f" y2="%.3f" style="fill:none;stroke:#f00;stroke-width:3px;"/>`, p.X, p.Y)
}

func minuteHand(w io.Writer, t time.Time) {
	p := makeHand(minuteHandPoint(t), minuteHandLength)
	fmt.Fprintf(w, `<line x1="150" y1="150" x2="%.3f" y2="%.3f" style="fill:none;stroke:#000;stroke-width:3px;"/>`, p.X, p.Y)
}

func makeHand(p Point, length float64) Point {
	p = Point{p.X * length, p.Y * length}
	p = Point{p.X, -p.Y}
	return Point{p.X + clockCentreX, p.Y + clockCentreY}
}
```

```
PASS
ok  	clockface	0.007s
```

[目前进度在这里](https://github.com/quii/learn-go-with-tests/tree/main/math/v9/clockface)。

瞧……现在只剩时针了！

### 先写测试

```go
func TestSVGWriterHourHand(t *testing.T) {
	cases := []struct {
		time time.Time
		line Line
	}{
		{
			simpleTime(6, 0, 0),
			Line{150, 150, 150, 200},
		},
	}

	for _, c := range cases {
		t.Run(testName(c.time), func(t *testing.T) {
			b := bytes.Buffer{}
			clockface.SVGWriter(&b, c.time)

			svg := SVG{}
			xml.Unmarshal(b.Bytes(), &svg)

			if !containsLine(c.line, svg.Line) {
				t.Errorf("Expected to find the hour hand line %+v, in the SVG lines %+v", c.line, svg.Line)
			}
		})
	}
}
```

### 试着运行测试

```
clockface_acceptance_test.go:113: Expected to find the hour hand line {X1:150 Y1:150 X2:150 Y2:200}, in the SVG lines [{X1:150 Y1:150 X2:150 Y2:60} {X1:150 Y1:150 X2:150 Y2:70}]
```

老规矩，先把这个测试注释掉，等底层测试有了些覆盖再说：

### 先写测试

```go
func TestHoursInRadians(t *testing.T) {
	cases := []struct {
		time  time.Time
		angle float64
	}{
		{simpleTime(6, 0, 0), math.Pi},
	}

	for _, c := range cases {
		t.Run(testName(c.time), func(t *testing.T) {
			got := hoursInRadians(c.time)
			if got != c.angle {
				t.Fatalf("Wanted %v radians, but got %v", c.angle, got)
			}
		})
	}
}
```

### 试着运行测试

```
./clockface_test.go:97:11: undefined: hoursInRadians
```

### 写最少的代码让测试能运行，并检查失败的测试输出

```go
func hoursInRadians(t time.Time) float64 {
	return math.Pi
}
```

```
PASS
ok  	clockface	0.007s
```

### 为新需求重复以上步骤

```go
func TestHoursInRadians(t *testing.T) {
	cases := []struct {
		time  time.Time
		angle float64
	}{
		{simpleTime(6, 0, 0), math.Pi},
		{simpleTime(0, 0, 0), 0},
	}

	for _, c := range cases {
		t.Run(testName(c.time), func(t *testing.T) {
			got := hoursInRadians(c.time)
			if got != c.angle {
				t.Fatalf("Wanted %v radians, but got %v", c.angle, got)
			}
		})
	}
}
```

### 试着运行测试

```
clockface_test.go:100: Wanted 0 radians, but got 3.141592653589793
```

### 写足够的代码让测试通过

```go
func hoursInRadians(t time.Time) float64 {
	return (math.Pi / (6 / float64(t.Hour())))
}
```

### 为新需求重复以上步骤

```go
func TestHoursInRadians(t *testing.T) {
	cases := []struct {
		time  time.Time
		angle float64
	}{
		{simpleTime(6, 0, 0), math.Pi},
		{simpleTime(0, 0, 0), 0},
		{simpleTime(21, 0, 0), math.Pi * 1.5},
	}

	for _, c := range cases {
		t.Run(testName(c.time), func(t *testing.T) {
			got := hoursInRadians(c.time)
			if got != c.angle {
				t.Fatalf("Wanted %v radians, but got %v", c.angle, got)
			}
		})
	}
}
```

### 试着运行测试

```
clockface_test.go:101: Wanted 4.71238898038469 radians, but got 10.995574287564276
```

### 写足够的代码让测试通过

```go
func hoursInRadians(t time.Time) float64 {
	return (math.Pi / (6 / (float64(t.Hour() % 12))))
}
```

记住，这不是 24 小时制的钟；得用取余运算符（remainder operator）求出当前小时除以 12 的余数。

```
PASS
ok  	learn-go-with-tests/math/clockface	0.008s
```

### 先写测试

现在试着让时针根据已经流逝的分钟和秒数在表盘上移动。

```go
func TestHoursInRadians(t *testing.T) {
	cases := []struct {
		time  time.Time
		angle float64
	}{
		{simpleTime(6, 0, 0), math.Pi},
		{simpleTime(0, 0, 0), 0},
		{simpleTime(21, 0, 0), math.Pi * 1.5},
		{simpleTime(0, 1, 30), math.Pi / ((6 * 60 * 60) / 90)},
	}

	for _, c := range cases {
		t.Run(testName(c.time), func(t *testing.T) {
			got := hoursInRadians(c.time)
			if got != c.angle {
				t.Fatalf("Wanted %v radians, but got %v", c.angle, got)
			}
		})
	}
}
```

### 试着运行测试

```
clockface_test.go:102: Wanted 0.013089969389957472 radians, but got 0
```

### 写足够的代码让测试通过

这回又得动动脑子。时针需要随分钟和秒数一起往前蹭。幸运的是，分钟和秒数对应的角度我们手头就有——`minutesInRadians` 的返回值。可以复用！

唯一的问题是：这个角度要按什么系数缩小。对分针来说转一整圈是一小时，对时针来说是十二小时。所以把 `minutesInRadians` 返回的角度除以十二即可：

```go
func hoursInRadians(t time.Time) float64 {
	return (minutesInRadians(t) / 12) +
		(math.Pi / (6 / float64(t.Hour()%12)))
}
```

然后请看：

```
clockface_test.go:104: Wanted 0.013089969389957472 radians, but got 0.01308996938995747
```

浮点运算又双叒来了。

把测试更新一下，改用 `roughlyEqualFloat64` 来比较角度。

```go
func TestHoursInRadians(t *testing.T) {
	cases := []struct {
		time  time.Time
		angle float64
	}{
		{simpleTime(6, 0, 0), math.Pi},
		{simpleTime(0, 0, 0), 0},
		{simpleTime(21, 0, 0), math.Pi * 1.5},
		{simpleTime(0, 1, 30), math.Pi / ((6 * 60 * 60) / 90)},
	}

	for _, c := range cases {
		t.Run(testName(c.time), func(t *testing.T) {
			got := hoursInRadians(c.time)
			if !roughlyEqualFloat64(got, c.angle) {
				t.Fatalf("Wanted %v radians, but got %v", c.angle, got)
			}
		})
	}
}
```

```
PASS
ok  	clockface	0.007s
```

### 重构

既然要在*一个*弧度测试里用 `roughlyEqualFloat64`，那很可能*所有*弧度测试都该用它。这是个清爽的小重构，改完[长这样](https://github.com/quii/learn-go-with-tests/tree/main/math/v10/clockface)。

## 时针端点

好，是时候通过求单位向量来计算时针端点的位置了。

### 先写测试

```go
func TestHourHandPoint(t *testing.T) {
	cases := []struct {
		time  time.Time
		point Point
	}{
		{simpleTime(6, 0, 0), Point{0, -1}},
		{simpleTime(21, 0, 0), Point{-1, 0}},
	}

	for _, c := range cases {
		t.Run(testName(c.time), func(t *testing.T) {
			got := hourHandPoint(c.time)
			if !roughlyEqualPoint(got, c.point) {
				t.Fatalf("Wanted %v Point, but got %v", c.point, got)
			}
		})
	}
}
```

等等，我要*一次*写*两个*测试用例？这难道不是*糟糕的 TDD*吗？

### 关于 TDD 狂热

测试驱动开发不是宗教。有些人偏要表现得像宗教——通常是那些自己不搞 TDD、却热衷在 Twitter 或 Dev.to 上发牢骚说"只有狂热分子才搞 TDD"的人，轮到他们不写测试时，就自称"务实"。但它不是宗教。它是工具。

我*知道*这两个测试会是什么样——另外两根指针我就是用一模一样的方式测的——我也已经知道实现会长什么样——分针那一轮里，我就写好了把角度换算成点的通用函数。

我不会为仪式而仪式。TDD 是一项帮我更好地理解"我正在写的代码"——以及"我将要写的代码"——的技术。TDD 给我反馈、知识和洞见。但如果这些我已经有了，就不会无缘无故把全套仪式再走一遍。测试和 TDD 都不是目的本身。

我的信心增长了，所以我觉得可以迈更大的步子。我会"跳过"几个步骤，因为我知道自己在哪、要去哪，而且这条路我以前走过。

但也请注意：我没有完全跳过写测试——测试依然是先写的。只是它们的粒度变粗了一些。

### 试着运行测试

```
./clockface_test.go:119:11: undefined: hourHandPoint
```

### 写足够的代码让测试通过

```go
func hourHandPoint(t time.Time) Point {
	return angleToPoint(hoursInRadians(t))
}
```

如我所说，我知道自己在哪，也知道要去哪。何必装作不知道？如果错了，测试很快会告诉我。

```
PASS
ok  	learn-go-with-tests/math/clockface	0.009s
```

## 画时针

终于轮到画时针了。把那条验收测试的注释取消掉就行：

```go
func TestSVGWriterHourHand(t *testing.T) {
	cases := []struct {
		time time.Time
		line Line
	}{
		{
			simpleTime(6, 0, 0),
			Line{150, 150, 150, 200},
		},
	}

	for _, c := range cases {
		t.Run(testName(c.time), func(t *testing.T) {
			b := bytes.Buffer{}
			clockface.SVGWriter(&b, c.time)

			svg := SVG{}
			xml.Unmarshal(b.Bytes(), &svg)

			if !containsLine(c.line, svg.Line) {
				t.Errorf("Expected to find the hour hand line %+v, in the SVG lines %+v", c.line, svg.Line)
			}
		})
	}
}
```

### 试着运行测试

```
clockface_acceptance_test.go:113: Expected to find the hour hand line {X1:150 Y1:150 X2:150 Y2:200},
    in the SVG lines [{X1:150 Y1:150 X2:150 Y2:60} {X1:150 Y1:150 X2:150 Y2:70}]
```

### 写足够的代码让测试通过

现在可以对写 SVG 的常量和函数做最后调整了：

```go
const (
	secondHandLength = 90
	minuteHandLength = 80
	hourHandLength   = 50
	clockCentreX     = 150
	clockCentreY     = 150
)

// SVGWriter 把显示时间 t 的模拟时钟的 SVG 表示写入 writer w
func SVGWriter(w io.Writer, t time.Time) {
	io.WriteString(w, svgStart)
	io.WriteString(w, bezel)
	secondHand(w, t)
	minuteHand(w, t)
	hourHand(w, t)
	io.WriteString(w, svgEnd)
}

// ...

func hourHand(w io.Writer, t time.Time) {
	p := makeHand(hourHandPoint(t), hourHandLength)
	fmt.Fprintf(w, `<line x1="150" y1="150" x2="%.3f" y2="%.3f" style="fill:none;stroke:#000;stroke-width:3px;"/>`, p.X, p.Y)
}

```

于是……

```
ok  	clockface	0.007s
```

编译并运行 `clockface` 程序，亲自确认一下。

![时钟](assets/clock-2.svg)

### 重构

看看 `clockface.go`，还飘着几个"魔法数字"。它们全都围绕"绕表盘半圈对应多少小时/分钟/秒"打转。来重构一下，把它们的含义摆到明面上。

```go
const (
	secondsInHalfClock = 30
	secondsInClock     = 2 * secondsInHalfClock
	minutesInHalfClock = 30
	minutesInClock     = 2 * minutesInHalfClock
	hoursInHalfClock   = 6
	hoursInClock       = 2 * hoursInHalfClock
)
```

为什么要这么做？因为它把每个数字在等式中的*含义*挑明了。如果——*不如说当*——我们回到这段代码时，这些名字会帮我们搞清状况。

再者，万一哪天我们想做些非常、非常*怪*的钟——比如时针一圈只走 4 小时、秒针一圈只走 20 秒——这些常量可以轻松变成参数。我们这是在给未来留一扇门（哪怕永远没人走进去）。

## 总结

还需要做点别的什么吗？

首先，拍拍自己的肩膀——我们写出了一个能生成 SVG 表盘的程序。它能跑，而且很棒。它只会画一种表盘——但这没什么不好！也许你*就想要*一种表盘。一个只解决特定问题的程序，无可指摘。

### 一个程序……以及一个库

不过，我们写的代码*确实*解决了一组更通用的、与画表盘相关的问题。因为我们借助测试把问题的每个小部分单独想清楚，又用函数把这种隔离固化下来，我们已经攒出了一个相当像样的表盘计算小 API。

我们可以继续经营这个项目，把它变成更通用的东西——一个计算表盘角度和/或向量的库。

实际上，把库和程序一起提供*是个绝妙的主意*。它不花我们一分钱，却提升了程序的实用性，还顺便充当了"程序如何工作"的文档。

> API 应当伴随程序而生，反之亦然。一个必须写 C 代码才能用、没法从命令行方便调用的 API，学起来用起来都更难。反过来，如果一套接口唯一的公开、有文档的形式是程序，导致你没法从 C 程序里方便地调用它们，那也是奇烦无比。-- Henry Spencer，《*The Art of Unix Programming*》

在[这个程序的最终版](https://github.com/quii/learn-go-with-tests/tree/main/math/vFinal/clockface)里，我把 `clockface` 内部的非导出函数升级成了库的公开 API，提供计算每根指针角度和单位向量的函数。我还把生成 SVG 的部分拆成了独立的 `svg` 包，`clockface` 程序直接使用它。自然，每个函数和包我都补了文档。

说到 SVG……

### 最有价值的测试

你一定注意到了：整段代码里最精巧的 SVG 处理逻辑压根不在我们的应用代码里，而在测试代码里。这该让我们心里发毛吗？我们是不是应该改成：

* 用 `text/template` 的模板？
* 用一个 XML 库（就像我们在测试里做的那样）？
* 用一个 SVG 库？

这些做法我们都可以通过重构实现，而且可以放心去做，因为用*什么办法*产出 SVG 并不重要，重要的是产出*什么东西*——*一份 SVG*。因此，系统里最需要了解 SVG、对"什么才算 SVG"最该一丝不苟的，恰恰是针对 SVG 输出的那几个测试：它们必须对"SVG 是什么"有足够的上下文和知识，我们才能确信自己输出的确实是 SVG。SVG 的*是什么*住在测试里；*怎么做*住在代码里。

往那几个 SVG 测试里砸那么多时间和功夫——导入 XML 库、解析 XML、重构结构体——我们心里可能犯嘀咕，但那些测试代码是代码库里很有价值的一部分——说不定比当前的生产代码还有价值。无论日后我们选择用什么来产出 SVG，它们都能帮我们保证输出始终是一份合法的 SVG。

测试不是二等公民——它们不是"用完即弃"的代码。好测试的寿命远长于它们所测的那一版代码。永远不要觉得自己"在写测试上花了太多时间"。那是一种投资。

1. 简而言之，这样在圆上做计算更容易：如果用普通的度数，π 总是会以角度的形式反复冒出来；而直接用 π 来计量角度，所有等式都会更简单。
