# 命令行与项目结构

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/command-line)**

我们的产品负责人现在想*转型*（pivot）一下：引入第二个应用——一个命令行应用。

眼下它只需要做到一件事：当用户输入 `Ruth wins` 时，记录下这名玩家赢了一局。长远打算则是把它做成一个帮用户玩扑克的工具。

产品负责人希望两个应用共享同一个数据库，这样新应用里记录的胜场也能反映到联赛数据里。

## 目前的代码

我们手头的应用有一个 `main.go`，负责启动一个 HTTP 服务器。这次练习里 HTTP 服务器本身不是重点，重点在它背后的抽象。它依赖一个 `PlayerStore`。

```go
type PlayerStore interface {
	GetPlayerScore(name string) int
	RecordWin(name string)
	GetLeague() League
}
```

上一章我们写了一个实现该接口的 `FileSystemPlayerStore`。新应用应该能复用它的一部分。

## 先来一点项目重构

我们的项目现在要构建出两个二进制可执行文件：现有的 Web 服务器，以及命令行应用。

在扎进新工作之前，得先把项目结构调整好，好容纳这两个应用。

到目前为止，所有代码都住在一个文件夹里，路径形如

`$GOPATH/src/github.com/your-name/my-app`

要用 Go 写一个应用，你需要在 `package main` 里有一个 `main` 函数。迄今为止，我们所有的"领域"代码都住在 `package main` 里，`func main` 可以直接引用其中的一切。

到目前为止这样没什么问题，而且不过度设计包结构本身就是好实践。你要是花点时间翻翻标准库，会发现里面几乎看不到层层叠叠的文件夹和结构。

好在等到*需要结构的时候*再加，也挺简单。

在现有项目里建一个 `cmd` 目录，里面再建一个 `webserver` 目录（比如 `mkdir -p cmd/webserver`）。

`cmd` 是 Go 社区广泛沿用的一个约定：把项目要构建的各个应用的 `main` 包放在这里，与项目根目录下那些可供导入的库代码分开。

把 `main.go` 挪进去。

如果你装了 `tree`，可以跑一下，结构应该长这样

```
.
|-- file_system_store.go
|-- file_system_store_test.go
|-- cmd
|   |-- webserver
|       |-- main.go
|-- league.go
|-- server.go
|-- server_integration_test.go
|-- server_test.go
|-- tape.go
|-- tape_test.go
```

这样一来，我们实际上已经把应用代码和库代码分开了，但现在还得改几个包名。记住：要构建一个 Go 应用，它的包*必须*是 `main`。

把其余所有代码的包都改成 `poker`。

最后，我们需要把这个包导入 `main.go`，才能用它创建 Web 服务器。之后就可以通过 `poker.FunctionName` 这样的方式来使用库代码。

路径在你的电脑上会不太一样，但应该类似下面这样：

```go
// cmd/webserver/main.go
package main

import (
	"github.com/quii/learn-go-with-tests/command-line/v1"
	"log"
	"net/http"
	"os"
)

const dbFileName = "game.db.json"

func main() {
	db, err := os.OpenFile(dbFileName, os.O_RDWR|os.O_CREATE, 0666)

	if err != nil {
		log.Fatalf("problem opening %s %v", dbFileName, err)
	}

	store, err := poker.NewFileSystemPlayerStore(db)

	if err != nil {
		log.Fatalf("problem creating file system player store, %v ", err)
	}

	server := poker.NewPlayerServer(store)

	log.Fatal(http.ListenAndServe(":5000", server))
}
```

`dbFileName` 是一个相对路径，所以 `game.db.json` 会以你*运行*可执行文件时所在的目录为准来创建（或读取），而不是看可执行文件本身住在哪个目录。产品负责人要求 CLI 和 Web 服务器共享同一个数据库，这就变得要紧了：如果两个程序从不同的目录启动，它们会各自默默地拿到一份互不相干的 `game.db.json`。下文"最终检查"一节还会回到这个问题。

