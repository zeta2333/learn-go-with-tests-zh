# OS Exec

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/q-and-a/os-exec)**

[keith6014](https://www.reddit.com/user/keith6014) 在 [reddit](https://www.reddit.com/r/golang/comments/aaz8ji/testdata_and_function_setup_help/) 上提问：

> 我在用 os/exec.Command() 执行一个命令来生成 XML 数据，这个命令会在一个叫 GetData() 的函数里执行。
>
> 为了测试 GetData()，我准备了一些自己造的 testdata。
>
> 在我的 _test.go 里有一个 TestGetData，它会去调用 GetData()，但这样一来就会真的用到 os/exec；我希望它改用我的 testdata。
>
> 有什么好办法能做到这一点？调用 GetData 的时候，是不是该加一个 "test" 标志模式，让它去读文件，比如 GetData(mode string)？

有这么几点

- 当一段代码变得难以测试时，往往是因为关注点分离没有做对
- 不要往代码里塞 "test 模式"，而是用[依赖注入](./dependency-injection.md)，这样你才能为依赖建模、分离关注点。

我冒昧猜了猜这段代码可能长什么样

```go
type Payload struct {
	Message string `xml:"message"`
}

func GetData() string {
	cmd := exec.Command("cat", "msg.xml")

	out, _ := cmd.StdoutPipe()
	var payload Payload
	decoder := xml.NewDecoder(out)

	// 下面这 3 行都可能返回错误，为了简洁这里先忽略
	cmd.Start()
	decoder.Decode(&payload)
	cmd.Wait()

	return strings.ToUpper(payload.Message)
}
```

- 它用 `exec.Command` 来执行一个相对于进程的外部命令
- 我们用 `cmd.StdoutPipe` 捕获输出，它会返回一个 `io.ReadCloser`（这一点马上就会变得重要）
- 其余代码多多少少是从[那份出色的文档](https://golang.org/pkg/os/exec/#example_Cmd_StdoutPipe)里复制粘贴来的
    - 我们把 stdout 的输出捕获进一个 `io.ReadCloser`，然后 `Start` 这个命令，再调用 `Wait` 等所有数据读完。在这两个调用之间，我们把数据解码进 `Payload` 结构体。

`msg.xml` 里的内容是这样的

```xml
<payload>
    <message>Happy New Year!</message>
</payload>
```

我写了一个简单的测试来看看它的实际效果

```go
func TestGetData(t *testing.T) {
	got := GetData()
	want := "HAPPY NEW YEAR!"

	if got != want {
		t.Errorf("got %q, want %q", got, want)
	}
}
```

## 可测试的代码

可测试的代码是解耦的、单一用途的。在我看来，这段代码有两个主要的关注点

1. 拿到原始的 XML 数据
2. 解码 XML 数据并应用业务逻辑（在这里是对 `<message>` 做 `strings.ToUpper`）

第一部分不过是照抄标准库的示例。

第二部分才是业务逻辑所在。仔细看代码，就能看出逻辑的"接缝"（seam）从哪儿开始——就在我们拿到 `io.ReadCloser` 的地方。我们可以借助这个现成的抽象来分离关注点，让代码变得可测试。

**GetData 的问题在于业务逻辑和获取 XML 的手段耦合在了一起。想让设计更好，就得把它们解耦**

我们的 `TestGetData` 可以充当两个关注点之间的集成测试（integration test），所以把它留着，确保一切照常工作。

拆分之后的新代码长这样

```go
type Payload struct {
	Message string `xml:"message"`
}

func GetData(data io.Reader) string {
	var payload Payload
	xml.NewDecoder(data).Decode(&payload)
	return strings.ToUpper(payload.Message)
}

func getXMLFromCommand() io.Reader {
	cmd := exec.Command("cat", "msg.xml")
	out, _ := cmd.StdoutPipe()

	cmd.Start()
	data, _ := io.ReadAll(out)
	cmd.Wait()

	return bytes.NewReader(data)
}

func TestGetDataIntegration(t *testing.T) {
	got := GetData(getXMLFromCommand())
	want := "HAPPY NEW YEAR!"

	if got != want {
		t.Errorf("got %q, want %q", got, want)
	}
}
```

现在 `GetData` 的输入只是一个 `io.Reader`，我们把它变得可测试了，它也不再关心数据是怎么取回来的；任何人都可以拿任何能给出 `io.Reader` 的东西（这极其常见）来复用这个函数。比如以后我们可以改成从 URL 抓取 XML，而不是从命令行。

```go
func TestGetData(t *testing.T) {
	input := strings.NewReader(`
<payload>
    <message>Cats are the best animal</message>
</payload>`)

	got := GetData(input)
	want := "CATS ARE THE BEST ANIMAL"

	if got != want {
		t.Errorf("got %q, want %q", got, want)
	}
}

```

这就是给 `GetData` 写单元测试的一个例子。

把关注点分离开，再加上复用 Go 里现成的抽象，测试我们重要的业务逻辑就成了一件轻松的事。
