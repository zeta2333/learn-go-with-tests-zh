# 结构体、方法与接口

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/structs)**

假设我们需要一些几何代码，在给定高和宽的情况下计算矩形的周长。可以写一个 `Perimeter(width float64, height float64)` 函数，其中的 `float64` 用来表示 `123.45` 这样的浮点数。

TDD 循环到现在你应该已经很熟了。

## 先写测试

```go
func TestPerimeter(t *testing.T) {
	got := Perimeter(10.0, 10.0)
	want := 40.0

	if got != want {
		t.Errorf("got %.2f want %.2f", got, want)
	}
}
```

注意到新的格式化字符串了吗？`f` 对应我们的 `float64`，`.2` 表示打印两位小数。

## 试着运行测试

`./shapes_test.go:6:9: undefined: Perimeter`

## 写最少量的代码让测试得以运行，并查看失败的输出

```go
func Perimeter(width float64, height float64) float64 {
	return 0
}
```

结果是 `shapes_test.go:10: got 0.00 want 40.00`。

## 写足够的代码让测试通过

```go
func Perimeter(width float64, height float64) float64 {
	return 2 * (width + height)
}
```

到目前为止都很简单。接下来我们创建一个名为 `Area(width, height float64)` 的函数，返回矩形的面积。

试试自己动手，照着 TDD 循环走一遍。

你的测试最后应该长这样

```go
func TestPerimeter(t *testing.T) {
	got := Perimeter(10.0, 10.0)
	want := 40.0

	if got != want {
		t.Errorf("got %.2f want %.2f", got, want)
	}
}

func TestArea(t *testing.T) {
	got := Area(12.0, 6.0)
	want := 72.0

	if got != want {
		t.Errorf("got %.2f want %.2f", got, want)
	}
}
```

代码则是这样

```go
func Perimeter(width float64, height float64) float64 {
	return 2 * (width + height)
}

func Area(width float64, height float64) float64 {
	return width * height
}
```

你可能听说过，用 `!=`/`==` 比较浮点数不是个好主意，这是由浮点数在内存中的表示方式决定的：

```go
func Example_floatComparison() {
	fmt.Println(0.1+0.2 == 0.3)

	var a, b, c float64 = 0.1, 0.2, 0.3
	fmt.Println(a+b == c)

	// Output:
	// true
	// false
}
```

第二个比较之所以是 `false`，是因为 `0.1` 和 `0.2` 没办法用 `float64` 精确表示，两个数加起来也不会正好落在 `0.3` 上。第一个之所以是 `true`，只是因为它是按字面量表达式来写的——Go 对字面量按任意精度求值（而不是按 `float64`），直到它们被赋给某个东西为止。

不过这种不精确并不影响上面的 `Area` 测试：我们用到的每一个值（`12.0`、`6.0`、`72.0` 等等）都是整数，`float64` *能*精确表示它们，而两个可精确表示的数相乘，只要结果还在表示范围内，得到的同样是可精确表示的数。只有当你引入无法精确表示的值（比如 `0.1`）或运算结果（比如除法）时，精确比较才会变得不安全。如果发现自己要写那样的测试，请改用带可接受容差的比较，比如 `go-cmp` 的 [`cmp.Diff` 配合 `cmpopts.EquateApprox`](https://pkg.go.dev/github.com/google/go-cmp/cmp/cmpopts#EquateApprox)。

## 重构

我们的代码能干活，但里面没有任何明确提到“矩形”的地方。一个不小心的开发者可能会把三角形的宽和高传给这些函数，却没意识到函数会返回错误的答案。

我们当然可以把函数名起得更具体，比如 `RectangleArea`。但更优雅的方案是自定义一个叫 `Rectangle` 的*类型*，让它替我们把这个概念封装起来。

我们可以用**结构体**（struct）来创建一个简单的类型。[结构体](https://golang.org/ref/spec#Struct_types)不过是一组命了名的字段（field），你可以在里面存放数据。

在 `shapes.go` 里像这样声明一个结构体

```go
type Rectangle struct {
	Width  float64
	Height float64
}
```

现在我们重构测试，不再用裸的 `float64`，改用 `Rectangle`。

```go
func TestPerimeter(t *testing.T) {
	rectangle := Rectangle{10.0, 10.0}
	got := Perimeter(rectangle)
	want := 40.0

	if got != want {
		t.Errorf("got %.2f want %.2f", got, want)
	}
}

func TestArea(t *testing.T) {
	rectangle := Rectangle{12.0, 6.0}
	got := Area(rectangle)
	want := 72.0

	if got != want {
		t.Errorf("got %.2f want %.2f", got, want)
	}
}
```

记得在动手修之前先跑测试。测试会给出一条有用的报错，比如

```text
./shapes_test.go:7:18: not enough arguments in call to Perimeter
    have (Rectangle)
    want (float64, float64)
```

用 `myStruct.field` 这样的语法就能访问结构体的字段。

修改这两个函数，让测试通过。

```go
func Perimeter(rectangle Rectangle) float64 {
	return 2 * (rectangle.Width + rectangle.Height)
}

func Area(rectangle Rectangle) float64 {
	return rectangle.Width * rectangle.Height
}
```

相信你也同意，把 `Rectangle` 传给函数更能表明我们的意图；使用结构体还有别的好处，后面会讲到。

下一个需求：为圆写一个 `Area` 函数。

## 先写测试

```go
func TestArea(t *testing.T) {

	t.Run("rectangles", func(t *testing.T) {
		rectangle := Rectangle{12, 6}
		got := Area(rectangle)
		want := 72.0

		if got != want {
			t.Errorf("got %g want %g", got, want)
		}
	})

	t.Run("circles", func(t *testing.T) {
		circle := Circle{10}
		got := Area(circle)
		want := 314.1592653589793

		if got != want {
			t.Errorf("got %g want %g", got, want)
		}
	})

}
```

如你所见，`f` 换成了 `g`，而且理由充分。
使用 `g` 的话，错误信息里会打印出更精确的小数（见 [fmt 选项](https://golang.org/pkg/fmt/)）。
比如计算半径 1.5 的圆面积时，`f` 会显示 `7.068583`，而 `g` 会显示 `7.0685834705770345`。

## 试着运行测试

`./shapes_test.go:28:13: undefined: Circle`

## 写最少量的代码让测试得以运行，并查看失败的输出

我们需要定义 `Circle` 类型。

```go
type Circle struct {
	Radius float64
}
```

现在再试着跑一次测试

`./shapes_test.go:29:14: cannot use circle (type Circle) as type Rectangle in argument to Area`

有些编程语言允许你写出这样的代码：

```go
func Area(circle Circle) float64       {}
func Area(rectangle Rectangle) float64 {}
```

但在 Go 里不行

`./shapes.go:20:32: Area redeclared in this block`

我们有两个选择：

* 不同的*包*里可以声明同名的函数。所以我们可以在一个新的包里创建 `Area(Circle)`，但在这里感觉有点杀鸡用牛刀。
* 也可以改为在我们新定义的类型上定义[_方法_](https://golang.org/ref/spec#Method_declarations)（method）。

### 方法是什么？

到目前为止我们只写过*函数*，但其实也一直在用方法。调用 `t.Errorf` 时，我们就是在 `t`（`testing.T`）这个实例上调用 `Errorf` 方法。

方法就是带接收者（receiver）的函数。
方法声明会把一个标识符（即方法名）绑定到一个方法上，并将该方法与接收者的基本类型关联起来。

方法跟函数非常相似，但方法要通过某个特定类型的实例来调用。函数可以随时随地想调就调，比如 `Area(rectangle)`；方法却只能调用在“东西”上。

举个例子更容易明白。我们先把测试改成调用方法，然后再去修代码。

```go
func TestArea(t *testing.T) {

	t.Run("rectangles", func(t *testing.T) {
		rectangle := Rectangle{12, 6}
		got := rectangle.Area()
		want := 72.0

		if got != want {
			t.Errorf("got %g want %g", got, want)
		}
	})

	t.Run("circles", func(t *testing.T) {
		circle := Circle{10}
		got := circle.Area()
		want := 314.1592653589793

		if got != want {
			t.Errorf("got %g want %g", got, want)
		}
	})

}
```

如果我们试着运行测试，会得到

```text
./shapes_test.go:19:19: rectangle.Area undefined (type Rectangle has no field or method Area)
./shapes_test.go:29:16: circle.Area undefined (type Circle has no field or method Area)
```

> type Circle has no field or method Area

我想再强调一次，编译器在这里有多好用。花点时间慢慢读懂拿到的报错信息非常重要，从长远看这会让你受益匪浅。

## 写最少量的代码让测试得以运行，并查看失败的输出

给我们的类型加上方法吧

```go
type Rectangle struct {
	Width  float64
	Height float64
}

func (r Rectangle) Area() float64 {
	return 0
}

type Circle struct {
	Radius float64
}

func (c Circle) Area() float64 {
	return 0
}
```

声明方法的语法跟函数几乎一模一样，因为它们实在太像了。唯一的区别是方法接收者的语法：`func (receiverName ReceiverType) MethodName(args)`。

当方法被该类型的一个变量调用时，你就能通过 `receiverName` 变量访问它的数据。在很多其他编程语言里这一步是隐式完成的，你用 `this` 来访问接收者。

Go 的惯例是让接收者变量名取类型名的首字母。

```
r Rectangle
```

再跑一次测试，这次应该能编译通过了，并给你一些失败的输出。

## 写足够的代码让测试通过

现在来修好我们的新方法，让矩形的测试通过

```go
func (r Rectangle) Area() float64 {
	return r.Width * r.Height
}
```

再跑一次测试，矩形的应该过了，圆的应该还在失败。

要让圆的 `Area` 通过，我们从 `math` 包借一个 `Pi` 常量来用（记得导入它）。

```go
func (c Circle) Area() float64 {
	return math.Pi * c.Radius * c.Radius
}
```

## 重构

我们的测试存在一些重复。

我们想做的无非是：取一组*形状*，对它们调用 `Area()` 方法，然后检查结果。

我们想写一个类似 `checkArea` 的函数，`Rectangle` 和 `Circle` 都能传进去，但如果试图传入不是形状的东西，就编译不过。

在 Go 里，我们可以用**接口**（interface）把这一意图固化成代码。

[接口](https://golang.org/ref/spec#Interface_types)在 Go 这样的静态类型语言里是一个非常强大的概念：它让你能写出可以配合不同类型使用的函数，写出高度解耦的代码，同时还保持类型安全。

我们先重构测试，把它引进来。

```go
func TestArea(t *testing.T) {

	checkArea := func(t testing.TB, shape Shape, want float64) {
		t.Helper()
		got := shape.Area()
		if got != want {
			t.Errorf("got %g want %g", got, want)
		}
	}

	t.Run("rectangles", func(t *testing.T) {
		rectangle := Rectangle{12, 6}
		checkArea(t, rectangle, 72.0)
	})

	t.Run("circles", func(t *testing.T) {
		circle := Circle{10}
		checkArea(t, circle, 314.1592653589793)
	})

}
```

我们创建了一个辅助函数，跟其他练习里一样，只是这次要求传入一个 `Shape`。如果拿不是形状的东西去调用它，代码就无法编译。

一个东西怎么才算形状？我们用接口声明告诉 Go `Shape` 是什么就行了

```go
type Shape interface {
	Area() float64
}
```

我们又创建了一个新的 `type`，跟之前的 `Rectangle` 和 `Circle` 一样，只不过这次是 `interface` 而不是 `struct`。

把它加进代码，测试就会通过。

### 等等，这是怎么回事？

这跟大多数其他编程语言里的接口很不一样。通常你得专门写代码声明 `My type Foo implements interface Bar`（我的类型 Foo 实现了接口 Bar）。

但在我们的例子里

* `Rectangle` 有一个叫 `Area` 的方法，返回 `float64`，所以它满足 `Shape` 接口
* `Circle` 有一个叫 `Area` 的方法，返回 `float64`，所以它满足 `Shape` 接口
* `string` 没有这样的方法，所以它不满足这个接口
* 诸如此类

在 Go 里**接口是隐式满足的**。你传入的类型只要符合接口的要求，代码就能编译。

### 解耦

注意，我们的辅助函数完全不必关心形状到底是 `Rectangle`、`Circle` 还是 `Triangle`。通过声明接口，辅助函数与具体类型*解耦*了，手里只留下它干本职工作所需的那个方法。

这种用接口**只声明你需要的东西**的做法在软件设计中非常重要，后面的章节会更详细地讨论。

## 进一步重构

现在你对结构体已经有了一些了解，我们可以介绍“表驱动测试”（table driven tests）了。

当你想构建一组能用同样方式测试的用例时，[表驱动测试](https://go.dev/wiki/TableDrivenTests)就派上用场了。

```go
func TestArea(t *testing.T) {

	areaTests := []struct {
		shape Shape
		want  float64
	}{
		{Rectangle{12, 6}, 72.0},
		{Circle{10}, 314.1592653589793},
	}

	for _, tt := range areaTests {
		got := tt.shape.Area()
		if got != tt.want {
			t.Errorf("got %g want %g", got, tt.want)
		}
	}

}
```

这里唯一的新语法是创建了一个“匿名结构体”（anonymous struct）`areaTests`。我们用 `[]struct` 声明了一个结构体切片，它有两个字段：`shape` 和 `want`。然后往切片里填入一个个用例。

接着我们像遍历其他任何切片一样遍历它们，利用结构体的字段来运行测试。

可以看到，开发者引入一个新形状、实现 `Area`、再把它加进测试用例会非常容易。另外，如果 `Area` 里发现了 bug，也很容易先加一个新用例把问题复现出来，再去修它。

表驱动测试可以成为你工具箱里的一件利器，但要确认你真的需要测试里多出来的这点“噪音”。
当你想测试一个接口的多种实现，或者传入函数的数据有很多不同的条件都需要测到时，它就非常合适。

下面我们再加一个形状并测试它，把上面讲的都演示一遍：三角形。

## 先写测试

给新形状添加一个测试非常容易。只要往列表里添上 `{Triangle{12, 6}, 36.0},` 就行。

```go
func TestArea(t *testing.T) {

	areaTests := []struct {
		shape Shape
		want  float64
	}{
		{Rectangle{12, 6}, 72.0},
		{Circle{10}, 314.1592653589793},
		{Triangle{12, 6}, 36.0},
	}

	for _, tt := range areaTests {
		got := tt.shape.Area()
		if got != tt.want {
			t.Errorf("got %g want %g", got, tt.want)
		}
	}

}
```

## 试着运行测试

记住，不断尝试运行测试，让编译器指引你找到解法。

## 写最少量的代码让测试得以运行，并查看失败的输出

`./shapes_test.go:25:4: undefined: Triangle`

我们还没定义 `Triangle` 呢

```go
type Triangle struct {
	Base   float64
	Height float64
}
```

再试一次

```text
./shapes_test.go:25:8: cannot use Triangle literal (type Triangle) as type Shape in field value:
    Triangle does not implement Shape (missing Area method)
```

它在告诉我们：不能把 `Triangle` 当作形状用，因为它没有 `Area()` 方法。那就先加一个空实现，让测试能跑起来

```go
func (t Triangle) Area() float64 {
	return 0
}
```

代码终于能编译了，我们也等到了那条报错

`shapes_test.go:31: got 0.00 want 36.00`

## 写足够的代码让测试通过

```go
func (t Triangle) Area() float64 {
	return (t.Base * t.Height) * 0.5
}
```

测试全过了！

## 重构

和之前一样，实现没问题，但测试还可以再改进改进。

当你一眼扫过这段

```
{Rectangle{12, 6}, 72.0},
{Circle{10}, 314.1592653589793},
{Triangle{12, 6}, 36.0},
```

这些数字各自代表什么，并不是一眼就能看明白，而你的测试应该力求让人容易理解。

到目前为止，我们只给你看过创建结构体实例的语法 `MyStruct{val1, val2}`，但你还可以选择把字段名写出来。

来看看是什么样子

```
        {shape: Rectangle{Width: 12, Height: 6}, want: 72.0},
        {shape: Circle{Radius: 10}, want: 314.1592653589793},
        {shape: Triangle{Base: 12, Height: 6}, want: 36.0},
```

在《[测试驱动开发](https://g.co/kgs/yCzDLF)》（Test-Driven Development by Example）里，Kent Beck 把一些测试重构到某个程度后断言：

> 测试向我们诉说得更清楚了，仿佛它是一条对事实的断言，**而不是一串操作**

（引文中的强调是我加的）

现在，我们的测试——更确切地说，是那份用例列表——就是在对各个形状及其面积做出事实般的断言。

## 确保测试输出有帮助

还记得前面实现 `Triangle` 时那个失败的测试吗？它打印的是 `shapes_test.go:31: got 0.00 want 36.00`。

我们之所以知道它说的是 `Triangle`，是因为我们刚好正在弄它。
可要是某个 bug 悄悄溜进了表里 20 个用例中的某一个呢？
开发者要怎么知道是哪个用例失败了？
这种体验对开发者来说可不怎么样：他们得手动翻遍所有用例，才能找出真正失败的那一个。

我们可以把错误信息改成 `%#v got %g want %g`。`%#v` 这个格式化字符串会把我们的结构体连同字段里的值一起打印出来，开发者一眼就能看到被测的属性。

为了进一步提升用例的可读性，我们可以把 `want` 字段改成一个更有描述性的名字，比如 `hasArea`。

关于表驱动测试还有最后一条技巧：使用 `t.Run` 并给测试用例起名字。

把每个用例包进 `t.Run`，失败时的测试输出会更清晰，因为它会打印出用例的名字

```text
--- FAIL: TestArea (0.00s)
    --- FAIL: TestArea/Rectangle (0.00s)
        shapes_test.go:33: main.Rectangle{Width:12, Height:6} got 72.00 want 72.10
```

而且可以用 `go test -run TestArea/Rectangle` 只运行表里的某个特定测试。

下面是体现这些要点的最终版测试代码

```go
func TestArea(t *testing.T) {

	areaTests := []struct {
		name    string
		shape   Shape
		hasArea float64
	}{
		{name: "Rectangle", shape: Rectangle{Width: 12, Height: 6}, hasArea: 72.0},
		{name: "Circle", shape: Circle{Radius: 10}, hasArea: 314.1592653589793},
		{name: "Triangle", shape: Triangle{Base: 12, Height: 6}, hasArea: 36.0},
	}

	for _, tt := range areaTests {
		// 使用用例里的 tt.name 作为 `t.Run` 的测试名
		t.Run(tt.name, func(t *testing.T) {
			got := tt.shape.Area()
			if got != tt.hasArea {
				t.Errorf("%#v got %g want %g", tt.shape, got, tt.hasArea)
			}
		})

	}

}
```

## 总结

这又是一次 TDD 练习：围绕基础的数学问题迭代我们的解法，并在测试的驱动下学习新的语言特性。

* 声明结构体来创建自己的数据类型，让你能把相关的数据打包到一起，让代码的意图更清晰
* 声明接口，让你能定义可供不同类型使用的函数（[特设多态](https://en.wikipedia.org/wiki/Ad_hoc_polymorphism)）
* 添加方法，为你的数据类型添加功能，也让你得以实现接口
* 表驱动测试，让你的断言更清晰，让你的测试套件更容易扩展和维护

这是重要的一章，因为我们现在开始定义自己的类型了。在 Go 这样的静态类型语言里，能设计好自己的类型，是构建易于理解、易于拼装、易于测试的软件的关键。

接口是把复杂度对系统的其他部分藏起来的好工具。拿我们的例子来说，测试辅助*代码*并不需要知道它断言的具体是哪个形状，只需要知道怎么“索要”它的面积。

等你对 Go 越来越熟悉，你会开始体会到接口与标准库的真正威力。你会了解到标准库里定义的那些*到处都在用*的接口——只要在自己的类型上实现它们，你就能非常快地复用大量优秀的功能。
