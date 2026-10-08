# 整数

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/integers)**

整数的行为和你预期的一样。我们来写一个 `Add` 函数试试手。先创建一个名为 `adder_test.go` 的测试文件，写入以下代码。

**注意：** Go 源文件在一个目录里只能属于一个 `package`。请确保你的文件按各自的包组织好。[这里有一篇很好的讲解](https://dave.cheney.net/2014/12/01/five-suggestions-for-setting-up-a-go-project)。

你的项目目录看起来大概是这样：

```
learnGoWithTests
    |
    |-> helloworld
    |    |- hello.go
    |    |- hello_test.go
    |
    |-> integers
    |    |- adder_test.go
    |
    |- go.mod
    |- README.md
```

## 先写测试

```go
package integers

import "testing"

func TestAdder(t *testing.T) {
	sum := Add(2, 2)
	expected := 4

	if sum != expected {
		t.Errorf("expected '%d' but got '%d'", expected, sum)
	}
}
```

你可能注意到了，这次我们的格式化字符串用的是 `%d` 而不是 `%q`。因为我们想打印的是整数，而不是字符串。

另外注意，我们不再使用 main 包，而是定义了一个名为 `integers` 的包。顾名思义，这个包用来收纳跟整数打交道的函数，比如 `Add`。

## 试着跑一下测试

运行测试 `go test`

看看编译错误

`./adder_test.go:6:9: undefined: Add`

## 写最少的代码让测试跑起来，并查看失败的测试输出

写刚好能满足编译器的代码，*仅此而已*——记住，我们要确认测试失败的理由是正确的。

```go
package integers

func Add(x, y int) int {
	return 0
}
```

记住，当多个参数的类型相同（我们这里是两个整数），不必写 `(x int, y int)`，可以简写成 `(x, y int)`。

现在跑一下测试，测试准确地报告了问题所在，我们应该对此感到满意。

`adder_test.go:10: expected '4' but got '0'`

你可能已经发现，我们在[上一章](hello-world.md#最后一次重构)学过*具名返回值*，但这里并没有用。一般来说，只有当返回值的含义从上下文里看不清楚时才该用它；而我们这个例子，`Add` 函数会把参数加起来，这几乎一目了然。更多细节可以参考[这篇 wiki](https://go.dev/wiki/CodeReviewComments#named-result-parameters)。

## 写足够的代码让测试通过

严格来说，按照 TDD 的规矩，我们现在应该写*刚好让测试通过的最少代码*。较真的程序员可能会这么写

```go
func Add(x, y int) int {
	return 4
}
```

啊哈！又被摆了一道——这么说 TDD 果然是个骗局咯？

我们可以再写一个测试，换几个不同的数字，逼着这种实现露馅，但这就有点像[猫捉老鼠](https://en.m.wikipedia.org/wiki/Cat_and_mouse)的游戏了。

等我们对 Go 的语法更熟一些，我会介绍一种叫*“基于属性的测试”（Property Based Testing）*的技术，它能让开发者不再这么抓狂，还能帮你找到 bug。

眼下，我们还是把它正经修好

```go
func Add(x, y int) int {
	return x + y
}
```

再跑一遍测试，应该就能通过了。

## 重构

在*真正的*代码里，我们其实没什么可再改进的了。

前面我们已经见识过：给返回值起个名字，它就会出现在文档里，也会出现在大多数开发者的文本编辑器中。

这很棒，因为它让你写的代码更好用。最理想的状态是：使用者只看类型签名和文档，就明白你的代码该怎么用。

你可以用注释给函数添加文档，它们会出现在 Go Doc 里，就跟你在标准库文档里看到的一样。

```go
// Add 接收两个整数，返回它们的和。
func Add(x, y int) int {
	return x + y
}
```

### 可测试示例

如果你还想更进一步，可以做[可测试示例（Testable Examples）](https://blog.golang.org/examples)。标准库文档里就有很多这样的示例。

散落在代码库之外的代码示例（比如 readme 文件里的那些）常常会过时、跟实际代码对不上，因为没人检查它们。

而每次执行测试时，Example 函数都会被编译。正因如此，这类示例经过了 Go 编译器的检验，你可以放心：文档里的示例永远反映代码当前的行为。

Example 函数以 `Example` 开头（正如测试函数以 `Test` 开头），并且放在包的 `_test.go` 文件里。把下面这个 `ExampleAdd` 函数添加到 `adder_test.go` 中。

```go
func ExampleAdd() {
	sum := Add(1, 5)
	fmt.Println(sum)
	// Output: 6
}
```

（如果你的编辑器不会自动帮你导入包，编译会失败，因为 `adder_test.go` 里缺了 `import "fmt"`。强烈建议研究一下，在你手头的编辑器里怎么让这类错误被自动修好。）

加上这段代码后，示例就会出现在你的文档里，代码也变得更容易上手。一旦代码发生变化、示例不再成立，构建就会失败。

跑一下这个包的测试套件，可以看到 `ExampleAdd` 示例函数自动被执行了，不需要我们做任何额外安排：

```bash
$ go test -v
=== RUN   TestAdder
--- PASS: TestAdder (0.00s)
=== RUN   ExampleAdd
--- PASS: ExampleAdd (0.00s)
```

注意这行注释的特殊格式：`// Output: 6`。示例函数永远都会被编译，但加上这行注释之后，示例还会被*执行*。动手试试：临时删掉 `// Output: 6` 这行注释，再跑 `go test`，你会看到 `ExampleAdd` 不再被执行。

不带输出注释的示例也有用武之地：它可以演示那些没法当单元测试跑的代码（比如要访问网络的代码），同时保证示例至少能编译通过。

要查看示例文档，我们来快速认识一下 `pkgsite`。在进入你的项目目录之前，先确保你已经装好了 `pkgsite`，运行这条命令即可：`go install golang.org/x/pkgsite/cmd/pkgsite@latest`。然后运行 `pkgsite -open .`，它会帮你打开浏览器，指向 `http://localhost:8080`。页面里能看到 Go 标准库的所有包，外加你本地安装的第三方包；在其中你应该能看到 `github.com/quii/learn-go-with-tests` 的示例文档。点进去，找到 `Integers`，再找 `func Add`，展开 `Example`，就能看到你刚写的那个 `sum := Add(1, 5)` 示例。

如果你把带示例的代码发布到公开的 URL，就可以在 [pkg.go.dev](https://pkg.go.dev/) 上分享你的代码文档。比如，本章最终的 API 就在[这里](https://pkg.go.dev/github.com/quii/learn-go-with-tests/integers/v2)。这个网站可以检索标准库和第三方包的文档。

## 总结

本章我们覆盖了：

* 更多 TDD 工作流的练习
* 整数与加法
* 写更好的文档，让代码的使用者能快速弄懂怎么用
* 展示代码用法的示例，并且它们会作为测试的一部分接受检查
