# 基于属性的测试入门

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/roman-numerals)**

有些公司在面试环节会让你做[罗马数字 Kata](http://codingdojo.org/kata/RomanNumerals/)——Kata 是编程道场里的练习题。本章就带你看看怎么用 TDD 拿下它。

我们要写一个函数，把[阿拉伯数字](https://en.wikipedia.org/wiki/Arabic_numerals)（0 到 9）表示的数转换成罗马数字。

如果你没听说过[罗马数字](https://en.wikipedia.org/wiki/Roman_numerals)，先补一句：它就是罗马人记数的方式。

把符号拼在一起就能组成罗马数字，这些符号各自代表一个数

所以 `I` 是"一"，`III` 是三。

看着挺简单，但有几条有意思的规则。`V` 表示五，而 4 要写成 `IV`（不是 `IIII`）。

`MCMLXXXIV` 是 1984。这看上去就复杂多了，很难一开始就想清楚怎么写代码把它搞定。

正如本书一直强调的，软件开发者的一项关键技能，是学会从*有用的*功能里切出"瘦垂直切片"（thin vertical slices），然后**持续迭代**。TDD 工作流恰好能助推这种迭代式开发。

所以先别急着奔向 1984，我们从 1 开始。

## 先写测试

```go
func TestRomanNumerals(t *testing.T) {
	got := ConvertToRoman(1)
	want := "I"

	if got != want {
		t.Errorf("got %q, want %q", got, want)
	}
}
```

如果你一路读到了这里，希望这一步对你来说已经无聊透顶、纯属例行公事了。这是好事。

## 试着运行测试

```console
./numeral_test.go:6:9: undefined: ConvertToRoman
```

让编译器为我们指路

## 写出刚好能让测试运行的最少代码，并检查失败测试的输出

把函数创建出来，但先别让测试通过——永远要确认测试按你预期的方式失败

```go
func ConvertToRoman(arabic int) string {
	return ""
}
```

现在测试应该能运行了

```console
=== RUN   TestRomanNumerals
--- FAIL: TestRomanNumerals (0.00s)
    numeral_test.go:10: got '', want 'I'
FAIL
```

## 写足够的代码让测试通过

```go
func ConvertToRoman(arabic int) string {
	return "I"
}
```

## 重构

暂时还没什么好重构的。

*我知道*，直接把结果硬编码进去感觉怪怪的，但玩 TDD 时，我们要尽可能久地不让自己停留在"红"的状态。*感觉上*我们没干成什么，但我们已经定义了 API，还让一个测试捕获住了一条规则——哪怕"真正的"代码相当蠢。

接着就带着这份不安，去写一个新测试，逼自己把代码写得稍微不那么蠢。

## 先写测试

我们可以用子测试把用例归置得漂漂亮亮

```go
func TestRomanNumerals(t *testing.T) {
	t.Run("1 gets converted to I", func(t *testing.T) {
		got := ConvertToRoman(1)
		want := "I"

		if got != want {
			t.Errorf("got %q, want %q", got, want)
		}
	})

	t.Run("2 gets converted to II", func(t *testing.T) {
		got := ConvertToRoman(2)
		want := "II"

		if got != want {
			t.Errorf("got %q, want %q", got, want)
		}
	})
}
```

## 试着运行测试

```console
=== RUN   TestRomanNumerals/2_gets_converted_to_II
    --- FAIL: TestRomanNumerals/2_gets_converted_to_II (0.00s)
        numeral_test.go:20: got 'I', want 'II'
```

没什么意外。

## 写足够的代码让测试通过

```go
func ConvertToRoman(arabic int) string {
	if arabic == 2 {
		return "II"
	}
	return "I"
}
```

是的，感觉还是没真正在解决问题。所以我们得写更多测试，推着自己往前走。

## 重构

我们的测试里出现了重复。当你在测的东西感觉上就是"给定输入 X，期望输出 Y"时，多半就该用表驱动测试了。

```go
func TestRomanNumerals(t *testing.T) {
	cases := []struct {
		Description string
		Arabic      int
		Want        string
	}{
		{"1 gets converted to I", 1, "I"},
		{"2 gets converted to II", 2, "II"},
	}

	for _, test := range cases {
		t.Run(test.Description, func(t *testing.T) {
			got := ConvertToRoman(test.Arabic)
			if got != test.Want {
				t.Errorf("got %q, want %q", got, test.Want)
			}
		})
	}
}
```

这下再加用例就轻松了，不用再写任何测试样板代码。

一鼓作气，冲向 3

## 先写测试

往 cases 里加一条

```
{"3 gets converted to III", 3, "III"},
```

## 试着运行测试

```console
=== RUN   TestRomanNumerals/3_gets_converted_to_III
    --- FAIL: TestRomanNumerals/3_gets_converted_to_III (0.00s)
        numeral_test.go:20: got 'I', want 'III'
```

## 写足够的代码让测试通过

```go
func ConvertToRoman(arabic int) string {
	if arabic == 3 {
		return "III"
	}
	if arabic == 2 {
		return "II"
	}
	return "I"
}
```

## 重构

好了，我开始受不了这些 if 语句了；把代码盯得够久你会发现，我们其实是在按 `arabic` 的大小拼一串 `I`。

我们"知道"，数字再复杂一点，就得做些算术运算加字符串拼接了。

带着这些念头试一把重构，它*未必*就是最终方案，但没关系。手里有测试指路，随时可以推倒代码从头再来。

```go
func ConvertToRoman(arabic int) string {

	var result strings.Builder

	for i := 0; i < arabic; i++ {
		result.WriteString("I")
	}

	return result.String()
}
```

你可能还记得 [`strings.Builder`](https://golang.org/pkg/strings/#Builder)，我们在讲[基准测试](iteration.md#基准测试)时提过它

> Builder 用来通过 Write 方法高效地构建字符串，能尽量减少内存拷贝。

一般来说，没碰上真实的性能问题我不会折腾这类优化，但这段代码比"手动"拼接字符串也没多写几行，那不妨直接用更快的写法。

在我看来代码更顺眼了，而且描述了*我们眼下所认识的*领域。

### 罗马人也深谙 DRY 之道……

事情从现在开始变复杂了。罗马人很有智慧地意识到，字符重复太多会不好认、不好数。所以罗马数字有条规则：同一个字符连续重复不能超过 3 次。

作为替代，你要取高一级的符号，然后在它左边放一个符号来"做减法"。不是所有符号都能当减数（subtractor），只有 I（1）、X（10）和 C（100）可以。

比如罗马数字里 `5` 是 `V`。要表示 4，不写 `IIII`，而是写 `IV`。

减数只能放在它"家族"里比它高一级或高两级的符号前面：`I` 只能放在 `V` 或 `X` 前面（4 是 `IV`，9 是 `IX`），`X` 只能放在 `L` 或 `C` 前面（40 是 `XL`，90 是 `XC`），`C` 只能放在 `D` 或 `M` 前面（400 是 `CD`，900 是 `CM`）。所以尽管 `I`、`X`、`C` 都是合法的减数，也不能随意混搭——99 不是 `IC`（而是 `XCIX`，90 + 9），499 也不是 `ID`（而是 `CDXCIX`，400 + 90 + 9）。

## 先写测试

```
{"4 gets converted to IV (can't repeat more than 3 times)", 4, "IV"},
```

## 试着运行测试

```console
=== RUN   TestRomanNumerals/4_gets_converted_to_IV_(cant_repeat_more_than_3_times)
    --- FAIL: TestRomanNumerals/4_gets_converted_to_IV_(cant_repeat_more_than_3_times) (0.00s)
        numeral_test.go:24: got 'IIII', want 'IV'
```

## 写足够的代码让测试通过

```go
func ConvertToRoman(arabic int) string {

	if arabic == 4 {
		return "IV"
	}

	var result strings.Builder

	for i := 0; i < arabic; i++ {
		result.WriteString("I")
	}

	return result.String()
}
```

## 重构

我们把"拼字符串"的模式给破坏了，我对此不"满意"，我想把它延续下去。

```go
func ConvertToRoman(arabic int) string {

	var result strings.Builder

	for i := arabic; i > 0; i-- {
		if i == 4 {
			result.WriteString("IV")
			break
		}
		result.WriteString("I")
	}

	return result.String()
}
```

为了让 4 能"塞进"我当前的思路，现在改成从阿拉伯数往下数，一边数一边往字符串里添加符号。不确定这招长远来看行不行，走着瞧！

来让 5 跑通

## 先写测试

```
{"5 gets converted to V", 5, "V"},
```

## 试着运行测试

```console
=== RUN   TestRomanNumerals/5_gets_converted_to_V
    --- FAIL: TestRomanNumerals/5_gets_converted_to_V (0.00s)
        numeral_test.go:25: got 'IIV', want 'V'
```

## 写足够的代码让测试通过

照搬 4 的套路就行

```go
func ConvertToRoman(arabic int) string {

	var result strings.Builder

	for i := arabic; i > 0; i-- {
		if i == 5 {
			result.WriteString("V")
			break
		}
		if i == 4 {
			result.WriteString("IV")
			break
		}
		result.WriteString("I")
	}

	return result.String()
}
```

## 重构

循环里出现这样的重复，通常说明有个抽象在等着被提取出来。让循环提前退出（短路）是提升可读性的利器，但它也可能在暗示你别的事情。

我们在阿拉伯数上循环，碰到特定符号就调用 `break`，但我们*真正*在做的事，其实是以一种笨拙的方式对 `i` 做减法。

```go
func ConvertToRoman(arabic int) string {

	var result strings.Builder

	for arabic > 0 {
		switch {
		case arabic > 4:
			result.WriteString("V")
			arabic -= 5
		case arabic > 3:
			result.WriteString("IV")
			arabic -= 4
		default:
			result.WriteString("I")
			arabic--
		}
	}

	return result.String()
}
```

- 从代码传递出的信号看（这些信号来自我们对一些非常基础场景的测试），我意识到：要构建罗马数字，就得在应用符号的同时从 `arabic` 里做减法
- `for` 循环不再依赖 `i`，而是不断拼我们的字符串，直到从 `arabic` 里减掉了足够的符号值。

我很确定这套做法对 6（VI）、7（VII）和 8（VIII）同样适用。尽管如此，还是把这些用例加进测试套件验证一下（为省篇幅我就不贴代码了，心里没底就去 GitHub 上看示例）。

9 跟 4 是同一条规则：应该从下一个数的表示里减去 `I`。10 在罗马数字里用 `X` 表示，所以 9 就应该是 `IX`。

## 先写测试

```
{"9 gets converted to IX", 9, "IX"},
```

## 试着运行测试

```console
=== RUN   TestRomanNumerals/9_gets_converted_to_IX
    --- FAIL: TestRomanNumerals/9_gets_converted_to_IX (0.00s)
        numeral_test.go:29: got 'VIV', want 'IX'
```

## 写足够的代码让测试通过

我们应该能沿用之前的套路

```
case arabic > 8:
    result.WriteString("IX")
    arabic -= 9
```

## 重构

*感觉*代码还在暗示某处藏着一次重构，但我还没完全看出来，那就继续往前走。

这次的代码我也先按下不表，不过请在测试用例里加一条 `10` 应转换为 `X` 的测试，并在继续往下读之前让它通过。

下面是我加的几个测试，我有信心我们的代码一直到 39 都能正常工作

```
{"10 gets converted to X", 10, "X"},
{"14 gets converted to XIV", 14, "XIV"},
{"18 gets converted to XVIII", 18, "XVIII"},
{"20 gets converted to XX", 20, "XX"},
{"39 gets converted to XXXIX", 39, "XXXIX"},
```

如果你写过面向对象（OO）编程，就该知道对 `switch` 语句要多留个心眼。通常，你本可以把概念或数据收进类的结构里，结果却把它们捕进了命令式代码中。

Go 算不上严格的 OO 语言，但这不等于要把 OO 给我们的启示全盘扔掉（尽管总有人劝你干脆别管这些）。

我们的 `switch` 语句既描述了罗马数字的若干事实，又混进了行为。

我们可以把数据从行为里解耦出来，完成这次重构。

```go
type RomanNumeral struct {
	Value  int
	Symbol string
}

var allRomanNumerals = []RomanNumeral{
	{10, "X"},
	{9, "IX"},
	{5, "V"},
	{4, "IV"},
	{1, "I"},
}

func ConvertToRoman(arabic int) string {

	var result strings.Builder

	for _, numeral := range allRomanNumerals {
		for arabic >= numeral.Value {
			result.WriteString(numeral.Symbol)
			arabic -= numeral.Value
		}
	}

	return result.String()
}
```

感觉好多了。我们把围绕罗马数字的一部分规则声明成了数据，而不是藏在算法里，还能清楚地看到我们是怎么处理阿拉伯数的：逐个试着把符号加进结果，合适就留下。

这个抽象对更大的数还好使吗？扩展测试套件，让它覆盖 50 对应的罗马数字 `L`。

下面是一些测试用例，试着让它们通过。

```
{"40 gets converted to XL", 40, "XL"},
{"47 gets converted to XLVII", 47, "XLVII"},
{"49 gets converted to XLIX", 49, "XLIX"},
{"50 gets converted to L", 50, "L"},
```

需要帮助？该加哪些符号可以看[这个 gist](https://gist.github.com/pamelafox/6c7b948213ba55332d86efd0f0b037de)。

## 剩下的符号！

下面是剩下的符号

| 阿拉伯数字 | 罗马数字 |
| ------ | :---: |
| 100    |   C   |
| 500    |   D   |
| 1000   |   M   |

对剩下的符号如法炮制，无非是往测试和我们的符号数组里再添点数据。

你的代码能搞定 `1984`：`MCMLXXXIV` 了吗？

这是我最终的测试套件

```go
func TestRomanNumerals(t *testing.T) {
	cases := []struct {
		Arabic int
		Roman  string
	}{
		{Arabic: 1, Roman: "I"},
		{Arabic: 2, Roman: "II"},
		{Arabic: 3, Roman: "III"},
		{Arabic: 4, Roman: "IV"},
		{Arabic: 5, Roman: "V"},
		{Arabic: 6, Roman: "VI"},
		{Arabic: 7, Roman: "VII"},
		{Arabic: 8, Roman: "VIII"},
		{Arabic: 9, Roman: "IX"},
		{Arabic: 10, Roman: "X"},
		{Arabic: 14, Roman: "XIV"},
		{Arabic: 18, Roman: "XVIII"},
		{Arabic: 20, Roman: "XX"},
		{Arabic: 39, Roman: "XXXIX"},
		{Arabic: 40, Roman: "XL"},
		{Arabic: 47, Roman: "XLVII"},
		{Arabic: 49, Roman: "XLIX"},
		{Arabic: 50, Roman: "L"},
		{Arabic: 100, Roman: "C"},
		{Arabic: 90, Roman: "XC"},
		{Arabic: 400, Roman: "CD"},
		{Arabic: 500, Roman: "D"},
		{Arabic: 900, Roman: "CM"},
		{Arabic: 1000, Roman: "M"},
		{Arabic: 1984, Roman: "MCMLXXXIV"},
		{Arabic: 3999, Roman: "MMMCMXCIX"},
		{Arabic: 2014, Roman: "MMXIV"},
		{Arabic: 1006, Roman: "MVI"},
		{Arabic: 798, Roman: "DCCXCVIII"},
	}
	for _, test := range cases {
		t.Run(fmt.Sprintf("%d gets converted to %q", test.Arabic, test.Roman), func(t *testing.T) {
			got := ConvertToRoman(test.Arabic)
			if got != test.Roman {
				t.Errorf("got %q, want %q", got, test.Roman)
			}
		})
	}
}
```

- 我去掉了 `description`，因为*数据*本身已经把信息描述得够清楚了。
- 我又加了几个自己发现的边界用例，好让自己多一点底气。有了表驱动测试，这事儿成本极低。

算法一行没改，要做的只是更新 `allRomanNumerals` 数组。

```go
var allRomanNumerals = []RomanNumeral{
	{1000, "M"},
	{900, "CM"},
	{500, "D"},
	{400, "CD"},
	{100, "C"},
	{90, "XC"},
	{50, "L"},
	{40, "XL"},
	{10, "X"},
	{9, "IX"},
	{5, "V"},
	{4, "IV"},
	{1, "I"},
}
```

## 解析罗马数字

还没完呢。接下来我们要写一个函数，把罗马数字*反向*转换成 `int`

## 先写测试

稍作重构，就能在这里复用我们的测试用例

把 `cases` 变量挪到测试函数外面，放进一个 `var` 块，作为包级变量。

```go
func TestConvertingToArabic(t *testing.T) {
	for _, test := range cases[:1] {
		t.Run(fmt.Sprintf("%q gets converted to %d", test.Roman, test.Arabic), func(t *testing.T) {
			got := ConvertToArabic(test.Roman)
			if got != test.Arabic {
				t.Errorf("got %d, want %d", got, test.Arabic)
			}
		})
	}
}
```

注意我用切片只切出了一个用例（`cases[:1]`）——想一口吃成胖子、让所有用例一次全过，步子就迈得太大了

## 试着运行测试

```console
./numeral_test.go:60:11: undefined: ConvertToArabic
```

## 写出刚好能让测试运行的最少代码，并检查失败测试的输出

加上我们的新函数定义

```go
func ConvertToArabic(roman string) int {
	return 0
}
```

现在测试应该能运行并且失败了

```console
--- FAIL: TestConvertingToArabic (0.00s)
    --- FAIL: TestConvertingToArabic/'I'_gets_converted_to_1 (0.00s)
        numeral_test.go:62: got 0, want 1
```

## 写足够的代码让测试通过

你知道该怎么做的

```go
func ConvertToArabic(roman string) int {
	return 1
}
```

接下来，改一下测试里的切片索引，挪到下一个用例（比如 `cases[:2]`）。自己用你能想到的最蠢的代码让它通过；第三个用例也继续写蠢代码（本书史上最佳，对吧？）。这是我的蠢代码。

```go
func ConvertToArabic(roman string) int {
	if roman == "III" {
		return 3
	}
	if roman == "II" {
		return 2
	}
	return 1
}
```

透过*能跑通的真实代码*所透出的这股蠢劲儿，我们像之前一样开始看出一点模式：需要遍历输入，构建*某个东西*，在这里是一个总数。

```go
func ConvertToArabic(roman string) int {
	total := 0
	for range roman {
		total++
	}
	return total
}
```

## 先写测试

接着挪到 `cases[:4]`（`IV`），这次失败了，因为函数返回了 2——那是字符串的长度。

## 写足够的代码让测试通过

```go
// 前面的代码……
var allRomanNumerals = RomanNumerals{
	{1000, "M"},
	{900, "CM"},
	{500, "D"},
	{400, "CD"},
	{100, "C"},
	{90, "XC"},
	{50, "L"},
	{40, "XL"},
	{10, "X"},
	{9, "IX"},
	{5, "V"},
	{4, "IV"},
	{1, "I"},
}

// 后面的代码……
func ConvertToArabic(roman string) int {
	var arabic = 0

	for _, numeral := range allRomanNumerals {
		for strings.HasPrefix(roman, numeral.Symbol) {
			arabic += numeral.Value
			roman = strings.TrimPrefix(roman, numeral.Symbol)
		}
	}

	return arabic
}
```

这基本上就是把 `ConvertToRoman(int)` 的算法反过来用。这里我们遍历给定的罗马数字字符串：
- 我们在字符串开头寻找取自 `allRomanNumerals` 的罗马数字符号，从大到小。
- 找到前缀，就把它的值加进 `arabic`，并把前缀裁掉。

最后，我们把这个总和作为阿拉伯数返回。

`HasPrefix(s, prefix)` 检查字符串 `s` 是否以 `prefix` 开头，`TrimPrefix(s, prefix)` 则把 `prefix` 从 `s` 中去掉，这样就能继续处理剩下的罗马数字符号了。`IV` 以及所有其他测试用例都能通过。

你也可以把它实现成递归函数，（在我看来）那样更优雅，但可能更慢。这个就留给你和几个 `Benchmark...` 测试去掂量了。

现在我们有了阿拉伯数与罗马数字互转的两个函数，可以把测试再往前推进一步：

## 基于属性的测试入门

本章行文至此，罗马数字这个领域已经出现过几条规则：

- 同一个符号连续出现不能超过 3 个
- 只有 I（1）、X（10）和 C（100）能当"减数"
- 把 `ConvertToRoman(N)` 的结果传给 `ConvertToArabic`，应该返回 `N`

到目前为止我们写的测试，都可以归为"基于示例的测试"（example based tests）：我们给测试工具提供*例子*，让它去验证。

要是能把这些我们已知的领域规则，想办法拿来锤炼我们的代码呢？

基于属性的测试帮你做到这一点：往你的代码里扔随机数据，验证你所描述的规则始终成立。很多人以为基于属性的测试主要就是随机数据，那就搞错了。它真正的难点在于：你得对自己的领域有*透彻*的理解，才能写出这些属性。

废话不多说，看代码吧

> **⚠️ Linux 用户：** 请**不要**立刻运行下面的测试。它很可能会把你的系统整个冻住（只能硬重启）。
>
> <details>
> <summary>点开看看为什么（技术解释）</summary>
>
> `testing/quick` 包会生成最大到 `int64` 上限的随机整数。我们眼下这个朴素的实现，会试图在内存里构建那么长的字符串（千万亿级别的字符）。
>
> macOS 和 Windows 通常还能从容应对（界面照样响应），Linux 内核则往往会陷入"swap 抖动"（swap thrashing），进程还没来得及被杀掉，整个系统就先卡死了。
> </details>

```go
func TestPropertiesOfConversion(t *testing.T) {
	assertion := func(arabic int) bool {
		roman := ConvertToRoman(arabic)
		fromRoman := ConvertToArabic(roman)
		return fromRoman == arabic
	}

	if err := quick.Check(assertion, nil); err != nil {
		t.Error("failed checks", err)
	}
}
```

### 这个属性背后的道理

我们的第一个测试要验证的是：把一个数转换成罗马数字之后，再用另一个函数转回去时，拿到的仍是最初那个数。

- 给定一个随机数（比如 `4`）。
- 用这个随机数调用 `ConvertToRoman`（如果是 `4`，应该返回 `IV`）。
- 把上面的结果传给 `ConvertToArabic`。
- 上一步应该还给我们最初的输入（`4`）。

这个测试很适合帮我们建立信心，因为任何一边藏着 bug，它都会挂掉。它唯一能"通过"的方式，是两边恰好有同一种 bug；这不是不可能，但感觉上不太可能。

### 技术解释

我们用的是标准库的 [testing/quick](https://golang.org/pkg/testing/quick/) 包

从测试代码的底部往上读：我们交给 `quick.Check` 一个函数，它会拿一系列随机输入去运行这个函数；只要函数返回 `false`，就算没通过检查。

上面的 `assertion` 函数接收一个随机数，跑一遍我们的函数来验证这条属性。

### 运行我们的测试

试着跑一下；你的电脑可能会卡上一阵子，等烦了就把它杀掉 :)

这是怎么回事？试着把断言代码改成下面这样。

```go
assertion := func(arabic int) bool {
	if arabic < 0 || arabic > 3999 {
		log.Println(arabic)
		return true
	}
	roman := ConvertToRoman(arabic)
	fromRoman := ConvertToArabic(roman)
	return fromRoman == arabic
}
```

你会看到类似这样的输出：

```console
=== RUN   TestPropertiesOfConversion
2019/07/09 14:41:27 6849766357708982977
2019/07/09 14:41:27 -7028152357875163913
2019/07/09 14:41:27 -6752532134903680693
2019/07/09 14:41:27 4051793897228170080
2019/07/09 14:41:27 -1111868396280600429
2019/07/09 14:41:27 8851967058300421387
2019/07/09 14:41:27 562755830018219185
```

光跑这一条非常简单的属性，就暴露了实现中的一个缺陷。我们拿 `int` 当输入，但是：

- 罗马数字表示不了负数
- 按照"同一符号最多连续 3 个"的规则，我们表示不了大于 3999 的数（[嗯，也不算绝对](https://www.quora.com/Which-is-the-maximum-number-in-Roman-numerals)），而 `int` 的最大值可比 3999 大得多了。

这很棒！基于属性的测试逼着我们更深入地思考自己的领域，这正是它真正的强项。

显然 `int` 不是个好类型。换一个更贴切的试试？

### [`uint16`](https://golang.org/pkg/builtin/#uint16)

Go 为*无符号整数*准备了专门的类型，也就是说它们不能为负；这一下就直接消灭了我们代码里的一类 bug。至于那个 16，意思是它是 16 位整数，最多能存 `65535`，仍然太大，但离我们的需求更近了一步。

试着把代码里的 `int` 换成 `uint16`。我顺便更新了测试里的 `assertion`，让输出更直观一点。

> 注意，代码里的 `arabic` 变量也得改成 `uint16`（测试会提醒你）。更费劲的可能是 `arabic += numeral.Value` 这一行报的错。之所以报错，是因为我们在 `ConvertToArabic` 里用 `var arabic = 0` 声明了 `arabic`。这个声明本身没错，但 `0` 会被当作 `int` 值。`int` 值和 `uint16` 值相加是行不通的。Go 是有类型的语言，这样就是不行。所以，别忘了把 `var arabic = 0` 改成 `var arabic uint16 = 0`，让 `arabic` 变量变成 `uint16`。

```go
assertion := func(arabic uint16) bool {
	t.Log("testing", arabic)
	roman := ConvertToRoman(arabic)
	fromRoman := ConvertToArabic(roman)
	return fromRoman == arabic
}
```

注意，现在我们是用测试框架的 `log` 方法来打印输入的。运行 `go test` 时记得带上 `-v` 标志，才能打印出这些额外输出（`go test -v`）。

这时再跑测试，它真的跑得起来了，而且你能看到它到底在测什么。这让我对代码按我们期望的方式工作有了十足的底气。

但还留着一个不易察觉的缺口：`uint16` 最大到 65535，而超过 3999 的值并不是合法的罗马数字。随机数仍然会落进那个区间——我们的函数处理不了它们，往返转换会悄无声息地给出错误结果，而我们毫无察觉。你可以在断言里加一句 `if arabic > 3999 { return true }` 来挡一下，但那只是把问题盖住：那些迭代全成了空转。

更好的做法是告诉 `quick.Check`，只生成我们真正关心的值。用 `quick.Config` 的 `Values` 字段就能做到：

```go
if err := quick.Check(assertion, &quick.Config{
	MaxCount: 1000,
	Values: func(args []reflect.Value, r *rand.Rand) {
		args[0] = reflect.ValueOf(uint16(r.Intn(4000)))
	},
}); err != nil {
	t.Error("failed checks", err)
}
```

`Values` 是一个函数，它接收 `quick.Check` 将传给你断言的参数值切片，外加一个随机源。我们往 `args[0]` 里填一个取自 `[0, 3999]` 的 `uint16`。这样，1000 次运行里的每一次都在真正锻炼转换逻辑——一次都不浪费。

### 进一步的工作

- 你能不能写出属性测试，验证我们前面描述的其他几条属性？
- 你能不能想个办法，让别人根本没法用大于 3999 的数来调用我们的代码？
    - 可以返回一个 error
    - 或者创建一个无法表示大于 3999 的新类型
        - 你觉得哪种更好？

## 总结

### 借迭代式开发再练一遍 TDD

一想到要写代码把 1984 转换成 MCMLXXXIV，起初是不是有点发怵？我就发怵，而且我写软件已经很多年了。

诀窍向来不变：**从简单的东西入手**，**小步前进**。

这整个过程里，我们没有做过任何大跨越，没有做过任何大重构，也没有陷入过混乱。

我都能听到有人阴阳怪气地说"这不就是个 kata 嘛"。没法反驳，但我做的每一个项目用的都是同一套路子。我从来不会第一步就端出一个大型分布式系统，而是先找到团队能发布的那个最简单的东西（通常是一个"Hello world"网站），然后在可控的小块功能上持续迭代——就跟本章做的一样。

真正的功夫在于知道*怎么*拆分工作，这得靠练习，也靠一点美好的 TDD 一路相助。

### 基于属性的测试

- 标准库自带
- 只要你能想到用代码描述领域规则的办法，它们就是帮你提升信心的绝佳工具
- 逼你深入思考自己的领域
- 或许能为你的测试套件锦上添花

## 后记

本书能写成，离不开社区的宝贵反馈。[Dave](http://github.com/gypsydave5) 几乎在每一章都帮了大忙。不过这一章我对"阿拉伯数字"（Arabic numerals）的用法惹得他狠狠吐槽了一番，为了完全透明起见，把他的原话放在这里。

> 我就来写写为什么 `int` 类型的值其实算不上"阿拉伯数字"。可能是我较真儿过了头，你要是让我滚蛋，我完全能理解。
>
> *数字*（digit）是用来表示数的字符——词源是拉丁语的"手指"，因为我们通常有十根手指。在阿拉伯（也称印度-阿拉伯）数字系统中，这样的字符有十个。这些阿拉伯数字是：
>
> ```console
>   0 1 2 3 4 5 6 7 8 9
> ```
>
> *记数形式*（numeral）则是用一组数字表示出来的一个数。阿拉伯记数形式就是用阿拉伯数字在十进制位值制下表示出来的数。之所以说"位值制"，是因为每个数字的值取决于它在记数形式中所处的位置。所以
>
> ```console
>   1337
> ```
>
> `1` 的值是一千，因为它在这个四位的记数形式里排第一位。
>
> 罗马记数形式用的数字种类更少（`I`、`V` 等），这些字符大多直接作为数值来拼出记数形式。有一点位置因素，但大体上 `I` 永远表示"一"。
>
> 那么，照这么说，`int` 算"阿拉伯数"吗？"数"这个概念跟它的表示根本不绑定——问问自己，下面这个数的正确表示是什么，就清楚了：
>
> ```console
> 255
> 11111111
> two-hundred and fifty-five
> FF
> 377
> ```
>
> 没错，这是个脑筋急转弯。它们全都正确。它们分别是同一个数在十进制、二进制、英语、十六进制和八进制体系下的表示。
>
> 一个数作为记数形式的表示，跟它作为数的性质是*相互独立*的——看看 Go 里的整数字面量就明白了：
>
> ```go
> 	0xFF == 255 // true
> ```
>
> 而且在格式化字符串里还能这样打印整数：
>
> ```go
> n := 255
> fmt.Printf("%b %c %d %o %q %x %X %U", n, n, n, n, n, n, n, n)
> // 11111111 ÿ 255 377 'ÿ' ff FF U+00FF
> ```
>
> 同一个整数，既可以写成十六进制记数形式，也可以写成阿拉伯（十进制）记数形式。
>
> 所以，当函数签名长成 `ConvertToRoman(arabic int) string` 这个样子时，它其实对调用方式做了点假设。因为 `arabic` 有时会写成十进制整数字面量
>
> ```go
> 	ConvertToRoman(255)
> ```
>
> 但也完全可能写成
>
> ```go
> 	ConvertToRoman(0xFF)
> ```
>
> 说真的，我们根本不是在从"阿拉伯记数形式"做转换，而是在"打印"——把一个 `int` 表示成罗马数字——而 `int` 根本不是记数形式，阿拉伯的也好，别的也罢；它们只是数。`ConvertToRoman` 这个函数其实更像 `strconv.Itoa`：都是把 `int` 变成 `string`。
>
> 不过 kata 的其他所有版本都不在乎这层区别，所以 :shrug:
