# 反射

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/reflection)**

[来自 X](https://x.com/peterbourgon/status/1011403901419937792?s=09)

> golang 挑战：写一个函数 `walk(x interface{}, fn func(string))`，接收一个结构体 `x`，对 `x` 里找到的所有 string 字段都调用一次 `fn`。难度等级：递归地。

要做到这一点，我们需要用上_反射_（reflection）。

> 计算机领域的反射，指的是程序检视自身结构的能力，尤其是通过类型来检视；它是元编程（metaprogramming）的一种形式。同时也是制造困惑的一大源泉。

来自 [Go 官方博客《反射定律》](https://blog.golang.org/laws-of-reflection)

## 什么是 `interface{}`？

一直以来，我们都在享受 Go 类型安全（type safety）带来的好处：函数处理的都是已知类型，比如 `string`、`int`，还有我们自己定义的 `BankAccount` 之类的类型。

这意味着我们能白得一份“文档”，而且一旦把错误的类型传给函数，编译器就会立刻抱怨。

不过你迟早会碰到这样的场景：想写一个函数，可在编译期还不知道传进来的类型是什么。

Go 给我们的解法是 `interface{}` 类型，你可以把它理解为_任意_类型（实际上，Go 里的 `any` 就是 `interface{}` 的一个[别名](https://cs.opensource.google/go/go/+/master:src/builtin/builtin.go;drc=master;l=95)）。

所以 `walk(x interface{}, fn func(string))` 的参数 `x` 可以接收任何值。

### 那为什么不干脆全都用 `interface{}`，写出一堆超级灵活的函数呢？

- 对函数的_使用者_来说，接收 `interface{}` 意味着失去类型安全。假如你本想传 `string` 类型的 `Herd.species`，结果手一滑传成了 `int` 类型的 `Herd.count`，编译器可没办法提醒你犯错了。而且你也完全不知道_到底_什么才能传给这个函数。知道函数接收的是 `UserService`，这个信息本身就非常有用。
- 对这种函数的_作者_来说，你必须有能力检视传进来的_任何东西_，弄清楚它是什么类型、能拿它做什么。这就要靠_反射_来做了。反射代码往往相当笨拙、难以阅读，性能通常也更差（因为你必须在运行时做各种检查）。

一句话：除非真的需要，否则别用反射。

如果你想要的是多态函数，先想想能不能围绕接口（interface，注意不是 `interface{}`，确实很容易搞混）来设计。这样只要使用者的类型实现了你的函数正常工作所需的那些方法，就能用这一个函数处理多种类型。

我们的函数需要能应对五花八门的东西。老规矩，我们采用迭代的方式：每想支持一种新东西，就先为它写测试，一路重构，直到完工。

## 先写测试

我们想用一个带 string 字段的结构体（`x`）去调用函数，然后 spy（监视）传进来的函数 `fn`，看它有没有被调用。

```go
func TestWalk(t *testing.T) {

	expected := "Chris"
	var got []string

	x := struct {
		Name string
	}{expected}

	walk(x, func(input string) {
		got = append(got, input)
	})

	if len(got) != 1 {
		t.Errorf("wrong number of function calls, got %d want %d", len(got), 1)
	}
}
```

- 我们需要一个 string 切片（`got`），用来记录 `walk` 传给 `fn` 的都是哪些字符串。在前几章里，我们常常为此专门定义一些类型，用它们 spy 函数/方法的调用；但这次我们只需给 `fn` 传一个匿名函数（anonymous function），它在闭包（closure）中捕获了 `got`。
- 我们用一个带 `Name` 字段（string 类型）的匿名结构体（anonymous struct）来走最简单的“快乐路径”（happy path）。
- 最后，把 `x` 和那个 spy 一起传给 `walk`，眼下只检查 `got` 的长度就够了；等最基本的东西跑通了，我们再把断言写得更具体。

## 试着运行测试

```
./reflection_test.go:21:2: undefined: walk
```

## 写最少的代码让测试能运行，并检查失败的测试输出

我们需要定义 `walk`

```go
func walk(x interface{}, fn func(input string)) {

}
```

再试着运行一次测试

```
=== RUN   TestWalk
--- FAIL: TestWalk (0.00s)
    reflection_test.go:19: wrong number of function calls, got 0 want 1
FAIL
```

## 写足够的代码让测试通过

随便传个字符串给 spy 就能让测试通过。

```go
func walk(x interface{}, fn func(input string)) {
	fn("I still can't believe South Korea beat Germany 2-0 to put them last in their group")
}
```

测试现在应该过了。接下来我们要做的，是对 `fn` 被调用时收到的参数做更具体的断言。

## 先写测试

在现有测试里加上下面几行，检查传给 `fn` 的字符串对不对

```go
if got[0] != expected {
	t.Errorf("got %q, want %q", got[0], expected)
}
```

## 试着运行测试

```
=== RUN   TestWalk
--- FAIL: TestWalk (0.00s)
    reflection_test.go:23: got 'I still can't believe South Korea beat Germany 2-0 to put them last in their group', want 'Chris'
FAIL
```

## 写足够的代码让测试通过

```go
func walk(x interface{}, fn func(input string)) {
	val := reflect.ValueOf(x)
	field := val.Field(0)
	fn(field.String())
}
```

这段代码_非常不安全，也非常天真_，但记住：处于“红灯”状态（测试失败）时，我们的目标是写出尽可能少的代码。之后我们再写更多测试来解决自己的顾虑。

我们需要用反射来检视 `x`，看看它都有哪些属性。

[reflect 包](https://pkg.go.dev/reflect)提供了一个函数 `ValueOf`，它会返回给定变量的一个 `Value`。`Value` 上有一系列检视值的方法，其中就包括获取字段——下一行用到的正是它。

接着，我们对传进来的值做了一些非常乐观的假设：

- 我们只看了第一个字段，并默认它是唯一的字段。但值里可能压根没有字段，那就会 panic。
- 然后我们调用了 `String()`，它会把底层值按字符串返回。但如果这个字段根本不是 string，这么调用就是错的。

## 重构

简单场景下代码已经能通过，但我们知道它还有不少短板。

接下来我们会写一批测试：传入不同的值，检查 `fn` 被调用时收到的字符串数组。

我们应该把测试重构成表驱动测试，这样之后继续添加新场景会容易得多。

```go
func TestWalk(t *testing.T) {

	cases := []struct {
		Name          string
		Input         interface{}
		ExpectedCalls []string
	}{
		{
			"struct with one string field",
			struct {
				Name string
			}{"Chris"},
			[]string{"Chris"},
		},
	}

	for _, test := range cases {
		t.Run(test.Name, func(t *testing.T) {
			var got []string
			walk(test.Input, func(input string) {
				got = append(got, input)
			})

			if !reflect.DeepEqual(got, test.ExpectedCalls) {
				t.Errorf("got %v, want %v", got, test.ExpectedCalls)
			}
		})
	}
}
```

现在我们可以轻松添加一个场景，看看有不止一个 string 字段时会怎样。

## 先写测试

在 `cases` 里加上下面这个场景。

```
{
    "struct with two string fields",
    struct {
        Name string
        City string
    }{"Chris", "London"},
    []string{"Chris", "London"},
},
```

## 试着运行测试

```
=== RUN   TestWalk/struct_with_two_string_fields
    --- FAIL: TestWalk/struct_with_two_string_fields (0.00s)
        reflection_test.go:40: got [Chris], want [Chris London]
```

## 写足够的代码让测试通过

```go
func walk(x interface{}, fn func(input string)) {
	val := reflect.ValueOf(x)

	for i := 0; i < val.NumField(); i++ {
		field := val.Field(i)
		fn(field.String())
	}
}
```

`val` 上有一个 `NumField` 方法，返回这个值里的字段数量。有了它，我们就能遍历所有字段并逐一调用 `fn`，测试也随之通过。

## 重构

眼下看不出有什么能让代码明显变好的重构，我们继续前进。

`walk` 的下一个短板是：它假设每个字段都是 `string`。我们来给这个场景写个测试。

## 先写测试

加上下面这个用例

```
{
    "struct with non string field",
    struct {
        Name string
        Age  int
    }{"Chris", 33},
    []string{"Chris"},
},
```

## 试着运行测试

```
=== RUN   TestWalk/struct_with_non_string_field
    --- FAIL: TestWalk/struct_with_non_string_field (0.00s)
        reflection_test.go:46: got [Chris <int Value>], want [Chris]
```

## 写足够的代码让测试通过

我们需要检查字段的类型是不是 `string`。

```go
func walk(x interface{}, fn func(input string)) {
	val := reflect.ValueOf(x)

	for i := 0; i < val.NumField(); i++ {
		field := val.Field(i)

		if field.Kind() == reflect.String {
			fn(field.String())
		}
	}
}
```

这可以借助它的 [`Kind`](https://pkg.go.dev/reflect#Kind) 来判断。

## 重构

同样，这段代码目前看来还算像样。

下一个场景：如果传进来的不是一个“扁平”的 `struct` 呢？换句话说，`struct` 里带嵌套字段时会发生什么？

## 先写测试

我们一直在测试里用匿名结构体语法临时声明类型，所以可以继续这么写：

```
{
    "nested fields",
    struct {
        Name string
        Profile struct {
            Age  int
            City string
        }
    }{"Chris", struct {
        Age  int
        City string
    }{33, "London"}},
    []string{"Chris", "London"},
},
```

但可以看出来，一旦涉及内层的匿名结构体，语法就有点乱了。[有一个提案想让这套语法更友好一些](https://github.com/golang/go/issues/12854)。

不如干脆重构一下：为这个场景定义一个正经的类型，然后在测试里引用它。这样做多了一层间接——测试的一部分代码跑到了测试外面——但读者应该能从初始化的写法中推断出这个 `struct` 的结构。

在测试文件的任意位置加上下面这些类型声明

```go
type Person struct {
	Name    string
	Profile Profile
}

type Profile struct {
	Age  int
	City string
}
```

现在把它加进我们的用例里，读起来比之前清晰多了

```
{
    "nested fields",
    Person{
        "Chris",
        Profile{33, "London"},
    },
    []string{"Chris", "London"},
},
```

## 试着运行测试

```
=== RUN   TestWalk/Nested_fields
    --- FAIL: TestWalk/nested_fields (0.00s)
        reflection_test.go:54: got [Chris], want [Chris London]
```

问题在于：我们只遍历了类型层级中第一层的字段。

## 写足够的代码让测试通过

```go
func walk(x interface{}, fn func(input string)) {
	val := reflect.ValueOf(x)

	for i := 0; i < val.NumField(); i++ {
		field := val.Field(i)

		if field.Kind() == reflect.String {
			fn(field.String())
		}

		if field.Kind() == reflect.Struct {
			walk(field.Interface(), fn)
		}
	}
}
```

解法相当简单：我们再次检视 `Kind`，如果它恰好是 `struct`，就对内层那个 `struct` 再调用一次 `walk`。

## 重构

```go
func walk(x interface{}, fn func(input string)) {
	val := reflect.ValueOf(x)

	for i := 0; i < val.NumField(); i++ {
		field := val.Field(i)

		switch field.Kind() {
		case reflect.String:
			fn(field.String())
		case reflect.Struct:
			walk(field.Interface(), fn)
		}
	}
}
```

当你对同一个值做了不止一次比较时，_一般_来说，重构成 `switch` 能提升可读性，也让代码更容易扩展。

那如果传进来的结构体值是个指针呢？

## 先写测试

加上这个用例

```
{
    "pointers to things",
    &Person{
        "Chris",
        Profile{33, "London"},
    },
    []string{"Chris", "London"},
},
```

## 试着运行测试

```
=== RUN   TestWalk/pointers_to_things
panic: reflect: call of reflect.Value.NumField on ptr Value [recovered]
    panic: reflect: call of reflect.Value.NumField on ptr Value
```

## 写足够的代码让测试通过

```go
func walk(x interface{}, fn func(input string)) {
	val := reflect.ValueOf(x)

	if val.Kind() == reflect.Pointer {
		val = val.Elem()
	}

	for i := 0; i < val.NumField(); i++ {
		field := val.Field(i)

		switch field.Kind() {
		case reflect.String:
			fn(field.String())
		case reflect.Struct:
			walk(field.Interface(), fn)
		}
	}
}
```

指针类型的 `Value` 上不能用 `NumField`，我们得先用 `Elem()` 把底层值取出来才行。

## 重构

我们把“从给定的 `interface{}` 中取出 `reflect.Value`”这一职责封装成一个函数。

```go
func walk(x interface{}, fn func(input string)) {
	val := getValue(x)

	for i := 0; i < val.NumField(); i++ {
		field := val.Field(i)

		switch field.Kind() {
		case reflect.String:
			fn(field.String())
		case reflect.Struct:
			walk(field.Interface(), fn)
		}
	}
}

func getValue(x interface{}) reflect.Value {
	val := reflect.ValueOf(x)

	if val.Kind() == reflect.Pointer {
		val = val.Elem()
	}

	return val
}
```

这样其实_多_写了一些代码，但我觉得抽象的层次刚刚好。

- 拿到 `x` 的 `reflect.Value`，这样我就能检视它，至于怎么拿到的，我不关心。
- 遍历各个字段，根据字段的类型做该做的事。

接下来，我们需要支持切片。

## 先写测试

```
{
    "slices",
    []Profile {
        {33, "London"},
        {34, "Reykjavík"},
    },
    []string{"London", "Reykjavík"},
},
```

## 试着运行测试

```
=== RUN   TestWalk/slices
panic: reflect: call of reflect.Value.NumField on slice Value [recovered]
    panic: reflect: call of reflect.Value.NumField on slice Value
```

## 写最少的代码让测试能运行，并检查失败的测试输出

这和之前的指针场景类似：我们试图在 `reflect.Value` 上调用 `NumField`，但它不是 struct，所以根本没有这个方法。

## 写足够的代码让测试通过

```go
func walk(x interface{}, fn func(input string)) {
	val := getValue(x)

	if val.Kind() == reflect.Slice {
		for i := 0; i < val.Len(); i++ {
			walk(val.Index(i).Interface(), fn)
		}
		return
	}

	for i := 0; i < val.NumField(); i++ {
		field := val.Field(i)

		switch field.Kind() {
		case reflect.String:
			fn(field.String())
		case reflect.Struct:
			walk(field.Interface(), fn)
		}
	}
}
```

## 重构

能跑了，但实在有点恶心。别担心，我们有测试撑腰、能正常工作的代码，想怎么折腾都行。

稍微抽象一点想，我们要对下面两种东西调用 `walk`：

- struct 里的每个字段
- 切片里的每个_元素_

我们现在的代码确实做到了这件事，但代码没能把这一点体现出来。它只是在开头检查了一下是不是切片（是的话就 `return`，不再执行后面的代码），不是的话就默认它是个 struct。

我们来改写代码，改成_先_判断类型，然后再干活。

```go
func walk(x interface{}, fn func(input string)) {
	val := getValue(x)

	switch val.Kind() {
	case reflect.Struct:
		for i := 0; i < val.NumField(); i++ {
			walk(val.Field(i).Interface(), fn)
		}
	case reflect.Slice:
		for i := 0; i < val.Len(); i++ {
			walk(val.Index(i).Interface(), fn)
		}
	case reflect.String:
		fn(val.String())
	}
}
```

好看多了！如果是 struct 或切片，就遍历其中的值，对每个值调用 `walk`；否则，如果是 `reflect.String`，就直接调用 `fn`。

不过在我看来，它还能更好。遍历字段/值然后调用 `walk` 的操作重复出现了两次，但概念上它们明明是同一回事。

```go
func walk(x interface{}, fn func(input string)) {
	val := getValue(x)

	numberOfValues := 0
	var getField func(int) reflect.Value

	switch val.Kind() {
	case reflect.String:
		fn(val.String())
	case reflect.Struct:
		numberOfValues = val.NumField()
		getField = val.Field
	case reflect.Slice:
		numberOfValues = val.Len()
		getField = val.Index
	}

	for i := 0; i < numberOfValues; i++ {
		walk(getField(i).Interface(), fn)
	}
}
```

如果这个 `value` 是 `reflect.String`，那就照常调用 `fn`。

否则，我们的 `switch` 会根据类型提取出两样东西：

- 有多少个值
- 怎么把 `Value` 取出来（用 `Field` 还是 `Index`）

一旦确定了这两件事，我们就能循环 `numberOfValues` 次，用 `getField` 函数的结果去调用 `walk`。

做到这一步，支持数组就是小菜一碟了。

## 先写测试

往用例里加

```
{
    "arrays",
    [2]Profile {
        {33, "London"},
        {34, "Reykjavík"},
    },
    []string{"London", "Reykjavík"},
},
```

## 试着运行测试

```
=== RUN   TestWalk/arrays
    --- FAIL: TestWalk/arrays (0.00s)
        reflection_test.go:78: got [], want [London Reykjavík]
```

## 写足够的代码让测试通过

数组可以用和切片完全一样的方式处理，所以只需用逗号把它加进同一个 case

```go
func walk(x interface{}, fn func(input string)) {
	val := getValue(x)

	numberOfValues := 0
	var getField func(int) reflect.Value

	switch val.Kind() {
	case reflect.String:
		fn(val.String())
	case reflect.Struct:
		numberOfValues = val.NumField()
		getField = val.Field
	case reflect.Slice, reflect.Array:
		numberOfValues = val.Len()
		getField = val.Index
	}

	for i := 0; i < numberOfValues; i++ {
		walk(getField(i).Interface(), fn)
	}
}
```

下一个要支持的类型是 `map`。

## 先写测试

```
{
    "maps",
    map[string]string{
        "Cow": "Moo",
        "Sheep": "Baa",
    },
    []string{"Moo", "Baa"},
},
```

## 试着运行测试

```
=== RUN   TestWalk/maps
    --- FAIL: TestWalk/maps (0.00s)
        reflection_test.go:86: got [], want [Moo Baa]
```

## 写足够的代码让测试通过

再抽象地想一下，你会发现 `map` 跟 `struct` 非常相似，只不过它的 key 在编译期是未知的。

```go
func walk(x interface{}, fn func(input string)) {
	val := getValue(x)

	numberOfValues := 0
	var getField func(int) reflect.Value

	switch val.Kind() {
	case reflect.String:
		fn(val.String())
	case reflect.Struct:
		numberOfValues = val.NumField()
		getField = val.Field
	case reflect.Slice, reflect.Array:
		numberOfValues = val.Len()
		getField = val.Index
	case reflect.Map:
		for _, key := range val.MapKeys() {
			walk(val.MapIndex(key).Interface(), fn)
		}
	}

	for i := 0; i < numberOfValues; i++ {
		walk(getField(i).Interface(), fn)
	}
}
```

然而，按照设计，你没法按下标从 map 里取值，只能按_键_取，这下我们的抽象被打破了，真气人。

## 重构

你现在感觉如何？当时觉得这是个挺漂亮的抽象，可现在这份代码就有点别扭了。

_这很正常！_重构是一场旅程，我们难免会犯点错。TDD 的一大意义，就是给了我们放手尝试的自由。

只要小步前进、测试护航，就没有什么是不可挽回的。我们把代码改回重构之前的样子就好。

```go
func walk(x interface{}, fn func(input string)) {
	val := getValue(x)

	walkValue := func(value reflect.Value) {
		walk(value.Interface(), fn)
	}

	switch val.Kind() {
	case reflect.String:
		fn(val.String())
	case reflect.Struct:
		for i := 0; i < val.NumField(); i++ {
			walkValue(val.Field(i))
		}
	case reflect.Slice, reflect.Array:
		for i := 0; i < val.Len(); i++ {
			walkValue(val.Index(i))
		}
	case reflect.Map:
		for _, key := range val.MapKeys() {
			walkValue(val.MapIndex(key))
		}
	}
}
```

我们引入了 `walkValue`，把 `switch` 里对 `walk` 的调用去重（DRY）了，这样各个分支只需要从 `val` 中取出 `reflect.Value`。

### 最后一个问题

别忘了，Go 的 map 不保证顺序。所以你的测试有时会失败，因为我们断言了对 `fn` 的调用要按特定顺序发生。

要解决这个问题，我们需要把针对 map 的断言挪到一个新的测试里，在那个测试中我们不关心顺序。

```go
t.Run("with maps", func(t *testing.T) {
	aMap := map[string]string{
		"Cow":   "Moo",
		"Sheep": "Baa",
	}

	var got []string
	walk(aMap, func(input string) {
		got = append(got, input)
	})

	assertContains(t, got, "Moo")
	assertContains(t, got, "Baa")
})
```

`assertContains` 的定义如下

```go
func assertContains(t testing.TB, haystack []string, needle string) {
	t.Helper()
	contains := false
	for _, x := range haystack {
		if x == needle {
			contains = true
		}
	}
	if !contains {
		t.Errorf("expected %v to contain %q but it didn't", haystack, needle)
	}
}
```

把 map 挪进新测试后，我们还没见过它的失败信息。这里请故意把 `with maps` 测试弄挂，亲眼确认一下错误信息，然后再修好，让所有测试通过。

我们放弃了对 `got` _顺序_的检查，因为 map 本来就不保证顺序，但这不意味着要对 `got` 的“形状”全盘撒手。只靠 `assertContains` 的话，就算 `walk` 把某个 map 条目访问了两次，或者漏掉一个、只检查了剩下的条目，测试照样会通过——只要我们找的那些值出现在某个地方，出现几次都无所谓。跟顺序不同，`got` 的_长度_与 map 的遍历顺序无关，完全可以预测，所以我们也对它加断言。

```go
func assertLength(t testing.TB, got []string, want int) {
	t.Helper()
	if len(got) != want {
		t.Errorf("got %d values but expected %d", len(got), want)
	}
}
```

在 `with maps` 测试的开头加上对它的调用。

```go
t.Run("with maps", func(t *testing.T) {
	aMap := map[string]string{
		"Cow":   "Moo",
		"Sheep": "Baa",
	}

	var got []string
	walk(aMap, func(input string) {
		got = append(got, input)
	})

	assertLength(t, got, len(aMap))
	assertContains(t, got, "Moo")
	assertContains(t, got, "Baa")
})
```

下一个要支持的类型是 `chan`。

## 先写测试

```go
t.Run("with channels", func(t *testing.T) {
	aChannel := make(chan Profile)

	go func() {
		aChannel <- Profile{33, "Berlin"}
		aChannel <- Profile{34, "Katowice"}
		close(aChannel)
	}()

	var got []string
	want := []string{"Berlin", "Katowice"}

	walk(aChannel, func(input string) {
		got = append(got, input)
	})

	if !reflect.DeepEqual(got, want) {
		t.Errorf("got %v, want %v", got, want)
	}
})
```

## 试着运行测试

```
--- FAIL: TestWalk (0.00s)
    --- FAIL: TestWalk/with_channels (0.00s)
        reflection_test.go:115: got [], want [Berlin Katowice]
```

## 写足够的代码让测试通过

我们可以用 `Recv()` 一直读取 channel（通道）里发来的值，直到它被关闭为止

```go
func walk(x interface{}, fn func(input string)) {
	val := getValue(x)

	walkValue := func(value reflect.Value) {
		walk(value.Interface(), fn)
	}

	switch val.Kind() {
	case reflect.String:
		fn(val.String())
	case reflect.Struct:
		for i := 0; i < val.NumField(); i++ {
			walkValue(val.Field(i))
		}
	case reflect.Slice, reflect.Array:
		for i := 0; i < val.Len(); i++ {
			walkValue(val.Index(i))
		}
	case reflect.Map:
		for _, key := range val.MapKeys() {
			walkValue(val.MapIndex(key))
		}
	case reflect.Chan:
		for {
			if v, ok := val.Recv(); ok {
				walkValue(v)
			} else {
				break
			}
		}
	}
}
```

下一个要支持的类型是 `func`。

## 先写测试

```go
t.Run("with function", func(t *testing.T) {
	aFunction := func() (Profile, Profile) {
		return Profile{33, "Berlin"}, Profile{34, "Katowice"}
	}

	var got []string
	want := []string{"Berlin", "Katowice"}

	walk(aFunction, func(input string) {
		got = append(got, input)
	})

	if !reflect.DeepEqual(got, want) {
		t.Errorf("got %v, want %v", got, want)
	}
})
```

## 试着运行测试

```
--- FAIL: TestWalk (0.00s)
    --- FAIL: TestWalk/with_function (0.00s)
        reflection_test.go:132: got [], want [Berlin Katowice]
```

## 写足够的代码让测试通过

在这个场景里，接收非零个参数的函数似乎说不太通。但我们应该允许任意多的返回值。

```go
func walk(x interface{}, fn func(input string)) {
	val := getValue(x)

	walkValue := func(value reflect.Value) {
		walk(value.Interface(), fn)
	}

	switch val.Kind() {
	case reflect.String:
		fn(val.String())
	case reflect.Struct:
		for i := 0; i < val.NumField(); i++ {
			walkValue(val.Field(i))
		}
	case reflect.Slice, reflect.Array:
		for i := 0; i < val.Len(); i++ {
			walkValue(val.Index(i))
		}
	case reflect.Map:
		for _, key := range val.MapKeys() {
			walkValue(val.MapIndex(key))
		}
	case reflect.Chan:
		for v, ok := val.Recv(); ok; v, ok = val.Recv() {
			walkValue(v)
		}
	case reflect.Func:
		valFnResult := val.Call(nil)
		for _, res := range valFnResult {
			walkValue(res)
		}
	}
}
```

## 总结

- 介绍了 `reflect` 包里的一些概念。
- 用递归遍历了任意的数据结构。
- 做了一次事后回想挺糟糕的重构，但也没太往心里去。配合测试迭代开发，这真不算什么大事。
- 这里只讲了反射的一小部分。[Go 博客上有一篇非常棒的文章，涵盖了更多细节](https://blog.golang.org/laws-of-reflection)。
- 既然你已经了解反射了，那就请尽全力避免使用它。

### 已知局限：循环引用

如果传给 `walk` 的结构体里有一个指回自身的指针（或者任何由指针构成的环），它就会栈溢出（stack overflow）。比如：

```go
type Person struct {
    Name   string
    Friend *Person
}
p := Person{Name: "Alice"}
p.Friend = &p  // 循环引用！
walk(p, fn)  // fatal error: stack overflow
```

修复这个问题留作练习。标准做法是记录下哪些指针地址已经访问过，再次遇到时直接跳过。你会需要一个 `map[uintptr]bool`——`uintptr` 是指针的原始数字地址，对指针 kind 的值可以通过 `reflect.Value.Pointer()` 拿到。由于这个 map 需要在整个遍历过程中一直存在，你会希望由一个内部辅助函数把它作为参数一路携带，公开的 `walk` 负责创建这个 map 并调用它。
