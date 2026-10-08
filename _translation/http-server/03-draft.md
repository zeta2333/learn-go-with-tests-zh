# HTTP 服务器

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/http-server)**

现在交给你一个需求：做一个 web 服务器，让用户可以追踪每位玩家赢了多少场游戏。

-   `GET /players/{name}` 应返回一个数字，表示该玩家的总胜场数
-   `POST /players/{name}` 应为该名字记下一次胜利，之后每发一次 `POST` 就加一

我们会遵循 TDD 的路子，尽快先拿到能工作的软件，然后一点点迭代改进，直到做出最终的解决方案。这样做可以

-   让问题域在任何时刻都保持很小
-   不一头栽进兔子洞
-   万一卡住或迷路了，revert 回去也不会损失大把工作成果。

## 红、绿、重构

纵观全书，我们一直在强调 TDD 的流程：先写测试并看它失败（红），再写*最少*的代码让它通过（绿），然后重构。

这种"只写最少代码"的纪律，正是 TDD 安全性的重要来源。你应该努力尽早从"红"里脱身。

Kent Beck 是这样描述的：

> 尽快让测试通过，过程中不管犯下什么"罪行"。

你之所以敢犯这些"罪行"，是因为之后你会在测试的保护下重构，把代码收拾干净。

### 不这么做会怎样？

在"红"的状态里做的改动越多，就越容易引入更多测试没覆盖到的问题。

这套思路的目的是：以小步迭代的方式，在测试的驱动下持续写出有用的代码，免得一不小心掉进兔子洞就是几个小时。

### 先有鸡还是先有蛋

我们该怎么增量地把它做出来？没存过数据就没法 `GET` 一个玩家的分数；而 `GET` 端点还不存在，似乎又很难知道 `POST` 到底有没有生效。

这正是 mock（模拟）大显身手的地方。

-   `GET` 需要一个 `PlayerStore` 这样的*东西*来获取玩家的分数。它应该是一个接口，这样测试时我们就能造一个简单的 stub 代替它，不用先写任何真实的存储代码。
-   至于 `POST`，我们可以 spy 住它对 `PlayerStore` 的调用，确保它正确地记录了玩家。这样"保存"的实现就不会跟"查询"耦合在一起。
-   为了尽快有能工作的软件，我们可以先写一个非常简单的内存版实现，之后再换成背后接任何我们喜欢的存储方案的实现。

## 先写测试

我们可以先写一个测试，让它通过返回一个硬编码的值来通过，好有个起点。Kent Beck 把这叫 "Faking it"（先拿假货糊弄过去）。有了能通过的测试，我们再写更多测试，帮我们把这个常量消灭掉。

通过这一小步，我们就能先办成一件重要的事——让整个项目结构正确运转起来，而不用太操心应用逻辑本身。

在 Go 里创建 web 服务器，通常要调用 [ListenAndServe](https://golang.org/pkg/net/http/#ListenAndServe)。

```go
func ListenAndServe(addr string, handler Handler) error
```

它会启动一个 web 服务器在某个端口上监听，为每个请求创建一个 goroutine，并把它交给一个 [`Handler`](https://golang.org/pkg/net/http/#Handler) 去处理。

```go
type Handler interface {
	ServeHTTP(ResponseWriter, *Request)
}
```

一个类型只要实现了 `ServeHTTP` 方法，就实现了 `Handler` 接口。这个方法接收两个参数：第一个是我们*写入响应*的地方，第二个是发到服务器的 HTTP 请求。

我们来建一个 `server_test.go` 文件，为一个函数 `PlayerServer` 写测试，它接收这两个参数。传进来的请求用于获取玩家的分数，我们期望返回 `"20"`。
```go
func TestGETPlayers(t *testing.T) {
	t.Run("returns Pepper's score", func(t *testing.T) {
		request, _ := http.NewRequest(http.MethodGet, "/players/Pepper", nil)
		response := httptest.NewRecorder()

		PlayerServer(response, request)

		got := response.Body.String()
		want := "20"

		if got != want {
			t.Errorf("got %q, want %q", got, want)
		}
	})
}
```

为了测试服务器，我们需要一个 `Request` 传进去，还要能 spy 住处理器往 `ResponseWriter` 里写了什么。

-   我们用 `http.NewRequest` 创建请求。第一个参数是请求的方法，第二个是请求的路径。`nil` 指的是请求体，这里用不着设置。
-   `net/http/httptest` 已经为我们准备好了一个 spy，叫 `ResponseRecorder`，直接拿来用就行。它有很多实用的方法，可以检查写入的响应内容。

## 试着运行测试

`./server_test.go:13:2: undefined: PlayerServer`

## 写最少量的代码让测试能跑起来，并检查失败的测试输出

编译器就是来帮你的，听它的话就好。

新建一个 `server.go` 文件，定义 `PlayerServer`

```go
func PlayerServer() {}
```

再试一次

```
./server_test.go:13:14: too many arguments in call to PlayerServer
    have (*httptest.ResponseRecorder, *http.Request)
    want ()
```

给函数加上参数

```go
import "net/http"

func PlayerServer(w http.ResponseWriter, r *http.Request) {

}
```

代码现在能编译了，测试失败

```
=== RUN   TestGETPlayers/returns_Pepper's_score
    --- FAIL: TestGETPlayers/returns_Pepper's_score (0.00s)
        server_test.go:20: got '', want '20'
```

## 写足够的代码让它通过

在依赖注入一章里，我们借一个 `Greet` 函数初步接触了 HTTP 服务器。当时我们学到，net/http 的 `ResponseWriter` 也实现了 io `Writer`，所以可以用 `fmt.Fprint` 把字符串作为 HTTP 响应发送出去。

```go
func PlayerServer(w http.ResponseWriter, r *http.Request) {
	fmt.Fprint(w, "20")
}
```

测试现在应该通过了。

## 搭好脚手架

接下来要把它接进一个应用程序里。这一步很重要，因为

-   我们会有*真正能运行的软件*，写测试可不是为了写而写，能看到代码跑起来总是好的。
-   随着代码重构，程序的结构很可能会变。按照增量式的路子，我们也要确保应用本身同步反映这些变化。

新建一个 `main.go` 文件作为应用程序，写入以下代码

```go
package main

import (
	"log"
	"net/http"
)

func main() {
	handler := http.HandlerFunc(PlayerServer)
	log.Fatal(http.ListenAndServe(":5000", handler))
}
```

到目前为止，我们所有的应用代码都挤在一个文件里。但对更大的项目来说，这可不是最佳实践——你会希望把代码拆到不同的文件里去。

要运行它，先执行 `go build`，它会把目录下的所有 `.go` 文件编译成一个程序，然后你就可以用 `./myprogram` 执行它了。

### `http.HandlerFunc`

前面我们已经研究过，要做出一个服务器，需要实现的就是 `Handler` 接口。*通常*的做法是创建一个结构体，为它实现自己的 `ServeHTTP` 方法，从而满足这个接口。然而结构体的用武之地是持有数据，可*眼下*我们没有任何状态，为了它硬造一个结构体总觉得不太对劲。

[HandlerFunc](https://golang.org/pkg/net/http/#HandlerFunc) 让我们绕开了这个问题。

> The HandlerFunc type is an adapter to allow the use of ordinary functions as HTTP handlers. If f is a function with the appropriate signature, HandlerFunc(f) is a Handler that calls f.

```go
type HandlerFunc func(ResponseWriter, *Request)
```

从文档可以看到，类型 `HandlerFunc` 已经实现了 `ServeHTTP` 方法。
只要用它对我们的 `PlayerServer` 函数做一次类型转换，我们就把要求的 `Handler` 实现好了。

### `http.ListenAndServe(":5000"...)`

`ListenAndServe` 接收一个要监听的端口和一个 `Handler`。如果出了问题，web 服务器会返回一个错误，比如端口已经被占用。所以我们要把这次调用包在 `log.Fatal` 里，把错误记录下来告知用户。

现在我们要做的是*再写一个*测试，逼着自己做出积极的改变，摆脱硬编码的值。

## 先写测试

我们往测试套件里再加一个子测试，尝试获取另一个玩家的分数，这会打破硬编码的方案。

```go
t.Run("returns Floyd's score", func(t *testing.T) {
	request, _ := http.NewRequest(http.MethodGet, "/players/Floyd", nil)
	response := httptest.NewRecorder()

	PlayerServer(response, request)

	got := response.Body.String()
	want := "10"

	if got != want {
		t.Errorf("got %q, want %q", got, want)
	}
})
```

你心里可能在犯嘀咕

> 我们显然需要某种存储的概念，才能控制哪个玩家是多少分吧？测试里这些值看起来这么随意，也太怪了。

记住，我们只是在尽量把每一步迈得小一点，所以眼下只是要打破这个常量而已。

## 试着运行测试

```
=== RUN   TestGETPlayers/returns_Pepper's_score
    --- PASS: TestGETPlayers/returns_Pepper's_score (0.00s)
=== RUN   TestGETPlayers/returns_Floyd's_score
    --- FAIL: TestGETPlayers/returns_Floyd's_score (0.00s)
        server_test.go:34: got '20', want '10'
```

## 写足够的代码让它通过

```go
//server.go
func PlayerServer(w http.ResponseWriter, r *http.Request) {
	player := strings.TrimPrefix(r.URL.Path, "/players/")

	if player == "Pepper" {
		fmt.Fprint(w, "20")
		return
	}

	if player == "Floyd" {
		fmt.Fprint(w, "10")
		return
	}
}
```

这个测试逼着我们真正去看请求的 URL 并做出决策。所以虽然我们脑子里还在惦记着 player store 和接口，下一步合乎逻辑的行动其实落在了*路由*上。

如果我们一开始就去写 store 的代码，需要做的改动会比现在大得多。**这一步朝着最终目标迈得更小，而且是由测试驱动的**。

我们现在忍住了用任何路由库的诱惑，只走让测试通过的最小一步。

`r.URL.Path` 返回请求的路径，接着我们可以用 [`strings.TrimPrefix`](https://golang.org/pkg/strings/#TrimPrefix) 把 `/players/` 前缀裁掉，拿到请求的玩家名。这不太健壮，但眼下够用了。

## 重构

我们可以把取分数的逻辑拆到一个单独的函数里，让 `PlayerServer` 更简洁

```go
//server.go
func PlayerServer(w http.ResponseWriter, r *http.Request) {
	player := strings.TrimPrefix(r.URL.Path, "/players/")

	fmt.Fprint(w, GetPlayerScore(player))
}

func GetPlayerScore(name string) string {
	if name == "Pepper" {
		return "20"
	}

	if name == "Floyd" {
		return "10"
	}

	return ""
}
```

测试代码也可以做些辅助函数来去去重（DRY）

```go
//server_test.go
func TestGETPlayers(t *testing.T) {
	t.Run("returns Pepper's score", func(t *testing.T) {
		request := newGetScoreRequest("Pepper")
		response := httptest.NewRecorder()

		PlayerServer(response, request)

		assertResponseBody(t, response.Body.String(), "20")
	})

	t.Run("returns Floyd's score", func(t *testing.T) {
		request := newGetScoreRequest("Floyd")
		response := httptest.NewRecorder()

		PlayerServer(response, request)

		assertResponseBody(t, response.Body.String(), "10")
	})
}

func newGetScoreRequest(name string) *http.Request {
	req, _ := http.NewRequest(http.MethodGet, fmt.Sprintf("/players/%s", name), nil)
	return req
}

func assertResponseBody(t testing.TB, got, want string) {
	t.Helper()
	if got != want {
		t.Errorf("response body is wrong, got %q want %q", got, want)
	}
}
```

不过，我们还是不该满足。服务器自己知道分数，这感觉不对劲。

我们的重构已经把该做什么指得相当明白了。

我们把分数的计算从处理器的主体里挪出来，放进了一个函数 `GetPlayerScore`。这感觉正是用接口做关注点分离的合适位置。

我们把这个重构出来的函数改成接口吧

```go
type PlayerStore interface {
	GetPlayerScore(name string) int
}
```

`PlayerServer` 要想用上 `PlayerStore`，就得持有一个对它的引用。现在是改造架构的好时机：让 `PlayerServer` 变成一个结构体。

```go
type PlayerServer struct {
	store PlayerStore
}
```

最后，给这个新结构体加一个方法，把现有的处理器代码放进去，这样就实现了 `Handler` 接口。

```go
func (p *PlayerServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	player := strings.TrimPrefix(r.URL.Path, "/players/")
	fmt.Fprint(w, p.store.GetPlayerScore(player))
}
```

唯一的另一处变化是：现在我们调用 `store.GetPlayerScore` 来获取分数，而不是之前定义的本地函数（它可以删掉了）。

下面是服务器的完整代码

```go
//server.go
type PlayerStore interface {
	GetPlayerScore(name string) int
}

type PlayerServer struct {
	store PlayerStore
}

func (p *PlayerServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	player := strings.TrimPrefix(r.URL.Path, "/players/")
	fmt.Fprint(w, p.store.GetPlayerScore(player))
}
```

### 修好编译问题

这一轮改动不小，我们知道测试和应用都编译不过了，不过放松，让编译器带着我们一个个解决就好。

`./main.go:9:58: type PlayerServer is not an expression`

我们需要把测试改成创建一个新的 `PlayerServer` 实例，然后调用它的 `ServeHTTP` 方法。

```go
//server_test.go
func TestGETPlayers(t *testing.T) {
	server := &PlayerServer{}

	t.Run("returns Pepper's score", func(t *testing.T) {
		request := newGetScoreRequest("Pepper")
		response := httptest.NewRecorder()

		server.ServeHTTP(response, request)

		assertResponseBody(t, response.Body.String(), "20")
	})

	t.Run("returns Floyd's score", func(t *testing.T) {
		request := newGetScoreRequest("Floyd")
		response := httptest.NewRecorder()

		server.ServeHTTP(response, request)

		assertResponseBody(t, response.Body.String(), "10")
	})
}
```

注意，我们*暂时*还是不去操心 store 怎么做，眼下只求编译器尽快闭嘴。

你应该养成这样的习惯：先保证代码能编译，再保证代码能通过测试。

在代码还编译不过的时候就去加功能（比如 stub store），只会让潜在的编译问题*越滚越多*。

现在 `main.go` 也因为同样的原因编译不过了。

```go
func main() {
	server := &PlayerServer{}
	log.Fatal(http.ListenAndServe(":5000", server))
}
```

终于，代码全部能编译了，但测试还在失败

```
=== RUN   TestGETPlayers/returns_the_Pepper's_score
panic: runtime error: invalid memory address or nil pointer dereference [recovered]
    panic: runtime error: invalid memory address or nil pointer dereference
```

原因是我们没有在测试里传入 `PlayerStore`。我们得现造一个 stub 出来。

```go
//server_test.go
type StubPlayerStore struct {
	scores map[string]int
}

func (s *StubPlayerStore) GetPlayerScore(name string) int {
	score := s.scores[name]
	return score
}
```

map 是为测试快速搭一个键值存储 stub 的好办法。现在让我们为测试创建这样一个 store，并把它传给 `PlayerServer`。

```go
//server_test.go
func TestGETPlayers(t *testing.T) {
	store := StubPlayerStore{
		map[string]int{
			"Pepper": 20,
			"Floyd":  10,
		},
	}
	server := &PlayerServer{&store}

	t.Run("returns Pepper's score", func(t *testing.T) {
		request := newGetScoreRequest("Pepper")
		response := httptest.NewRecorder()

		server.ServeHTTP(response, request)

		assertResponseBody(t, response.Body.String(), "20")
	})

	t.Run("returns Floyd's score", func(t *testing.T) {
		request := newGetScoreRequest("Floyd")
		response := httptest.NewRecorder()

		server.ServeHTTP(response, request)

		assertResponseBody(t, response.Body.String(), "10")
	})
}
```

测试现在通过了，代码看起来也更舒服了。有了 store 的引入，代码背后的*意图*更清楚了。我们是在告诉读者：因为*这些数据存在 `PlayerStore` 里*，所以把它跟 `PlayerServer` 一起使用时，你应该得到如下的响应。

### 运行应用程序

现在测试通过了，完成这次重构前还剩最后一件事：确认应用程序真的能工作。程序应该能启动，但如果你访问 `http://localhost:5000/players/Pepper`，会得到一个糟糕的响应。

原因是我们没有传入 `PlayerStore`。

我们需要做一个它的实现，但眼下这很难，因为我们还没存任何有意义的数据，所以暂时只能硬编码。

```go
//main.go
type InMemoryPlayerStore struct{}

func (i *InMemoryPlayerStore) GetPlayerScore(name string) int {
	return 123
}

func main() {
	server := &PlayerServer{&InMemoryPlayerStore{}}
	log.Fatal(http.ListenAndServe(":5000", server))
}
```

再跑一次 `go build`，访问同一个 URL，你应该会得到 `"123"`。不怎么样，但在真正存数据之前，我们也只能做到这一步了。
另外，应用启动了却实际上不能用，这种感觉也不好——我们只能靠手动测试才能发现问题。

接下来我们有几个选择

-   处理玩家不存在的情况
-   处理 `POST /players/{name}` 场景

虽然 `POST` 场景能让我们离"正常路径"更近，但我觉得先解决玩家缺失的场景会更容易些，因为我们正身处这个上下文之中。剩下的后面再说。

## 先写测试

往现有的测试套件里加一个玩家缺失的场景

```go
//server_test.go
t.Run("returns 404 on missing players", func(t *testing.T) {
	request := newGetScoreRequest("Apollo")
	response := httptest.NewRecorder()

	server.ServeHTTP(response, request)

	got := response.Code
	want := http.StatusNotFound

	if got != want {
		t.Errorf("got status %d want %d", got, want)
	}
})
```

## 试着运行测试

```
=== RUN   TestGETPlayers/returns_404_on_missing_players
    --- FAIL: TestGETPlayers/returns_404_on_missing_players (0.00s)
        server_test.go:56: got status 200 want 404
```

## 写足够的代码让它通过

```go
//server.go
func (p *PlayerServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	player := strings.TrimPrefix(r.URL.Path, "/players/")

	w.WriteHeader(http.StatusNotFound)

	fmt.Fprint(w, p.store.GetPlayerScore(player))
}
```

有时候，TDD 布道者念叨"千万只写刚好让测试通过的最少代码"，我会狠狠翻白眼，感觉实在太学究气了。

但这个场景把道理讲得明明白白。我做了最不地道的事（明知它不对）——给**所有响应**都写上 `StatusNotFound`，可我们所有的测试竟然全过！

**只做让测试通过的最小改动，恰恰能暴露出你测试里的缺口**。拿我们的例子来说，我们并没有断言"当玩家*确实*存在于 store 中时应该返回 `StatusOK`"。

把另外两个测试更新为也断言状态码，然后把代码修好。

下面是新的测试

```go
//server_test.go
func TestGETPlayers(t *testing.T) {
	store := StubPlayerStore{
		map[string]int{
			"Pepper": 20,
			"Floyd":  10,
		},
	}
	server := &PlayerServer{&store}

	t.Run("returns Pepper's score", func(t *testing.T) {
		request := newGetScoreRequest("Pepper")
		response := httptest.NewRecorder()

		server.ServeHTTP(response, request)

		assertStatus(t, response.Code, http.StatusOK)
		assertResponseBody(t, response.Body.String(), "20")
	})

	t.Run("returns Floyd's score", func(t *testing.T) {
		request := newGetScoreRequest("Floyd")
		response := httptest.NewRecorder()

		server.ServeHTTP(response, request)

		assertStatus(t, response.Code, http.StatusOK)
		assertResponseBody(t, response.Body.String(), "10")
	})

	t.Run("returns 404 on missing players", func(t *testing.T) {
		request := newGetScoreRequest("Apollo")
		response := httptest.NewRecorder()

		server.ServeHTTP(response, request)

		assertStatus(t, response.Code, http.StatusNotFound)
	})
}

func assertStatus(t testing.TB, got, want int) {
	t.Helper()
	if got != want {
		t.Errorf("did not get correct status, got %d, want %d", got, want)
	}
}

func newGetScoreRequest(name string) *http.Request {
	req, _ := http.NewRequest(http.MethodGet, fmt.Sprintf("/players/%s", name), nil)
	return req
}

func assertResponseBody(t testing.TB, got, want string) {
	t.Helper()
	if got != want {
		t.Errorf("response body is wrong, got %q want %q", got, want)
	}
}
```

现在所有测试都要检查状态码，所以我写了一个辅助函数 `assertStatus` 来省点事。

现在前两个测试因为 404（而不是 200）而失败了，接下来就可以修改 `PlayerServer`，让它只在分数为 0 时返回 not found。

```go
//server.go
func (p *PlayerServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	player := strings.TrimPrefix(r.URL.Path, "/players/")

	score := p.store.GetPlayerScore(player)

	if score == 0 {
		w.WriteHeader(http.StatusNotFound)
	}

	fmt.Fprint(w, score)
}
```

### 存储分数

现在我们已经能从 store 里查询分数了，接下来顺理成章的就是能存入新的分数。

## 先写测试

```go
//server_test.go
func TestStoreWins(t *testing.T) {
	store := StubPlayerStore{
		map[string]int{},
	}
	server := &PlayerServer{&store}

	t.Run("it returns accepted on POST", func(t *testing.T) {
		request, _ := http.NewRequest(http.MethodPost, "/players/Pepper", nil)
		response := httptest.NewRecorder()

		server.ServeHTTP(response, request)

		assertStatus(t, response.Code, http.StatusAccepted)
	})
}
```

一开始我们先只检查：用 POST 访问这个特定路由时能拿到正确的状态码。这样可以先把"接受另一种请求并区别对待"的功能做出来，跟 `GET /players/{name}` 区分开。等这个跑通了，我们再开始断言处理器跟 store 的交互。

## 试着运行测试

```
=== RUN   TestStoreWins/it_returns_accepted_on_POST
    --- FAIL: TestStoreWins/it_returns_accepted_on_POST (0.00s)
        server_test.go:70: did not get correct status, got 404, want 202
```

## 写足够的代码让它通过

记住，我们是在故意犯"罪行"，所以一个基于请求方法的 `if` 语句就够用了。

```go
//server.go
func (p *PlayerServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {

	if r.Method == http.MethodPost {
		w.WriteHeader(http.StatusAccepted)
		return
	}

	player := strings.TrimPrefix(r.URL.Path, "/players/")

	score := p.store.GetPlayerScore(player)

	if score == 0 {
		w.WriteHeader(http.StatusNotFound)
	}

	fmt.Fprint(w, score)
}
```

## 重构

处理器现在看着有点乱了。我们把它拆开，让代码更好读，把不同的功能隔离进新的函数。

```go
//server.go
func (p *PlayerServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {

	switch r.Method {
	case http.MethodPost:
		p.processWin(w)
	case http.MethodGet:
		p.showScore(w, r)
	}

}

func (p *PlayerServer) showScore(w http.ResponseWriter, r *http.Request) {
	player := strings.TrimPrefix(r.URL.Path, "/players/")

	score := p.store.GetPlayerScore(player)

	if score == 0 {
		w.WriteHeader(http.StatusNotFound)
	}

	fmt.Fprint(w, score)
}

func (p *PlayerServer) processWin(w http.ResponseWriter) {
	w.WriteHeader(http.StatusAccepted)
}
```

这样一来，`ServeHTTP` 的路由部分清晰了一些，也意味着后续在存储方面的迭代只需要待在 `processWin` 里进行。

接下来，我们要确认执行 `POST /players/{name}` 时，`PlayerStore` 会被告知记录这次胜利。

## 先写测试

我们可以给 `StubPlayerStore` 加一个新方法 `RecordWin`，然后 spy 住它的调用。

```go
//server_test.go
type StubPlayerStore struct {
	scores   map[string]int
	winCalls []string
}

func (s *StubPlayerStore) GetPlayerScore(name string) int {
	score := s.scores[name]
	return score
}

func (s *StubPlayerStore) RecordWin(name string) {
	s.winCalls = append(s.winCalls, name)
}
```

现在扩展我们的测试，第一步先检查调用次数

```go
//server_test.go
func TestStoreWins(t *testing.T) {
	store := StubPlayerStore{
		map[string]int{},
	}
	server := &PlayerServer{&store}

	t.Run("it records wins when POST", func(t *testing.T) {
		request := newPostWinRequest("Pepper")
		response := httptest.NewRecorder()

		server.ServeHTTP(response, request)

		assertStatus(t, response.Code, http.StatusAccepted)

		if len(store.winCalls) != 1 {
			t.Errorf("got %d calls to RecordWin want %d", len(store.winCalls), 1)
		}
	})
}

func newPostWinRequest(name string) *http.Request {
	req, _ := http.NewRequest(http.MethodPost, fmt.Sprintf("/players/%s", name), nil)
	return req
}
```

## 试着运行测试

```
./server_test.go:26:20: too few values in struct initializer
./server_test.go:65:20: too few values in struct initializer
```

## 写最少量的代码让测试能跑起来，并检查失败的测试输出

我们需要更新创建 `StubPlayerStore` 的地方，因为我们加了一个新字段

```go
//server_test.go
store := StubPlayerStore{
	map[string]int{},
	nil,
}
```

```
--- FAIL: TestStoreWins (0.00s)
    --- FAIL: TestStoreWins/it_records_wins_when_POST (0.00s)
        server_test.go:80: got 0 calls to RecordWin want 1
```

## 写足够的代码让它通过

因为我们只断言调用次数而不关心具体的值，所以首轮迭代可以更小一点。

要想能调用 `RecordWin`，我们需要通过修改接口来更新 `PlayerServer` 对 `PlayerStore` 的"认知"。

```go
//server.go
type PlayerStore interface {
	GetPlayerScore(name string) int
	RecordWin(name string)
}
```

这样一来，`main` 就编译不过了

```
./main.go:17:46: cannot use InMemoryPlayerStore literal (type *InMemoryPlayerStore) as type PlayerStore in field value:
    *InMemoryPlayerStore does not implement PlayerStore (missing RecordWin method)
```

编译器告诉了我们哪里出了问题。我们来给 `InMemoryPlayerStore` 补上这个方法。

```go
//main.go
type InMemoryPlayerStore struct{}

func (i *InMemoryPlayerStore) RecordWin(name string) {}
```

试着跑一下测试，代码应该又能编译了——但测试仍在失败。

现在 `PlayerStore` 有了 `RecordWin`，我们就可以在 `PlayerServer` 里调用它了

```go
//server.go
func (p *PlayerServer) processWin(w http.ResponseWriter) {
	p.store.RecordWin("Bob")
	w.WriteHeader(http.StatusAccepted)
}
```

跑一下测试，应该通过了！显然，`"Bob"` 并不是我们真想传给 `RecordWin` 的值，那就进一步完善测试。

## 先写测试

```go
//server_test.go
func TestStoreWins(t *testing.T) {
	store := StubPlayerStore{
		map[string]int{},
		nil,
	}
	server := &PlayerServer{&store}

	t.Run("it records wins on POST", func(t *testing.T) {
		player := "Pepper"

		request := newPostWinRequest(player)
		response := httptest.NewRecorder()

		server.ServeHTTP(response, request)

		assertStatus(t, response.Code, http.StatusAccepted)

		if len(store.winCalls) != 1 {
			t.Fatalf("got %d calls to RecordWin want %d", len(store.winCalls), 1)
		}

		if store.winCalls[0] != player {
			t.Errorf("did not store correct winner got %q want %q", store.winCalls[0], player)
		}
	})
}
```

现在我们知道了 `winCalls` 切片里有一个元素，就可以放心地引用第一个元素，检查它是否等于 `player`。

## 试着运行测试

```
=== RUN   TestStoreWins/it_records_wins_on_POST
    --- FAIL: TestStoreWins/it_records_wins_on_POST (0.00s)
        server_test.go:86: did not store correct winner got 'Bob' want 'Pepper'
```

## 写足够的代码让它通过

```go
//server.go
func (p *PlayerServer) processWin(w http.ResponseWriter, r *http.Request) {
	player := strings.TrimPrefix(r.URL.Path, "/players/")
	p.store.RecordWin(player)
	w.WriteHeader(http.StatusAccepted)
}
```

我们把 `processWin` 改成接收 `http.Request`，这样就能查看 URL 并提取玩家名。拿到之后，用正确的值调用 `store`，测试就通过了。

## 重构

我们可以在两处地方用同样的方式提取玩家名，那就把这段代码 DRY 一下

```go
//server.go
func (p *PlayerServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	player := strings.TrimPrefix(r.URL.Path, "/players/")

	switch r.Method {
	case http.MethodPost:
		p.processWin(w, player)
	case http.MethodGet:
		p.showScore(w, player)
	}
}

func (p *PlayerServer) showScore(w http.ResponseWriter, player string) {
	score := p.store.GetPlayerScore(player)

	if score == 0 {
		w.WriteHeader(http.StatusNotFound)
	}

	fmt.Fprint(w, score)
}

func (p *PlayerServer) processWin(w http.ResponseWriter, player string) {
	p.store.RecordWin(player)
	w.WriteHeader(http.StatusAccepted)
}
```

尽管测试全过，我们其实还没有真正能工作的软件。如果你试着运行 `main` 并按预期使用这个软件，它是不好使的，因为我们还没来得及正确实现 `PlayerStore`。不过这没关系；专注于处理器本身，让我们识别出了需要的接口，而不是试图预先把接口设计出来。

我们*可以*围绕 `InMemoryPlayerStore` 写一些测试，但它只是临时驻扎在这儿，等我们实现了更健壮的分数持久化方式（比如数据库），它就得让位了。

眼下我们要做的，是在 `PlayerServer` 和 `InMemoryPlayerStore` 之间写一个*集成测试*（integration test），把功能收个尾。这样我们就能朝"确信应用能正常工作"的目标迈进，而不必直接测试 `InMemoryPlayerStore`。不仅如此，等日后用数据库实现 `PlayerStore` 时，同一个集成测试还能直接拿来测那个实现。

### 集成测试

集成测试对验证系统中较大范围的部分能否协作很有用，但你必须记住：

-   它们更难写
-   一旦失败，往往很难定位原因（通常是集成测试里某个组件的 bug），修起来也更费劲
-   它们有时跑得更慢（因为经常要搭配"真实"组件，比如数据库）

出于这些原因，推荐你去了解一下*测试金字塔*（The Test Pyramid）。

## 先写测试

为省篇幅，我直接把最终重构好的集成测试拿给你看。

```go
// server_integration_test.go
package main

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestRecordingWinsAndRetrievingThem(t *testing.T) {
	store := InMemoryPlayerStore{}
	server := PlayerServer{&store}
	player := "Pepper"

	server.ServeHTTP(httptest.NewRecorder(), newPostWinRequest(player))
	server.ServeHTTP(httptest.NewRecorder(), newPostWinRequest(player))
	server.ServeHTTP(httptest.NewRecorder(), newPostWinRequest(player))

	response := httptest.NewRecorder()
	server.ServeHTTP(response, newGetScoreRequest(player))
	assertStatus(t, response.Code, http.StatusOK)

	assertResponseBody(t, response.Body.String(), "3")
}
```

-   我们创建了要集成到一起的两个组件：`InMemoryPlayerStore` 和 `PlayerServer`。
-   然后连发 3 个请求，为 `player` 记录 3 次胜利。这个测试里我们不太关心状态码，因为它们跟"集成得好不好"无关。
-   最后一次响应才是我们在意的（所以我们把它存进了变量 `response`），因为我们要尝试获取 `player` 的分数。

## 试着运行测试

```
--- FAIL: TestRecordingWinsAndRetrievingThem (0.00s)
    server_integration_test.go:24: response body is wrong, got '123' want '3'
```

## 写足够的代码让它通过

接下来我要放开手脚，在没写测试的情况下写的代码可能会多到让你坐立不安。

*这是允许的！*我们仍然有一个测试在检查系统能否正确工作，只不过它没有围着我们要处理的那个具体单元（`InMemoryPlayerStore`）转。

如果我在这类场景里卡住了，我会把改动 revert 回那个失败的测试，然后围绕 `InMemoryPlayerStore` 写更具体的单元测试，帮我一步步逼出解决方案。

```go
//in_memory_player_store.go
func NewInMemoryPlayerStore() *InMemoryPlayerStore {
	return &InMemoryPlayerStore{map[string]int{}}
}

type InMemoryPlayerStore struct {
	store map[string]int
}

func (i *InMemoryPlayerStore) RecordWin(name string) {
	i.store[name]++
}

func (i *InMemoryPlayerStore) GetPlayerScore(name string) int {
	return i.store[name]
}
```

-   我们需要把数据存起来，所以我给 `InMemoryPlayerStore` 结构体加了一个 `map[string]int`
-   为了方便，我写了 `NewInMemoryPlayerStore` 来初始化 store，并更新了集成测试来使用它：
    ```go
    //server_integration_test.go
    store := NewInMemoryPlayerStore()
    server := PlayerServer{store}
    ```
-   其余代码就是给这个 `map` 包了一层

集成测试通过了，现在只需把 `main` 改成使用 `NewInMemoryPlayerStore()`

```go
// main.go
package main

import (
	"log"
	"net/http"
)

func main() {
	server := &PlayerServer{NewInMemoryPlayerStore()}
	log.Fatal(http.ListenAndServe(":5000", server))
}
```

构建、运行，然后用 `curl` 试试。

-   多跑几次，想换玩家名也随你 `curl -X POST http://localhost:5000/players/Pepper`
-   用 `curl http://localhost:5000/players/Pepper` 查分数

漂亮！你已经做出了一个类 REST 的服务。想继续往前走，你需要选一个数据存储，把分数持久化得比程序的运行时间更久。

-   选一个存储（Bolt？Mongo？Postgres？文件系统？）
-   让 `PostgresPlayerStore` 实现 `PlayerStore`
-   用 TDD 把功能做出来，确保它没问题
-   把它插进集成测试，确认一切照旧
-   最后把它接进 `main`

## 重构

胜利在望！现在花点功夫，防止出现这样的并发错误

```
fatal error: concurrent map read and map write
```

通过加互斥锁（mutex），我们可以强制保证并发安全，尤其是 `RecordWin` 函数里那个计数器。关于互斥锁的更多内容，可以在 [Sync 一章](./sync.md)里读到。

## 收尾

### `http.Handler`

-   实现这个接口就能创建 web 服务器
-   用 `http.HandlerFunc` 把普通函数变成 `http.Handler`
-   用 `httptest.NewRecorder` 传进去充当 `ResponseWriter`，让你能 spy 住处理器发出的响应
-   用 `http.NewRequest` 构造你预期会进入系统的请求

### 接口、mock 与 DI

-   让你能把系统拆成小块迭代地搭起来
-   让你开发一个需要存储的处理器时不必先有真实的存储
-   用 TDD 逼出你需要的接口

### 先犯"罪行"，再重构（然后再 commit 到版本控制）

-   你要把编译失败或测试失败当作"红"的状态，需要尽快脱身。
-   只写必要的代码走到那一步。*然后*再重构，把代码收拾漂亮。
-   在代码编译不过或测试失败时还试图做太多改动，只会让问题滚雪球。
-   坚持这套做法会逼着你写小测试，小测试意味着小改动，这让复杂系统的开发始终可控。