这么长的路径看着可能有点别扭，但正是通过它，你才能把*任何*公开可用的库导入自己的代码。

把领域代码拆成独立的包、提交到 GitHub 这样的公共仓库之后，任何 Go 开发者都可以在自己的代码里导入这个包，直接用上我们写好的这些功能。第一次运行时编译器会抱怨这个包不存在，这时只需跑一下 `go get`。

此外，使用者还可以[在 pkg.go.dev 上查阅文档](https://pkg.go.dev/github.com/quii/learn-go-with-tests/command-line/v1)。

### 最终检查

- 在项目根目录跑 `go test`，确认测试依然全部通过
- 进入 `cmd/webserver`，执行 `go run main.go`
  - 访问 `http://localhost:5000/league`，应该能看到一切照常工作

本章稍后我们会构建第二个应用 `cmd/cli`，它要与 Web 服务器共享同一份 `game.db.json`。由于 `dbFileName` 是相对当前工作目录解析的，你得让两个可执行文件*从同一个目录*启动，它们才能看见彼此的更新。比如先把两者构建出来，再在项目根目录下运行这两个可执行文件（`go build -o webserver ./cmd/webserver && go build -o cli ./cmd/cli`，然后运行 `./webserver` 和 `./cli`），而不是分别钻进各自的 `cmd` 子目录里用 `go run main.go` 启动。

### 行走骨架

在埋头写测试之前，先给项目添加一个将要构建的新应用。在 `cmd` 里再建一个名为 `cli`（command line interface，命令行界面）的目录，放一个 `main.go`，内容如下

```go
// cmd/cli/main.go
package main

import "fmt"

func main() {
	fmt.Println("Let's play poker")
}
```

我们要处理的第一个需求是：当用户输入 `{PlayerName} wins` 时记录一次胜场。

## 先写测试

我们知道要做一个叫 `CLI` 的东西，有了它就能 `Play` 扑克。它得能读取用户输入，再把胜场记录到一个 `PlayerStore` 里。

不过先别跑太远，我们只写一个测试，检查它跟 `PlayerStore` 的集成方式是否符合我们的期望。

在 `CLI_test.go` 里写（放在项目根目录，不要放进 `cmd`）

```go
// CLI_test.go
package poker

import "testing"

func TestCLI(t *testing.T) {
	playerStore := &StubPlayerStore{}
	cli := &CLI{playerStore}
	cli.PlayPoker()

	if len(playerStore.winCalls) != 1 {
		t.Fatal("expected a win call but didn't get any")
	}
}
```

- 可以复用其他测试里的 `StubPlayerStore`
- 把依赖传给尚不存在的 `CLI` 类型
- 通过还没写的 `PlayPoker` 方法触发游戏
- 检查是否记录了一次胜场

## 试着运行测试

```
# github.com/quii/learn-go-with-tests/command-line/v2
./cli_test.go:25:10: undefined: CLI
```

## 写最少的代码让测试能运行，并检查失败的测试输出

写到这里，你应该已经轻车熟路了：给新的 `CLI` 结构体加上存放依赖的相应字段，再加一个方法。

你最后写出来的代码应该类似这样

```go
// CLI.go
package poker

type CLI struct {
	playerStore PlayerStore
}

func (cli *CLI) PlayPoker() {}
```

记住，我们只是想让测试先跑起来，好确认它按我们预期的方式失败

```
--- FAIL: TestCLI (0.00s)
    cli_test.go:30: expected a win call but didn't get any
FAIL
```

## 写足够的代码让测试通过

```go
//CLI.go
func (cli *CLI) PlayPoker() {
	cli.playerStore.RecordWin("Cleo")
}
```

这样测试就该过了。

接下来，我们需要模拟从 `Stdin`（用户的输入）读取数据，这样才能为特定的玩家记录胜场。

我们来扩展测试，把这部分行为也测起来。

## 先写测试

```go
//CLI_test.go
func TestCLI(t *testing.T) {
	in := strings.NewReader("Chris wins\n")
	playerStore := &StubPlayerStore{}

	cli := &CLI{playerStore, in}
	cli.PlayPoker()

	if len(playerStore.winCalls) != 1 {
		t.Fatal("expected a win call but didn't get any")
	}

	got := playerStore.winCalls[0]
	want := "Chris"

	if got != want {
		t.Errorf("didn't record correct winner, got %q, want %q", got, want)
	}
}
```

在 `main` 里，我们将用 `os.Stdin` 来获取用户的输入。它本质上是个 `*File`，也就是说它实现了 `io.Reader`——到现在你该知道了，这是捕获文本的一件称手工具。

测试里我们用同样称手的 `strings.NewReader` 造出一个 `io.Reader`，里面填的就是我们预期用户会敲的内容。

## 试着运行测试

`./CLI_test.go:12:32: too many values in struct initializer`

## 写最少的代码让测试能运行，并检查失败的测试输出

我们需要把新依赖加进 `CLI`。

```go
//CLI.go
type CLI struct {
	playerStore PlayerStore
	in          io.Reader
}
```

```
--- FAIL: TestCLI (0.00s)
    CLI_test.go:23: didn't record the correct winner, got 'Cleo', want 'Chris'
FAIL
```

## 写足够的代码让测试通过

记住，先做严格来说最省事的改动

```go
func (cli *CLI) PlayPoker() {
	cli.playerStore.RecordWin("Chris")
}
```

测试过了。接下来我们会再写一个测试，逼自己写出真正的代码，但在那之前，先重构。

## 重构

之前在 `server_test` 里我们就写过跟这里一样的"胜场是否被记录"的检查。把这些断言 DRY（Don't Repeat Yourself，别重复自己）一下，抽成一个辅助函数

```go
//server_test.go
func assertPlayerWin(t testing.TB, store *StubPlayerStore, winner string) {
	t.Helper()

	if len(store.winCalls) != 1 {
		t.Fatalf("got %d calls to RecordWin want %d", len(store.winCalls), 1)
	}

	if store.winCalls[0] != winner {
		t.Errorf("did not store correct winner got %q want %q", store.winCalls[0], winner)
	}
}
```

现在把 `server_test.go` 和 `CLI_test.go` 里的断言都换成它。

测试现在读起来应该是这样

```go
//CLI_test.go
func TestCLI(t *testing.T) {
	in := strings.NewReader("Chris wins\n")
	playerStore := &StubPlayerStore{}

	cli := &CLI{playerStore, in}
	cli.PlayPoker()

	assertPlayerWin(t, playerStore, "Chris")
}
```

现在我们再写*另一个*测试，换一份用户输入，逼我们真正去读用户输入。

## 先写测试

```go
//CLI_test.go
func TestCLI(t *testing.T) {

	t.Run("record chris win from user input", func(t *testing.T) {
		in := strings.NewReader("Chris wins\n")
		playerStore := &StubPlayerStore{}

		cli := &CLI{playerStore, in}
		cli.PlayPoker()

		assertPlayerWin(t, playerStore, "Chris")
	})

	t.Run("record cleo win from user input", func(t *testing.T) {
		in := strings.NewReader("Cleo wins\n")
		playerStore := &StubPlayerStore{}

		cli := &CLI{playerStore, in}
		cli.PlayPoker()

		assertPlayerWin(t, playerStore, "Cleo")
	})

}
```

## 试着运行测试

```
=== RUN   TestCLI
--- FAIL: TestCLI (0.00s)
=== RUN   TestCLI/record_chris_win_from_user_input
    --- PASS: TestCLI/record_chris_win_from_user_input (0.00s)
=== RUN   TestCLI/record_cleo_win_from_user_input
    --- FAIL: TestCLI/record_cleo_win_from_user_input (0.00s)
        CLI_test.go:27: did not store correct winner got 'Chris' want 'Cleo'
FAIL
```

## 写足够的代码让测试通过

我们会用一个 [`bufio.Scanner`](https://golang.org/pkg/bufio/) 从 `io.Reader` 里读取输入。

> bufio 包实现了缓冲 I/O。它把一个 io.Reader 或 io.Writer 对象包起来，生成另一个对象（Reader 或 Writer），后者同样实现了该接口，但额外提供了缓冲功能，还为文本 I/O 带来了一些便利。

把代码更新成下面这样

```go
//CLI.go
type CLI struct {
	playerStore PlayerStore
	in          io.Reader
}

func (cli *CLI) PlayPoker() {
	reader := bufio.NewScanner(cli.in)
	reader.Scan()
	cli.playerStore.RecordWin(extractWinner(reader.Text()))
}

func extractWinner(userInput string) string {
	return strings.Replace(userInput, " wins", "", 1)
}
```

测试现在会全部通过。

- `Scanner.Scan()` 会一直读到换行符为止。
- 然后我们用 `Scanner.Text()` 把扫描器读到的 `string` 返回出来。

既然手头已经有一些通过的测试了，我们就该把它接进 `main`。记住，我们要始终尽可能快地让软件完整集成、真正能跑。

在 `main.go` 里加上下面的内容并运行它。（第二个依赖的路径可能得按你电脑上的实际情况调整）

```go
package main

import (
	"fmt"
	"github.com/quii/learn-go-with-tests/command-line/v3"
	"log"
	"os"
)

const dbFileName = "game.db.json"

func main() {
	fmt.Println("Let's play poker")
	fmt.Println("Type {Name} wins to record a win")

	db, err := os.OpenFile(dbFileName, os.O_RDWR|os.O_CREATE, 0666)

	if err != nil {
		log.Fatalf("problem opening %s %v", dbFileName, err)
	}

	store, err := poker.NewFileSystemPlayerStore(db)

	if err != nil {
		log.Fatalf("problem creating file system player store, %v ", err)
	}

	game := poker.CLI{store, os.Stdin}
	game.PlayPoker()
}
```

你应该会看到一个错误

```
command-line/v3/cmd/cli/main.go:32:25: implicit assignment of unexported field 'playerStore' in poker.CLI literal
command-line/v3/cmd/cli/main.go:32:34: implicit assignment of unexported field 'in' in poker.CLI literal
```

报错的原因是：我们试图给 `CLI` 里的 `playerStore` 和 `in` 字段赋值，而它们是未导出（unexported，即私有）字段。在测试代码里我们*可以*这么干，因为测试跟 `CLI` 在同一个包（`poker`）里；但我们的 `main` 属于 `main` 包，无权访问。

这恰恰说明了*集成你的工作*有多重要。我们把 `CLI` 的依赖设为私有（这很合理，因为我们不想把它们暴露给 `CLI` 的使用者），却还没有给使用者提供一个构造它的途径。

有没有办法更早地抓住这个问题呢？

### `package mypackage_test`

在到目前为止的其他所有例子里，我们建测试文件时声明的都是被测代码所在的那个包。

这没什么问题，而且偶尔想测包内部的东西时，我们也确实用得上那些未导出的类型。

但既然我们一直主张*通常都不*测包内部的东西，Go 能不能帮我们把这条纪律强制执行起来？假如我们测试代码时只能访问导出的类型（就像 `main` 那样），会怎么样？

当你写的项目有多个包时，我强烈建议给测试包的名字末尾加上 `_test`。这样做之后，你就只能访问包里公开的类型。这不仅能解眼下的燃眉之急，还有助于守住"只测公开 API"的纪律。如果确实还想测内部实现，可以单独再写一个使用原包名的测试。

TDD 圈有句老话：如果你的代码不好测，那你的代码的使用者多半也很难把它集成进去。使用 `package foo_test` 能逼你像包的使用者那样，以导入的方式来测试代码，正好有助于此。

在修 `main` 之前，先把 `CLI_test.go` 里测试的包改成 `poker_test`。

如果你的 IDE 配置得当，你会瞬间看见一片红色！跑一下编译器，会得到如下错误

```
./CLI_test.go:12:19: undefined: StubPlayerStore
./CLI_test.go:17:3: undefined: assertPlayerWin
./CLI_test.go:22:19: undefined: StubPlayerStore
./CLI_test.go:27:3: undefined: assertPlayerWin
```

就这样，我们又一头撞上了几个关于包设计的新问题。为了测试软件，我们造了一些未导出的 stub 和辅助函数，可现在 `CLI_test` 里用不上它们了，因为它们定义在 `poker` 包的 `_test.go` 文件里。

#### 要不要把我们的 stub 和辅助函数"公开"？

这是个见仁见智的问题。有人会主张：不该让辅助测试的代码污染包的 API。

在 Mitchell Hashimoto 的演讲[《Advanced Testing with Go》](https://speakerdeck.com/mitchellh/advanced-testing-with-go?slide=53)里，他讲到 HashiCorp 就提倡这么做，这样包的使用者写测试时就不必重复造轮子、自己写 stub。放到我们的场景，这意味着任何想拿我们的 `poker` 包来写代码的人，都不必再自己造一个 stub 版的 `PlayerStore`。

就我自己的经验而言，我在其他共享包里用过这招，事实证明它特别好使——使用者集成我们的包时省下了不少时间。

那我们就建一个名为 `testing.go` 的文件，把 stub 和辅助函数都放进去。

```go
// testing.go
package poker

import "testing"

type StubPlayerStore struct {
	scores   map[string]int
	winCalls []string
	league   []Player
}

func (s *StubPlayerStore) GetPlayerScore(name string) int {
	score := s.scores[name]
	return score
}

func (s *StubPlayerStore) RecordWin(name string) {
	s.winCalls = append(s.winCalls, name)
}

func (s *StubPlayerStore) GetLeague() League {
	return s.league
}

func AssertPlayerWin(t testing.TB, store *StubPlayerStore, winner string) {
	t.Helper()

	if len(store.winCalls) != 1 {
		t.Fatalf("got %d calls to RecordWin want %d", len(store.winCalls), 1)
	}

	if store.winCalls[0] != winner {
		t.Errorf("did not store correct winner got %q want %q", store.winCalls[0], winner)
	}
}

// 留给你的作业——把其余的辅助函数也补上
```

要让包的导入者用上这些辅助函数，你得把它们改成公开的（记住，首字母大写即导出）。

在我们的 `CLI` 测试里，调用方式得当成在另一个包里用它一样。

```go
//CLI_test.go
func TestCLI(t *testing.T) {

	t.Run("record chris win from user input", func(t *testing.T) {
		in := strings.NewReader("Chris wins\n")
		playerStore := &poker.StubPlayerStore{}

		cli := &poker.CLI{playerStore, in}
		cli.PlayPoker()

		poker.AssertPlayerWin(t, playerStore, "Chris")
	})

	t.Run("record cleo win from user input", func(t *testing.T) {
		in := strings.NewReader("Cleo wins\n")
		playerStore := &poker.StubPlayerStore{}

		cli := &poker.CLI{playerStore, in}
		cli.PlayPoker()

		poker.AssertPlayerWin(t, playerStore, "Cleo")
	})

}
```

现在你会看到，`main` 里遇到的问题又来了

```
./CLI_test.go:15:26: implicit assignment of unexported field 'playerStore' in poker.CLI literal
./CLI_test.go:15:39: implicit assignment of unexported field 'in' in poker.CLI literal
./CLI_test.go:25:26: implicit assignment of unexported field 'playerStore' in poker.CLI literal
./CLI_test.go:25:39: implicit assignment of unexported field 'in' in poker.CLI literal
```

要绕开它，最简单的办法就是像给其他类型做的那样，配一个构造函数。我们还要顺手改一改 `CLI`，让它存 `bufio.Scanner` 而不是 reader，因为包装这一步在构造时就自动完成了。

```go
//CLI.go
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
```

这样一来，我们就能把读取的代码简化、重构一番

```go
//CLI.go
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

把测试改成用构造函数，测试就应该重新变绿了。

最后，回到新的 `main.go`，用上我们刚写的构造函数

```go
//cmd/cli/main.go
game := poker.NewCLI(store, os.Stdin)
```

试着跑一跑，输入 "Bob wins"。

### 重构

我们的两个应用里都有一些重复代码：打开一个文件、根据文件内容创建 `file_system_store`。这感觉是我们包设计上的一个小弱点，所以应该在包里做一个函数，把"从路径打开文件、返回 `PlayerStore`"这件事封装起来。

```go
//file_system_store.go
func FileSystemPlayerStoreFromFile(path string) (*FileSystemPlayerStore, func(), error) {
	db, err := os.OpenFile(path, os.O_RDWR|os.O_CREATE, 0666)

	if err != nil {
		return nil, nil, fmt.Errorf("problem opening %s %v", path, err)
	}

	closeFunc := func() {
		db.Close()
	}

	store, err := NewFileSystemPlayerStore(db)

	if err != nil {
		return nil, nil, fmt.Errorf("problem creating file system player store, %v ", err)
	}

	return store, closeFunc, nil
}
```

现在把我们的两个应用都重构一下，改用这个函数来创建 store。

#### CLI 应用的代码

```go
// cmd/cli/main.go
package main

import (
	"fmt"
	"github.com/quii/learn-go-with-tests/command-line/v3"
	"log"
	"os"
)

const dbFileName = "game.db.json"

func main() {
	store, close, err := poker.FileSystemPlayerStoreFromFile(dbFileName)

	if err != nil {
		log.Fatal(err)
	}
	defer close()

	fmt.Println("Let's play poker")
	fmt.Println("Type {Name} wins to record a win")
	poker.NewCLI(store, os.Stdin).PlayPoker()
}
```

#### Web 服务器应用的代码

```go
// cmd/webserver/main.go
package main

import (
	"github.com/quii/learn-go-with-tests/command-line/v3"
	"log"
	"net/http"
)

const dbFileName = "game.db.json"

func main() {
	store, close, err := poker.FileSystemPlayerStoreFromFile(dbFileName)

	if err != nil {
		log.Fatal(err)
	}
	defer close()

	server := poker.NewPlayerServer(store)

	if err := http.ListenAndServe(":5000", server); err != nil {
		log.Fatalf("could not listen on port 5000 %v", err)
	}
}
```

注意这里的对称性：尽管用户界面截然不同，初始化代码却几乎一模一样。这感觉是对我们目前设计的一次很好的验证。
还要注意 `FileSystemPlayerStoreFromFile` 返回了一个负责关闭的函数，这样用完 Store 之后，我们就能把底层的文件关掉。

## 总结

### 包结构

这一章的目标是创建两个应用，同时复用我们迄今为止写好的领域代码。为此，我们需要调整包结构，给各自的 `main` 留出独立的文件夹。

在这个过程中，我们因为未导出的值碰上了集成问题，这也进一步印证了小步"切片"式工作、频繁集成的价值。

我们学到，`mypackage_test` 能帮我们营造出这样一个测试环境：体验上与别人拿其他包来集成你的代码时别无二致，帮你及早抓住集成问题，也让你看清自己的代码用起来到底有多顺手（还是难用得要命！）。

### 读取用户输入

我们看到，从 `os.Stdin` 读取输入非常省事，因为它实现了 `io.Reader`。我们还用 `bufio.Scanner` 轻松实现了逐行读取用户输入。

### 简单的抽象带来更省事的代码复用

把 `PlayerStore` 集成进新应用几乎没费什么力气（在完成包调整之后），随后的测试也非常轻松，因为我们决定连自己的 stub 版本也一并公开。
